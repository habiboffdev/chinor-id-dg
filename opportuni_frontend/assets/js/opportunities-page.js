// Opportunities Page Controller

class OpportunitiesPage {
  constructor() {
    this.opportunities = [];
    this.loading = false;
  }

  async init() {
    try {
      console.log('OpportunitiesPage: Starting initialization...');
      
      // Check if we have a token first
      const token = window.Utils?.storage?.get('auth_token');
      console.log('OpportunitiesPage: Token exists:', !!token);
      
      // Wait for auth to be ready
      if (window.auth && window.auth.userLoadPromise) {
        console.log('OpportunitiesPage: Waiting for auth to be ready...');
        try {
          await window.auth.userLoadPromise;
        } catch (authError) {
          console.error('OpportunitiesPage: Auth load failed:', authError);
          // If auth fails, redirect to login
          window.location.href = '../login.html';
          return;
        }
      }

      // Additional wait to ensure currentUser is loaded
      if (!window.auth.getCurrentUser()) {
        console.log('OpportunitiesPage: User still null, waiting for user load...');
        try {
          await window.auth.waitForUser();
        } catch (userError) {
          console.error('OpportunitiesPage: User load failed:', userError);
          // If user load fails, redirect to login
          window.location.href = '../login.html';
          return;
        }
      }

      // Check if user is logged in and is an organization
      if (!window.auth?.isLoggedIn?.()) {
        console.log('OpportunitiesPage: User not logged in, redirecting to login');
        window.location.href = '../login.html';
        return;
      }

      const currentUser = window.auth.getCurrentUser();
      console.log('OpportunitiesPage: Current user after wait:', currentUser);
      
      if (!currentUser) {
        console.log('OpportunitiesPage: Current user is still null, redirecting to login');
        window.location.href = '../login.html';
        return;
      }
      
      if (currentUser?.user_type !== 'organization') {
        console.log('OpportunitiesPage: User is not organization type, redirecting to dashboard');
        window.location.href = '../dashboard.html';
        return;
      }

      console.log('OpportunitiesPage: Auth checks passed, loading opportunities...');
      await this.loadOpportunities();
    } catch (error) {
      console.error('OpportunitiesPage: Failed to initialize:', error);
      this.showError('Failed to load opportunities');
    }
  }

  async loadOpportunities() {
    try {
      this.showLoading(true);
      
      if (!window.api?.opportunities?.getList) {
        throw new Error('API not available');
      }

      // Get all opportunities for this organization (not just active ones)
      // The backend will automatically filter by organization for authenticated org users
      console.log('OpportunitiesPage: Calling API to get opportunities...');
      const response = await window.api.opportunities.getList();
      console.log('OpportunitiesPage: API response:', response);
      
      this.opportunities = response.results || response || [];
      console.log('OpportunitiesPage: Loaded opportunities:', this.opportunities.length);
      
      this.renderOpportunities();
    } catch (error) {
      console.error('Failed to load opportunities:', error);
      this.showError('Failed to load opportunities');
    } finally {
      this.showLoading(false);
    }
  }

  renderOpportunities() {
    const cardBody = document.querySelector('.org-card__body');
    if (!cardBody) return;

    if (this.opportunities.length === 0) {
      cardBody.innerHTML = `
        <div class="empty-state">
          <div class="empty-state__icon">
            <i class="fas fa-briefcase"></i>
          </div>
          <h3 class="empty-state__title">No opportunities yet</h3>
          <p class="empty-state__text">
            Create your first opportunity to start connecting with talented students.
          </p>
          <a href="opportunity-create.html" class="btn btn--primary">
            <i class="fas fa-plus"></i>
            Create Your First Opportunity
          </a>
        </div>
      `;
      return;
    }

    // Render opportunities list
    const opportunitiesHtml = this.opportunities.map(opp => this.renderOpportunityCard(opp)).join('');
    cardBody.innerHTML = `
      <div class="opportunities-grid">
        ${opportunitiesHtml}
      </div>
    `;
  }

  renderOpportunityCard(opportunity) {
    const statusClass = this.getStatusClass(opportunity.status);
    const typeIcon = this.getTypeIcon(opportunity.opportunity_type);
    
    return `
      <div class="opportunity-card">
        <div class="opportunity-card__header">
          <div class="opportunity-card__icon">
            <i class="${typeIcon}"></i>
          </div>
          <div class="opportunity-card__status ${statusClass}">
            ${opportunity.status}
          </div>
        </div>
        <div class="opportunity-card__body">
          <h3 class="opportunity-card__title">${Utils.escapeHTML(opportunity.title)}</h3>
          <p class="opportunity-card__type">${opportunity.opportunity_type}</p>
          <p class="opportunity-card__location">
            <i class="fas fa-map-marker-alt"></i>
            ${opportunity.is_remote ? 'Remote' : Utils.escapeHTML(opportunity.location)}
          </p>
          <div class="opportunity-card__meta">
            <span class="meta-item">
              <i class="fas fa-users"></i>
              ${opportunity.application_count || 0} applications
            </span>
            <span class="meta-item">
              <i class="fas fa-calendar"></i>
              Deadline: ${this.formatDate(opportunity.application_deadline)}
            </span>
          </div>
        </div>
        <div class="opportunity-card__actions">
          <a href="opportunity-edit.html?id=${opportunity.id}" class="btn btn--ghost btn--small">
            <i class="fas fa-edit"></i>
            Edit
          </a>
          <a href="applications.html?opportunity=${opportunity.id}" class="btn btn--primary btn--small">
            <i class="fas fa-users"></i>
            View Applications
          </a>
        </div>
      </div>
    `;
  }

  getStatusClass(status) {
    const statusClasses = {
      'published': 'status--success',
      'draft': 'status--warning',
      'closed': 'status--danger',
      'cancelled': 'status--danger'
    };
    return statusClasses[status] || 'status--default';
  }

  getTypeIcon(type) {
    const typeIcons = {
      'internship': 'fas fa-briefcase',
      'job': 'fas fa-building',
      'volunteer': 'fas fa-heart',
      'scholarship': 'fas fa-graduation-cap',
      'competition': 'fas fa-trophy',
      'workshop': 'fas fa-chalkboard-teacher',
      'conference': 'fas fa-microphone-alt'
    };
    return typeIcons[type] || 'fas fa-briefcase';
  }

  formatDate(dateString) {
    if (!dateString) return 'Not set';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Invalid date';
    }
  }

  showLoading(show) {
    this.loading = show;
    const cardBody = document.querySelector('.org-card__body');
    if (!cardBody) return;

    if (show) {
      cardBody.innerHTML = `
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Loading opportunities...</p>
        </div>
      `;
    }
  }

  showError(message) {
    const cardBody = document.querySelector('.org-card__body');
    if (!cardBody) return;

    cardBody.innerHTML = `
      <div class="error-state">
        <div class="error-state__icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <h3 class="error-state__title">Error</h3>
        <p class="error-state__text">${Utils.escapeHTML(message)}</p>
        <button type="button" class="btn btn--primary" onclick="opportunitiesPage.loadOpportunities()">
          <i class="fas fa-refresh"></i>
          Retry
        </button>
      </div>
    `;
  }
}

// Initialize page
let opportunitiesPage;
document.addEventListener('DOMContentLoaded', async () => {
  opportunitiesPage = new OpportunitiesPage();
  await opportunitiesPage.init();
});
