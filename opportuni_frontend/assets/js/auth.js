// Authentication module for Opportuni Platform

class AuthManager {
    constructor() {
        this.currentUser = null;
        this.userLoadPromise = null;
        this.init();
    }

    // Initialize authentication
    init() {
        this.userLoadPromise = this.loadCurrentUser();
        this.setupTokenRefresh();
    }

    // Wait for user to be loaded
    async waitForUser() {
        if (this.userLoadPromise) {
            await this.userLoadPromise;
        }
        return this.currentUser;
    }

    // Load current user from storage
    async loadCurrentUser() {
        const token = Utils.storage.get('auth_token');
        if (token) {
            try {
                // Make sure the token is set in the API instance first
                api.setToken(token);
                this.currentUser = await api.auth.getProfile();
                this.updateUIForLoggedInUser();
                console.log('Successfully loaded user profile:', this.currentUser);
            } catch (error) {
                console.error('Failed to load user profile:', error, error.stack);
                // Don't log out immediately, retry once more after a small delay
                setTimeout(async () => {
                    try {
                        this.currentUser = await api.auth.getProfile();
                        this.updateUIForLoggedInUser();
                        console.log('Successfully loaded user profile on retry:', this.currentUser);
                    } catch (retryError) {
                        console.error('Failed to load user profile after retry:', retryError);
                        this.logout();
                    }
                }, 1000);
            }
        }
    }

    // Setup automatic token refresh
    setupTokenRefresh() {
        const refreshToken = Utils.storage.get('refresh_token');
        if (refreshToken) {
            // Refresh token every 14 minutes (assuming 15 min token expiry)
            setInterval(async () => {
                try {
                    await api.auth.refresh(refreshToken);
                } catch (error) {
                    console.error('Token refresh failed:', error);
                    this.logout();
                }
            }, 14 * 60 * 1000);
        }
    }

