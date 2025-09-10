// Theme Toggle Utility for Opportuni
// Manages light/dark mode switching with localStorage persistence

class ThemeManager {
    constructor() {
        this.storageKey = 'opportuni-theme';
        this.attrName = 'data-theme';
        this.init();
    }

    init() {
        // Load saved theme or default to dark mode
        const savedTheme = this.getSavedTheme();
        const preferredTheme = savedTheme || this.getSystemPreference();
        
        this.setTheme(preferredTheme);
        this.setupToggleButtons();
        this.listenForSystemChanges();
    }

    getSavedTheme() {
        try {
            return localStorage.getItem(this.storageKey);
        } catch (error) {
            console.warn('Failed to read theme from localStorage:', error);
            return null;
        }
    }

    getSystemPreference() {
        // Default to dark mode as per brand guidelines
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            return 'light';
        }
        return 'dark';
    }

    setTheme(theme) {
        const body = document.body;
        const isDark = theme === 'dark';

        // Apply new attribute-based theming (pro approach)
        body.setAttribute(this.attrName, theme); // e.g. data-theme="dark" or "light"
        // Maintain backward compatibility with existing .light-mode selectors
        body.classList.toggle('light-mode', !isDark); // TODO: remove after full migration

        // Persist preference
        try { localStorage.setItem(this.storageKey, theme); } catch (e) { /* ignore */ }

        this.updateToggleButtons(theme);

        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme, isDark } }));
    }

    getCurrentTheme() {
        // Prefer attribute; fallback to legacy class
        const attr = document.body.getAttribute(this.attrName);
        if (attr === 'light' || attr === 'dark') return attr;
        return document.body.classList.contains('light-mode') ? 'light' : 'dark';
    }

    toggleTheme() {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        document.body.classList.add('theme-transitioning');
        setTimeout(() => document.body.classList.remove('theme-transitioning'), 300);
    }

    setupToggleButtons() {
        // Find all theme toggle buttons and setup click handlers
        const toggleButtons = document.querySelectorAll('.theme-toggle, [data-theme-toggle]');
        
        toggleButtons.forEach((button) => {
            button.removeEventListener('click', this.handleToggleClick);
            button.addEventListener('click', this.handleToggleClick.bind(this));
        });

        // Also setup a global click listener for dynamically added buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-toggle, [data-theme-toggle]')) {
                console.log('ThemeManager: Global click handler triggered');
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }

    handleToggleClick(e) {
        e.preventDefault();
        this.toggleTheme();
    }

    updateToggleButtons(theme) {
        const toggleButtons = document.querySelectorAll('.theme-toggle, [data-theme-toggle]');
        const isDark = theme === 'dark';
        
        toggleButtons.forEach(button => {
            // Update aria-label for accessibility
            button.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} mode`);
            
            // Update title tooltip
            button.setAttribute('title', `Switch to ${isDark ? 'light' : 'dark'} mode`);
            
            // Handle data-theme-icon approach (used in navbars)
            const lightIcon = button.querySelector('[data-theme-icon="light"]');
            const darkIcon = button.querySelector('[data-theme-icon="dark"]');
            
            if (lightIcon && darkIcon) {
                if (isDark) {
                    // Show sun icon (for switching to light)
                    lightIcon.style.display = 'inline-block';
                    darkIcon.style.display = 'none';
                } else {
                    // Show moon icon (for switching to dark)
                    lightIcon.style.display = 'none';
                    darkIcon.style.display = 'inline-block';
                }
            }
            
            // Handle traditional icon-sun/icon-moon approach
            const sunIcon = button.querySelector('.icon-sun, .fa-sun:not([data-theme-icon])');
            const moonIcon = button.querySelector('.icon-moon, .fa-moon:not([data-theme-icon])');
            
            if (sunIcon && moonIcon) {
                if (isDark) {
                    sunIcon.style.display = 'inline-block';
                    moonIcon.style.display = 'none';
                } else {
                    sunIcon.style.display = 'none';
                    moonIcon.style.display = 'inline-block';
                }
            }
            
            // Update text content if it contains theme info
            const text = button.querySelector('.theme-text');
            if (text) {
                text.textContent = isDark ? 'Light mode' : 'Dark mode';
            }
        });
    }

    listenForSystemChanges() {
    // Listen for system theme changes (only if user hasn't explicitly chosen)
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
            
            mediaQuery.addEventListener('change', (e) => {
                // Only auto-switch if user hasn't manually set a preference
                const savedTheme = this.getSavedTheme();
                if (!savedTheme) {
                    const newTheme = e.matches ? 'light' : 'dark';
                    this.setTheme(newTheme);
                }
            });
        }
    }

    // Method to reinitialize buttons (call this after dynamic content loads)
    reinitializeButtons() {
        this.setupToggleButtons();
        this.updateToggleButtons(this.getCurrentTheme());
    }

    // Utility method to create a theme toggle button
    createToggleButton(options = {}) {
        const button = document.createElement('button');
        const {
            className = 'theme-toggle',
            showText = false,
            iconOnly = true
        } = options;
        
        button.className = className;
        button.setAttribute('aria-label', 'Toggle theme');
        button.setAttribute('title', 'Toggle light/dark mode');
        
        if (iconOnly) {
            button.innerHTML = `
                <i class="fas fa-sun icon-sun"></i>
                <i class="fas fa-moon icon-moon"></i>
            `;
        } else {
            button.innerHTML = `
                <i class="fas fa-sun icon-sun"></i>
                <i class="fas fa-moon icon-moon"></i>
                ${showText ? '<span class="theme-text ml-2">Light mode</span>' : ''}
            `;
        }
        
        // Setup click handler
        button.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleTheme();
        });
        
        return button;
    }
}

// Add smooth theme transition CSS
if (!document.getElementById('theme-transition-styles')) {
    const style = document.createElement('style');
    style.id = 'theme-transition-styles';
    style.textContent = `
        .theme-transitioning * {
            transition: background-color 300ms ease-out, 
                       color 300ms ease-out, 
                       border-color 300ms ease-out,
                       box-shadow 300ms ease-out !important;
        }
        
        .theme-transitioning .brand-nav::after {
            transition: background 300ms ease-out !important;
        }
    `;
    document.head.appendChild(style);
}

// Initialize theme manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager = new ThemeManager();
    });
} else {
    window.themeManager = new ThemeManager();
}

// Also try to reinitialize after a short delay to catch any dynamically loaded content
setTimeout(() => { window.themeManager?.reinitializeButtons(); }, 600);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
