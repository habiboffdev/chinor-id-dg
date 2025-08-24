// Dashboard-specific JavaScript for Opportuni Platform

// Prevent duplicate initialization
let DASHBOARD_INIT_STARTED = false;
document.addEventListener('DOMContentLoaded', function() {
    if (DASHBOARD_INIT_STARTED) return;
    DASHBOARD_INIT_STARTED = true;
    initializeDashboard();
});

// Initialize dashboard functionality
async function initializeDashboard() {
    if (window.DEBUG && window.Logger) Logger.info('Initializing dashboard');
    
    // Case 1: No token at all, redirect to login immediately 
    const token = Utils.storage.get('auth_token');
    if (!token) {
        if (window.DEBUG && window.Logger) Logger.info('No auth token found, redirecting to login');
        window.location.href = '/login.html';
        return;
    }
    
    // Case 2: Token exists, but check if it's invalid
    if (window.DEBUG && window.Logger) Logger.info('Auth token found, checking validity');
    
    // Set the token on the API instance explicitly
    api.setToken(token); 
    
    // Try to validate authentication
    try {
        // First see if we already have a user object
        if (auth.getCurrentUser()) {
            if (window.DEBUG && window.Logger) Logger.info('User already loaded in memory, proceeding with dashboard');
            continueInitialization();
            return;
        }
        
        // If not, try loading the profile to validate the token
        if (window.DEBUG && window.Logger) Logger.info('Attempting to load user profile');
        const userProfile = await api.auth.getProfile();
        
        // If we get here, the profile loaded successfully
        if (window.DEBUG && window.Logger) Logger.info('Profile loaded successfully');
        auth.currentUser = userProfile; // Set the user directly
        auth.updateUIForLoggedInUser(); // Update UI
        continueInitialization();
    } catch (error) {
        if (window.Logger) Logger.error('Failed to validate token', error);
        if (window.DEBUG && window.Logger) Logger.info('Redirecting to login page');
        window.location.href = '/login.html';
    }
}

async function continueInitialization() {
    // Check if user is a student
    const user = auth.getCurrentUser();
    if (window.DEBUG && window.Logger) Logger.info('Current user present', { present: !!user, type: user?.user_type });
    
    if (!user) {
        console.error('User object is null but auth check passed');
        showToast('Error loading user data. Please try logging in again.', 'error');
        setTimeout(() => {
            auth.logout();
        }, 2000);
        return;
    }
    
    if (user.user_type !== 'student') {
        showToast('This dashboard is for students only', 'error');
        auth.redirectToDashboard();
        return;
    }
    
    try {
        // Load dashboard data
        await loadDashboardData();
        await loadRecentApplications();
        await loadRecommendedOpportunities();
        await loadNotifications();
        
        // Setup UI interactions
        setupDashboardInteractions();
        setupResumeUpload();
        
    if (window.DEBUG && window.Logger) Logger.info('Dashboard fully loaded successfully');
    } catch (error) {
    if (window.Logger) Logger.error('Dashboard initialization error', error);
        showToast('Some dashboard data could not be loaded. Please refresh the page.', 'warning');
    }
}

// Load dashboard statistics
async function loadDashboardData() {
    try {
        const stats = await api.students.getDashboardStats();
        updateDashboardStats(stats);
    } catch (error) {
        if (window.Logger) Logger.error('Failed to load dashboard stats', error);
        // Show default stats if API fails
        updateDashboardStats({
            total_applications: 0,
            pending_applications: 0,
            accepted_applications: 0,
            rejected_applications: 0
        });
    }
}

