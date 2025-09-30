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
    if (this.debug && window.Logger) Logger.info('API token set');
    }

    // Remove authentication token
    removeToken() {
        this.token = null;
        Utils.storage.remove('auth_token');
    if (this.debug && window.Logger) Logger.info('API token removed');
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
            if (window.Logger) Logger.info('API Request', { url, method: config.method || 'GET', headers: safeHeaders, hasToken: !!this.token, endpoint });
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
                if (this.debug && window.Logger) {
            Logger.error('API Error', new Error(`HTTP ${response.status} ${response.statusText}`), { url, endpoint, status: response.status, statusText: response.statusText, data });
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
            if (this.debug && window.Logger) Logger.error('API Request Error', error, { endpoint });
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
        if (this.debug && window.Logger) {
            Logger.info('PUT method called', { endpoint, isFormData });
        }
        
    // Do not log FormData contents to avoid leaking PII
        
        const requestOptions = {
            method: 'PUT',
            body: isFormData ? data : JSON.stringify(data),
            contentType: isFormData ? null : 'application/json',
        };
        
    if (this.debug && window.Logger) Logger.info('Request options', { method: requestOptions.method, contentType: requestOptions.contentType });
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
                if (this.debug && window.Logger) Logger.info('Login successful, setting token');
                this.setToken(response.access);
            } else {
                if (window.Logger) Logger.error('Login response missing access token');
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
        },

        // Telegram authentication
        telegramAuth: async (telegramData) => {
            return this.post('/auth/telegram-auth/', telegramData);
        },

        // Get Telegram bot configuration
        getTelegramConfig: async () => {
            return this.get('/auth/telegram-config/');
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
            if (this.debug && window.Logger) Logger.info('API: Adding experience', { hasToken: this.hasToken() });
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

        // Social links endpoints
        getSocialLinks: async () => {
            return this.get('/students/social-links/');
        },
        addSocialLink: async (data) => {
            return this.post('/students/social-links/', data);
        },
        updateSocialLink: async (id, data) => {
            return this.put(`/students/social-links/${id}/`, data);
        },
        deleteSocialLink: async (id) => {
            return this.delete(`/students/social-links/${id}/`);
        },
        upsertSocialLink: async (data) => {
            return this.post('/students/social-links/upsert/', data);
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

        // Academic exams & scores
        getExams: async () => {
            return this.get('/students/exams/');
        },
        getExamSections: async (examId) => {
            return this.get(`/students/exams/${examId}/sections/`);
        },
        getExamScores: async () => {
            return this.get('/students/exam-scores/');
        },
        addExamScore: async (payload) => {
            return this.post('/students/exam-scores/', payload);
        },
        updateExamScore: async (id, payload) => {
            return this.put(`/students/exam-scores/${id}/`, payload);
        },
        deleteExamScore: async (id) => {
            return this.delete(`/students/exam-scores/${id}/`);
        },
        seedDefaultExams: async () => {
            return this.post('/students/exams/seed-defaults/');
        },

        // Public Opportuni Card (no auth required)
        getPublicCard: async (studentId) => {
            return this.get(`/students/card/${encodeURIComponent(studentId)}/`);
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
            // Backend provides dashboard data at /organizations/dashboard/
            return this.get('/organizations/dashboard/');
        },

        // Get application stats for current organization
        getApplicationStats: async () => {
            return this.get('/applications/stats/');
        },

        // Student management endpoints
        getStudentStats: async () => {
            return this.get('/organizations/students/stats/');
        },

        getStudents: async (params = {}) => {
            return this.get('/organizations/students/', params);
        },

        inviteStudents: async (inviteData) => {
            return this.post('/organizations/students/invite/', inviteData);
        },

        exportStudents: async (params = {}) => {
            // Return blob for CSV download
            const response = await this.request('/organizations/students/export/', {
                method: 'GET',
                params,
                headers: {
                    ...this.getHeaders(),
                    'Accept': 'text/csv'
                }
            });
            return response.blob();
        },

        getStudentLocations: async () => {
            return this.get('/organizations/students/locations/');
        },

        getPopularSkills: async () => {
            return this.get('/organizations/students/skills/');
        },

        // Get organization opportunities (active by default via dedicated endpoint)
        getOpportunities: async (params = {}) => {
            // Prefer org-scoped active endpoint when no explicit scope provided
            const useOrgActive = params && ('is_active' in params || Object.keys(params).length === 0);
            return useOrgActive
                ? this.get('/opportunities/mine/active/', params)
                : this.get('/opportunities/', params);
        },

        // Get applications list (maps date filters to backend expectations)
        getApplications: async (params = {}) => {
            const { date_from, date_to, ...rest } = params || {};
            const mapped = { ...rest };
            if (date_from) {
                // Backend expects applied_after as DateTime; send ISO start of day
                mapped.applied_after = new Date(date_from).toISOString();
            }
            if (date_to) {
                // Backend expects applied_before as DateTime; send ISO end of day
                const end = new Date(date_to);
                end.setHours(23,59,59,999);
                mapped.applied_before = end.toISOString();
            }
            // Use org-scoped listing for clarity
            return this.get('/applications/org/', mapped);
        },

        // Search organizations
        search: async (query, filters = {}) => {
            // Backend lists organizations at /organizations/?search=...
            const params = { ...(filters || {}) };
            if (query) params.search = query;
            return this.get('/organizations/', params);
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

        // Create opportunity with file upload
        createWithFile: async (formData) => {
            return this.request('/opportunities/', {
                method: 'POST',
                body: formData,
                contentType: null // Let browser set Content-Type for FormData
            });
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

        // Check if user has applied to specific opportunity
        checkStatus: async (opportunityId) => {
            return this.get(`/applications/check-status/${opportunityId}/`);
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

        // Update only status (convenience)
        updateStatus: async (id, payload) => {
            return this.put(`/applications/${id}/`, payload);
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
        },

        // Bulk update application statuses (organization only)
        bulkUpdateStatus: async (application_ids = [], status, reason = '') => {
            return this.post('/applications/bulk-update/', { application_ids, status, reason });
        },

        // Organization-specific application methods
        listForOrg: async (params = {}) => {
            return this.get('/applications/org/', params);
        },

        getDetail: async (id) => {
            return this.get(`/applications/${id}/`);
        },

        updateReview: async (id, reviewData) => {
            return this.put(`/applications/${id}/review/`, reviewData);
        },

        bulkUpdate: async (data) => {
            return this.post('/applications/bulk-update/', data);
        },

        downloadResume: async (applicationId) => {
            const response = await this.request(`/applications/${applicationId}/resume/`, {
                method: 'GET'
            });
            return response.blob();
        },

        getLocations: async () => {
            return this.get('/applications/locations/');
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
            // Backend exposes bulk send at /communications/send-bulk/
            return this.post('/communications/send-bulk/', emailData);
        },

        // Get message/email history (backend exposes as messages)
        getEmailHistory: async (params = {}) => {
            return this.get('/communications/messages/', params);
        },

        // Real-time messaging methods
        getConversations: async (params = {}) => {
            return this.get('/communications/conversations/', params);
        },

        getMessages: async (conversationId, params = {}) => {
            return this.get(`/communications/conversations/${conversationId}/messages/`, params);
        },

        sendMessage: async (messageData) => {
            return this.post('/communications/messages/', messageData);
        },

        sendNewMessage: async (messageData) => {
            return this.post('/communications/conversations/', messageData);
        },

        startConversation: async (participantId) => {
            return this.post('/communications/conversations/', { participant_id: participantId });
        },

        markAsRead: async (conversationId) => {
            return this.put(`/communications/conversations/${conversationId}/read/`);
        },

        markMessageAsRead: async (messageId) => {
            return this.put(`/communications/messages/${messageId}/read/`);
        },

        searchRecipients: async (query) => {
            return this.get('/communications/search-recipients/', { q: query });
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
            // Backend exposes explicit read endpoint
            return this.request(`/notifications/${id}/read/`, { method: 'PUT' });
        },

        // Mark all notifications as read
        markAllAsRead: async () => {
            return this.request('/notifications/mark-all-read/', { method: 'PUT' });
        },

        // Delete notification (use explicit delete endpoint)
        delete: async (id) => {
            return this.request(`/notifications/${id}/delete/`, { method: 'DELETE' });
        },

        // Optional: get notification settings
        getSettings: async () => {
            return this.get('/notifications/settings/');
        },

        // Get unread count
        getUnreadCount: async () => {
            const stats = await this.get('/notifications/stats/');
            // Normalize to { count } for callers
            return { count: stats.unread_notifications ?? 0 };
        }
    };

    // Skills endpoints
    skills = {
        // Get all available skills
        getAvailable: async () => {
            return this.get('/students/skills/available/');
        }
    };
}

// Create global API instance
window.api = new API();
