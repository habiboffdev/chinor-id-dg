// Reusable UI Components for Opportuni Platform

// Toast notification system
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = Utils.$('#toast-container');
    if (!toastContainer) {
        console.error('Toast container not found');
        return;
    }

    const toast = Utils.createElement('div', `toast-enter bg-white border-l-4 p-4 rounded-lg shadow-lg max-w-sm ${getToastStyles(type)}`);
    
    const row = Utils.createElement('div', 'flex items-center');
    const iconWrap = Utils.createElement('div', 'flex-shrink-0');
    iconWrap.innerHTML = `<i class="fas ${getToastIcon(type)} text-lg"></i>`;
    const textWrap = Utils.createElement('div', 'ml-3 flex-1');
    const textP = Utils.createElement('p', 'text-sm text-gray-900');
    textP.textContent = String(message);
    textWrap.appendChild(textP);
    const closeWrap = Utils.createElement('div', 'ml-4 flex-shrink-0');
    const btn = Utils.createElement('button', 'text-gray-400 hover:text-gray-600 focus:outline-none');
    btn.addEventListener('click', () => removeToast(toast));
    btn.innerHTML = '<i class="fas fa-times"></i>';
    closeWrap.appendChild(btn);
    row.appendChild(iconWrap);
    row.appendChild(textWrap);
    row.appendChild(closeWrap);
    toast.appendChild(row);
    
    toastContainer.appendChild(toast);
    
    // Auto remove after duration
    setTimeout(() => removeToast(toast), duration);
}

function getToastStyles(type) {
    switch (type) {
        case 'success':
            return 'border-green-500 text-green-700';
        case 'error':
            return 'border-red-500 text-red-700';
        case 'warning':
            return 'border-yellow-500 text-yellow-700';
        default:
            return 'border-blue-500 text-blue-700';
    }
}

function getToastIcon(type) {
    switch (type) {
        case 'success':
            return 'fa-check-circle text-green-500';
        case 'error':
            return 'fa-exclamation-circle text-red-500';
        case 'warning':
            return 'fa-exclamation-triangle text-yellow-500';
        default:
            return 'fa-info-circle text-blue-500';
    }
}

function removeToast(toast) {
    if (!toast) return;
    toast.classList.remove('toast-enter');
    toast.classList.add('toast-exit');
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}

// Loading spinner
function showLoading(show = true) {
    const spinner = Utils.$('#loadingOverlay');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
        if (show) {
            spinner.classList.remove('hidden');
        } else {
            spinner.classList.add('hidden');
        }
    }
}

// Card component
function createCard(options = {}) {
    const {
        title = '',
        content = '',
        footer = '',
        className = '',
        onClick = null
    } = options;
    
    const card = Utils.createElement('div', `bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 ${className}`);
    
    if (onClick) {
        card.style.cursor = 'pointer';
        card.addEventListener('click', onClick);
    }
    
    card.innerHTML = `
        ${title ? `<div class="p-6 pb-4"><h3 class="text-lg font-semibold text-gray-900">${title}</h3></div>` : ''}
        ${content ? `<div class="px-6 pb-4">${content}</div>` : ''}
        ${footer ? `<div class="px-6 py-4 bg-gray-50 rounded-b-xl">${footer}</div>` : ''}
    `;
    
    return card;
}

// Badge component
function createBadge(text, type = 'primary', size = 'md') {
    const sizeClasses = {
        sm: 'px-2 py-1 text-xs',
        md: 'px-3 py-1 text-sm',
        lg: 'px-4 py-2 text-base'
    };
    
    const typeClasses = {
        primary: 'bg-primary-100 text-primary-800',
        secondary: 'bg-secondary-100 text-secondary-800',
        success: 'bg-green-100 text-green-800',
        warning: 'bg-yellow-100 text-yellow-800',
        error: 'bg-red-100 text-red-800',
        gray: 'bg-gray-100 text-gray-800'
    };
    
    return Utils.createElement(
        'span',
        `inline-flex items-center font-medium rounded-full ${sizeClasses[size]} ${typeClasses[type]}`,
        text
    );
}