// Update dashboard statistics display
function updateDashboardStats(stats) {
    const statsContainer = Utils.$('#dashboard-stats');
    if (!statsContainer) return;
    
    statsContainer.innerHTML = `
        <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
            <div class="flex items-center">
                <div class="p-3 bg-primary-100 rounded-full">
                    <i class="fas fa-file-alt text-primary-600 text-xl"></i>
                </div>
                <div class="ml-4">
                    <h3 class="text-2xl font-bold text-gray-900">${stats.total_applications || 0}</h3>
                    <p class="text-gray-600">Total Applications</p>
                </div>
            </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
            <div class="flex items-center">
                <div class="p-3 bg-yellow-100 rounded-full">
                    <i class="fas fa-clock text-yellow-600 text-xl"></i>
                </div>
                <div class="ml-4">
                    <h3 class="text-2xl font-bold text-gray-900">${stats.pending_applications || 0}</h3>
                    <p class="text-gray-600">Pending</p>
                </div>
            </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
            <div class="flex items-center">
                <div class="p-3 bg-green-100 rounded-full">
                    <i class="fas fa-check-circle text-green-600 text-xl"></i>
                </div>
                <div class="ml-4">
                    <h3 class="text-2xl font-bold text-gray-900">${stats.accepted_applications || 0}</h3>
                    <p class="text-gray-600">Accepted</p>
                </div>
            </div>
        </div>
        
        <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300">
            <div class="flex items-center">
                <div class="p-3 bg-red-100 rounded-full">
                    <i class="fas fa-times-circle text-red-600 text-xl"></i>
                </div>
                <div class="ml-4">
                    <h3 class="text-2xl font-bold text-gray-900">${stats.rejected_applications || 0}</h3>
                    <p class="text-gray-600">Rejected</p>
                </div>
            </div>
        </div>
    `;
}

// Load recent applications
async function loadRecentApplications() {
    try {
        const applications = await api.applications.getList({ limit: 5, ordering: '-created_at' });
        displayRecentApplications(applications.results || applications);
    } catch (error) {
        if (window.Logger) Logger.error('Failed to load recent applications', error);
        displayRecentApplications([]);
    }
}

