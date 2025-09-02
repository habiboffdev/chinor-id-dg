// Utility functions for Opportuni Platform

// API Base URL - automatically detects environment
const host = window.location.hostname;
const port = window.location.port;
const proto = window.location.protocol;
// Treat common dev/lan hosts as local
const isLoopbackHost = ['localhost', '127.0.0.1', '0.0.0.0', '::1'].includes(host);
const isPrivateIP = /^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[0-1])\.)/.test(host);
const isDevLike = isLoopbackHost || isPrivateIP;

// Allow runtime override before api.js loads
let API_BASE_URL;
if (typeof window !== 'undefined' && typeof window.API_BASE_URL === 'string' && window.API_BASE_URL) {
    API_BASE_URL = window.API_BASE_URL;
} else if (isDevLike) {
    // If frontend runs on 8080 or 8081, assume Django on 8000
    const backendHost = host === '0.0.0.0' ? 'localhost' : host;
    const isFrontendDevPort = port === '8080' || port === '8081' || port === '';
    const backendPort = isFrontendDevPort ? '8000' : (port || '8000');
    API_BASE_URL = `${proto}//${backendHost}:${backendPort}/api`;
} else {
    // Default to same-origin /api in production behind proxy
    API_BASE_URL = '/api';
}

// Global debug flag (set to true in dev HTML if needed)
window.DEBUG = window.DEBUG ?? isDevLike;

// Safe Logger to avoid leaking sensitive info + keep a small ring buffer for sharing logs
const Logger = (() => {
    // Capture original console to avoid recursion if window.console is overridden later
    const rawConsole = (typeof window !== 'undefined' && window.console) ? window.console : {
        log: () => {}, info: () => {}, debug: () => {}, warn: () => {}, error: () => {}
    };
    const enabled = !!window.DEBUG;
    // In-memory ring buffer (bounded) for easy sharing
    const CAP = 500;
    const buf = [];
    const pushBuf = (level, args) => {
        try {
            const ts = new Date().toISOString();
            const safe = args.map(sanitize);
            const line = `[${ts}] ${level.toUpperCase()} ${safe.map(a => (typeof a === 'string' ? a : JSON.stringify(a))).join(' ')}`;
            buf.push(line);
            if (buf.length > CAP) buf.shift();
        } catch { /* noop */ }
    };

    const maskEmail = (email) => {
        if (typeof email !== 'string') return email;
        const [user, domain] = email.split('@');
        if (!domain) return email;
        const maskedUser = user.length <= 2 ? '*'.repeat(user.length) : user[0] + '*'.repeat(Math.max(1, user.length - 2)) + user.slice(-1);
        return `${maskedUser}@${domain}`;
    };

    const redactObject = (value, keyPath = '') => {
        if (value == null) return value;
        const lowerKey = keyPath.toLowerCase();
        // Redact sensitive keys (exact or well-known patterns), but allow benign keys like hasToken
        const sensitiveExact = new Set(['password', 'token', 'access', 'refresh', 'authorization', 'auth', 'secret', 'apikey', 'api_key', 'jwt', 'bearer']);
        const isSensitive = sensitiveExact.has(lowerKey) || /(^|_)token$/.test(lowerKey) || lowerKey === 'authorization';
        if (isSensitive) return '[redacted]';
        if (lowerKey.endsWith('email')) return maskEmail(String(value));
        return value;
    };

    const sanitize = (arg) => {
        try {
            if (arg == null) return arg;
            if (typeof arg === 'string') return arg.replace(/(Bearer\s+)?[A-Za-z0-9-_]{10,}\.[A-Za-z0-9-_]{10,}(\.[A-Za-z0-9-_]{10,})?/g, '[redacted-token]');
            if (typeof arg !== 'object') return arg;
            // Shallow copy with key-based redaction
            if (Array.isArray(arg)) return arg.slice(0, 10).map((v) => sanitize(v));
            const out = {};
            Object.keys(arg).slice(0, 50).forEach(k => {
                const v = arg[k];
                out[k] = sanitize(redactObject(v, k));
            });
            return out;
        } catch {
            return '[unserializable]';
        }
    };

    const wrap = (level) => (...args) => {
        // Always buffer logs (sanitized), even if console printing is disabled
        pushBuf(level, args);
        if (level === 'error') {
            // Always log a minimal error; include details only when DEBUG
            const [msg, err, ...rest] = args;
            if (enabled) {
                rawConsole.error('[ERROR]', sanitize(msg), sanitize(err?.message || err), err && err.stack ? String(err.stack).split('\n').slice(0, 2).join('\n') : undefined, ...rest.map(sanitize));
            } else {
                rawConsole.error('[ERROR]', sanitize(msg));
            }
            return;
        }
        if (!enabled) return; // Only log non-errors in debug
        const printer = rawConsole[level] || rawConsole.log;
        try {
            printer.apply(rawConsole, args.map(sanitize));
        } catch {
            // No-op if console not available
        }
    };

    return {
        debug: wrap('debug'),
        info: wrap('info'),
        warn: wrap('warn'),
        error: wrap('error'),
        dump: () => buf.join('\n'),
        clear: () => { buf.length = 0; },
    };
})();