    // Check if user is logged in
    isLoggedIn() {
        // Check for token first - this is the primary indicator of being logged in
        const hasToken = Utils.storage.get('auth_token') !== null;
        
        // Log both conditions to help debug
        console.log('isLoggedIn check - hasToken:', hasToken);
        console.log('isLoggedIn check - hasCurrentUser:', this.currentUser !== null);
        
        // Return true if we have a token, don't require currentUser to be loaded yet
        // This fixes the circular dependency where we need isLoggedIn to load the profile
        // but also needed the profile to be loaded to consider the user logged in
        return hasToken;
    }

    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }

    // Login user
    async login(credentials) {
        try {
            showLoading(true);
            const response = await api.auth.login(credentials);
            
            // Store tokens
            Utils.storage.set('auth_token', response.access);
            Utils.storage.set('refresh_token', response.refresh);
            
            // Make sure token is set in API instance
            api.setToken(response.access);
            console.log('Token set after login:', response.access);
            
            // Load user profile with a small delay to ensure token is properly set
            setTimeout(async () => {
                try {
                    this.currentUser = await api.auth.getProfile();
                    console.log('Profile loaded:', this.currentUser);
                    
                    // Update UI
                    this.updateUIForLoggedInUser();
                    
                    // Redirect to appropriate dashboard
                    this.redirectToDashboard();
                } catch (profileError) {
                    console.error('Failed to load profile after login:', profileError);
                    showToast('Login successful, but failed to load profile. Please refresh the page.', 'warning');
                }
            }, 300);
            
            showToast('Welcome back!', 'success');
            return response;
        } catch (error) {
            showToast(error.message || 'Login failed. Please try again.', 'error');
            throw error;
        } finally {
            showLoading(false);
        }
    }

    // Register user
    async register(userData) {
        try {
            showLoading(true);
            const response = await api.auth.register(userData);
            
            // Auto-login after registration
            if (response.access) {
                Utils.storage.set('auth_token', response.access);
                Utils.storage.set('refresh_token', response.refresh);
                this.currentUser = await api.auth.getProfile();
                this.updateUIForLoggedInUser();
                this.redirectToDashboard();
            }
            
            showToast('Account created successfully!', 'success');
            return response;
        } catch (error) {
            showToast(error.message || 'Registration failed. Please try again.', 'error');
            throw error;
        } finally {
            showLoading(false);
        }
    }

    // Logout user
    async logout() {
        try {
            await api.auth.logout();
        } catch (error) {
            console.error('Logout API call failed:', error);
        } finally {
            // Clear local data
            this.currentUser = null;
            Utils.storage.remove('auth_token');
            Utils.storage.remove('refresh_token');
            api.removeToken();
            
            // Update UI
            this.updateUIForLoggedOutUser();
            
            // Redirect to home
            window.location.href = '/';
            
            showToast('You have been logged out', 'info');
        }
    }

    // Update UI for logged in user
    updateUIForLoggedInUser() {
        // Hide auth buttons, show user menu
        const authButtons = Utils.$$('.auth-buttons');
        const userMenu = Utils.$$('.user-menu');
        
        authButtons.forEach(el => el.style.display = 'none');
        userMenu.forEach(el => el.style.display = 'block');
        
        // Update user info in UI
        if (this.currentUser) {
            // Handle both class-based and id-based user name elements
            const userNameElements = Utils.$$('.user-name');
            const userNameById = document.getElementById('userName');
            const userEmailElements = Utils.$$('.user-email');
            const userAvatarElements = Utils.$$('.user-avatar');
            
            const fullName = this.currentUser.first_name + ' ' + this.currentUser.last_name;
            
            userNameElements.forEach(el => {
                el.textContent = fullName;
            });
            
            if (userNameById) {
                userNameById.textContent = fullName;
            }
            
            userEmailElements.forEach(el => {
                el.textContent = this.currentUser.email;
            });
            
            userAvatarElements.forEach(el => {
                if (this.currentUser.avatar) {
                    el.src = this.currentUser.avatar;
                } else {
                    el.src = this.generateAvatarURL(this.currentUser.first_name, this.currentUser.last_name);
                }
            });
        }
    }

    // Update UI for logged out user
    updateUIForLoggedOutUser() {
        // Show auth buttons, hide user menu
        const authButtons = Utils.$$('.auth-buttons');
        const userMenu = Utils.$$('.user-menu');
        
        authButtons.forEach(el => el.style.display = 'block');
        userMenu.forEach(el => el.style.display = 'none');
    }

    // Redirect to appropriate dashboard
    redirectToDashboard() {
        console.log('redirectToDashboard called - DISABLED for debugging');
        console.trace('Redirect called from:');
        return; // DISABLED
        
        if (!this.currentUser) {
            console.error('Cannot redirect: currentUser is null');
            console.log('Will attempt to load user first...');
            
            // Try to load user and then redirect
            this.waitForUser().then(user => {
                if (user) {
                    console.log('User loaded, now redirecting...');
                    this.redirectToDashboard();
                } else {
                    console.error('Failed to load user for redirect');
                }
            });
            return;
        }
        
        console.log('Redirecting user type:', this.currentUser.user_type);
        
        // Use a small delay to ensure any pending operations complete
        setTimeout(() => {
            switch (this.currentUser.user_type) {
                case 'student':
                    window.location.href = '/dashboard.html';
                    break;
                case 'organization':
                    window.location.href = '/organization/dashboard.html';
                    break;
                case 'admin':
                    window.location.href = '/admin/dashboard.html';
                    break;
                default:
                    window.location.href = '/dashboard.html';
            }
        }, 200);
    }

    // Generate avatar URL using initials
    generateAvatarURL(firstName, lastName) {
        const initials = (firstName?.charAt(0) || '') + (lastName?.charAt(0) || '');
        return `https://ui-avatars.com/api/?name=${initials}&background=3b82f6&color=ffffff&size=40`;
    }

    // Require authentication for certain pages
    requireAuth() {
        console.log('requireAuth check - isLoggedIn:', this.isLoggedIn());
        console.log('Current user from requireAuth:', this.currentUser);
        
        if (!this.isLoggedIn()) {
            // Store the current page for redirect after login
            Utils.storage.set('redirect_after_login', window.location.pathname);
            
            // Redirect to login page instead of root
            window.location.href = '/login.html';
            return false;
        }
        return true;
    }

    // Require specific user type
    requireUserType(requiredType) {
        if (!this.requireAuth()) return false;
        
        if (this.currentUser?.user_type !== requiredType) {
            showToast('You do not have permission to access this page', 'error');
            this.redirectToDashboard();
            return false;
        }
        return true;
    }

    // Change password
    async changePassword(passwordData) {
        try {
            showLoading(true);
            await api.auth.changePassword(passwordData);
            showToast('Password changed successfully!', 'success');
        } catch (error) {
            showToast(error.message || 'Failed to change password', 'error');
            throw error;
        } finally {
            showLoading(false);
        }
    }

    // Reset password
    async resetPassword(email) {
        try {
            showLoading(true);
            await api.auth.resetPassword(email);
            showToast('Password reset instructions sent to your email', 'success');
        } catch (error) {
            showToast(error.message || 'Failed to send reset email', 'error');
            throw error;
        } finally {
            showLoading(false);
        }
    }

    // Update profile
    async updateProfile(profileData) {
        try {
            showLoading(true);
            const updatedUser = await api.auth.updateProfile(profileData);
            this.currentUser = { ...this.currentUser, ...updatedUser };
            this.updateUIForLoggedInUser();
            showToast('Profile updated successfully!', 'success');
            return updatedUser;
        } catch (error) {
            showToast(error.message || 'Failed to update profile', 'error');
            throw error;
        } finally {
            showLoading(false);
        }
    }
}