// Button component
function createButton(options = {}) {
    const {
        text = '',
        type = 'primary',
        size = 'md',
        icon = '',
        onClick = null,
        disabled = false,
        className = ''
    } = options;
    
    const sizeClasses = {
        sm: 'px-3 py-2 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg'
    };
    
    const typeClasses = {
        primary: 'text-white',
        secondary: 'bg-white border border-gray-300 hover:bg-gray-50 text-gray-700',
        success: 'bg-green-600 hover:bg-green-700 text-white',
        warning: 'bg-yellow-600 hover:bg-yellow-700 text-white',
        error: 'bg-red-600 hover:bg-red-700 text-white'
    };
    
    const button = Utils.createElement(
        'button',
        `btn-ripple font-semibold rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 ${sizeClasses[size]} ${typeClasses[type]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`
    );
    if (type === 'primary') button.style.background = 'var(--brand-primary)';
    
    button.innerHTML = `
        ${icon ? `<i class="fas ${icon} ${text ? 'mr-2' : ''}"></i>` : ''}
        ${text}
    `;
    
    if (onClick && !disabled) {
        button.addEventListener('click', onClick);
    }
    
    button.disabled = disabled;
    
    return button;
}

// Form input component
function createFormInput(options = {}) {
    const {
        type = 'text',
        name = '',
        label = '',
        placeholder = '',
        required = false,
        value = '',
        className = ''
    } = options;
    
    const container = Utils.createElement('div', `form-group ${className}`);
    
    container.innerHTML = `
        ${label ? `<label class="block text-sm font-medium text-gray-700 mb-2">${label}</label>` : ''}
        <input type="${type}" 
               name="${name}" 
               ${placeholder ? `placeholder="${placeholder}"` : ''}
               ${required ? 'required' : ''}
               value="${value}"
               class="form-input w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200">
    `;
    
    return container;
}

// Dropdown component
function createDropdown(options = {}) {
    const {
        trigger = '',
        items = [],
        className = ''
    } = options;
    
    const dropdown = Utils.createElement('div', `relative inline-block ${className}`);
    
    dropdown.innerHTML = `
        <button class="dropdown-trigger flex items-center justify-between w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500">
            ${trigger}
            <i class="fas fa-chevron-down ml-2"></i>
        </button>
        <div class="dropdown-menu hidden absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
            <div class="py-1">
                ${items.map(item => `
                    <a href="#" class="dropdown-item block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" data-value="${item.value}">
                        ${item.icon ? `<i class="fas ${item.icon} mr-2"></i>` : ''}
                        ${item.label}
                    </a>
                `).join('')}
            </div>
        </div>
    `;
    
    const trigger_btn = dropdown.querySelector('.dropdown-trigger');
    const menu = dropdown.querySelector('.dropdown-menu');
    
    trigger_btn.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('hidden');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
        menu.classList.add('hidden');
    });
    
    return dropdown;
}

// Modal component
function createModal(options = {}) {
    const {
        title = '',
        content = '',
        footer = '',
        size = 'md',
        onClose = null
    } = options;
    
    const sizeClasses = {
        sm: 'max-w-md',
        md: 'max-w-lg',
        lg: 'max-w-2xl',
        xl: 'max-w-4xl'
    };
    
    const modal = Utils.createElement('div', 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 modal-enter');
    
    modal.innerHTML = `
        <div class="bg-white rounded-2xl shadow-2xl ${sizeClasses[size]} w-full relative">
            <div class="flex items-center justify-between p-6 border-b">
                <h3 class="text-lg font-semibold text-gray-900">${title}</h3>
                <button class="modal-close text-gray-400 hover:text-gray-600 text-2xl">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="p-6">
                ${content}
            </div>
            ${footer ? `<div class="px-6 py-4 bg-gray-50 rounded-b-2xl">${footer}</div>` : ''}
        </div>
    `;
    
    const closeBtn = modal.querySelector('.modal-close');
    const closeModal = () => {
        modal.classList.remove('modal-enter');
        modal.classList.add('modal-exit');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
        if (onClose) onClose();
    };
    
    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    return modal;
}

// Table component
function createTable(options = {}) {
    const {
        headers = [],
        rows = [],
        className = '',
        sortable = true,
        pagination = false
    } = options;
    
    const table = Utils.createElement('div', `overflow-x-auto ${className}`);
    
    table.innerHTML = `
        <table class="min-w-full bg-white border border-gray-200 rounded-lg">
            <thead class="bg-gray-50">
                <tr>
                    ${headers.map(header => `
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${sortable ? 'cursor-pointer hover:bg-gray-100' : ''}" 
                            ${sortable ? `data-sort="${header.key}"` : ''}>
                            ${header.label}
                            ${sortable ? '<i class="fas fa-sort ml-1 text-gray-400"></i>' : ''}
                        </th>
                    `).join('')}
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
                ${rows.map(row => `
                    <tr class="hover:bg-gray-50">
                        ${headers.map(header => `
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                ${row[header.key] || ''}
                            </td>
                        `).join('')}
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    if (sortable) {
        setupTableSorting(table);
    }
    
    return table;
}

function setupTableSorting(table) {
    const headers = table.querySelectorAll('th[data-sort]');
    headers.forEach(header => {
        header.addEventListener('click', () => {
            const sortKey = header.dataset.sort;
            // Implementation for sorting would go here
            console.log('Sort by:', sortKey);
        });
    });
}

// Pagination component
function createPagination(options = {}) {
    const {
        currentPage = 1,
        totalPages = 1,
        onPageChange = null
    } = options;
    
    const pagination = Utils.createElement('div', 'flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200 sm:px-6');
    
    pagination.innerHTML = `
        <div class="flex-1 flex justify-between sm:hidden">
            <button class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}"
                    ${currentPage === 1 ? 'disabled' : ''} data-page="${currentPage - 1}">
                Previous
            </button>
            <button class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : ''}"
                    ${currentPage === totalPages ? 'disabled' : ''} data-page="${currentPage + 1}">
                Next
            </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
                <p class="text-sm text-gray-700">
                    Page <span class="font-medium">${currentPage}</span> of <span class="font-medium">${totalPages}</span>
                </p>
            </div>
            <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    ${generatePaginationButtons(currentPage, totalPages)}
                </nav>
            </div>
        </div>
    `;
    
    // Add click handlers
    pagination.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON' && e.target.dataset.page) {
            const page = parseInt(e.target.dataset.page);
            if (onPageChange && page >= 1 && page <= totalPages) {
                onPageChange(page);
            }
        }
    });
    
    return pagination;
}

