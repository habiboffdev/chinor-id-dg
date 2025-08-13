// Main JavaScript for Opportuni Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

// Initialize application
function initializeApp() {
    // Setup navigation
    setupNavigation();
    
    // Setup smooth scrolling
    setupSmoothScrolling();
    
    // Setup counter animations
    setupCounterAnimations();
    
    // Setup intersection observer for animations
    setupScrollAnimations();
    
    // Setup mobile menu
    setupMobileMenu();
    
    // Check authentication status - DISABLED for applications page
    // checkAuthStatus();
}

// Setup navigation effects
function setupNavigation() {
    const navbar = Utils.$('#navbar');
    if (!navbar) return;
    
    // Navbar scroll effect
    window.addEventListener('scroll', Utils.throttle(() => {
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    }, 100));
    
    // Active link highlighting
    const navLinks = Utils.$$('.nav-link');
    const sections = Utils.$$('section[id]');
    
    window.addEventListener('scroll', Utils.throttle(() => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (scrollY >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('text-primary-600');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('text-primary-600');
            }
        });
    }, 100));
}

// Setup smooth scrolling for anchor links
function setupSmoothScrolling() {
    document.addEventListener('click', (e) => {
        if (e.target.tagName === 'A' && e.target.getAttribute('href')?.startsWith('#')) {
            e.preventDefault();
            const targetId = e.target.getAttribute('href').substring(1);
            const targetElement = Utils.$(`#${targetId}`);
            
            if (targetElement) {
                Utils.scrollToElement(targetElement, 80);
            }
        }
    });
}

// Setup counter animations
function setupCounterAnimations() {
    const counters = Utils.$$('[data-count]');
    
    const animateCounters = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.dataset.count);
                Utils.animateCounter(counter, 0, target, 2000);
                observer.unobserve(counter);
            }
        });
    };
    
    const counterObserver = new IntersectionObserver(animateCounters, {
        threshold: 0.5
    });
    
    counters.forEach(counter => {
        counterObserver.observe(counter);
    });
}

// Setup scroll animations
function setupScrollAnimations() {
    const animatedElements = Utils.$$('.animate-slide-up, .animate-fade-in, .animate-bounce-in');
    
    const animateOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-up');
                observer.unobserve(entry.target);
            }
        });
    };
    
    const scrollObserver = new IntersectionObserver(animateOnScroll, {
        threshold: 0.1
    });
    
    animatedElements.forEach(element => {
        scrollObserver.observe(element);
    });
}

// Setup mobile menu
function setupMobileMenu() {
    window.toggleMobileMenu = () => {
        const mobileMenu = Utils.$('#mobile-menu');
        if (mobileMenu) {
            mobileMenu.classList.toggle('hidden');
        }
    };
}

// Check authentication status
async function checkAuthStatus() {
    const currentPath = window.location.pathname;
    const isIndexPage = currentPath === '/' || currentPath === '/index.html' || currentPath.endsWith('/index.html');
    
    // If on index page and user is already logged in, redirect to dashboard
    if (auth.isLoggedIn() && isIndexPage) {
        console.log('User already logged in on index page, waiting for profile then redirecting...');
        
        // Wait for user profile to be loaded before redirecting
        await auth.waitForUser();
        
        setTimeout(() => {
            // First update UI
            updateUIForLoggedInUser();
            
            // Then redirect to dashboard (only if currentUser exists)
            if (auth.getCurrentUser()) {
                auth.redirectToDashboard();
            } else {
                console.log('currentUser still null, skipping redirect');
            }
        }, 100);
    } else if (auth.isLoggedIn()) {
        // Otherwise just update UI without redirecting
        console.log('User logged in on non-index page, updating UI only');
        updateUIForLoggedInUser();
    } else {
        console.log('User not logged in, showing normal homepage');
    }
}

// Update UI for logged in user
function updateUIForLoggedInUser() {
    // Show dashboard link in navigation
    const nav = Utils.$('nav .ml-10');
    if (nav && !Utils.$('.dashboard-link')) {
        const dashboardLink = Utils.createElement('a', 'dashboard-link nav-link text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200');
        dashboardLink.href = '/dashboard.html';
        dashboardLink.textContent = 'Dashboard';
        nav.insertBefore(dashboardLink, nav.firstChild);
    }
}

// Page-specific initialization
function initializePage() {
    const pathname = window.location.pathname;
    
    switch (true) {
        case pathname.includes('dashboard'):
            initializeDashboard();
            break;
        case pathname.includes('opportunities'):
            initializeOpportunities();
            break;
        case pathname.includes('profile'):
            initializeProfile();
            break;
        case pathname.includes('organization'):
            initializeOrganization();
            break;
        default:
            initializeHomePage();
    }
}