// Global authentication functions
function showLoginModal() {
    try {
        const modal = createModal('login');
        document.body.appendChild(modal);
        // Add a debugging message
        modal.setAttribute('data-debug', 'Login modal added: ' + new Date().toISOString());
    } catch (error) {
        console.error('Error in showLoginModal:', error);
        const errorModal = document.createElement('div');
        errorModal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4';
        errorModal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md w-full">
                <h3 class="text-xl font-bold text-red-600">Error Loading Modal</h3>
                <p class="my-4">${error.message}</p>
                <pre class="bg-gray-100 p-2 text-xs overflow-auto max-h-60">${error.stack}</pre>
                <button onclick="this.closest('.fixed').remove()" class="mt-4 bg-red-500 text-white px-4 py-2 rounded">Close</button>
            </div>
        `;
        document.body.appendChild(errorModal);
    }
}

function showRegisterModal(userType = null) {
    try {
        const modal = createModal('register', { userType });
        document.body.appendChild(modal);
        // Add a debugging message
        modal.setAttribute('data-debug', 'Register modal added: ' + new Date().toISOString());
    } catch (error) {
        console.error('Error in showRegisterModal:', error);
        const errorModal = document.createElement('div');
        errorModal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4';
        errorModal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md w-full">
                <h3 class="text-xl font-bold text-red-600">Error Loading Modal</h3>
                <p class="my-4">${error.message}</p>
                <pre class="bg-gray-100 p-2 text-xs overflow-auto max-h-60">${error.stack}</pre>
                <button onclick="this.closest('.fixed').remove()" class="mt-4 bg-red-500 text-white px-4 py-2 rounded">Close</button>
            </div>
        `;
        document.body.appendChild(errorModal);
    }
}

function showForgotPasswordModal() {
    const modal = createModal('forgot-password');
    document.body.appendChild(modal);
}

