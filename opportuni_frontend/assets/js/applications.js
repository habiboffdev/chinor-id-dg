        // Student Applications Page Logic
        let currentPage = 1;
        let applicationToWithdraw = null;
        let isLoading = false;
        let isLoadingStats = false;
        
        // Utility function to escape HTML
        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
    document.addEventListener('DOMContentLoaded', async function() {
            console.log('Applications page loading...');
            
            // Simple auth check
            if (!auth.isLoggedIn()) {
                console.log('User not logged in, redirecting to index');
                window.location.href = 'index.html';
                return;
            }
            
            // Wait for user to be loaded
            await auth.waitForUser();
            
            const currentUser = auth.getCurrentUser();
            if (!currentUser || currentUser.user_type !== 'student') {
                console.log('User not student or null, redirecting to index');
                window.location.href = 'index.html';
                return;
            }

            console.log('User authenticated as student, initializing page...');

            // Initialize UI
            auth.updateUIForLoggedInUser();
            
            // Load data
            try {
                await loadStats();
                await loadApplications();
            } catch (error) {
                console.error('Error loading initial data:', error);
                showToast('Failed to load application data', 'error');
            }
            
            // Event listeners
            const statusChipRow = document.getElementById('statusChipRow');
            const closeModalBtn = document.getElementById('closeModalBtn');
            const cancelWithdrawBtn = document.getElementById('cancelWithdrawBtn');
            const confirmWithdrawBtn = document.getElementById('confirmWithdrawBtn');
            const userMenuBtn = document.getElementById('userMenuBtn');
            const userMenu = document.getElementById('userMenu');
            
            if (statusChipRow) {
                statusChipRow.addEventListener('click', (e)=>{
                    const btn = e.target.closest('.status-chip');
                    if(!btn) return;
                    statusChipRow.querySelectorAll('.status-chip').forEach(b=> b.classList.remove('active'));
                    btn.classList.add('active');
                    // Trigger reload using existing filter handler
                    handleFilter();
                });
            }
            // Sort change
            const sortSelect = document.getElementById('sortSelect');
            if (sortSelect) {
                sortSelect.addEventListener('change', ()=> handleFilter());
            }
            if (closeModalBtn) closeModalBtn.addEventListener('click', hideApplicationModal);
            if (cancelWithdrawBtn) cancelWithdrawBtn.addEventListener('click', hideWithdrawModal);
            if (confirmWithdrawBtn) confirmWithdrawBtn.addEventListener('click', handleWithdraw);
            
            // User menu dropdown functionality
            if (userMenuBtn && userMenu) {
                userMenuBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    userMenu.classList.toggle('hidden');
                });
                
                // Close dropdown when clicking outside
                document.addEventListener('click', function(e) {
                    if (!userMenuBtn.contains(e.target) && !userMenu.contains(e.target)) {
                        userMenu.classList.add('hidden');
                    }
                });
                
                // Handle logout button
                const logoutBtn = document.getElementById('logoutBtn');
                if (logoutBtn) {
                    logoutBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        userMenu.classList.add('hidden'); // Close dropdown first
                        auth.logout();
                    });
                }
            }
        });

        async function loadStats() {
            if (isLoadingStats) {
                console.log('Stats already loading, skipping...');
                return;
            }
            
            try {
                isLoadingStats = true;
                const response = await api.students.getApplicationStats();
                // The response should be the stats object directly, not nested in data
                const stats = response;
                
                document.getElementById('totalApplications').textContent = stats.total || 0;
                document.getElementById('pendingApplications').textContent = stats.pending || 0;
                document.getElementById('reviewingApplications').textContent = stats.under_review || stats.reviewing || 0;
                document.getElementById('acceptedApplications').textContent = stats.accepted || 0;
            } catch (error) {
                console.error('Error loading stats:', error);
                // Set default values on error
                document.getElementById('totalApplications').textContent = '0';
                document.getElementById('pendingApplications').textContent = '0';
                document.getElementById('reviewingApplications').textContent = '0';
                document.getElementById('acceptedApplications').textContent = '0';
            } finally {
                isLoadingStats = false;
            }
        }

    async function loadApplications(page = 1) {
            if (isLoading) {
                console.log('Applications already loading, skipping...');
                return;
            }
            
            try {
                isLoading = true;
                showLoading(true);
                const sortSelect = document.getElementById('sortSelect');
                const ordering = sortSelect ? sortSelect.value : '-created_at';
                const filters = { page, ordering };
                
                // Only add status filter if it's not empty
                const chipActive = document.querySelector('#statusChipRow .status-chip.active');
                const statusValue = chipActive ? chipActive.dataset.status : '';
                if (statusValue) {
                    filters.status = statusValue;
                }
                
                const response = await api.applications.getList(filters);
                
                renderApplications(response.results);
                renderPagination(response, page);
                currentPage = page;
                
                showLoading(false);
            } catch (error) {
                console.error('Error loading applications:', error);
                showToast('Failed to load applications: ' + (error.message || 'Unknown error'), 'error');
                showLoading(false);
            } finally {
                isLoading = false;
            }
        }

        function renderApplications(applications) {
            const container = document.getElementById('applicationsContainer');
            const emptyState = document.getElementById('emptyState');
            
            if (applications.length === 0) {
                container.innerHTML = '';
                emptyState.classList.remove('hidden');
                return;
            }
            
            emptyState.classList.add('hidden');
            container.innerHTML = applications.map(app => {
                const canWithdraw = ['pending', 'under_review'].includes(app.status);
                
                // Find cover letter from answers
                const coverLetterAnswer = app.answers ? app.answers.find(answer => 
                    answer.question_text && answer.question_text.toLowerCase().includes('cover letter')
                ) : null;
                
                return `
                    <div class="app-item">
                        <div class="flex items-start justify-between">
                            <div class="flex-1">
                                <div class="flex items-start space-x-4">
                                    <div class="app-icon flex-shrink-0">
                                        <i class="fas fa-building"></i>
                                    </div>
                                    <div class="flex-1 min-w-0">
                                        <h3 class="text-lg app-title mb-1">${escapeHtml(app.opportunity_title || app.opportunity?.title || 'Opportunity')}</h3>
                                        <p class="app-org mb-2">${escapeHtml(app.organization_name || app.opportunity?.organization?.name || 'Organization')}</p>
                                        <div class="app-meta mb-3">
                                            <span><i class="fas fa-calendar mr-1"></i>Applied ${formatDate(app.applied_at)}</span>
                                            <span><i class="fas fa-clock mr-1"></i>${escapeHtml(app.opportunity?.opportunity_type || 'Unknown')}</span>
                                            <span><i class="fas fa-map-marker-alt mr-1"></i>${escapeHtml(app.opportunity?.location || 'Remote')}</span>
                                        </div>
                                        ${coverLetterAnswer ? `
                                        <div class="rounded-lg p-3 mb-3" style="background: var(--ink-800); border:1px solid var(--slate-400);">
                                            <p class="text-sm" style="color: var(--mist-200); font-weight:600;">Cover Letter:</p>
                                            <p class="text-sm" style="color: var(--mist-300);">${escapeHtml(coverLetterAnswer.answer_text)}</p>
                                        </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                            <div class="ml-6 flex flex-col items-end space-y-3 app-tools">
                                ${getStatusBadge(app.status)}
                                <div class="flex gap-2">
                                    <button onclick="viewApplication(${app.id})" class="btn btn--ghost"><i class="fas fa-eye"></i><span>View</span></button>
                                    ${canWithdraw ? `
                                    <button onclick="showWithdrawModal(${app.id})" class="btn btn--secondary" style="background: var(--danger);"><i class="fas fa-times"></i><span>Withdraw</span></button>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        
                        <!-- Status Timeline -->
                        ${app.status_history && app.status_history.length > 0 ? `
                        <div class="mt-4 pt-4" style="border-top:1px solid var(--slate-400);">
                            <p class="text-sm" style="color: var(--mist-200); font-weight:600;">Status History</p>
                            <div class="flex space-x-4 overflow-x-auto">
                                ${app.status_history.slice(-3).map(history => `
                                    <div class="flex-shrink-0 text-center">
                                        <div class="w-8 h-8 rounded-full flex items-center justify-center mb-1" style="${getStatusDotStyle(history.status)}">
                                            <i class="fas ${getStatusIcon(history.status)} text-xs"></i>
                                        </div>
                                        <p class="text-xs" style="color: var(--mist-300);">${formatDate(history.created_at)}</p>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                `;
            }).join('');
        }

        function getStatusBadge(status) {
            const badges = {
                pending: '<span class="badge badge--pending">Pending</span>',
                under_review: '<span class="badge badge--review">Under Review</span>',
                reviewing: '<span class="badge badge--review">Under Review</span>',
                interview_scheduled: '<span class="badge badge--interview">Interview Scheduled</span>',
                shortlisted: '<span class="badge badge--shortlist">Shortlisted</span>',
                accepted: '<span class="badge badge--accepted">Accepted</span>',
                rejected: '<span class="badge badge--rejected">Rejected</span>',
                withdrawn: '<span class="badge badge--withdrawn">Withdrawn</span>'
            };
            return badges[status] || '<span class="badge" style="background: rgba(255,255,255,0.08); color: var(--mist-300);">Unknown</span>';
        }

        function getStatusDotStyle(status) {
            const map = {
                pending: 'background: var(--pill-status-pending-bg); color: var(--warning);',
                under_review: 'background: var(--pill-status-review-bg); color: var(--promo);',
                reviewing: 'background: var(--pill-status-review-bg); color: var(--promo);',
                interview_scheduled: 'background: var(--pill-status-interview-bg); color: var(--accent-2);',
                shortlisted: 'background: var(--pill-status-shortlist-bg); color: var(--accent-3);',
                accepted: 'background: var(--pill-status-accepted-bg); color: var(--success);',
                rejected: 'background: var(--pill-status-rejected-bg); color: var(--danger);',
                withdrawn: 'background: var(--pill-status-withdrawn-bg); color: var(--mist-300);'
            };
            return map[status] || 'background: var(--pill-status-withdrawn-bg); color: var(--mist-300);';
        }

        function getStatusIcon(status) {
            const icons = {
                pending: 'fa-clock',
                under_review: 'fa-search',
                reviewing: 'fa-search',
                interview_scheduled: 'fa-calendar-check',
                shortlisted: 'fa-star',
                accepted: 'fa-check',
                rejected: 'fa-times',
                withdrawn: 'fa-ban'
            };
            return icons[status] || 'fa-question';
        }

        function renderPagination(data, currentPage) {
            const container = document.getElementById('pagination');
            const totalPages = Math.ceil(data.count / 20);
            
            if (totalPages <= 1) {
                container.innerHTML = '';
                return;
            }
            
            let pagination = '<div class="flex items-center justify-between">';
            pagination += `<p class=\"text-sm\" style=\"color: var(--mist-300);\">Showing ${((currentPage - 1) * 20) + 1} to ${Math.min(currentPage * 20, data.count)} of ${data.count} results</p>`;
            pagination += '<div class="flex gap-2">';
            
            if (currentPage > 1) {
                pagination += `<button onclick=\"loadApplications(${currentPage - 1})\" class=\"btn btn--ghost btn--sm\">Previous</button>`;
            }
            
            for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
                const isActive = i === currentPage;
                pagination += `<button onclick=\"loadApplications(${i})\" class=\"btn btn--sm ${isActive ? 'btn--secondary' : 'btn--ghost'}\">${i}</button>`;
            }
            
            if (currentPage < totalPages) {
                pagination += `<button onclick=\"loadApplications(${currentPage + 1})\" class=\"btn btn--ghost btn--sm\">Next</button>`;
            }
            
            pagination += '</div></div>';
            container.innerHTML = pagination;
        }

        async function viewApplication(applicationId) {
            try {
                showLoading(true);
                const response = await api.applications.getDetails(applicationId);
                const app = response;
                
                const modalContent = document.getElementById('applicationModalContent');
                modalContent.innerHTML = `
                    <!-- Hero Section -->
                    <div class="app-hero-card">
                        <div class="app-hero-content">
                            <h4 class="app-hero-title">${escapeHtml(app.opportunity_title || app.opportunity?.title || 'Opportunity')}</h4>
                            <p class="app-hero-org">${escapeHtml(app.organization_name || app.opportunity?.organization?.name || 'Organization')}</p>
                            <div class="app-hero-meta">
                                <div class="app-hero-meta-item">
                                    <i class="fas fa-briefcase"></i>
                                    <span>${escapeHtml(app.opportunity?.opportunity_type || 'Unknown')}</span>
                                </div>
                                <div class="app-hero-meta-item">
                                    <i class="fas fa-map-marker-alt"></i>
                                    <span>${escapeHtml(app.opportunity?.location || 'Remote')}</span>
                                </div>
                                <div class="app-hero-meta-item">
                                    <i class="fas fa-calendar-alt"></i>
                                    <span>Deadline: ${formatDate(app.opportunity?.application_deadline)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Application Information -->
                    <div class="app-section">
                        <h5 class="app-section-title">
                            <i class="fas fa-info-circle app-section-icon"></i>
                            Application Information
                        </h5>
                        <div class="app-info-grid">
                            <div class="app-info-item">
                                <span class="app-info-label">Applied on</span>
                                <span class="app-info-value">${formatDate(app.applied_at)}</span>
                            </div>
                            <div class="app-info-item">
                                <span class="app-info-label">Status</span>
                                <span class="app-info-value">${getStatusBadge(app.status)}</span>
                            </div>
                            <div class="app-info-item">
                                <span class="app-info-label">Last Updated</span>
                                <span class="app-info-value">${formatDate(app.updated_at)}</span>
                            </div>
                            <div class="app-info-item">
                                <span class="app-info-label">Resume</span>
                                <span class="app-info-value">
                                    ${app.resume ? `<a href="${app.resume}" target="_blank" class="app-document-link"><i class="fas fa-file-pdf"></i>View Resume</a>` : '<span style="color: var(--mist-300);">Not attached</span>'}
                                </span>
                            </div>
                        </div>
                    </div>
                    
                    ${app.answers && app.answers.length > 0 ? `
                    <!-- Application Answers -->
                    <div class="app-section">
                        <h5 class="app-section-title">
                            <i class="fas fa-question-circle app-section-icon"></i>
                            Application Answers
                        </h5>
                        <div class="app-answers-list">
                            ${app.answers.map(answer => {
                                const escapedQuestion = escapeHtml(answer.question_text || 'Question');
                                const escapedAnswer = escapeHtml(answer.answer_text || 'No answer provided');
                                const formattedAnswer = escapedAnswer.replace(/\n/g, '<br>');
                                
                                return `
                                <div class="app-answer-card">
                                    <div class="app-answer-question">${escapedQuestion}</div>
                                    <div class="app-answer-text">${formattedAnswer}</div>
                                </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${app.status_history && app.status_history.length > 0 ? `
                    <!-- Status History -->
                    <div class="app-section">
                        <h5 class="app-section-title">
                            <i class="fas fa-history app-section-icon"></i>
                            Status History
                        </h5>
                        <div class="app-status-timeline">
                            ${app.status_history.map(history => `
                                <div class="app-status-item status-${history.status}">
                                    <div class="app-status-dot">
                                        <i class="fas ${getStatusIcon(history.status)}"></i>
                                    </div>
                                    <div class="app-status-content">
                                        <div class="app-status-title">${formatStatusName(history.status)}</div>
                                        ${history.note ? `<div class="app-status-note">${escapeHtml(history.note)}</div>` : ''}
                                        <div class="app-status-date">${formatDate(history.created_at)}</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    <!-- Actions -->
                    <div class="app-section">
                        <h5 class="app-section-title">
                            <i class="fas fa-cog app-section-icon"></i>
                            Actions
                        </h5>
                        <div class="app-actions">
                            ${app.opportunity?.id ? `<a href="opportunity-detail.html?id=${app.opportunity.id}" class="btn btn--secondary"><i class="fas fa-eye"></i><span>View Opportunity</span></a>` : ''}
                            ${app.status === 'pending' ? `<button onclick="showWithdrawModal(${app.id})" class="btn btn--danger"><i class="fas fa-times"></i><span>Withdraw Application</span></button>` : ''}
                        </div>
                    </div>
                `;
                
                showLoading(false);
                showApplicationModal();
            } catch (error) {
                console.error('Error loading application:', error);
                showToast('Failed to load application details', 'error');
                showLoading(false);
            }
        }

        function showWithdrawModal(applicationId) {
            applicationToWithdraw = applicationId;
            document.getElementById('withdrawModal').classList.remove('hidden');
        }

        function hideWithdrawModal() {
            applicationToWithdraw = null;
            document.getElementById('withdrawModal').classList.add('hidden');
        }

        async function handleWithdraw() {
            if (!applicationToWithdraw) return;
            
            try {
                showLoading(true);
                await api.applications.withdraw(applicationToWithdraw);
                showLoading(false);
                hideWithdrawModal();
                showToast('Application withdrawn successfully', 'success');
                await loadApplications(currentPage);
                await loadStats();
            } catch (error) {
                console.error('Error withdrawing application:', error);
                showLoading(false);
                showToast('Failed to withdraw application', 'error');
            }
        }

        let filterTimeout;
        function handleFilter() {
            // Debounce the filter to prevent rapid requests
            clearTimeout(filterTimeout);
            filterTimeout = setTimeout(() => {
                currentPage = 1;
                loadApplications(1);
            }, 300);
        }

        function showApplicationModal() {
            document.getElementById('applicationModal').classList.remove('hidden');
        }

        function hideApplicationModal() {
            document.getElementById('applicationModal').classList.add('hidden');
        }

        function formatDate(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleDateString();
        }
        
        function formatStatusName(status) {
            const statusNames = {
                pending: 'Pending',
                under_review: 'Under Review',
                reviewing: 'Under Review',
                interview_scheduled: 'Interview Scheduled',
                shortlisted: 'Shortlisted',
                accepted: 'Accepted',
                rejected: 'Rejected',
                withdrawn: 'Withdrawn'
            };
            return statusNames[status] || status.charAt(0).toUpperCase() + status.slice(1);
        }