// API integration for Opportuni Platform

class API {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.token = Utils.storage.get('auth_token');
    this.debug = Boolean(window.DEBUG);
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        Utils.storage.set('auth_token', token);
    if (this.debug) console.log('API token set:', token ? '[redacted]' : 'No token');
    }

    // Remove authentication token
    removeToken() {
        this.token = null;
        Utils.storage.remove('auth_token');
    if (this.debug) console.log('API token removed');
    }
    
    // Check if token exists
    hasToken() {
        return !!this.token;
    }

    // Get request headers
    getHeaders(contentType = 'application/json') {
        const headers = {};

        // Only set Content-Type if it's not null (for FormData, browser should set it automatically)
        if (contentType !== null) {
            headers['Content-Type'] = contentType;
        }

        if (this.token) {
            headers.Authorization = `Bearer ${this.token}`;
        }

        return headers;
    }

    // Generic HTTP request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const baseHeaders = this.getHeaders(options.contentType);
        const config = {
            ...options,
            headers: { ...(options.headers || {}), ...baseHeaders },
        };

        if (this.debug) {
            const safeHeaders = { ...config.headers };
            if (safeHeaders.Authorization) safeHeaders.Authorization = 'Bearer [redacted]';
            console.log('API Request:', {
                url: url,
                method: config.method || 'GET',
                headers: safeHeaders,
                hasToken: !!this.token
            });
        }

        try {
            const response = await fetch(url, config);
            
            // Handle different response types
            let data;
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                // Log detailed error information for debugging
                if (this.debug) {
                    console.error('API Error Details:', {
                        status: response.status,
                        statusText: response.statusText,
                        url: url,
                        method: config.method || 'GET',
                        responseData: data
                    });
                }
                
                // Try to extract meaningful error message
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                if (typeof data === 'object' && data !== null) {
                    if (data.detail) {
                        errorMessage = data.detail;
                    } else if (data.message) {
                        errorMessage = data.message;
                    } else if (data.non_field_errors) {
                        errorMessage = data.non_field_errors.join(', ');
                    } else if (Object.keys(data).length > 0) {
                        // Handle field-specific errors
                        const fieldErrors = Object.entries(data).map(([field, errors]) => {
                            const errorList = Array.isArray(errors) ? errors : [errors];
                            return `${field}: ${errorList.join(', ')}`;
                        });
                        errorMessage = fieldErrors.join('; ');
                    }
                }
                
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            if (this.debug) console.error('API Request Error:', error);
            throw error;
        }
    }

    // GET request
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET',
        });
    }

    // POST request
    async post(endpoint, data = {}) {
        const isFormData = data instanceof FormData;
        return this.request(endpoint, {
            method: 'POST',
            body: isFormData ? data : JSON.stringify(data),
            contentType: isFormData ? null : 'application/json',
        });
    }

    // PUT request
    async put(endpoint, data = {}) {
        const isFormData = data instanceof FormData;
        if (this.debug) {
            console.log('PUT method called:', { endpoint, isFormData });
        }
        
    // Do not log FormData contents to avoid leaking PII
        
        const requestOptions = {
            method: 'PUT',
            body: isFormData ? data : JSON.stringify(data),
            contentType: isFormData ? null : 'application/json',
        };
        
    if (this.debug) console.log('Request options:', { method: requestOptions.method, contentType: requestOptions.contentType });
        return this.request(endpoint, requestOptions);
    }

    // PATCH request
    async patch(endpoint, data = {}) {
        const isFormData = data instanceof FormData;
        return this.request(endpoint, {
            method: 'PATCH',
            body: isFormData ? data : JSON.stringify(data),
            contentType: isFormData ? null : 'application/json',
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    }

    // File upload
    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request(endpoint, {
            method: 'POST',
            contentType: null, // Let browser set content type for FormData
            body: formData,
        });
    }

    // Authentication endpoints
    auth = {
        // Register user
        register: async (userData) => {
            return this.post('/auth/register/', userData);
        },

        // Login user
        login: async (credentials) => {
            const response = await this.post('/auth/login/', credentials);
            if (response.access) {
                console.log('Login successful, setting token');
                this.setToken(response.access);
            } else {
                console.error('Login response missing access token:', response);
            }
            return response;
        },

        // Logout user
        logout: async () => {
            try {
                await this.post('/auth/logout/');
            } finally {
                this.removeToken();
            }
        },

        // Refresh token
        refresh: async (refreshTokenParam) => {
            const currentRefresh = refreshTokenParam || Utils.storage.get('refresh_token');
            const response = await this.post('/auth/refresh/', { refresh: currentRefresh });
            if (response.access) this.setToken(response.access);
            if (response.refresh) {
                // Token rotation support
                Utils.storage.set('refresh_token', response.refresh);
            }
            return response;
        },

        // Get current user profile
        getProfile: async () => {
            return this.get('/auth/profile/');
        },

        // Update user profile
        updateProfile: async (profileData) => {
            return this.put('/auth/profile/', profileData);
        },

        // Change password
        changePassword: async (passwordData) => {
            return this.post('/auth/change-password/', passwordData);
        },

        // Reset password
        resetPassword: async (email) => {
            return this.post('/auth/reset-password/', { email });
        }
    };

    // Student endpoints
    students = {
        // Get student profile
        getProfile: async () => {
            return this.get('/students/profile/');
        },

        // Update student profile
        updateProfile: async (profileData) => {
            return this.put('/students/profile/', profileData);
        },

        // Education endpoints
        getEducation: async () => {
            return this.get('/students/education/');
        },

        addEducation: async (educationData) => {
            return this.post('/students/education/', educationData);
        },

        updateEducation: async (id, educationData) => {
            return this.put(`/students/education/${id}/`, educationData);
        },

        deleteEducation: async (id) => {
            return this.delete(`/students/education/${id}/`);
        },

        // Experience endpoints
        getExperience: async () => {
            return this.get('/students/experience/');
        },

        addExperience: async (experienceData) => {
            console.log('API: Adding experience with data:', experienceData);
            console.log('API: Current token exists:', this.hasToken());
            return this.post('/students/experience/', experienceData);
        },

        updateExperience: async (id, experienceData) => {
            return this.put(`/students/experience/${id}/`, experienceData);
        },

        deleteExperience: async (id) => {
            return this.delete(`/students/experience/${id}/`);
        },

        // Skills endpoints
        getSkills: async () => {
            return this.get('/students/skills/');
        },

        addSkill: async (skillData) => {
            return this.post('/students/skills/', skillData);
        },

        updateSkill: async (id, skillData) => {
            return this.put(`/students/skills/${id}/`, skillData);
        },

        deleteSkill: async (id) => {
            return this.delete(`/students/skills/${id}/`);
        },

        // Projects endpoints
        getProjects: async () => {
            return this.get('/students/projects/');
        },

        addProject: async (projectData) => {
            return this.post('/students/projects/', projectData);
        },

        updateProject: async (id, projectData) => {
            return this.put(`/students/projects/${id}/`, projectData);
        },

        deleteProject: async (id) => {
            return this.delete(`/students/projects/${id}/`);
        },

        // Achievements endpoints
        getAchievements: async () => {
            return this.get('/students/achievements/');
        },

        addAchievement: async (achievementData) => {
            return this.post('/students/achievements/', achievementData);
        },

        updateAchievement: async (id, achievementData) => {
            return this.put(`/students/achievements/${id}/`, achievementData);
        },

        deleteAchievement: async (id) => {
            return this.delete(`/students/achievements/${id}/`);
        },

        // Languages endpoints
        getLanguages: async () => {
            return this.get('/students/languages/');
        },

        addLanguage: async (languageData) => {
            return this.post('/students/languages/', languageData);
        },

        updateLanguage: async (id, languageData) => {
            return this.put(`/students/languages/${id}/`, languageData);
        },

        deleteLanguage: async (id) => {
            return this.delete(`/students/languages/${id}/`);
        },

        // Upload resume
        uploadResume: async (file) => {
            const formData = new FormData();
            formData.append('resume', file);  // Use 'resume' field name as expected by backend
            
            return this.request('/students/upload-resume/', {
                method: 'POST',
                contentType: null,
                body: formData,
            });
        },

        // Upload profile picture
        uploadProfilePicture: async (file) => {
            const formData = new FormData();
            formData.append('avatar', file);  // Use 'avatar' field name as expected by backend
            
            return this.request('/students/upload-profile-picture/', {
                method: 'POST',
                contentType: null,
                body: formData,
            });
        },

        // Get dashboard stats
        getDashboardStats: async () => {
            return this.get('/students/dashboard/');
        },

        // Get application stats
        getApplicationStats: async () => {
            return this.get('/students/application-stats/');
        },
    };

    // Organization endpoints
    organizations = {
        // Get organization profile
        getProfile: async () => {
            return this.get('/organizations/profile/');
        },

        // Update organization profile
        updateProfile: async (profileData) => {
            return this.put('/organizations/profile/', profileData);
        },

        // Upload logo
        uploadLogo: async (file) => {
            return this.uploadFile('/organizations/upload-logo/', file);
        },

        // Get team members
        getMembers: async () => {
            return this.get('/organizations/members/');
        },

        // Invite team member
        inviteMember: async (memberData) => {
            return this.post('/organizations/invite-member/', memberData);
        },

        // Get dashboard stats
        getDashboardStats: async () => {
            return this.get('/organizations/dashboard-stats/');
        },

        // Search organizations
        search: async (query, filters = {}) => {
            return this.get('/organizations/search/', { q: query, ...filters });
        }
    };

    // Opportunities endpoints
    opportunities = {
        // Get opportunities list
        getList: async (params = {}) => {
            return this.get('/opportunities/', params);
        },

        // Get opportunity by ID
        getById: async (id) => {
            return this.get(`/opportunities/${id}/`);
        },

        // Create opportunity
        create: async (opportunityData) => {
            return this.post('/opportunities/', opportunityData);
        },

        // Update opportunity
        update: async (id, opportunityData) => {
            return this.put(`/opportunities/${id}/`, opportunityData);
        },

        // Delete opportunity
        delete: async (id) => {
            return this.delete(`/opportunities/${id}/`);
        },

        // Get featured opportunities
        getFeatured: async () => {
            return this.get('/opportunities/featured/');
        },

        // Search opportunities
        search: async (query, filters = {}) => {
            return this.get('/opportunities/search/', { q: query, ...filters });
        },

        // Get opportunity categories
        getCategories: async () => {
            return this.get('/opportunities/categories/');
        },

        // Debug information about opportunities
        getDebugInfo: async () => {
            return this.get('/opportunities/debug/');
        }
    };

    // Applications endpoints
    applications = {
        // Get applications list
        getList: async (params = {}) => {
            return this.get('/applications/', params);
        },

        // Get application by ID
        getById: async (id) => {
            return this.get(`/applications/${id}/`);
        },

        // Get application details (alias for getById for compatibility)
        getDetails: async (id) => {
            return this.get(`/applications/${id}/`);
        },

        // Submit application
        submit: async (applicationData) => {
            return this.post('/applications/', applicationData);
        },

        // Update application
        update: async (id, applicationData) => {
            return this.put(`/applications/${id}/`, applicationData);
        },

        // Withdraw application
        withdraw: async (id) => {
            return this.post(`/applications/${id}/withdraw/`);
        },

        // Get application stats
        getStats: async () => {
            return this.get('/applications/stats/');
        },

        // Upload application document
        uploadDocument: async (file) => {
            return this.uploadFile('/applications/upload-document/', file);
        }
    };

    // Communications endpoints
    communications = {
        // Get email templates
        getTemplates: async () => {
            return this.get('/communications/templates/');
        },

        // Create email template
        createTemplate: async (templateData) => {
            return this.post('/communications/templates/', templateData);
        },

        // Update email template
        updateTemplate: async (id, templateData) => {
            return this.put(`/communications/templates/${id}/`, templateData);
        },

        // Delete email template
        deleteTemplate: async (id) => {
            return this.delete(`/communications/templates/${id}/`);
        },

        // Send email
        sendEmail: async (emailData) => {
            return this.post('/communications/send-email/', emailData);
        },

        // Get email history
        getEmailHistory: async (params = {}) => {
            return this.get('/communications/emails/', params);
        }
    };

    // Notifications endpoints
    notifications = {
        // Get notifications
        getList: async (params = {}) => {
            return this.get('/notifications/', params);
        },

        // Mark notification as read
        markAsRead: async (id) => {
            return this.patch(`/notifications/${id}/`, { is_read: true });
        },

        // Mark all notifications as read
        markAllAsRead: async () => {
            return this.post('/notifications/mark-all-read/');
        },

        // Delete notification
        delete: async (id) => {
            return this.delete(`/notifications/${id}/`);
        },

        // Get unread count
        getUnreadCount: async () => {
            return this.get('/notifications/unread-count/');
        }
    };
}

// Create global API instance
window.api = new API();