// Create authentication modals
function createModal(type, options = {}) {
    try {
        const modalContainer = Utils.createElement('div', 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 modal-enter');
        
        let modalContent = '';
        
        // Add debug info
        console.log(`Creating modal of type: ${type}`);
        
        switch (type) {
            case 'login':
                modalContent = createLoginModal();
                console.log(`Login modal content length: ${modalContent ? modalContent.length : 'undefined'}`);
                break;
            case 'register':
                modalContent = createRegisterModal(options.userType);
                console.log(`Register modal content length: ${modalContent ? modalContent.length : 'undefined'}`);
                break;
            case 'forgot-password':
                modalContent = createForgotPasswordModal();
                console.log(`Forgot password modal content length: ${modalContent ? modalContent.length : 'undefined'}`);
                break;
            default:
                console.error(`Unknown modal type: ${type}`);
                modalContent = '<div class="bg-white p-6 rounded-lg">Unknown modal type</div>';
        }
        
        // Check if modalContent is valid
        if (!modalContent) {
            throw new Error(`Modal content for type "${type}" is empty or undefined`);
        }
        
        // This is where we set the innerHTML - add debug info
        console.log(`Setting innerHTML with content (first 50 chars): ${modalContent.substring(0, 50)}...`);
        modalContainer.innerHTML = modalContent;
        console.log(`Modal innerHTML length after setting: ${modalContainer.innerHTML.length}`);
        
        // Close modal on backdrop click
        modalContainer.addEventListener('click', (e) => {
            if (e.target === modalContainer) {
                closeModal(modalContainer);
            }
        });
        
        return modalContainer;
    } catch (error) {
        console.error('Error creating modal:', error);
        
        // Return an error modal instead
        const errorModal = Utils.createElement('div', 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4');
        errorModal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md w-full">
                <h3 class="text-xl font-bold text-red-600">Error Creating Modal</h3>
                <p class="my-4">${error.message}</p>
                <button onclick="this.closest('.fixed').remove()" class="mt-4 bg-red-500 text-white px-4 py-2 rounded">Close</button>
            </div>
        `;
        return errorModal;
    }
    
    // Setup form handlers
    setTimeout(() => setupModalHandlers(modalContainer, type), 0);
    
    return modalContainer;
}

function createLoginModal() {
    return `
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
            <button onclick="closeModal(this.closest('.fixed'))" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="text-center mb-8">
                <h2 class="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h2>
                <p class="text-gray-600">Sign in to your account</p>
            </div>
            
            <form id="login-form" class="space-y-6">
                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input type="email" name="email" required 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200">
                </div>
                
                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                    <div class="relative">
                        <input type="password" name="password" required 
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200">
                        <button type="button" onclick="togglePassword(this)" 
                                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </div>
                
                <div class="flex items-center justify-between">
                    <label class="flex items-center">
                        <input type="checkbox" name="remember" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                        <span class="ml-2 text-sm text-gray-600">Remember me</span>
                    </label>
                    <button type="button" onclick="showForgotPasswordModal(); closeModal(this.closest('.fixed'))" 
                            class="text-sm text-primary-600 hover:text-primary-500">
                        Forgot password?
                    </button>
                </div>
                
                <button type="submit" 
                        class="w-full bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white py-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105">
                    Sign In
                </button>
            </form>
            
            <div class="mt-6 text-center">
                <p class="text-gray-600">
                    Don't have an account? 
                    <button onclick="showRegisterModal(); closeModal(this.closest('.fixed'))" 
                            class="text-primary-600 hover:text-primary-500 font-semibold">
                        Sign up
                    </button>
                </p>
            </div>
        </div>
    `;
}

function createRegisterModal(userType) {
    return `
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
            <button onclick="closeModal(this.closest('.fixed'))" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="text-center mb-8">
                <h2 class="text-3xl font-bold text-gray-900 mb-2">Join Opportuni</h2>
                <p class="text-gray-600">Create your account and start exploring opportunities</p>
            </div>
            
            <form id="register-form" class="space-y-6">
                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Account Type</label>
                    <select name="user_type" required 
                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        <option value="">Select account type</option>
                        <option value="student" ${userType === 'student' ? 'selected' : ''}>Student</option>
                        <option value="organization" ${userType === 'organization' ? 'selected' : ''}>Organization</option>
                    </select>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                    <div class="form-group">
                        <label class="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                        <input type="text" name="first_name" required 
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    </div>
                    <div class="form-group">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                        <input type="text" name="last_name" required 
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                    </div>
                </div>
                
                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input type="email" name="email" required 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                </div>
                
                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                    <div class="relative">
                        <input type="password" name="password" required 
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                        <button type="button" onclick="togglePassword(this)" 
                                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">Minimum 8 characters with letters and numbers</p>
                </div>
                
                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
                    <input type="password" name="confirm_password" required 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                </div>
                
                <div class="flex items-center">
                    <input type="checkbox" name="terms" required class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                    <span class="ml-2 text-sm text-gray-600">
                        I agree to the <a href="#" class="text-primary-600 hover:text-primary-500">Terms of Service</a> and 
                        <a href="#" class="text-primary-600 hover:text-primary-500">Privacy Policy</a>
                    </span>
                </div>
                
                <button type="submit" 
                        class="w-full bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white py-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105">
                    Create Account
                </button>
            </form>
            
            <div class="mt-6 text-center">
                <p class="text-gray-600">
                    Already have an account? 
                    <button onclick="showLoginModal(); closeModal(this.closest('.fixed'))" 
                            class="text-primary-600 hover:text-primary-500 font-semibold">
                        Sign in
                    </button>
                </p>
            </div>
        </div>
    `;
}

function createForgotPasswordModal() {
    return `
        <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
            <button onclick="closeModal(this.closest('.fixed'))" class="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl">
                <i class="fas fa-times"></i>
            </button>
            
            <div class="text-center mb-8">
                <h2 class="text-3xl font-bold text-gray-900 mb-2">Reset Password</h2>
                <p class="text-gray-600">Enter your email and we'll send you a link to reset your password</p>
            </div>
            
            <form id="forgot-password-form" class="space-y-6">
                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input type="email" name="email" required 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                </div>
                
                <button type="submit" 
                        class="w-full bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white py-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105">
                    Send Reset Link
                </button>
            </form>
            
            <div class="mt-6 text-center">
                <p class="text-gray-600">
                    Remember your password? 
                    <button onclick="showLoginModal(); closeModal(this.closest('.fixed'))" 
                            class="text-primary-600 hover:text-primary-500 font-semibold">
                        Sign in
                    </button>
                </p>
            </div>
        </div>
    `;
}

function setupModalHandlers(modal, type) {
    const form = modal.querySelector('form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = Utils.getFormData(form);
        
        try {
            switch (type) {
                case 'login':
                    await auth.login(formData);
                    closeModal(modal);
                    break;
                    
                case 'register':
                    if (formData.password !== formData.confirm_password) {
                        showToast('Passwords do not match', 'error');
                        return;
                    }
                    delete formData.confirm_password;
                    delete formData.terms;
                    
                    await auth.register(formData);
                    closeModal(modal);
                    break;
                    
                case 'forgot-password':
                    await auth.resetPassword(formData.email);
                    closeModal(modal);
                    break;
            }
        } catch (error) {
            console.error('Form submission error:', error);
        }
    });
}

function closeModal(modal) {
    modal.classList.remove('modal-enter');
    modal.classList.add('modal-exit');
    setTimeout(() => {
        if (modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
    }, 300);
}

function togglePassword(button) {
    const input = button.parentNode.querySelector('input');
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// Create global auth manager instance
window.auth = new AuthManager();

// Export any needed functions for standalone pages
window.togglePassword = togglePassword;