// Expose Logger globally
window.Logger = Logger;

// Global error hooks to capture unexpected issues
window.addEventListener('error', (e) => {
    try { Logger.error('UncaughtError', e.error || e.message || e); } catch {}
});
window.addEventListener('unhandledrejection', (e) => {
    try { Logger.error('UnhandledRejection', e.reason || e); } catch {}
});

// Utility functions
const Utils = {
    // Security helpers
    escapeHTML(str) {
        if (str == null) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    sanitizeHTML(html) {
        // Lightweight sanitizer: strips scripts and dangerous attributes; allow only http(s) in href/src
        try {
            const template = document.createElement('template');
            template.innerHTML = html || '';
            const walker = (node) => {
                // Remove script/style/iframe
                if (node.nodeType === 1) {
                    const tag = node.tagName.toLowerCase();
                    if (['script', 'style', 'iframe', 'object', 'embed'].includes(tag)) {
                        node.remove();
                        return;
                    }
                    // Remove event handlers and javascript: URLs
                    [...node.attributes].forEach(attr => {
                        const name = attr.name.toLowerCase();
                        const value = attr.value || '';
                        if (name.startsWith('on')) {
                            node.removeAttribute(attr.name);
                            return;
                        }
                        if ((name === 'href' || name === 'src')) {
                            const valLower = value.trim().toLowerCase();
                            if (valLower.startsWith('javascript:') || valLower.startsWith('data:')) {
                                node.removeAttribute(attr.name);
                            }
                        }
                        if (name === 'target' && value === '_blank') {
                            // Ensure noopener for new tabs
                            if (!node.getAttribute('rel')) node.setAttribute('rel', 'noopener noreferrer');
                        }
                    });
                }
                // Recurse
                let child = node.firstChild;
                while (child) {
                    const next = child.nextSibling;
                    walker(child);
                    child = next;
                }
            };
            walker(template.content || template);
            return template.innerHTML;
        } catch {
            return '';
        }
    },
    // DOM helpers
    $(selector) {
        return document.querySelector(selector);
    },

    $$(selector) {
        return document.querySelectorAll(selector);
    },

    createElement(tag, className = '', innerHTML = '') {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (innerHTML) element.innerHTML = Utils.sanitizeHTML(innerHTML);
        return element;
    },

    // Local storage helpers
    storage: {
        set(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (error) {
                Logger.error('Error saving to localStorage', error);
            }
        },

        get(key) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : null;
            } catch (error) {
                Logger.error('Error reading from localStorage', error);
                return null;
            }
        },

        remove(key) {
            try {
                localStorage.removeItem(key);
            } catch (error) {
                Logger.error('Error removing from localStorage', error);
            }
        },

        clear() {
            try {
                localStorage.clear();
            } catch (error) {
                Logger.error('Error clearing localStorage', error);
            }
        }
    },

    // URL helpers
    getQueryParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params.entries()) {
            result[key] = value;
        }
        return result;
    },

    updateURL(params) {
        const url = new URL(window.location);
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.set(key, params[key]);
            } else {
                url.searchParams.delete(key);
            }
        });
        window.history.pushState({}, '', url);
    },

    // Form helpers
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    },

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    validatePhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    },

    validateURL(url) {
        try {
            const u = new URL(url);
            return u.protocol === 'http:' || u.protocol === 'https:';
        } catch {
            return false;
        }
    },

    // Date helpers
    formatDate(date, options = {}) {
        if (!date) return 'No date provided';
        try {
            const defaultOptions = {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            };
            return new Date(date).toLocaleDateString('en-US', { ...defaultOptions, ...options });
        } catch (e) {
            Logger.error('Error formatting date', e);
            return 'Invalid date';
        }
    },

    formatDateTime(date) {
        if (!date) return 'No date provided';
        try {
            return new Date(date).toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            Logger.error('Error formatting date time', e);
            return 'Invalid date';
        }
    },

    getRelativeTime(date) {
        if (!date) return 'Unknown time';
        
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        const weeks = Math.floor(days / 7);
        const months = Math.floor(days / 30);
        const years = Math.floor(days / 365);

        if (years > 0) return `${years} year${years > 1 ? 's' : ''} ago`;
        if (months > 0) return `${months} month${months > 1 ? 's' : ''} ago`;
        if (weeks > 0) return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    },

    // String helpers
    truncate(str, length = 100) {
        if (!str) return '';
        if (str.length <= length) return str;
        return str.substring(0, length) + '...';
    },

    slugify(str) {
        return str
            .toLowerCase()
            .replace(/[^\w ]+/g, '')
            .replace(/ +/g, '-');
    },

    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    // Number helpers
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    },

    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    // Array helpers
    groupBy(array, key) {
        return array.reduce((groups, item) => {
            const value = item[key];
            if (!groups[value]) {
                groups[value] = [];
            }
            groups[value].push(item);
            return groups;
        }, {});
    },

    sortBy(array, key, direction = 'asc') {
        return [...array].sort((a, b) => {
            const aVal = a[key];
            const bVal = b[key];
            
            if (direction === 'asc') {
                return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
            } else {
                return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
            }
        });
    },

    // Async helpers
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // File helpers
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    isImageFile(file) {
        return file.type.startsWith('image/');
    },

    isPDFFile(file) {
        return file.type === 'application/pdf';
    },

    // Animation helpers
    animateCounter(element, start, end, duration = 1000) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= end) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current);
        }, 16);
    },

    // Scroll helpers
    scrollToTop(smooth = true) {
        window.scrollTo({
            top: 0,
            behavior: smooth ? 'smooth' : 'auto'
        });
    },

    scrollToElement(element, offset = 0) {
        const elementPosition = element.offsetTop - offset;
        window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
        });
    },

    // Device detection
    isMobile() {
        return window.innerWidth <= 768;
    },

    isTablet() {
        return window.innerWidth > 768 && window.innerWidth <= 1024;
    },

    isDesktop() {
        return window.innerWidth > 1024;
    },

    // Color helpers
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    },

    // Random helpers
    generateId() {
        return Math.random().toString(36).substr(2, 9);
    },

    randomColor() {
        const colors = [
            'bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500',
            'bg-purple-500', 'bg-pink-500', 'bg-indigo-500', 'bg-orange-500'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    },

    // Toast notification system
    showToast(message, type = 'info', duration = 3000) {
        // Create toast container if it doesn't exist
        let toastContainer = this.$('#toast-container');
        if (!toastContainer) {
            toastContainer = this.createElement('div', 'fixed top-4 right-4 z-50 space-y-2');
            toastContainer.id = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        const borderClass = type === 'success' ? 'border-green-400' :
            type === 'error' ? 'border-red-400' :
            type === 'warning' ? 'border-yellow-400' : 'border-blue-400';
        const icon = type === 'success' ? 'check-circle' :
            type === 'error' ? 'exclamation-circle' :
            type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        const iconColor = type === 'success' ? 'text-green-400' :
            type === 'error' ? 'text-red-400' :
            type === 'warning' ? 'text-yellow-400' : 'text-blue-400';

        const toast = this.createElement('div', `transform transition-all duration-300 translate-x-full opacity-0 max-w-sm bg-white border-l-4 rounded-lg shadow-lg p-4 ${borderClass}`);
        const row = this.createElement('div', 'flex items-center');
        const iconWrap = this.createElement('div', 'flex-shrink-0');
        const iconEl = this.createElement('i', `fas fa-${icon} ${iconColor}`);
        iconWrap.appendChild(iconEl);
        const textWrap = this.createElement('div', 'ml-3');
        const textP = this.createElement('p', 'text-sm font-medium text-gray-900');
        textP.textContent = String(message);
        textWrap.appendChild(textP);
        const closeWrap = this.createElement('div', 'ml-auto pl-3');
        const closeBtn = this.createElement('button', 'text-gray-400 hover:text-gray-600');
        closeBtn.setAttribute('type', 'button');
        const closeIcon = this.createElement('i', 'fas fa-times');
        closeBtn.addEventListener('click', () => {
            if (toast.parentElement) toast.parentElement.removeChild(toast);
        });
        closeBtn.appendChild(closeIcon);
        closeWrap.appendChild(closeBtn);
        row.appendChild(iconWrap);
        row.appendChild(textWrap);
        row.appendChild(closeWrap);
        toast.appendChild(row);
        toastContainer.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
        }, 100);

        // Auto remove
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('translate-x-full', 'opacity-0');
                setTimeout(() => {
                    if (toast.parentElement) toast.remove();
                }, 300);
            }
        }, duration);
    },

    // Cookie helpers
    setCookie(name, value, days = 7) {
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
    },

    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    },

    deleteCookie(name) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    }
};

// Export for use in other modules
window.Utils = Utils;