function generatePaginationButtons(currentPage, totalPages) {
    let buttons = [];
    
    // Previous button
    buttons.push(`
        <button class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : ''}"
                ${currentPage === 1 ? 'disabled' : ''} data-page="${currentPage - 1}">
            <i class="fas fa-chevron-left"></i>
        </button>
    `);
    
    // Page numbers (simplified for space)
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        buttons.push(`
            <button class="relative inline-flex items-center px-4 py-2 border text-sm font-medium ${i === currentPage ? 'z-10 bg-primary-50 border-primary-500 text-primary-600' : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'}"
                    data-page="${i}">
                ${i}
            </button>
        `);
    }
    
    // Next button
    buttons.push(`
        <button class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : ''}"
                ${currentPage === totalPages ? 'disabled' : ''} data-page="${currentPage + 1}">
            <i class="fas fa-chevron-right"></i>
        </button>
    `);
    
    return buttons.join('');
}

// File upload component
function createFileUpload(options = {}) {
    const {
        accept = '',
        multiple = false,
        onFileSelect = null,
        className = ''
    } = options;
    
    const container = Utils.createElement('div', `file-upload ${className}`);
    
    container.innerHTML = `
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-500 transition-colors duration-200">
            <input type="file" class="hidden" ${accept ? `accept="${accept}"` : ''} ${multiple ? 'multiple' : ''}>
            <i class="fas fa-cloud-upload-alt text-4xl text-gray-400 mb-4"></i>
            <p class="text-gray-600 mb-2">Click to upload or drag and drop</p>
            <p class="text-sm text-gray-500">PNG, JPG, PDF up to 10MB</p>
        </div>
        <div class="file-list mt-4 hidden"></div>
    `;
    
    const input = container.querySelector('input[type="file"]');
    const dropZone = container.querySelector('.border-dashed');
    const fileList = container.querySelector('.file-list');
    
    // Click to upload
    dropZone.addEventListener('click', () => input.click());
    
    // File selection
    input.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        if (onFileSelect) onFileSelect(files);
        displayFiles(files, fileList);
    });
    
    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-primary-500');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-primary-500');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-primary-500');
        const files = Array.from(e.dataTransfer.files);
        if (onFileSelect) onFileSelect(files);
        displayFiles(files, fileList);
    });
    
    return container;
}

function displayFiles(files, container) {
    if (files.length === 0) {
        container.classList.add('hidden');
        return;
    }
    
    container.classList.remove('hidden');
    container.innerHTML = files.map(file => `
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-2">
            <div class="flex items-center">
                <i class="fas ${Utils.isImageFile(file) ? 'fa-image' : 'fa-file'} text-primary-600 mr-3"></i>
                <div>
                    <p class="text-sm font-medium text-gray-900">${file.name}</p>
                    <p class="text-xs text-gray-500">${Utils.formatFileSize(file.size)}</p>
                </div>
            </div>
            <button class="text-red-500 hover:text-red-700">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
}

// Export components
window.Components = {
    showToast,
    showLoading,
    createCard,
    createBadge,
    createButton,
    createFormInput,
    createDropdown,
    createModal,
    createTable,
    createPagination,
    createFileUpload
};
