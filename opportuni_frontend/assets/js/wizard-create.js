/**
 * Wizard Create - Clean Step-by-Step Opportunity Creation
 * No jQuery, pure vanilla JS with robust step management
 */

class WizardApp {
  constructor() {
    this.currentStep = 1;
    this.totalSteps = 8;
    this.data = {};
    this.requirements = [];
    this.questions = [];
    this.skills = [];
    
    this.init();
  }

  init() {
    this.updateProgress();
    this.showStep(1);
  }

  // Step Navigation
  nextStep() {
    if (this.currentStep < this.totalSteps) {
      if (this.validateCurrentStep()) {
        this.saveCurrentStepData();
        this.currentStep++;
        this.updateProgress();
        this.showStep(this.currentStep);
      }
    } else {
      // Final step - submit
      this.submitOpportunity();
    }
  }

  prevStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.updateProgress();
      this.showStep(this.currentStep);
    }
  }

  // Progress Updates
  updateProgress() {
    const progressText = document.getElementById('progress-text');
    const progressStatus = document.getElementById('progress-status');
    const progressFill = document.getElementById('progress-fill');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    // Progress percentage
    const percentage = (this.currentStep / this.totalSteps) * 100;
    progressFill.style.width = `${percentage}%`;
    
    // Step text
    progressText.textContent = `Step ${this.currentStep} of ${this.totalSteps}`;
    
    // Status
    const statuses = [
      'Basic Information',
      'Opportunity Type & Details', 
      'Timeline & Deadlines',
      'Location & Compensation',
      'Student Requirements',
      'Application Questions',
      'Skills & Qualifications',
      'Review & Publish'
    ];
    progressStatus.textContent = statuses[this.currentStep - 1];

    // Button states
    btnPrev.disabled = this.currentStep === 1;
    btnNext.textContent = this.currentStep === this.totalSteps ? 
      'Publish Opportunity' : 'Next';
    
    if (this.currentStep === this.totalSteps) {
      btnNext.innerHTML = '<i class="fas fa-rocket"></i> Publish Opportunity';
    } else {
      btnNext.innerHTML = 'Next <i class="fas fa-chevron-right"></i>';
    }
  }

  // Step Content Rendering
  showStep(step) {
    const title = document.getElementById('wizard-title');
    const hint = document.getElementById('wizard-hint');
    const content = document.getElementById('wizard-content');

    switch(step) {
      case 1:
        title.textContent = 'Tell us about your opportunity';
        hint.textContent = "Let's start with the basics - what kind of opportunity are you offering?";
        content.innerHTML = this.renderStep1();
        break;
      case 2:
        title.textContent = 'Opportunity details';
        hint.textContent = 'Help students understand what this opportunity involves.';
        content.innerHTML = this.renderStep2();
        break;
      case 3:
        title.textContent = 'Timeline & deadlines';
        hint.textContent = 'When can students apply and when does the opportunity begin?';
        content.innerHTML = this.renderStep3();
        break;
      case 4:
        title.textContent = 'Location & compensation';
        hint.textContent = 'Where will students work and how will they be compensated?';
        content.innerHTML = this.renderStep4();
        break;
      case 5:
        title.textContent = 'Student requirements';
        hint.textContent = 'What academic requirements must students meet to apply?';
        content.innerHTML = this.renderStep5();
        break;
      case 6:
        title.textContent = 'Application questions';
        hint.textContent = 'Add custom questions to learn more about applicants.';
        content.innerHTML = this.renderStep6();
        break;
      case 7:
        title.textContent = 'Skills & qualifications';
        hint.textContent = 'What skills or qualifications are you looking for?';
        content.innerHTML = this.renderStep7();
        break;
      case 8:
        title.textContent = 'Review & publish';
        hint.textContent = 'Review your opportunity details before publishing.';
        content.innerHTML = this.renderStep8();
        break;
    }

    // Populate existing data
    this.populateStepData(step);
  }

  // Step 1: Basic Information
  renderStep1() {
    return `
      <div class="step-field">
        <label for="step_title">Opportunity Title *</label>
        <input type="text" id="step_title" class="step-input step-large" 
               placeholder="e.g. Software Development Internship" required>
      </div>
      
      <div class="step-field">
        <label for="step_description">Description *</label>
        <textarea id="step_description" class="step-input step-textarea" 
                  placeholder="Describe what students will do, learn, and gain from this opportunity..." required></textarea>
        <div class="step-tip">
          <i class="fas fa-lightbulb"></i>
          <span>Include key responsibilities, learning outcomes, and what makes this opportunity unique.</span>
        </div>
      </div>
    `;
  }

  // Step 2: Type & Details
  renderStep2() {
    return `
      <div class="step-field">
        <label>Opportunity Type *</label>
        <div class="step-segments">
          <button type="button" class="segment-btn" data-value="internship">Internship</button>
          <button type="button" class="segment-btn" data-value="job">Job</button>
          <button type="button" class="segment-btn" data-value="scholarship">Scholarship</button>
          <button type="button" class="segment-btn" data-value="competition">Competition</button>
          <button type="button" class="segment-btn" data-value="volunteer">Volunteer</button>
          <button type="button" class="segment-btn" data-value="event">Event</button>
        </div>
      </div>

      <div class="step-field">
        <label for="step_max_applications">Maximum Applications</label>
        <input type="number" id="step_max_applications" class="step-input" 
               placeholder="e.g. 50" min="1">
        <div class="step-tip">
          <i class="fas fa-info-circle"></i>
          <span>Leave blank for unlimited applications. Applications will automatically close when limit is reached.</span>
        </div>
      </div>

      <div class="step-field">
        <div class="step-checkbox">
          <input type="checkbox" id="step_featured">
          <label for="step_featured">Feature this opportunity (appears at top of listings)</label>
        </div>
        <div class="step-checkbox">
          <input type="checkbox" id="step_urgent">
          <label for="step_urgent">Mark as urgent (deadline approaching)</label>
        </div>
      </div>
    `;
  }

  // Step 3: Timeline
  renderStep3() {
    return `
      <div class="step-field">
        <label for="step_application_deadline">Application Deadline *</label>
        <input type="datetime-local" id="step_application_deadline" class="step-input" required>
      </div>
      
      <div class="step-grid">
        <div class="step-field">
          <label for="step_start_date">Start Date</label>
          <input type="datetime-local" id="step_start_date" class="step-input">
        </div>
        <div class="step-field">
          <label for="step_end_date">End Date</label>
          <input type="datetime-local" id="step_end_date" class="step-input">
        </div>
      </div>

      <div class="step-tip">
        <i class="fas fa-calendar-alt"></i>
        <span>Start and end dates help students understand the time commitment involved.</span>
      </div>
    `;
  }

  // Step 4: Location & Compensation
  renderStep4() {
    return `
      <div class="step-field">
        <label>Work Location Type *</label>
        <div class="step-segments">
          <button type="button" class="segment-btn" data-value="on_site">On-site</button>
          <button type="button" class="segment-btn" data-value="remote">Remote</button>
          <button type="button" class="segment-btn" data-value="hybrid">Hybrid</button>
        </div>
      </div>

      <div class="step-field">
        <label for="step_location">Location Details</label>
        <input type="text" id="step_location" class="step-input" 
               placeholder="e.g. San Francisco, CA or Anywhere USA">
      </div>

      <div class="step-grid">
        <div class="step-field">
          <label for="step_compensation_type">Compensation Type</label>
          <select id="step_compensation_type" class="step-input">
            <option value="">Select type...</option>
            <option value="stipend">Stipend</option>
            <option value="salary">Salary</option>
            <option value="hourly">Hourly</option>
            <option value="scholarship">Scholarship</option>
            <option value="unpaid">Unpaid</option>
          </select>
        </div>
        <div class="step-field">
          <label for="step_compensation_amount">Amount ($)</label>
          <input type="number" id="step_compensation_amount" class="step-input" 
                 placeholder="0" min="0">
        </div>
      </div>
    `;
  }

  // Step 5: Student Requirements
  renderStep5() {
    return `
      <div class="step-grid">
        <div class="step-field">
          <label for="step_min_gpa">Minimum GPA</label>
          <input type="number" id="step_min_gpa" class="step-input" 
                 placeholder="3.0" min="0" max="4" step="0.1">
        </div>
        <div class="step-field">
          <label for="step_required_major">Required Major</label>
          <input type="text" id="step_required_major" class="step-input" 
                 placeholder="e.g. Computer Science">
        </div>
      </div>

      <div class="step-grid">
        <div class="step-field">
          <label for="step_min_year">Minimum Year</label>
          <select id="step_min_year" class="step-input">
            <option value="">Any year</option>
            <option value="freshman">Freshman</option>
            <option value="sophomore">Sophomore</option>
            <option value="junior">Junior</option>
            <option value="senior">Senior</option>
            <option value="graduate">Graduate</option>
          </select>
        </div>
        <div class="step-field">
          <label for="step_max_year">Maximum Year</label>
          <select id="step_max_year" class="step-input">
            <option value="">Any year</option>
            <option value="freshman">Freshman</option>
            <option value="sophomore">Sophomore</option>
            <option value="junior">Junior</option>
            <option value="senior">Senior</option>
            <option value="graduate">Graduate</option>
          </select>
        </div>
      </div>

      <div class="builder-section">
        <div class="builder-header">
          <span class="builder-title">Additional Requirements</span>
          <button type="button" class="btn btn--ghost btn-small" onclick="wizardApp.addRequirement()">
            <i class="fas fa-plus"></i> Add
          </button>
        </div>
        <ul id="requirements-list" class="builder-list">
          <!-- Dynamic requirements -->
        </ul>
      </div>
    `;
  }

  // Step 6: Application Questions
  renderStep6() {
    return `
      <div class="step-field">
        <label for="step_application_instructions">Application Instructions</label>
        <textarea id="step_application_instructions" class="step-input step-textarea" 
                  placeholder="Tell students what to include in their application, how to apply, or any special instructions..."></textarea>
      </div>

      <div class="builder-section">
        <div class="builder-header">
          <span class="builder-title">Custom Questions</span>
          <button type="button" class="btn btn--ghost btn-small" onclick="wizardApp.addQuestion()">
            <i class="fas fa-plus"></i> Add Question
          </button>
        </div>
        <ul id="questions-list" class="builder-list">
          <!-- Dynamic questions -->
        </ul>
      </div>

      <div class="step-tip">
        <i class="fas fa-question-circle"></i>
        <span>Ask questions that help you evaluate candidates beyond their resume.</span>
      </div>
    `;
  }

  // Step 7: Skills & Qualifications
  renderStep7() {
    return `
      <div class="builder-section">
        <div class="builder-header">
          <span class="builder-title">Required Skills</span>
          <button type="button" class="btn btn--ghost btn-small" onclick="wizardApp.addSkill()">
            <i class="fas fa-plus"></i> Add Skill
          </button>
        </div>
        <ul id="skills-list" class="builder-list">
          <!-- Dynamic skills -->
        </ul>
      </div>

      <div class="step-tip">
        <i class="fas fa-code"></i>
        <span>List technical skills, programming languages, tools, or soft skills you're looking for.</span>
      </div>
    `;
  }

  // Step 8: Review
  renderStep8() {
    return `
      <div class="review-section">
        <div id="review-content">
          <!-- Review content populated by JS -->
        </div>
      </div>
    `;
  }

  // Data Management
  saveCurrentStepData() {
    const step = this.currentStep;
    
    switch(step) {
      case 1:
        this.data.title = document.getElementById('step_title')?.value || '';
        this.data.description = document.getElementById('step_description')?.value || '';
        break;
      case 2:
        this.data.type = document.querySelector('.segment-btn.active')?.dataset.value || '';
        this.data.max_applications = document.getElementById('step_max_applications')?.value || null;
        this.data.featured = document.getElementById('step_featured')?.checked || false;
        this.data.urgent = document.getElementById('step_urgent')?.checked || false;
        break;
      case 3:
        this.data.application_deadline = document.getElementById('step_application_deadline')?.value || '';
        this.data.start_date = document.getElementById('step_start_date')?.value || '';
        this.data.end_date = document.getElementById('step_end_date')?.value || '';
        break;
      case 4:
        this.data.location_type = document.querySelector('.segment-btn.active')?.dataset.value || '';
        this.data.location = document.getElementById('step_location')?.value || '';
        this.data.compensation_type = document.getElementById('step_compensation_type')?.value || '';
        this.data.compensation_amount = document.getElementById('step_compensation_amount')?.value || null;
        break;
      case 5:
        this.data.min_gpa = document.getElementById('step_min_gpa')?.value || null;
        this.data.required_major = document.getElementById('step_required_major')?.value || '';
        this.data.min_year = document.getElementById('step_min_year')?.value || '';
        this.data.max_year = document.getElementById('step_max_year')?.value || '';
        break;
      case 6:
        this.data.application_instructions = document.getElementById('step_application_instructions')?.value || '';
        break;
    }
  }

  populateStepData(step) {
    // Wait for next tick to ensure DOM is rendered
    setTimeout(() => {
      switch(step) {
        case 1:
          if (this.data.title) document.getElementById('step_title').value = this.data.title;
          if (this.data.description) document.getElementById('step_description').value = this.data.description;
          break;
        case 2:
          this.setupSegmentButtons();
          if (this.data.type) this.activateSegment(this.data.type);
          if (this.data.max_applications) document.getElementById('step_max_applications').value = this.data.max_applications;
          if (this.data.featured) document.getElementById('step_featured').checked = this.data.featured;
          if (this.data.urgent) document.getElementById('step_urgent').checked = this.data.urgent;
          break;
        case 3:
          if (this.data.application_deadline) document.getElementById('step_application_deadline').value = this.data.application_deadline;
          if (this.data.start_date) document.getElementById('step_start_date').value = this.data.start_date;
          if (this.data.end_date) document.getElementById('step_end_date').value = this.data.end_date;
          break;
        case 4:
          this.setupSegmentButtons();
          if (this.data.location_type) this.activateSegment(this.data.location_type);
          if (this.data.location) document.getElementById('step_location').value = this.data.location;
          if (this.data.compensation_type) document.getElementById('step_compensation_type').value = this.data.compensation_type;
          if (this.data.compensation_amount) document.getElementById('step_compensation_amount').value = this.data.compensation_amount;
          break;
        case 5:
          if (this.data.min_gpa) document.getElementById('step_min_gpa').value = this.data.min_gpa;
          if (this.data.required_major) document.getElementById('step_required_major').value = this.data.required_major;
          if (this.data.min_year) document.getElementById('step_min_year').value = this.data.min_year;
          if (this.data.max_year) document.getElementById('step_max_year').value = this.data.max_year;
          this.renderRequirements();
          break;
        case 6:
          if (this.data.application_instructions) document.getElementById('step_application_instructions').value = this.data.application_instructions;
          this.renderQuestions();
          break;
        case 7:
          this.renderSkills();
          break;
        case 8:
          this.renderReview();
          break;
      }
    }, 50);
  }

  // Segment Button Logic
  setupSegmentButtons() {
    document.querySelectorAll('.segment-btn').forEach(btn => {
      btn.onclick = () => this.activateSegment(btn.dataset.value);
    });
  }

  activateSegment(value) {
    document.querySelectorAll('.segment-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.value === value);
    });
  }

  // Builders
  addRequirement() {
    const text = prompt('Enter requirement:');
    if (text?.trim()) {
      this.requirements.push(text.trim());
      this.renderRequirements();
    }
  }

  removeRequirement(index) {
    this.requirements.splice(index, 1);
    this.renderRequirements();
  }

  renderRequirements() {
    const list = document.getElementById('requirements-list');
    if (!list) return;
    
    list.innerHTML = this.requirements.map((req, i) => `
      <li class="builder-item">
        <span>${req}</span>
        <div class="builder-controls">
          <button type="button" class="btn btn--ghost btn-small" onclick="wizardApp.removeRequirement(${i})">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </li>
    `).join('');
  }

  addQuestion() {
    const text = prompt('Enter question:');
    if (text?.trim()) {
      this.questions.push(text.trim());
      this.renderQuestions();
    }
  }

  removeQuestion(index) {
    this.questions.splice(index, 1);
    this.renderQuestions();
  }

  renderQuestions() {
    const list = document.getElementById('questions-list');
    if (!list) return;
    
    list.innerHTML = this.questions.map((q, i) => `
      <li class="builder-item">
        <span>${q}</span>
        <div class="builder-controls">
          <button type="button" class="btn btn--ghost btn-small" onclick="wizardApp.removeQuestion(${i})">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </li>
    `).join('');
  }

  addSkill() {
    const text = prompt('Enter skill or qualification:');
    if (text?.trim()) {
      this.skills.push(text.trim());
      this.renderSkills();
    }
  }

  removeSkill(index) {
    this.skills.splice(index, 1);
    this.renderSkills();
  }

  renderSkills() {
    const list = document.getElementById('skills-list');
    if (!list) return;
    
    list.innerHTML = this.skills.map((skill, i) => `
      <li class="builder-item">
        <span>${skill}</span>
        <div class="builder-controls">
          <button type="button" class="btn btn--ghost btn-small" onclick="wizardApp.removeSkill(${i})">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </li>
    `).join('');
  }

  // Review Content
  renderReview() {
    const content = document.getElementById('review-content');
    if (!content) return;

    content.innerHTML = `
      <div class="review-item">
        <div class="review-label">Title</div>
        <div class="review-value">${this.data.title || 'Not set'}</div>
      </div>
      <div class="review-item">
        <div class="review-label">Type</div>
        <div class="review-value">${this.data.type || 'Not set'}</div>
      </div>
      <div class="review-item">
        <div class="review-label">Description</div>
        <div class="review-value">${this.data.description || 'Not set'}</div>
      </div>
      <div class="review-item">
        <div class="review-label">Deadline</div>
        <div class="review-value">${this.data.application_deadline || 'Not set'}</div>
      </div>
      <div class="review-item">
        <div class="review-label">Location</div>
        <div class="review-value">${this.data.location || 'Not set'} (${this.data.location_type || 'Not set'})</div>
      </div>
      <div class="review-item">
        <div class="review-label">Compensation</div>
        <div class="review-value">$${this.data.compensation_amount || '0'} ${this.data.compensation_type || ''}</div>
      </div>
      <div class="review-item">
        <div class="review-label">Requirements</div>
        <div class="review-value">${this.requirements.length} items</div>
      </div>
      <div class="review-item">
        <div class="review-label">Questions</div>
        <div class="review-value">${this.questions.length} items</div>
      </div>
      <div class="review-item">
        <div class="review-label">Skills</div>
        <div class="review-value">${this.skills.length} items</div>
      </div>
    `;
  }

  // Validation
  validateCurrentStep() {
    const step = this.currentStep;
    
    switch(step) {
      case 1:
        const title = document.getElementById('step_title')?.value;
        const description = document.getElementById('step_description')?.value;
        if (!title?.trim() || !description?.trim()) {
          alert('Please fill in all required fields.');
          return false;
        }
        break;
      case 2:
        const type = document.querySelector('.segment-btn.active')?.dataset.value;
        if (!type) {
          alert('Please select an opportunity type.');
          return false;
        }
        break;
      case 3:
        const deadline = document.getElementById('step_application_deadline')?.value;
        if (!deadline) {
          alert('Please set an application deadline.');
          return false;
        }
        break;
      case 4:
        const locationType = document.querySelector('.segment-btn.active')?.dataset.value;
        if (!locationType) {
          alert('Please select a location type.');
          return false;
        }
        break;
    }
    
    return true;
  }

  // Draft & Submit
  saveDraft() {
    this.saveCurrentStepData();
    alert('Draft saved! You can continue editing later.');
  }

  async submitOpportunity() {
    try {
      // Wait for auth to be ready if it's still loading
      if (window.auth && window.auth.userLoadPromise) {
        try {
          await window.auth.userLoadPromise;
        } catch (e) {
          console.warn('Auth load failed:', e);
        }
      }

      // Debug logging
      const isLoggedIn = window.auth?.isLoggedIn?.();
      const currentUser = window.auth?.getCurrentUser?.();
      console.log('Auth debug:', { isLoggedIn, currentUser, userType: currentUser?.user_type });

      // Check authentication
      if (!isLoggedIn) {
        throw new Error('You must be logged in to create opportunities');
      }

      // Check if user is organization
      if (currentUser?.user_type !== 'organization') {
        throw new Error('Only organizations can create opportunities');
      }

      // Check API availability
      if (!window.api?.opportunities?.create) {
        throw new Error('API not available. Please refresh the page and try again.');
      }

      this.saveCurrentStepData();
      
      // Prepare payload according to backend API structure
      const payload = {
        // Basic fields (step 1)
        title: this.data.title,
        description: this.data.description,
        
        // Type and settings (step 2)
        opportunity_type: this.data.type, // backend expects 'opportunity_type'
        max_applications: this.data.max_applications || null,
        featured: this.data.featured || false,
        status: 'published', // publish directly
        
        // Timeline (step 3)
        application_deadline: this.data.application_deadline,
        start_date: this.data.start_date ? this.data.start_date.split('T')[0] : new Date().toISOString().split('T')[0], // default to today if empty
        end_date: this.data.end_date ? this.data.end_date.split('T')[0] : null,
        
        // Location and compensation (step 4)
        location: this.data.location || '',
        is_remote: this.data.location_type === 'remote',
        compensation: this.formatCompensation(),
        
        // Requirements (step 5)
        min_gpa: this.data.min_gpa || null,
        required_major: this.data.required_major || '',
        graduation_year_min: this.convertYearToNumber(this.data.min_year),
        graduation_year_max: this.convertYearToNumber(this.data.max_year),
        
        // Related objects
        requirements: this.requirements.map((req, index) => ({
          requirement: req,
          is_mandatory: true,
          order: index
        })),
        additional_questions: this.questions.map((q, index) => ({
          question: q,
          question_type: 'textarea',
          is_required: false,
          order: index
        })),
        required_skills: [] // Will be populated with skill IDs later
      };

      console.log('Submitting opportunity with payload:', payload);
      
      // Show loading state
      const btnNext = document.getElementById('btn-next');
      const originalText = btnNext.innerHTML;
      btnNext.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publishing...';
      btnNext.disabled = true;
      
      // Submit via API
      const response = await window.api.opportunities.create(payload);
      
      if (response && (response.id || response.success !== false)) {
        // Success
        this.showSuccessMessage();
        setTimeout(() => {
          window.location.href = 'opportunities.html';
        }, 2000);
      } else {
        // Check for validation errors
        if (response && response.errors) {
          const errorMessages = this.formatValidationErrors(response.errors);
          throw new Error(errorMessages);
        }
        throw new Error(response?.error || response?.message || response?.detail || 'Failed to create opportunity');
      }
    } catch (error) {
      console.error('Submit error:', error);
      
      // Reset button
      const btnNext = document.getElementById('btn-next');
      btnNext.innerHTML = '<i class="fas fa-rocket"></i> Publish Opportunity';
      btnNext.disabled = false;
      
      // Show error
      this.showErrorMessage(error.message || 'Failed to create opportunity. Please try again.');
    }
  }

  // Helper methods for data formatting
  formatCompensation() {
    if (this.data.compensation_type === 'unpaid' || !this.data.compensation_type) {
      return 'Unpaid';
    }
    
    const amount = this.data.compensation_amount;
    const type = this.data.compensation_type;
    
    if (!amount || amount === '0') {
      return this.capitalizeFirst(type);
    }
    
    return `$${amount} ${type}`;
  }

  convertYearToNumber(yearString) {
    if (!yearString) return null;
    
    const yearMap = {
      'freshman': 1,
      'sophomore': 2,
      'junior': 3,
      'senior': 4,
      'graduate': 5
    };
    
    return yearMap[yearString] || null;
  }

  capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  formatValidationErrors(errors) {
    if (typeof errors === 'string') return errors;
    
    const messages = [];
    for (const [field, fieldErrors] of Object.entries(errors)) {
      if (Array.isArray(fieldErrors)) {
        messages.push(`${field}: ${fieldErrors.join(', ')}`);
      } else {
        messages.push(`${field}: ${fieldErrors}`);
      }
    }
    return messages.join('\n');
  }

  formatValidationErrors(errors) {
    if (typeof errors === 'string') return errors;
    
    const messages = [];
    for (const [field, fieldErrors] of Object.entries(errors)) {
      const fieldName = field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      if (Array.isArray(fieldErrors)) {
        messages.push(`${fieldName}: ${fieldErrors.join(', ')}`);
      } else {
        messages.push(`${fieldName}: ${fieldErrors}`);
      }
    }
    return messages.join('\n');
  }

  showSuccessMessage() {
    const content = document.getElementById('wizard-content');
    content.innerHTML = `
      <div class="success-message">
        <div class="success-icon">
          <i class="fas fa-check-circle"></i>
        </div>
        <h3>Opportunity Published Successfully!</h3>
        <p>Your opportunity is now live and students can start applying.</p>
        <div class="success-actions">
          <button type="button" class="btn btn--ghost" onclick="window.location.href='opportunities.html'">
            View All Opportunities
          </button>
        </div>
      </div>
    `;
  }

  showErrorMessage(message) {
    const content = document.getElementById('wizard-content');
    content.innerHTML = `
      <div class="error-message">
        <div class="error-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3>Error Creating Opportunity</h3>
        <p>${message}</p>
        <div class="error-actions">
          <button type="button" class="btn btn--primary" onclick="wizardApp.showStep(${this.currentStep})">
            <i class="fas fa-redo"></i>
            Try Again
          </button>
          <button type="button" class="btn btn--ghost" onclick="window.location.href='opportunities.html'">
            Cancel
          </button>
        </div>
      </div>
    `;
  }
}

// Initialize app
let wizardApp;
document.addEventListener('DOMContentLoaded', async () => {
  // Wait for auth to be ready
  if (window.auth && window.auth.userLoadPromise) {
    try {
      await window.auth.userLoadPromise;
    } catch (e) {
      console.warn('Auth initialization failed:', e);
    }
  }
  
  wizardApp = new WizardApp();
});