// Initialize home page
function initializeHomePage() {
    // Add any home page specific functionality
    console.log('Home page initialized');
}

// Initialize dashboard
function initializeDashboard() {
    // Require authentication
    if (!auth.requireAuth()) return;
    
    // Load dashboard data
    loadDashboardData();
}

// Initialize opportunities page
function initializeOpportunities() {
    // Setup search and filters
    setupOpportunitySearch();
    setupOpportunityFilters();
    
    // Load opportunities
    loadOpportunities();
}

// Initialize profile page
function initializeProfile() {
    // Require authentication
    if (!auth.requireAuth()) return;
    
    // Load profile data
    loadProfileData();
    
    // Setup form handlers
    setupProfileForms();
}

// Initialize organization pages
function initializeOrganization() {
    // Require organization user type
    if (!auth.requireUserType('organization')) return;
    
    // Load organization data
    loadOrganizationData();
}

// Dashboard functionality
async function loadDashboardData() {
    try {
        showLoading(true);
        
        const user = auth.getCurrentUser();
        if (user.user_type === 'student') {
            const stats = await api.students.getDashboardStats();
            updateDashboardStats(stats);
        } else if (user.user_type === 'organization') {
            const stats = await api.organizations.getDashboardStats();
            updateOrganizationStats(stats);
        }
    } catch (error) {
        showToast('Failed to load dashboard data', 'error');
        console.error('Dashboard load error:', error);
    } finally {
        showLoading(false);
    }
}