// Display recent applications
function displayRecentApplications(applications) {
    const container = Utils.$('#recent-applications');
    if (!container) return;
    
    if (!applications || applications.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-file-alt text-4xl text-gray-300 mb-4"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No applications yet</h3>
                <p class="text-gray-600 mb-4">Start by browsing available opportunities</p>
                <a href="/opportunities.html" class="text-white px-6 py-2 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105" style="background: var(--brand-primary);">
                    Browse Opportunities
                </a>
            </div>
        `;
        return;
    }
    
    container.innerHTML = Utils.sanitizeHTML(applications.map(application => `
        <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all duration-200">
            <div class="flex items-center space-x-4">
                <div class="w-12 h-12 rounded-lg flex items-center justify-center" style="background: rgba(124,131,255,0.15);">
                    <i class="fas fa-briefcase text-primary-600"></i>
                </div>
                <div>
                    <h4 class="font-medium text-gray-900">${Utils.escapeHTML(application.opportunity_title || 'Opportunity')}</h4>
                    <p class="text-sm text-gray-600">${Utils.escapeHTML(application.organization_name || 'Organization')}</p>
                    <p class="text-xs text-gray-500">Applied ${Utils.getRelativeTime(application.created_at)}</p>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                ${getStatusBadge(application.status)}
                <button onclick="viewApplication('${Utils.escapeHTML(String(application.id))}')" class="text-primary-600 hover:text-primary-700">
                    <i class="fas fa-external-link-alt"></i>
                </button>
            </div>
        </div>
    `).join(''));
}

// Get status badge for application
function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="px-3 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">Pending</span>',
        'accepted': '<span class="px-3 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">Accepted</span>',
        'rejected': '<span class="px-3 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">Rejected</span>',
        'withdrawn': '<span class="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">Withdrawn</span>'
    };
    return badges[status] || badges['pending'];
}

// Load recommended opportunities
async function loadRecommendedOpportunities() {
    try {
        // This would typically use a recommendation algorithm
        const opportunities = await api.opportunities.getList({ limit: 3, featured: true });
        displayRecommendedOpportunities(opportunities.results || opportunities);
    } catch (error) {
        if (window.Logger) Logger.error('Failed to load recommended opportunities', error);
        displayRecommendedOpportunities([]);
    }
}

// Display recommended opportunities
function displayRecommendedOpportunities(opportunities) {
    const container = Utils.$('#recommended-opportunities');
    if (!container) return;
    
    if (!opportunities || opportunities.length === 0) {
        container.innerHTML = `
            <div class="text-center py-6">
                <i class="fas fa-lightbulb text-2xl text-gray-300 mb-2"></i>
                <p class="text-gray-600 text-sm">No recommendations available</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = opportunities.map(opportunity => `
        <div class="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all duration-200 cursor-pointer" onclick="viewOpportunity('${Utils.escapeHTML(String(opportunity.id))}')">
            <h4 class="font-medium text-gray-900 mb-1">${Utils.escapeHTML(Utils.truncate(opportunity.title, 40))}</h4>
            <p class="text-sm text-gray-600 mb-2">${Utils.escapeHTML(opportunity.organization_name)}</p>
            <span class="inline-flex items-center px-2 py-1 text-xs font-medium bg-primary-100 text-primary-800 rounded-full">
                ${Utils.escapeHTML(opportunity.opportunity_type)}
            </span>
        </div>
    `).join('');
}

// Load notifications
async function loadNotifications() {
    try {
        const notifications = await api.notifications.getList({ limit: 5, is_read: false });
        displayNotifications(notifications.results || notifications);
        updateNotificationCount(notifications.length || 0);
    } catch (error) {
        if (window.Logger) Logger.error('Failed to load notifications', error);
        displayNotifications([]);
        updateNotificationCount(0);
    }
}

// Display notifications
function displayNotifications(notifications) {
    const dropdown = Utils.$('#notifications-dropdown .max-h-96');
    if (!dropdown) return;
    
    if (!notifications || notifications.length === 0) {
        dropdown.innerHTML = `
            <div class="p-4 text-center">
                <i class="fas fa-bell-slash text-2xl text-gray-300 mb-2"></i>
                <p class="text-gray-600 text-sm">No new notifications</p>
            </div>
        `;
        return;
    }
    
    dropdown.innerHTML = Utils.sanitizeHTML(notifications.map(notification => `
        <div class="p-3 hover:bg-gray-50 border-b border-gray-100 cursor-pointer" onclick="markNotificationAsRead('${Utils.escapeHTML(String(notification.id))}')">
            <div class="flex items-start space-x-3">
                <div class="w-2 h-2 bg-primary-600 rounded-full mt-2 flex-shrink-0"></div>
                <div class="flex-1">
                    <p class="text-sm text-gray-900 font-medium">${Utils.escapeHTML(notification.title)}</p>
                    <p class="text-xs text-gray-600 mt-1">${Utils.escapeHTML(Utils.truncate(notification.message, 80))}</p>
                    <p class="text-xs text-gray-500 mt-1">${Utils.getRelativeTime(notification.created_at)}</p>
                </div>
            </div>
        </div>
    `).join(''));
}

// Update notification count
function updateNotificationCount(count) {
    const badge = Utils.$('#notification-count');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Setup dashboard interactions
function setupDashboardInteractions() {
    // Notification dropdown toggle
    window.toggleNotifications = () => {
        const dropdown = Utils.$('#notifications-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
        }
    };
    
    // User menu dropdown toggle
    window.toggleUserMenu = () => {
        const dropdown = Utils.$('#user-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
        }
    };
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        const notificationsBtn = e.target.closest('[onclick="toggleNotifications()"]');
        const userBtn = e.target.closest('[onclick="toggleUserMenu()"]');
        
        if (!notificationsBtn) {
            const notificationsDropdown = Utils.$('#notifications-dropdown');
            if (notificationsDropdown && !notificationsDropdown.contains(e.target)) {
                notificationsDropdown.classList.add('hidden');
            }
        }
        
        if (!userBtn) {
            const userDropdown = Utils.$('#user-dropdown');
            if (userDropdown && !userDropdown.contains(e.target)) {
                userDropdown.classList.add('hidden');
            }
        }
    });
}

// Setup resume upload functionality
function setupResumeUpload() {
    const dropZone = Utils.$('#resume-drop-zone');
    const fileInput = Utils.$('#resume-file');
    const fileInfo = Utils.$('#resume-file-info');
    const fileName = Utils.$('#resume-file-name');
    const uploadBtn = Utils.$('#upload-resume-btn');
    
    if (!dropZone || !fileInput) return;
    
    // Click to upload
    dropZone.addEventListener('click', () => fileInput.click());
    
    // File selection
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleResumeFile(file);
        }
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
        const file = e.dataTransfer.files[0];
        if (file) {
            handleResumeFile(file);
        }
    });
    
    // Handle file selection
    function handleResumeFile(file) {
        // Validate file type
        const allowedTypes = ['.pdf', '.doc', '.docx'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExtension)) {
            showToast('Please select a PDF, DOC, or DOCX file', 'error');
            return;
        }
        
        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            showToast('File size must be less than 10MB', 'error');
            return;
        }
        
        // Display file info
        fileName.textContent = file.name;
        fileInfo.classList.remove('hidden');
        uploadBtn.disabled = false;
        uploadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

