// assets/js/opportunity-detail.js

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('opportunity-detail-container');
    const skeleton = document.getElementById('loading-skeleton');

    const getOpportunityId = () => {
        const params = new URLSearchParams(window.location.search);
        return params.get('id');
    };

    const fetchOpportunityDetails = async (id) => {
        try {
            const response = await api.get(`/opportunities/${id}/`);
            return response;
        } catch (error) {
            console.error('Error fetching opportunity details:', error);
            container.innerHTML = `<p class="error">Could not load opportunity details. Please try again later.</p>`;
            return null;
        }
    };

    // Helper function to format status names
    const formatStatusName = (status) => {
        const statusMap = {
            'pending': 'Under Review',
            'accepted': 'Accepted',
            'rejected': 'Not Selected',
            'withdrawn': 'Withdrawn'
        };
        return statusMap[status] || status;
    };

    // Check if user has already applied to this opportunity
    const checkApplicationStatus = async (opportunityId) => {
        try {
            if (!auth.isLoggedIn()) {
                console.log('User not logged in, skipping application check');
                return null;
            }
            
            console.log('Checking application status for opportunity:', opportunityId);
            const result = await api.applications.checkStatus(opportunityId);
            
            if (result) {
                console.log('Found existing application:', result.id, 'status:', result.status);
                return result;
            } else {
                console.log('No existing application found');
                return null;
            }
        } catch (error) {
            console.error('Failed to check application status:', error);
            return null;
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    };

    const renderQuestion = (q) => {
        const isRequired = q.is_required ? 'required' : '';
        const placeholder = q.placeholder ? `placeholder="${q.placeholder}"` : '';
        const helpText = q.help_text ? `<small class="form-text text-muted">${q.help_text}</small>` : '';
        const label = `<label for="question-${q.id}">${q.question}${q.is_required ? ' *' : ''}</label>`;

        let inputHtml = '';
        switch (q.question_type) {
            case 'textarea':
                inputHtml = `<textarea id="question-${q.id}" class="input" data-question-id="${q.id}" ${placeholder} ${isRequired}></textarea>`;
                break;
            case 'number':
            case 'email':
            case 'url':
            case 'date':
                inputHtml = `<input type="${q.question_type}" id="question-${q.id}" class="input" data-question-id="${q.id}" ${placeholder} ${isRequired}>`;
                break;
            case 'select':
                if (q.options && Array.isArray(q.options) && q.options.length > 0) {
                    const optionsHtml = q.options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
                    inputHtml = `<select id="question-${q.id}" class="input" data-question-id="${q.id}" ${isRequired}><option value="">Select...</option>${optionsHtml}</select>`;
                } else {
                    // Fallback to text input if options are missing for a select type
                    inputHtml = `<input type="text" id="question-${q.id}" class="input" data-question-id="${q.id}" ${placeholder} ${isRequired}>`;
                }
                break;
            case 'text':
            default:
                inputHtml = `<input type="text" id="question-${q.id}" class="input" data-question-id="${q.id}" ${placeholder} ${isRequired}>`;
                break;
        }

        return `
            <div class="form-group">
                ${label}
                ${inputHtml}
                ${helpText}
            </div>
        `;
    };

    const renderOpportunity = async (data) => {
        skeleton.style.display = 'none';

        // Set cover image
        const coverImageContainer = document.querySelector('.cover-image-container');
        if (coverImageContainer && data.cover_image) {
            coverImageContainer.style.backgroundImage = `url(${data.cover_image})`;
        }
        
        // Wait for user to be loaded before checking auth status
        await auth.waitForUser();
        
        // Check if user has already applied
        console.log('Checking application status for opportunity ID:', data.id);
        const existingApplication = await checkApplicationStatus(data.id);
        console.log('Existing application found:', existingApplication);
        
        const canApply = data.can_apply && !existingApplication;
        const isLoggedIn = auth.isLoggedIn();
        const currentUser = auth.getCurrentUser();
        const isStudent = currentUser?.user_type === 'student';
        
        console.log('Render conditions:', {
            canApply,
            isLoggedIn,
            isStudent,
            currentUser,
            existingApplication: !!existingApplication,
            dataCanApply: data.can_apply
        });

        const html = `
            <div class="opportunity-main">
                <header class="opportunity-header">
                    <h1 class="opportunity-title">${data.title}</h1>
                    <p class="organization-name">at ${data.organization.name}</p>
                    <div class="tags">
                        <span class="tag tag-type">${data.opportunity_type}</span>
                        <span class="tag tag-status">${data.status}</span>
                        ${data.is_remote ? '<span class="tag tag-remote">Remote</span>' : ''}
                    </div>
                </header>

                <section class="section">
                    <h2 class="section-title">Description</h2>
                    <div class="description-content">
                        ${data.description.replace(/\n/g, '<br>')}
                    </div>
                </section>

                <section class="section">
                    <h2 class="section-title">Details</h2>
                    <div class="details-grid">
                        <div class="detail-item">
                            <div class="detail-item-label">Location</div>
                            <div class="detail-item-value">${data.location}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-item-label">Compensation</div>
                            <div class="detail-item-value">${data.compensation || 'Not specified'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-item-label">Start Date</div>
                            <div class="detail-item-value">${formatDate(data.start_date)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-item-label">End Date</div>
                            <div class="detail-item-value">${data.end_date ? formatDate(data.end_date) : 'N/A'}</div>
                        </div>
                    </div>
                </section>

                <section class="section">
                    <h2 class="section-title">Requirements</h2>
                    <div class="details-grid">
                        ${data.min_gpa ? `
                        <div class="detail-item">
                            <div class="detail-item-label">Minimum GPA</div>
                            <div class="detail-item-value">${data.min_gpa}</div>
                        </div>` : ''}
                        ${data.required_major ? `
                        <div class="detail-item">
                            <div class="detail-item-label">Required Major</div>
                            <div class="detail-item-value">${data.required_major}</div>
                        </div>` : ''}
                        ${(data.graduation_year_min || data.graduation_year_max) ? `
                        <div class="detail-item">
                            <div class="detail-item-label">Graduation Year</div>
                            <div class="detail-item-value">${data.graduation_year_min || ''} - ${data.graduation_year_max || ''}</div>
                        </div>` : ''}
                    </div>
                </section>

                ${data.required_skills.length > 0 ? `
                <section class="section">
                    <h2 class="section-title">Required Skills</h2>
                    <div class="skills-list">
                        ${data.required_skills.map(skill => `<span class="skill-tag">${skill.name}</span>`).join('')}
                    </div>
                </section>` : ''}
                
                ${data.benefits ? `
                <section class="section">
                    <h2 class="section-title">Benefits</h2>
                    <div class="description-content">
                        ${data.benefits.replace(/\n/g, '<br>')}
                    </div>
                </section>` : ''}
            </div>

            <aside class="opportunity-sidebar">
                <div class="sidebar-card">
                    ${existingApplication ? `
                        <!-- Already Applied State -->
                        <div class="application-status-card">
                            <div class="status-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <h3 class="status-title">Application Submitted</h3>
                            <p class="status-description">You have already applied to this opportunity.</p>
                            <div class="status-details">
                                <div class="status-item">
                                    <span class="status-label">Status:</span>
                                    <span class="status-badge status-${existingApplication.status}">${formatStatusName(existingApplication.status)}</span>
                                </div>
                                <div class="status-item">
                                    <span class="status-label">Applied:</span>
                                    <span class="status-value">${formatDate(existingApplication.applied_at)}</span>
                                </div>
                            </div>
                            <a href="applications.html" class="btn btn-secondary">
                                <i class="fas fa-eye"></i>
                                View Application Status
                            </a>
                        </div>
                    ` : `
                        <!-- Apply Section -->
                        ${isLoggedIn && isStudent ? `
                            <button id="apply-btn" class="btn btn-primary" ${!canApply ? 'disabled' : ''}>
                                ${canApply ? 'Apply Now' : 'Applications Closed'}
                            </button>
                        ` : `
                            <a href="login.html" class="btn btn-primary">Login to Apply</a>
                        `}
                        <button class="btn btn-secondary" style="margin-top: 1rem;">Save for Later</button>
                    `}
                </div>
                <div class="sidebar-card">
                    <h3 class="sidebar-title">Key Information</h3>
                    <ul class="info-list">
                        <li><i class="fas fa-calendar-times"></i> <strong>Deadline:</strong> ${formatDate(data.application_deadline)}</li>
                        <li><i class="fas fa-users"></i> <strong>Applications:</strong> ${data.application_count} received</li>
                        ${data.max_applications ? `<li><i class="fas fa-bullseye"></i> <strong>Limit:</strong> ${data.max_applications} applications</li>` : ''}
                    </ul>
                </div>
                <div class="sidebar-card">
                    <h3 class="sidebar-title">About ${data.organization.name}</h3>
                    <p style="font-size: 0.9rem; color: var(--mist-300);">${data.organization.bio || 'No bio available.'}</p>
                    <a href="${data.organization.website}" target="_blank" class="btn btn-secondary" style="margin-top: 1rem;">Visit Website</a>
                </div>
            </aside>
        `;

        container.innerHTML = html;
        
        if (canApply && isLoggedIn && isStudent) {
            document.getElementById('apply-btn').addEventListener('click', () => {
                openApplicationModal(data);
            });
        }
    };

    const openApplicationModal = (opportunityData) => {
        const modal = document.getElementById('applicationModal');
        const title = document.getElementById('modal-opportunity-title');
        const questionsContainer = document.getElementById('additional-questions-container');
        
        if (modal && title && questionsContainer) {
            title.textContent = `${opportunityData.title} at ${opportunityData.organization.name}`;
            
            // Render additional questions
            questionsContainer.innerHTML = ''; // Clear previous questions
            if (opportunityData.additional_questions && opportunityData.additional_questions.length > 0) {
                const questionsHtml = opportunityData.additional_questions.map(renderQuestion).join('');
                questionsContainer.innerHTML = questionsHtml;
            }

            modal.style.display = 'flex';
        }

        // Setup close buttons
        document.getElementById('closeApplicationModal').addEventListener('click', closeApplicationModal);
        document.getElementById('cancelApplication').addEventListener('click', closeApplicationModal);
    };

    const closeApplicationModal = () => {
        const modal = document.getElementById('applicationModal');
        if (modal) {
            modal.style.display = 'none';
        }
    };

    const handleApplicationSubmit = async (event) => {
        event.preventDefault();
        const submitBtn = document.getElementById('submitApplication');
        const submitText = document.getElementById('submitButtonText');
        const spinner = document.getElementById('submitSpinner');

        submitBtn.disabled = true;
        submitText.textContent = 'Submitting...';
        spinner.classList.remove('hidden');

        try {
            const opportunityId = getOpportunityId();
            const notes = document.getElementById('applicationNotes').value;
            const fileInput = document.getElementById('documentUpload');
            const files = fileInput.files;

            // Collect answers to additional questions
            const additionalAnswers = [];
            const questionElements = document.querySelectorAll('#additional-questions-container [data-question-id]');
            questionElements.forEach(input => {
                additionalAnswers.push({
                    question: input.dataset.questionId,
                    answer_text: input.value
                });
            });

            const applicationData = {
                opportunity: opportunityId,
                notes: notes,
                answers: additionalAnswers
                // We will handle file uploads separately if needed by the API
            };

            // This is a simplified submission. A real scenario might involve
            // uploading files first, then submitting the application with file URLs.
            const response = await api.applications.submit(applicationData);

            console.log('Application submitted:', response);
            Utils.showToast('Application submitted successfully!', 'success');
            closeApplicationModal();
            // Optionally, refresh some data on the page
            document.getElementById('apply-btn').textContent = 'Applied';
            document.getElementById('apply-btn').disabled = true;

        } catch (error) {
            console.error('Application submission failed:', error);
            Utils.showToast(error.message || 'Failed to submit application.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitText.textContent = 'Submit Application';
            spinner.classList.add('hidden');
        }
    };

    const init = async () => {
        const opportunityId = getOpportunityId();
        if (!opportunityId) {
            container.innerHTML = `<p class="error">No opportunity ID provided.</p>`;
            skeleton.style.display = 'none';
            return;
        }
        const opportunityData = await fetchOpportunityDetails(opportunityId);
        if (opportunityData) {
            renderOpportunity(opportunityData);

            // Setup application form submission handler
            document.getElementById('applicationForm').addEventListener('submit', handleApplicationSubmit);
        }
    };

    init();
});