function updateDashboardStats(stats) {
    // Update dashboard statistics
    const statsContainer = Utils.$('#dashboard-stats');
    if (statsContainer && stats) {
        statsContainer.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white p-6 rounded-xl shadow-lg">
                    <div class="flex items-center">
                        <div class="p-3 bg-primary-100 rounded-full">
                            <i class="fas fa-file-alt text-primary-600 text-xl"></i>
                        </div>
                        <div class="ml-4">
                            <h3 class="text-2xl font-bold text-gray-900">${stats.total_applications || 0}</h3>
                            <p class="text-gray-600">Applications</p>
                        </div>
                    </div>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-lg">
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
                <div class="bg-white p-6 rounded-xl shadow-lg">
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
            </div>
        `;
    }
}

// Opportunities functionality
function setupOpportunitySearch() {
    const searchInput = Utils.$('#opportunity-search');
    if (searchInput) {
        searchInput.addEventListener('input', Utils.debounce((e) => {
            const query = e.target.value;
            searchOpportunities(query);
        }, 300));
    }
}

function setupOpportunityFilters() {
    const filterElements = Utils.$$('.opportunity-filter');
    filterElements.forEach(filter => {
        filter.addEventListener('change', () => {
            applyOpportunityFilters();
        });
    });
}

async function loadOpportunities(params = {}) {
    try {
        showLoading(true);
        const opportunities = await api.opportunities.getList(params);
        displayOpportunities(opportunities);
    } catch (error) {
        showToast('Failed to load opportunities', 'error');
        console.error('Opportunities load error:', error);
    } finally {
        showLoading(false);
    }
}

async function searchOpportunities(query) {
    try {
        // Use the opportunities.js search functionality instead
        if (window.currentFilters) {
            window.currentFilters.search = query;
            if (typeof window.loadOpportunities === 'function') {
                window.loadOpportunities();
                return;
            }
        }
        
        // Fallback: if user is authenticated, use dedicated search endpoint; otherwise use list with q param
        const isAuthenticated = !!Utils.storage.get('auth_token');
        const response = isAuthenticated 
            ? await api.opportunities.search(query)
            : await api.opportunities.getList({ q: query });
        let opportunities;
        
        // Handle different response formats
        if (response && response.results) {
            opportunities = response.results;
        } else if (Array.isArray(response)) {
            opportunities = response;
        } else {
            opportunities = [];
        }
        
        displayOpportunitiesMain(opportunities);
    } catch (error) {
        console.error('Search error:', error);
        displayOpportunitiesMain([]);
    }
}

function applyOpportunityFilters() {
    // Use the opportunities.js filter functionality if available
    if (typeof window.loadOpportunities === 'function') {
        const filters = {};
        const filterElements = Utils.$$('.opportunity-filter');
        
        filterElements.forEach(filter => {
            if (filter.value) {
                filters[filter.name] = filter.value;
            }
        });
        
        // Update global filters and reload
        if (window.currentFilters) {
            Object.assign(window.currentFilters, filters);
        }
        
        window.loadOpportunities();
        return;
    }
    
    // Fallback to original logic
    const filters = {};
    const filterElements = Utils.$$('.opportunity-filter');
    
    filterElements.forEach(filter => {
        if (filter.value) {
            filters[filter.name] = filter.value;
        }
    });
    
    loadOpportunities(filters);
}

function displayOpportunitiesMain(opportunities) {
    const container = Utils.$('#opportunities-container');
    if (!container) return;
    
    // Ensure opportunities is an array
    if (!Array.isArray(opportunities)) {
        console.warn('displayOpportunitiesMain called with non-array:', typeof opportunities);
        opportunities = [];
    }
    
    if (opportunities.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-search text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No opportunities found</h3>
                <p class="text-gray-600">Try adjusting your search criteria or filters.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = opportunities.map(opportunity => `
        <div class="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 mb-6">
            <div class="flex justify-between items-start mb-4">
                <div class="flex-1">
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">${opportunity.title}</h3>
                    <p class="text-gray-600 mb-2">${opportunity.organization_name}</p>
                    <p class="text-gray-700 mb-4">${Utils.truncate(opportunity.description, 150)}</p>
                </div>
                <div class="ml-4">
                    ${createBadge(opportunity.opportunity_type, 'primary').outerHTML}
                </div>
            </div>
            
            <div class="flex items-center justify-between text-sm text-gray-600 mb-4">
                <div class="flex items-center">
                    <i class="fas fa-map-marker-alt mr-1"></i>
                    ${opportunity.location}
                </div>
                <div class="flex items-center">
                    <i class="fas fa-calendar mr-1"></i>
                    Deadline: ${Utils.formatDate(opportunity.application_deadline)}
                </div>
            </div>
            
            <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    ${opportunity.required_skills?.slice(0, 3).map(skill => 
                        createBadge(skill, 'gray', 'sm').outerHTML
                    ).join('') || ''}
                </div>
                <button onclick="viewOpportunity('${opportunity.id}')" 
                        class="bg-gradient-to-r from-primary-600 to-secondary-600 hover:from-primary-700 hover:to-secondary-700 text-white px-6 py-2 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105">
                    View Details
                </button>
            </div>
        </div>
    `).join('');
}

// View opportunity details - redirect to dedicated page
async function viewOpportunity(opportunityId) {
    try {
        console.log('Redirecting to opportunity details page for ID:', opportunityId);
        // Redirect to opportunity details page
        window.location.href = `opportunity-details.html?id=${opportunityId}`;
    } catch (error) {
        showToast('Error loading opportunity details', 'error');
        console.error('Opportunity navigation error:', error);
    }
}

// Apply to opportunity
async function applyToOpportunity(opportunityId) {
    try {
        showLoading(true);
        await api.applications.submit({ opportunity: opportunityId });
        showToast('Application submitted successfully!', 'success');
        
        // Redirect back to opportunities page
        window.location.href = 'opportunities.html';
    } catch (error) {
        showToast(error.message || 'Failed to submit application', 'error');
        console.error('Application submission error:', error);
    } finally {
        showLoading(false);
    }
}

// Profile functionality
async function loadProfileData() {
    try {
        showLoading(true);
        const user = auth.getCurrentUser();
        
        if (user.user_type === 'student') {
            const profile = await api.students.getProfile();
            displayStudentProfile(profile);
        } else if (user.user_type === 'organization') {
            const profile = await api.organizations.getProfile();
            displayOrganizationProfile(profile);
        }
    } catch (error) {
        showToast('Failed to load profile data', 'error');
        console.error('Profile load error:', error);
    } finally {
        showLoading(false);
    }
}

function setupProfileForms() {
    const profileForm = Utils.$('#profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = Utils.getFormData(profileForm);
            
            try {
                const user = auth.getCurrentUser();
                if (user.user_type === 'student') {
                    await api.students.updateProfile(formData);
                } else if (user.user_type === 'organization') {
                    await api.organizations.updateProfile(formData);
                }
                showToast('Profile updated successfully!', 'success');
            } catch (error) {
                showToast('Failed to update profile', 'error');
                console.error('Profile update error:', error);
            }
        });
    }
}

// Global functions for navigation (other functions are exposed from auth.js)
window.viewOpportunity = viewOpportunity;
window.applyToOpportunity = applyToOpportunity;

// Initialize page-specific functionality when DOM is ready
document.addEventListener('DOMContentLoaded', initializePage);