// Show resume upload modal
window.showResumeUpload = () => {
    const modal = Utils.$('#resume-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
};

// Close resume upload modal
window.closeResumeModal = () => {
    const modal = Utils.$('#resume-modal');
    const fileInput = Utils.$('#resume-file');
    const fileInfo = Utils.$('#resume-file-info');
    const uploadBtn = Utils.$('#upload-resume-btn');
    
    if (modal) {
        modal.classList.add('hidden');
    }
    
    // Reset form
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.classList.add('hidden');
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
};

// Remove selected resume file
window.removeResumeFile = () => {
    const fileInput = Utils.$('#resume-file');
    const fileInfo = Utils.$('#resume-file-info');
    const uploadBtn = Utils.$('#upload-resume-btn');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.classList.add('hidden');
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
};

// Upload resume
window.uploadResume = async () => {
    const fileInput = Utils.$('#resume-file');
    const file = fileInput?.files[0];
    
    if (!file) {
        showToast('Please select a file first', 'error');
        return;
    }
    
    try {
        showLoading(true);
        await api.students.uploadResume(file);
        showToast('Resume uploaded successfully!', 'success');
        closeResumeModal();
    } catch (error) {
        showToast(error.message || 'Failed to upload resume', 'error');
        console.error('Resume upload error:', error);
    } finally {
        showLoading(false);
    }
};

// View application details
window.viewApplication = async (applicationId) => {
    try {
        showLoading(true);
        const application = await api.applications.getById(applicationId);
        showApplicationModal(application);
    } catch (error) {
        showToast('Failed to load application details', 'error');
        console.error('Application load error:', error);
    } finally {
        showLoading(false);
    }
};

// Show application details modal
function showApplicationModal(application) {
    const modal = createModal({
        title: 'Application Details',
        size: 'lg',
    content: `
            <div class="space-y-6">
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
            <h4 class="font-semibold text-gray-900">${Utils.escapeHTML(application.opportunity_title)}</h4>
            <p class="text-gray-600">${Utils.escapeHTML(application.organization_name)}</p>
                    </div>
                    ${getStatusBadge(application.status)}
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <h5 class="font-semibold text-gray-900 mb-2">Applied Date</h5>
                        <p class="text-gray-700">${Utils.formatDate(application.created_at)}</p>
                    </div>
                    <div>
                        <h5 class="font-semibold text-gray-900 mb-2">Status</h5>
                        <p class="text-gray-700">${Utils.capitalize(application.status)}</p>
                    </div>
                </div>
                
        ${application.cover_letter ? `
                    <div>
                        <h5 class="font-semibold text-gray-900 mb-2">Cover Letter</h5>
            <p class="text-gray-700">${Utils.escapeHTML(application.cover_letter)}</p>
                    </div>
                ` : ''}
                
        ${application.notes ? `
                    <div>
                        <h5 class="font-semibold text-gray-900 mb-2">Notes</h5>
            <p class="text-gray-700">${Utils.escapeHTML(application.notes)}</p>
                    </div>
                ` : ''}
            </div>
        `,
        footer: `
            <div class="flex justify-between">
                <div>
                    ${application.status === 'pending' ? `
                        <button onclick="withdrawApplication('${application.id}')" 
                                class="px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50">
                            Withdraw Application
                        </button>
                    ` : ''}
                </div>
                <button onclick="closeModal(this.closest('.fixed'))" 
                        class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50">
                    Close
                </button>
            </div>
        `
    });
    
    document.body.appendChild(modal);
}

// Withdraw application
window.withdrawApplication = async (applicationId) => {
    if (!confirm('Are you sure you want to withdraw this application?')) {
        return;
    }
    
    try {
        showLoading(true);
        await api.applications.withdraw(applicationId);
        showToast('Application withdrawn successfully', 'success');
        
        // Close modal and refresh applications
        const modal = Utils.$('.fixed.inset-0');
        if (modal) closeModal(modal);
        
        await loadRecentApplications();
        await loadDashboardData();
    } catch (error) {
        showToast(error.message || 'Failed to withdraw application', 'error');
        console.error('Application withdrawal error:', error);
    } finally {
        showLoading(false);
    }
};

// Mark notification as read
window.markNotificationAsRead = async (notificationId) => {
    try {
        await api.notifications.markAsRead(notificationId);
        await loadNotifications();
    } catch (error) {
        console.error('Failed to mark notification as read:', error);
    }
};
