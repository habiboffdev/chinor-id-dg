// Opportunities page JavaScript for Opportuni Platform

// Global DOM references
let searchInput = null;

// State management
let currentViewMode = 'grid';
let currentPage = 1;
let totalPages = 1;
let currentFilters = {};
let searchSuggestions = [];
let recentSearches = JSON.parse(localStorage.getItem('recentSearches') || '[]');
let skillSuggestions = ['JavaScript', 'Python', 'React', 'Node.js', 'SQL', 'Git', 'HTML/CSS', 'Java', 'C++', 'Machine Learning', 'Data Analysis', 'Project Management', 'Communication', 'Leadership', 'Problem Solving'];
let selectedSkills = [];
let searchTimeout = null;
let filterHistory = [];
let currentApplicationOpportunityId = null;

// Performance optimization: Cache filter results
const filterCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Race condition prevention
let currentLoadRequest = null;
let isLoading = false;

// Utility functions
function getCachedResults(cacheKey) {
    const cached = filterCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data;
    }
    return null;
}

function setCachedResults(cacheKey, data) {
    filterCache.set(cacheKey, {
        data,
        timestamp: Date.now()
    });
    
    // Limit cache size
    if (filterCache.size > 50) {
        const firstKey = filterCache.keys().next().value;
        filterCache.delete(firstKey);
    }
}

// Generate cache key from current filters and page
function generateCacheKey() {
    const sortedFilters = Object.keys(currentFilters)
        .sort()
        .reduce((result, key) => {
            result[key] = currentFilters[key];
            return result;
        }, {});
    
    return JSON.stringify({
        filters: sortedFilters,
        page: currentPage,
        viewMode: currentViewMode
    });
}

// Show/hide loading skeleton
function showLoadingSkeleton(show) {
    const skeleton = Utils.$('#loading-skeleton');
    const container = Utils.$('#opportunities-container');
    
    if (show) {
        if (skeleton) skeleton.style.display = 'block';
        if (container) container.classList.add('filter-loading');
    } else {
        if (skeleton) skeleton.style.display = 'none';
        if (container) container.classList.remove('filter-loading');
    }
}

// Clear search function
function clearSearch() {
    if (searchInput) {
        searchInput.value = '';
        delete currentFilters.search;
        currentPage = 1;
        loadOpportunities();
        hideSearchSuggestions();
        
        const clearBtn = Utils.$('#clear-search');
        if (clearBtn) {
            clearBtn.classList.add('hidden');
        }
    }
}

// Analytics and performance tracking
function trackFilterUsage(filterType, filterValue) {
    const analytics = JSON.parse(localStorage.getItem('filterAnalytics') || '{}');
    const key = `${filterType}:${filterValue}`;
    analytics[key] = (analytics[key] || 0) + 1;
    localStorage.setItem('filterAnalytics', JSON.stringify(analytics));
}

// Initialize opportunities page
function initializeOpportunitiesPage() {
    console.log('🚀 INITIALIZING OPPORTUNITIES PAGE!');
    
    // Initialize global DOM references
    searchInput = Utils.$('#opportunity-search');
    console.log('🔍 Search input found:', searchInput);
    
    // Ensure clean initial state
    currentFilters = {};
    currentPage = 1;
    totalPages = 1;
    isLoading = false;
    currentLoadRequest = null;
    
    console.log('✅ Initial state reset');
    
    // Explicitly check and set token if it exists
    const token = Utils.storage.get('auth_token');
    if (token) {
        console.log('Found auth token, setting it in API...');
        api.setToken(token);
    } else {
        console.log('No auth token found, proceeding as guest...');
    }

    setupEventListeners();
    
    // Initialize enhanced components
    updateSavedFiltersDropdown();
    showRecentSearches();
    updateQuickFilterButtons();
    // updateActiveFilters(); // Removed to avoid interference during initialization
    initializeEnhancements();
    
    // Add a small delay to ensure everything is initialized, then load opportunities
    setTimeout(() => {
        console.log('🚀 Starting initial opportunities load...');
        loadOpportunities();
        updateViewModeButtons();
    }, 100);
    
    // Setup user dropdown
    window.toggleUserMenu = () => {
        const dropdown = Utils.$('#user-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
        }
    };
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const userBtn = e.target.closest('[onclick="toggleUserMenu()"]');
        if (!userBtn) {
            const userDropdown = Utils.$('#user-dropdown');
            if (userDropdown && !userDropdown.contains(e.target)) {
                userDropdown.classList.add('hidden');
            }
        }
    });
    
    // Initialize saved filters dropdown
    updateSavedFiltersDropdown();

    // Wire up application modal handlers once
    setupApplicationModalHandlers();
}

// Enhanced search functionality
function setupEnhancedSearch() {
    if (!searchInput) return;
    
    // Enhanced search with better debouncing and suggestions
    searchInput.addEventListener('input', Utils.debounce((e) => {
        const query = e.target.value.trim();
        
        // Show/hide clear button
        const clearBtn = Utils.$('#clear-search');
        if (clearBtn) {
            clearBtn.classList.toggle('hidden', !query);
        }
        
        if (query.length > 0) {
            currentFilters.search = query;
            showSearchSuggestions(query);
            saveToRecentSearches(query);
        } else {
            delete currentFilters.search;
            hideSearchSuggestions();
        }
        
        currentPage = 1;
        loadOpportunities();
    }, 300));
    
    // Handle focus events
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.length > 0) {
            showSearchSuggestions(searchInput.value);
        } else {
            showRecentSearches();
        }
    });
    
    // Handle blur events (with delay to allow clicking suggestions)
    searchInput.addEventListener('blur', () => {
        setTimeout(() => {
            hideSearchSuggestions();
        }, 200);
    });
    
    // Keyboard navigation for suggestions
    searchInput.addEventListener('keydown', handleSearchKeyNavigation);
}

// Show search suggestions
function showSearchSuggestions(query) {
    const suggestionsContainer = Utils.$('#search-suggestions');
    if (!suggestionsContainer) return;
    
    // Generate suggestions based on query
    const suggestions = generateSearchSuggestions(query);
    
    if (suggestions.length === 0) {
        hideSearchSuggestions();
        return;
    }
    
    suggestionsContainer.innerHTML = Utils.sanitizeHTML(suggestions.map(suggestion => 
        `<div class=\"search-suggestion-item\" data-suggestion=\"${encodeURIComponent(suggestion)}\">
            <i class=\"fas fa-search mr-2 text-gray-400\"></i>
            ${highlightSearchTerm(suggestion, query)}
        </div>`
    ).join(''));
    // Delegate click handling to avoid inline handlers removed by sanitizer
    suggestionsContainer.onclick = (e) => {
        const item = e.target.closest('.search-suggestion-item');
        if (item && suggestionsContainer.contains(item)) {
            const val = item.getAttribute('data-suggestion');
            if (val != null) {
                selectSearchSuggestion(decodeURIComponent(val));
            }
        }
    };
    
    suggestionsContainer.classList.remove('hidden');
}

// Generate search suggestions
function generateSearchSuggestions(query) {
    const suggestions = [];
    const lowercaseQuery = query.toLowerCase();
    
    // Add skill-based suggestions
    skillSuggestions.forEach(skill => {
        if (skill.toLowerCase().includes(lowercaseQuery)) {
            suggestions.push(`Skills: ${skill}`);
        }
    });
    
    // Add type-based suggestions
    const types = ['internship', 'scholarship', 'competition', 'volunteer', 'job', 'workshop'];
    types.forEach(type => {
        if (type.includes(lowercaseQuery)) {
            suggestions.push(`Type: ${type}`);
        }
    });
    
    // Add location-based suggestions
    const locations = ['remote', 'new york', 'california', 'texas', 'florida', 'international'];
    locations.forEach(location => {
        if (location.includes(lowercaseQuery)) {
            suggestions.push(`Location: ${location}`);
        }
    });
    
    return suggestions.slice(0, 5); // Limit to 5 suggestions
}

// Highlight search term in suggestions
function highlightSearchTerm(text, query) {
    // Escape regex special characters in query to avoid errors/injection
    const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const safeQuery = esc(query);
    try {
        const regex = new RegExp(`(${safeQuery})`, 'gi');
        return Utils.escapeHTML(text).replace(regex, '<strong class="text-primary-600">$1</strong>');
    } catch {
        return Utils.escapeHTML(text);
    }
}

// Show recent searches
function showRecentSearches() {
    const recentContainer = Utils.$('#recent-searches');
    
    if (recentSearches.length > 0) {
        if (recentContainer) {
            const recentList = Utils.$('#recent-searches-list');
            if (recentList) {
                recentList.innerHTML = Utils.sanitizeHTML(recentSearches.slice(0, 5).map(search => 
                    `<span class=\"recent-search-tag\" data-search=\"${encodeURIComponent(search)}\">${Utils.escapeHTML(search)}</span>`
                ).join(''));
                // Click handler delegation
                recentList.onclick = (e) => {
                    const tag = e.target.closest('.recent-search-tag');
                    if (tag && recentList.contains(tag)) {
                        const val = tag.getAttribute('data-search');
                        if (val != null) {
                            applyRecentSearch(decodeURIComponent(val));
                        }
                    }
                };
                recentContainer.classList.remove('hidden');
            }
        }
    }
}

// Hide search suggestions
function hideSearchSuggestions() {
    const suggestionsContainer = Utils.$('#search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.classList.add('hidden');
    }
}

// Select search suggestion
function selectSearchSuggestion(suggestion) {
    if (searchInput) {
        searchInput.value = suggestion;
        currentFilters.search = suggestion;
        currentPage = 1;
        loadOpportunities();
        hideSearchSuggestions();
    }
}

// Apply recent search
function applyRecentSearch(search) {
    if (searchInput) {
        searchInput.value = search;
        currentFilters.search = search;
        currentPage = 1;
        loadOpportunities();
        hideSearchSuggestions();
    }
}

// Save to recent searches
function saveToRecentSearches(query) {
    if (query.length < 3) return;
    
    // Remove if already exists
    recentSearches = recentSearches.filter(search => search !== query);
    
    // Add to beginning
    recentSearches.unshift(query);
    
    // Keep only last 10 searches
    recentSearches = recentSearches.slice(0, 10);
    
    // Save to localStorage
    localStorage.setItem('recentSearches', JSON.stringify(recentSearches));
}

// Handle keyboard navigation in search suggestions
function handleSearchKeyNavigation(e) {
    const suggestions = Utils.$$('.search-suggestion-item');
    if (suggestions.length === 0) return;
    
    let currentIndex = -1;
    suggestions.forEach((suggestion, index) => {
        if (suggestion.classList.contains('active')) {
            currentIndex = index;
        }
    });
    
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        currentIndex = Math.min(currentIndex + 1, suggestions.length - 1);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        currentIndex = Math.max(currentIndex - 1, -1);
    } else if (e.key === 'Enter' && currentIndex >= 0) {
        e.preventDefault();
        suggestions[currentIndex].click();
        return;
    } else if (e.key === 'Escape') {
        hideSearchSuggestions();
        return;
    }
    
    // Update active suggestion
    suggestions.forEach((suggestion, index) => {
        suggestion.classList.toggle('active', index === currentIndex);
    });
}

// Toggle advanced filters visibility
function toggleAdvancedFilters() {
    const advancedFilters = Utils.$('#advanced-filters');
    const toggleButton = Utils.$('#toggle-advanced-btn');
    const label = Utils.$('#advanced-filters-text');
    const toggleIcon = Utils.$('#advanced-filters-icon') || toggleButton?.querySelector('i');
    
    if (!advancedFilters) return;
    
    const isHidden = advancedFilters.style.display === 'none' || advancedFilters.classList.contains('hidden');
    
    if (isHidden) {
        // Show advanced filters
        advancedFilters.style.display = 'block';
        advancedFilters.classList.remove('hidden');
        if (label) label.textContent = 'Hide Advanced Filters';
        if (toggleIcon) {
            toggleIcon.classList.remove('fa-chevron-down');
            toggleIcon.classList.add('fa-chevron-up');
        }
    } else {
        // Hide advanced filters
        advancedFilters.style.display = 'none';
        advancedFilters.classList.add('hidden');
        if (label) label.textContent = 'Show Advanced Filters';
        if (toggleIcon) {
            toggleIcon.classList.remove('fa-chevron-up');
            toggleIcon.classList.add('fa-chevron-down');
        }
    }
}

// Update quick filter buttons state
function updateQuickFilterButtons() {
    const buttons = Utils.$$('.filter-quick-btn');
    buttons.forEach(btn => {
        const key = btn.getAttribute('data-filter');
        const val = btn.getAttribute('data-value');
        if (!key) { btn.classList.remove('active'); return; }
        const active = String(currentFilters[key]) === String(val);
        btn.classList.toggle('active', active);
    });
}

// Initialize enhanced components (placeholder)
function initializeEnhancements() {
    console.log('🔧 initializeEnhancements called');
}

// NOTE: showRecentSearches is defined earlier with rendering logic.

// (updateSavedFiltersDropdown is defined later with full implementation)

// Setup event listeners
function setupEventListeners() {
    console.log('🔧 setupEventListeners() called');
    
    try {
        // Setup enhanced search functionality
        console.log('🔧 Setting up enhanced search...');
        setupEnhancedSearch();
        console.log('✅ Enhanced search setup complete');
        
        // Setup skills filter
        console.log('🔧 Setting up skills filter...');
        setupSkillsFilter();
        console.log('✅ Skills filter setup complete');
        
    } catch (error) {
        console.error('❌ Error in setupEventListeners:', error);
        // Continue with filter setup even if other parts fail
    }
    
    console.log('🔧 Setting up filter event listeners...');
    
    // Filter elements (both selects and inputs)
    const filterElements = Utils.$$('.opportunity-filter');
    console.log('🔍 DEBUGGING: Found filter elements:', filterElements.length);
    console.log('🔍 DEBUGGING: Filter elements:', filterElements);
    
    if (filterElements.length === 0) {
        console.error('❌ NO FILTER ELEMENTS FOUND! Check HTML classes.');
        return;
    }
    
    filterElements.forEach((filter, index) => {
        console.log(`🔍 DEBUGGING: Setting up filter ${index}:`, filter.name, filter.tagName);
        const eventType = filter.tagName.toLowerCase() === 'input' ? 'input' : 'change';
        
        // Add debounced event handler to prevent rapid-fire API calls
        const debouncedHandler = Utils.debounce((e) => {
            console.log('🚨🚨🚨 FILTER EVENT TRIGGERED! 🚨🚨🚨');
            console.log('🚨 Event target:', e.target);
            const name = e.target.name;
            const value = e.target.value.trim();
            
            console.log(`� Filter ${eventType}: ${name} = "${value}"`);
            
            if (value) {
                currentFilters[name] = value;
                console.log('✅ Added filter:', name, '=', value);
            } else {
                delete currentFilters[name];
                console.log('�️ Removed filter:', name);
            }
            
            console.log('� Updated currentFilters:', JSON.stringify(currentFilters));
            
            // Debug filter state
            debugFilterState('after filter event');
            
            currentPage = 1;
            
            console.log('⏳ Loading opportunities with new filters...');
            loadOpportunities();
        }, 300); // 300ms debounce delay
        
        filter.addEventListener(eventType, debouncedHandler);
        
        console.log(`✅ Event listener added for ${filter.name}`);
    });
    
    // View mode toggles
    window.setViewMode = (mode) => {
        currentViewMode = mode;
        updateViewModeButtons();
        displayCurrentOpportunities();
    };
    
    // Clear filters (legacy support)
    window.clearFilters = clearAllFilters;
    
    // Initialize saved filters dropdown
    updateSavedFiltersDropdown();
    
    // Show recent searches on page load
    showRecentSearches();
}

// Display login required message
function displayLoginRequired() {
    const container = Utils.$('#opportunities-container');
    if (!container) return;
    
    showLoadingSkeleton(false);
    
    container.innerHTML = `
        <div class="text-center py-16">
            <i class="fas fa-lock text-6xl text-primary-300 mb-6"></i>
            <h3 class="text-2xl font-semibold text-gray-900 mb-4">Authentication Required</h3>
            <p class="text-gray-600 mb-8">
                You need to be logged in to view opportunities. Please sign in to continue.
            </p>
            <div class="flex justify-center gap-4">
                <a href="/login.html" class="text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105" style="background: var(--brand-primary);">
                    Sign In
                </a>
                <a href="/signup.html" class="bg-white border border-primary-600 text-primary-600 hover:bg-primary-50 px-6 py-3 rounded-lg font-semibold transition-all duration-200 transform hover:scale-105">
                    Create Account
                </a>
            </div>
        </div>
    `;
}

// Display empty state when no opportunities found
function displayEmptyState() {
    console.log('📭 displayEmptyState() called');
    
    const container = Utils.$('#opportunities-container');
    if (!container) {
        console.error('❌ Container not found in displayEmptyState!');
        return;
    }
    
    // Check if we have active filters
    const hasActiveFilters = currentFilters.search || 
                           currentFilters.location || 
                           currentFilters.type || 
                           currentFilters.isRemote || 
                           (currentFilters.skills && currentFilters.skills.length > 0) ||
                           (currentFilters.deadline && currentFilters.deadline !== 'all' && currentFilters.deadline !== 'undefined') ||
                           (currentFilters.dateRange && currentFilters.dateRange !== 'all' && currentFilters.dateRange !== 'undefined');
                           
    console.log('📭 Has active filters:', hasActiveFilters);
    console.log('📭 Setting empty state HTML...');
    
    container.innerHTML = Utils.sanitizeHTML(`
        <div class="text-center py-16">
            <div class="max-w-md mx-auto">
                <div class="mb-6">
                    <i class="fas fa-search text-6xl text-gray-300"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-4">
                    ${hasActiveFilters ? 'No opportunities match your filters' : 'No opportunities found'}
                </h3>
                <p class="text-gray-600 mb-6">
                    ${hasActiveFilters 
                        ? 'Try adjusting your filters to see more opportunities.' 
                        : 'There are currently no opportunities available. Please check back later.'}
                </p>
                ${hasActiveFilters ? `
                    <div class="space-y-3">
                        <button onclick="clearAllFilters()" 
                                class="bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors">
                            Clear All Filters
                        </button>
                        <div class="text-sm text-gray-500">
                            or try searching for different terms
                        </div>
                    </div>
                ` : `
                    <div class="space-y-3">
                        <p class="text-sm text-gray-500">
                            Want to be notified when new opportunities are posted?
                        </p>
                        <button onclick="setupNotifications()" 
                                class="bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors">
                            Set Up Notifications
                        </button>
                    </div>
                `}
            </div>
        </div>
    `);
}

// Load opportunities from API
async function loadOpportunities() {
    console.log('🚀 loadOpportunities() called!');
    console.log('🚀 Current filters:', currentFilters);
    
    // Debug filter state at start of load
    debugFilterState('start of loadOpportunities');
    
    // Prevent concurrent requests - cancel any existing request
    if (currentLoadRequest) {
        console.log('🚫 Cancelling previous request');
        currentLoadRequest.cancelled = true;
    }
    
    // Create new request tracker
    const requestId = Date.now();
    currentLoadRequest = { id: requestId, cancelled: false };
    
    // Prevent multiple simultaneous loads
    if (isLoading) {
        console.log('🚫 Already loading, skipping...');
        return;
    }
    
    isLoading = true;
    
    try {
        // Generate cache key for this request
        const cacheKey = generateCacheKey();
        
        // TEMPORARILY DISABLE CACHE FOR DEBUGGING FILTERS
        // Check cache first
        // const cachedResults = getCachedResults(cacheKey);
        // if (cachedResults) {
        //     console.log('Using cached results for:', cacheKey);
        //     displayOpportunities(cachedResults.opportunities);
        //     updateResultsCount(cachedResults.count);
        //     updatePagination();
        //     return;
        // }
        
        showLoadingSkeleton(true);
        
        // Check if this request was cancelled
        if (currentLoadRequest.cancelled || currentLoadRequest.id !== requestId) {
            console.log('🚫 Request cancelled before API call');
            return;
        }
        
        // Check if user is authenticated (optional for opportunities viewing)
        const isAuthenticated = auth.isLoggedIn();
        console.log('User authentication status:', isAuthenticated);
        
        // Note: Authentication is not required to view opportunities
        // Users can browse opportunities as guests
        
        // Transform filters to match API expectations
        const params = {
            page: currentPage,
            page_size: 12
        };
        
        // Map frontend filters to API parameters
        Object.keys(currentFilters).forEach(key => {
            const value = currentFilters[key];
            
            // Skip undefined, null, empty string, or whitespace-only values
            if (value === undefined || value === null || value === '' || 
                (typeof value === 'string' && value.trim() === '')) {
                console.log(`⚠️ Skipping filter ${key} with empty/undefined value:`, value);
                return;
            }
            
            console.log(`🔧 Processing filter: ${key} = ${value}`);
            
            switch(key) {
                case 'sort':
                    // Map sort to ordering parameter
                    params.ordering = value;
                    break;
                    
                case 'deadline':
                    // Map deadline filter to deadline_after
                    const now = new Date();
                    let deadlineDate;
                    
                    switch(value) {
                        case 'week':
                            deadlineDate = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
                            break;
                        case 'month':
                            deadlineDate = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
                            break;
                        case 'quarter':
                            deadlineDate = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000);
                            break;
                        default:
                            console.log(`⚠️ Unknown deadline value: ${value}`);
                            deadlineDate = null;
                    }
                    
                    if (deadlineDate) {
                        params.deadline_after = now.toISOString();
                        // Also add deadline before for the range
                        params.application_deadline__lte = deadlineDate.toISOString();
                        console.log(`✅ Deadline filter applied: ${now.toISOString()} to ${deadlineDate.toISOString()}`);
                    }
                    break;
                    
                case 'search':
                    // Search parameter is handled separately
                    if (value.trim()) {
                        params.search = value.trim();
                        console.log(`✅ Search filter applied: ${value.trim()}`);
                    }
                    break;
                    
                case 'page':
                    // Skip page parameter as it's handled separately
                    break;
                    
                case 'dateRange':
                    // Map dateRange to posted_after parameter
                    const postNow = new Date();
                    let postedAfterDate;
                    
                    switch(value) {
                        case 'today':
                            postedAfterDate = new Date(postNow.getFullYear(), postNow.getMonth(), postNow.getDate());
                            break;
                        case 'week':
                            postedAfterDate = new Date(postNow.getTime() - 7 * 24 * 60 * 60 * 1000);
                            break;
                        case 'month':
                            postedAfterDate = new Date(postNow.getTime() - 30 * 24 * 60 * 60 * 1000);
                            break;
                        case 'quarter':
                            postedAfterDate = new Date(postNow.getTime() - 90 * 24 * 60 * 60 * 1000);
                            break;
                        case 'all':
                        default:
                            postedAfterDate = null;
                    }
                    
                    if (postedAfterDate) {
                        params.created_at__gte = postedAfterDate.toISOString();
                        console.log(`✅ DateRange filter applied: posted after ${postedAfterDate.toISOString()}`);
                    }
                    break;
                    
                case 'isRemote':
                    // Map isRemote to is_remote parameter
                    if (value === true || value === 'true') {
                        params.is_remote = true;
                        console.log(`✅ Remote filter applied: ${value}`);
                    }
                    break;
                    
                case 'skills':
                    // Map skills array to required_skills parameter
                    if (Array.isArray(value) && value.length > 0) {
                        params.required_skills = value.join(',');
                        console.log(`✅ Skills filter applied: ${value.join(',')}`);
                    }
                    break;
                    
                case 'featured':
                    // Map featured to is_featured parameter
                    if (value === true || value === 'true') {
                        params.is_featured = true;
                        console.log(`✅ Featured filter applied: ${value}`);
                    }
                    break;
                    
                default:
                    // Direct mapping for other parameters
                    params[key] = value;
                    console.log(`✅ Direct mapping: ${key} = ${value}`);
                    break;
            }
        });
        
        // FINAL CLEANUP: Remove any undefined, null, or empty values from params before API call
        const cleanParams = {};
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '' && 
                !(typeof value === 'string' && value.trim() === '')) {
                cleanParams[key] = value;
                console.log(`✅ Clean param: ${key} = ${value}`);
            } else {
                console.log(`🧹 Removed undefined/empty param: ${key} = ${value}`);
            }
        });
        
        // Debug: Log the filters being sent
        console.log('Current filters being applied:', currentFilters);
        console.log('API params BEFORE cleanup:', params);
        console.log('API params AFTER cleanup:', cleanParams);
        
        // Track filter usage for analytics
        Object.entries(currentFilters).forEach(([key, value]) => {
            if (value) {
                trackFilterUsage(key, value);
            }
        });
        
        console.log('Fetching opportunities with CLEAN params:', cleanParams);
        
        // Make sure token is set in API
        const token = Utils.storage.get('auth_token');
        if (token) {
            api.setToken(token);
        }
        
        try {
            // Check if API is initialized properly
            console.log('API object:', api);
            console.log('API opportunities object:', api.opportunities);
            console.log('API token status:', api.hasToken());
        } catch (logError) {
            console.error('Error logging API status:', logError);
        }
        
        const response = await api.opportunities.getList(cleanParams);
        console.log('API Response:', response);
        
        // Validate response data
        if (!response) {
            throw new Error('Empty response from API');
        }
        
        // Handle both paginated and non-paginated responses
        let opportunities;
        
        if (response.results) {
            // Paginated response
            opportunities = response.results;
        } else if (Array.isArray(response)) {
            // Direct array response
            opportunities = response;
        } else if (response.data && Array.isArray(response.data)) {
            // Wrapped array response
            opportunities = response.data;
        } else {
            // Fallback - ensure we always have an array
            console.warn('Unexpected API response format:', response);
            opportunities = [];
        }
        
        // Final safety check - ensure opportunities is an array
        if (!Array.isArray(opportunities)) {
            console.error(`API returned non-array opportunities: ${typeof opportunities}`, opportunities);
            opportunities = [];
        }

        // Check if this request was cancelled during API call
        if (currentLoadRequest.cancelled || currentLoadRequest.id !== requestId) {
            console.log('🚫 Request cancelled after API call, ignoring results');
            return;
        }
        
        const count = response.count || opportunities.length;
        
        console.log('Opportunities count:', count);
        console.log('Opportunities data:', opportunities);
        
        // Validate each opportunity has necessary data
        opportunities.forEach((opp, index) => {
            // Check for required fields and provide defaults if missing
            if (!opp.id) console.warn(`Opportunity at index ${index} is missing id`);
            if (!opp.title) console.warn(`Opportunity at index ${index} is missing title`);
        });
        
        totalPages = Math.ceil(count / 12);
        
        // Cache the results
        setCachedResults(cacheKey, {
            opportunities,
            count,
            totalPages
        });

        // Final check before updating UI
        if (currentLoadRequest.cancelled || currentLoadRequest.id !== requestId) {
            console.log('🚫 Request cancelled before UI update, ignoring results');
            return;
        }
        
        console.log('✅ Updating UI with opportunities:', opportunities.length);
        displayOpportunities(opportunities);
        updateResultsCount(count);
        updatePagination();
        updateActiveFiltersDisplay(); // Update filter tags display
        
    } catch (error) {
        // Check if request was cancelled
        if (currentLoadRequest.cancelled || currentLoadRequest.id !== requestId) {
            console.log('🚫 Request cancelled, ignoring error');
            return;
        }
        console.error('Failed to load opportunities:', error);
        handleFilterError(error, 'loadOpportunities');
    } finally {
        // Clean up loading state
        isLoading = false;
        if (currentLoadRequest && currentLoadRequest.id === requestId) {
            currentLoadRequest = null;
        }
        showLoadingSkeleton(false);
    }
}

// Display opportunities
function displayOpportunities(opportunities) {
    console.log('📱 displayOpportunities() called with:', opportunities?.length || 0, 'opportunities');
    
    const container = Utils.$('#opportunities-container');
    if (!container) {
        console.error('❌ opportunities-container not found!');
        return;
    }
    
    console.log('📱 Container found:', container);
    
    // Store opportunities for view mode switching
    window.currentOpportunities = opportunities;
    
    console.log('📱 Calling displayCurrentOpportunities...');
    displayCurrentOpportunities();
}

// Display opportunities in current view mode
function displayCurrentOpportunities() {
    const opportunities = window.currentOpportunities || [];
    console.log('📱 displayCurrentOpportunities() called with:', opportunities?.length || 0, 'opportunities');
    console.log('📱 Current view mode:', currentViewMode);
    
    const container = Utils.$('#opportunities-container');
    if (!container) {
        console.error('❌ opportunities-container not found in displayCurrentOpportunities!');
        return;
    }
    
    if (opportunities.length === 0) {
        console.log('📱 No opportunities to display, showing empty state');
        displayEmptyState();
        return;
    }
    
    console.log('📱 Displaying opportunities in', currentViewMode, 'view');
    
    if (currentViewMode === 'grid') {
        displayGridView(opportunities);
    } else {
        displayListView(opportunities);
    }
}

// Display grid view
function displayGridView(opportunities) {
    console.log('📱 displayGridView() called with:', opportunities?.length || 0, 'opportunities');
    
    const container = Utils.$('#opportunities-container');
    if (!container) {
        console.error('❌ Container not found in displayGridView!');
        return;
    }
    
    // Ensure opportunities is an array
    if (!Array.isArray(opportunities)) {
        console.error('displayGridView called with non-array:', typeof opportunities, opportunities);
        displayEmptyState();
        return;
    }
    
    console.log('📱 Setting container class to opportunities-grid');
    container.className = 'opportunities-grid';
    
    if (opportunities.length === 0) {
        console.log('📱 No opportunities in grid view, showing empty state');
        displayEmptyState();
        return;
    }
    
    try {
        console.log('📱 Rendering grid view HTML for', opportunities.length, 'opportunities');
        const gridHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                ${opportunities.map(opportunity => createOpportunityCard(opportunity)).join('')}
            </div>
        `;
    console.log('📱 Setting container innerHTML...');
    container.innerHTML = gridHTML;
        console.log('✅ Grid view HTML set successfully');
    } catch (error) {
        console.error('Error rendering grid view:', error);
        displayEmptyState();
    }
}

// Display list view
function displayListView(opportunities) {
    console.log('📱 displayListView() called with:', opportunities?.length || 0, 'opportunities');
    
    const container = Utils.$('#opportunities-container');
    if (!container) {
        console.error('❌ Container not found in displayListView!');
        return;
    }
    
    // Ensure opportunities is an array
    if (!Array.isArray(opportunities)) {
        console.error('displayListView called with non-array:', typeof opportunities, opportunities);
        displayEmptyState();
        return;
    }
    
    container.className = 'opportunities-list';
    
    if (opportunities.length === 0) {
        displayEmptyState();
        return;
    }
    
    try {
        const listHTML = `
            <div class="space-y-4">
                ${opportunities.map(opportunity => createOpportunityListItem(opportunity)).join('')}
            </div>
        `;
        container.innerHTML = listHTML;
    } catch (error) {
        console.error('Error rendering list view:', error);
        displayEmptyState();
    }
}

// Create opportunity card for grid view
function createOpportunityCard(opportunity) {
    const title = Utils.escapeHTML(opportunity.title || 'Untitled');
    const orgName = Utils.escapeHTML(opportunity.organization_name || opportunity.organization?.name || 'Organization');
    const desc = Utils.escapeHTML(opportunity.description ? Utils.truncate(opportunity.description, 160) : 'No description available');
    const deadline = opportunity.application_deadline ? new Date(opportunity.application_deadline) : null;
    const isUrgent = deadline ? (deadline - new Date() < 7 * 24 * 60 * 60 * 1000) : false;
    const posted = opportunity.created_at ? Utils.getRelativeTime(opportunity.created_at) : null;
    const location = Utils.escapeHTML(opportunity.location || '—');
    const duration = opportunity.duration ? Utils.escapeHTML(opportunity.duration) : '';
    const compensation = opportunity.compensation || opportunity.pay || opportunity.stipend;
    const compText = compensation ? Utils.escapeHTML(String(compensation)) : '';
    const type = opportunity.opportunity_type;
    const logoInitials = getInitials(orgName);

    const deadlinePill = deadline ? `
        <span class="px-2 py-1 text-xs rounded-full" style="background:${isUrgent ? 'rgba(239,68,68,.18)' : 'rgba(255,255,255,.06)'}; color:${isUrgent ? '#ef4444' : 'var(--mist-200)'}; border:1px solid ${isUrgent ? 'rgba(239,68,68,.35)' : 'var(--slate-400)'};">
            <i class="fas fa-calendar-alt mr-1"></i> ${Utils.formatDate(opportunity.application_deadline)}
        </span>` : '';

    const remotePill = opportunity.is_remote ? `<span class="px-2 py-1 text-xs rounded-full" style="background: rgba(34,197,94,.15); color:#22c55e; border:1px solid rgba(34,197,94,.35);">Remote</span>` : '';

    const compPill = compText ? `<span class="px-2 py-1 text-xs rounded-full" style="background: rgba(255,255,255,.06); color: var(--mist-200); border:1px solid var(--slate-400);"><i class="fas fa-coins mr-1"></i>${compText}</span>` : '';
    const durationPill = duration ? `<span class="px-2 py-1 text-xs rounded-full" style="background: rgba(255,255,255,.06); color: var(--mist-200); border:1px solid var(--slate-400);"><i class="fas fa-clock mr-1"></i>${duration}</span>` : '';

    return `
        <div class="card card--hover transition-all cursor-pointer group" onclick="viewOpportunity('${Utils.escapeHTML(String(opportunity.id))}')">
            <div class="flex items-start justify-between mb-3">
                <div class="flex items-center gap-3 min-w-0">
                    <div class="w-10 h-10 rounded-full" style="background: var(--ink-800); border:1px solid var(--slate-400); display:flex; align-items:center; justify-content:center; font-weight:700; color: var(--mist-100);">${logoInitials}</div>
                    <div class="min-w-0">
                        <div class="text-sm text-muted truncate">${orgName}</div>
                        <h3 class="text-base font-semibold truncate group-hover:text-primary-400" style="color: var(--mist-100);">${title}</h3>
                    </div>
                </div>
                <div class="ml-3">${createTypeBadge(type)}</div>
            </div>
            <p class="text-sm mb-3 line-clamp-3" style="color: var(--mist-200);">${desc}</p>
            <div class="grid grid-cols-2 gap-2 mb-4 text-xs" style="color: var(--mist-300);">
                <div class="flex items-center gap-2"><i class="fas fa-map-marker-alt" style="color: var(--mist-400);"></i><span class="truncate">${location}</span></div>
                ${posted ? `<div class="flex items-center gap-2"><i class="fas fa-clock" style="color: var(--mist-400);"></i><span>Posted ${posted}</span></div>` : ''}
                <div class="flex items-center gap-2">${deadlinePill}</div>
                <div class="flex items-center gap-2">${remotePill} ${compPill} ${durationPill}</div>
            </div>
            <div class="flex justify-between items-center">
                <div class="flex flex-wrap gap-1">
                    ${opportunity.required_skills?.slice(0, 3).map(skill => 
                        `<span class="px-2 py-1 text-xs font-medium rounded-full" style="background: rgba(108,99,255,.18); color: var(--accent-2);">${Utils.escapeHTML(skill)}</span>`
                    ).join('') || ''}
                    ${opportunity.required_skills?.length > 3 ? 
                        `<span class="px-2 py-1 text-xs font-medium rounded-full" style="background: rgba(108,99,255,.18); color: var(--accent-2);">+${opportunity.required_skills.length - 3}</span>` : ''}
                </div>
                <a class="btn btn--secondary btn--pill text-sm" onclick="event.stopPropagation(); viewOpportunity('${Utils.escapeHTML(String(opportunity.id))}')">View</a>
            </div>
        </div>
    `;
}

// Create opportunity list item for list view
function createOpportunityListItem(opportunity) {
    const title = Utils.escapeHTML(opportunity.title || 'Untitled');
    const orgName = Utils.escapeHTML(opportunity.organization_name || opportunity.organization?.name || 'Organization');
    const desc = Utils.escapeHTML(opportunity.description ? Utils.truncate(opportunity.description, 240) : 'No description available');
    const deadline = opportunity.application_deadline ? new Date(opportunity.application_deadline) : null;
    const isUrgent = deadline ? (deadline - new Date() < 7 * 24 * 60 * 60 * 1000) : false;
    const posted = opportunity.created_at ? Utils.getRelativeTime(opportunity.created_at) : null;
    const location = Utils.escapeHTML(opportunity.location || '—');
    const duration = opportunity.duration ? Utils.escapeHTML(opportunity.duration) : '';
    const compensation = opportunity.compensation || opportunity.pay || opportunity.stipend;
    const compText = compensation ? Utils.escapeHTML(String(compensation)) : '';
    const type = opportunity.opportunity_type;
    const logoInitials = getInitials(orgName);

    const deadlinePill = deadline ? `
        <span class="px-2 py-1 text-xs rounded-full" style="background:${isUrgent ? 'rgba(239,68,68,.18)' : 'rgba(255,255,255,.06)'}; color:${isUrgent ? '#ef4444' : 'var(--mist-200)'}; border:1px solid ${isUrgent ? 'rgba(239,68,68,.35)' : 'var(--slate-400)'};">
            <i class="fas fa-calendar-alt mr-1"></i> ${Utils.formatDate(opportunity.application_deadline)}
        </span>` : '';
    const remotePill = opportunity.is_remote ? `<span class="px-2 py-1 text-xs rounded-full" style="background: rgba(34,197,94,.15); color:#22c55e; border:1px solid rgba(34,197,94,.35);">Remote</span>` : '';
    const compPill = compText ? `<span class="px-2 py-1 text-xs rounded-full" style="background: rgba(255,255,255,.06); color: var(--mist-200); border:1px solid var(--slate-400);"><i class="fas fa-coins mr-1"></i>${compText}</span>` : '';
    const durationPill = duration ? `<span class="px-2 py-1 text-xs rounded-full" style="background: rgba(255,255,255,.06); color: var(--mist-200); border:1px solid var(--slate-400);"><i class="fas fa-clock mr-1"></i>${duration}</span>` : '';

    return `
        <div class="card card--hover transition-all cursor-pointer group" onclick="viewOpportunity('${Utils.escapeHTML(String(opportunity.id))}')">
            <div class="flex items-start justify-between">
                <div class="flex items-start gap-4 flex-1 min-w-0">
                    <div class="w-12 h-12 rounded-full" style="background: var(--ink-800); border:1px solid var(--slate-400); display:flex; align-items:center; justify-content:center; font-weight:700; color: var(--mist-100);">${logoInitials}</div>
                    <div class="min-w-0">
                        <div class="flex items-center gap-3 mb-1">
                            <h3 class="text-lg font-semibold truncate group-hover:text-primary-400" style="color: var(--mist-100);">${title}</h3>
                            ${createTypeBadge(type)}
                            ${isUrgent ? '<span class="px-2 py-1 text-xs rounded-full" style="background: rgba(239,68,68,.18); color:#ef4444; border:1px solid rgba(239,68,68,.35);">Urgent</span>' : ''}
                        </div>
                        <div class="text-sm text-muted mb-2 truncate">${orgName}</div>
                        <p class="text-sm mb-3" style="color: var(--mist-200);">${desc}</p>
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4 text-xs" style="color: var(--mist-300);">
                            <div class="flex items-center gap-2"><i class="fas fa-map-marker-alt" style="color: var(--mist-400);"></i><span class="truncate">${location}</span></div>
                            ${posted ? `<div class="flex items-center gap-2"><i class="fas fa-clock" style="color: var(--mist-400);"></i><span>Posted ${posted}</span></div>` : ''}
                            <div class="flex items-center gap-2">${deadlinePill}</div>
                            <div class="flex items-center gap-2">${remotePill} ${compPill} ${durationPill}</div>
                        </div>
                        ${opportunity.required_skills?.length ? `
                            <div class="flex flex-wrap gap-2">
                                ${opportunity.required_skills.slice(0, 6).map(skill => 
                                    `<span class=\"px-2 py-1 text-xs font-medium rounded-full\" style=\"background: rgba(108,99,255,.18); color: var(--accent-2);\">${Utils.escapeHTML(skill)}</span>`
                                ).join('')}
                                ${opportunity.required_skills.length > 6 ? `<span class="px-2 py-1 text-xs font-medium rounded-full" style="background: rgba(108,99,255,.18); color: var(--accent-2);">+${opportunity.required_skills.length - 6}</span>` : ''}
                            </div>
                        ` : ''}
                    </div>
                </div>
                <div class="ml-6 flex flex-col items-end gap-2 shrink-0">
                    <a class="btn btn--secondary btn--pill" onclick="event.stopPropagation(); viewOpportunity('${Utils.escapeHTML(String(opportunity.id))}')">View</a>
                    ${auth.isLoggedIn() && auth.getCurrentUser()?.user_type === 'student' ? `
                        <button onclick="event.stopPropagation(); toggleApplicationForm('${Utils.escapeHTML(String(opportunity.id))}')" class="font-medium text-sm" style="color: var(--accent-3);">Apply</button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

// Create type badge for opportunities
function createTypeBadge(type) {
    if (!type) return '';
    const iconMap = {
        'internship': 'fas fa-user-graduate',
        'full-time': 'fas fa-briefcase',
        'part-time': 'fas fa-clock',
        'contract': 'fas fa-handshake',
        'volunteer': 'fas fa-heart',
        'remote': 'fas fa-laptop',
        'scholarship': 'fas fa-graduation-cap',
        'fellowship': 'fas fa-award'
    };
    const icon = iconMap[(type || '').toLowerCase()] || 'fas fa-tag';
    const label = Utils.escapeHTML(type.charAt(0).toUpperCase() + type.slice(1));
    return `
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium" style="background: rgba(108,99,255,.18); color: var(--accent-2); border:1px solid rgba(108,99,255,.35);">
            <i class="${icon}"></i>
            ${label}
        </span>
    `;
}

// Helpers
function getInitials(name) {
    if (!name) return '?';
    const parts = String(name).trim().split(/\s+/).slice(0,2);
    return parts.map(p => p[0]?.toUpperCase() || '').join('') || '?';
}

// Missing utility functions
function updateResultsCount(count) {
    console.log('📊 updateResultsCount() called with count:', count);
    
    const countElement = Utils.$('#results-count');
    if (countElement) {
        const text = `${count} ${count === 1 ? 'opportunity' : 'opportunities'} found`;
        countElement.textContent = text;
        console.log('📊 Results count updated:', text);
    } else {
        console.warn('❌ results-count element not found');
    }
    
    // Update analytics if element exists
    const analyticsCount = Utils.$('#analytics-total-results');
    if (analyticsCount) {
        analyticsCount.textContent = count;
        console.log('📊 Analytics count updated:', count);
    }
}

function handleFilterError(error, context = 'filter') {
    console.error(`Filter error in ${context}:`, error);
    
    // Show user-friendly error message
    if (error.message?.includes('network') || error.message?.includes('fetch')) {
        Utils.showToast('Network error. Please check your connection and try again.', 'error');
    } else if (error.message?.includes('unauthorized')) {
        Utils.showToast('Please log in to continue.', 'error');
        // Optionally redirect to login
    } else {
        Utils.showToast('Something went wrong. Please try again.', 'error');
    }
    
    // Show empty state if no opportunities loaded
    const container = Utils.$('#opportunities-container');
    if (container && (!window.currentOpportunities || window.currentOpportunities.length === 0)) {
        displayEmptyState();
    }
}

function applyQuickFilter(filterType, filterValue) {
    console.log('🚀 applyQuickFilter called:', filterType, '=', filterValue);
    
    // Reset current filters but preserve search
    const currentSearch = searchInput?.value || '';
    
    // Clear all filters except search
    currentFilters = {
        search: currentSearch
    };
    
    // Apply the specific quick filter
    if (filterType && filterValue) {
        currentFilters[filterType] = filterValue;
        console.log('✅ Applied quick filter:', filterType, '=', filterValue);
    }
    
    console.log('🔄 Updated currentFilters:', currentFilters);
    
    // Update UI to reflect filters
    updateFiltersUI();
    
    // Load opportunities with new filters
    currentPage = 1;
    loadOpportunities();
    
    // Track analytics
    trackFilterUsage('quick_filter', filterType);
    
    Utils.showToast(`Applied ${filterType} filter`, 'success');
}

function clearAllFilters() {
    console.log('🧹 Clearing all filters');
    
    // Reset all filters to empty/default values
    currentFilters = {};
    
    // Clear search input
    if (searchInput) {
        searchInput.value = '';
    }
    
    // Clear all filter form inputs
    const filterElements = document.querySelectorAll('.opportunity-filter');
    filterElements.forEach(element => {
        if (element.type === 'select-one') {
            element.selectedIndex = 0;
        } else if (element.type === 'checkbox') {
            element.checked = false;
        } else if (element.type === 'text' || element.type === 'search') {
            element.value = '';
        }
    });
    
    // Clear quick filter buttons
    const quickButtons = document.querySelectorAll('.filter-quick-btn');
    quickButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    console.log('✅ All filters cleared');
    
    // Update active filters display
    updateActiveFiltersDisplay();
    
    // Reset pagination
    currentPage = 1;
    
    // Load all opportunities
    loadOpportunities();
    
    // Track analytics
    trackFilterUsage('clear_all', 'manual');
    
    Utils.showToast('All filters cleared', 'success');
}

// Update filters UI to reflect current filter state
function updateFiltersUI() {
    // Update search input
    if (searchInput && currentFilters.search !== searchInput.value) {
        searchInput.value = currentFilters.search || '';
    }
    
    // Update inputs by name
    const inputs = Utils.$$('.opportunity-filter');
    inputs.forEach(el => {
        const key = el.name;
        if (!key) return;
        const val = currentFilters[key];
        if (val === undefined) {
            if (el.type === 'select-one') el.selectedIndex = 0;
            else if (el.type === 'checkbox') el.checked = false;
            else el.value = '';
            return;
        }
        if (el.type === 'checkbox') el.checked = !!val;
        else el.value = val;
    });
    
    // Update skills display
    updateSkillsDisplay();
    
    // Update active filters display
    updateActiveFiltersDisplay();

    // Update quick filter buttons active state
    updateQuickFilterButtons();
}

// Update skills display
function updateSkillsDisplay() {
    const skillsContainer = Utils.$('#selected-skills');
    if (!skillsContainer) return;
    
    if (!currentFilters.skills || currentFilters.skills.length === 0) {
        skillsContainer.innerHTML = '';
        return;
    }
    
    const skillsHTML = currentFilters.skills.map(skill => `
        <span class="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
            ${Utils.escapeHTML(skill)}
            <button data-skill="${encodeURIComponent(String(skill))}" 
                    class="remove-skill-btn text-blue-600 hover:text-blue-800">
                <i class="fas fa-times"></i>
            </button>
        </span>
    `).join('');
    
    skillsContainer.innerHTML = Utils.sanitizeHTML(skillsHTML);
    // Delegate click to handle removal after sanitization
    skillsContainer.onclick = (e) => {
        const btn = e.target.closest('.remove-skill-btn');
        if (btn && skillsContainer.contains(btn)) {
            const val = btn.getAttribute('data-skill');
            if (val != null) {
                removeSkill(decodeURIComponent(val));
            }
        }
    };
}

// Update active filters display
function updateActiveFilters() {
    updateActiveFiltersDisplay();
}

function updateActiveFiltersDisplay() {
    const activeFiltersContainer = Utils.$('#active-filters');
    if (!activeFiltersContainer) return;
    
    // Create a clean copy of filters for display only (don't modify the original)
    const displayFilters = {};
    Object.entries(currentFilters).forEach(([key, value]) => {
        // Only include valid values for display
        if (value !== undefined && 
            value !== null && 
            value !== '' && 
            value !== 'undefined' &&
            !(typeof value === 'string' && value.trim() === '') &&
            !(typeof value === 'string' && value.trim() === 'undefined') &&
            !(Array.isArray(value) && value.length === 0)) {
            displayFilters[key] = value;
        }
    });
    
    const activeFilters = [];
    
    // Check each filter type
    if (displayFilters.search && displayFilters.search.trim()) {
        activeFilters.push({
            type: 'search',
            label: `Search: "${Utils.escapeHTML(displayFilters.search)}"`,
            value: displayFilters.search
        });
    }
    
    if (displayFilters.location && displayFilters.location.trim()) {
        activeFilters.push({
            type: 'location',
            label: `Location: ${Utils.escapeHTML(displayFilters.location)}`,
            value: displayFilters.location
        });
    }
    
    if (displayFilters.type && displayFilters.type !== '') {
        activeFilters.push({
            type: 'type',
            label: `Type: ${Utils.escapeHTML(displayFilters.type)}`,
            value: displayFilters.type
        });
    }
    if (displayFilters.opportunity_type && displayFilters.opportunity_type !== '') {
        activeFilters.push({
            type: 'opportunity_type',
            label: `Type: ${Utils.escapeHTML(displayFilters.opportunity_type)}`,
            value: displayFilters.opportunity_type
        });
    }
    
    if (displayFilters.isRemote) {
        activeFilters.push({
            type: 'remote',
            label: 'Remote Only',
            value: 'remote'
        });
    }
    
    if (displayFilters.skills && displayFilters.skills.length > 0) {
    displayFilters.skills.forEach(skill => {
            activeFilters.push({
                type: 'skill',
        label: `Skill: ${Utils.escapeHTML(skill)}`,
                value: skill
            });
        });
    }
    
    if (displayFilters.deadline && displayFilters.deadline !== 'all' && displayFilters.deadline !== 'undefined') {
        activeFilters.push({
            type: 'deadline',
            label: `Deadline: ${Utils.escapeHTML(displayFilters.deadline)}`,
            value: displayFilters.deadline
        });
    }
    
    if (displayFilters.dateRange && displayFilters.dateRange !== 'all' && displayFilters.dateRange !== 'undefined') {
        activeFilters.push({
            type: 'dateRange',
            label: `Posted: ${Utils.escapeHTML(displayFilters.dateRange)}`,
            value: displayFilters.dateRange
        });
    }
    
    // Display active filters
    if (activeFilters.length === 0) {
        activeFiltersContainer.innerHTML = '<p class="text-gray-500 text-sm">No active filters</p>';
        return;
    }
    
    const filtersHTML = activeFilters.map(filter => `
        <span class="inline-flex items-center gap-2 px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
            ${filter.label}
        <button class="remove-filter-btn text-primary-600 hover:text-primary-800" 
            data-type="${Utils.escapeHTML(filter.type)}" 
            data-value="${encodeURIComponent(String(filter.value))}">
                <i class="fas fa-times"></i>
            </button>
        </span>
    `).join('');
    
    const activeHTML = `
        <div class="flex flex-wrap gap-2 items-center">
            ${filtersHTML}
            ${activeFilters.length > 1 ? `
                <button class=\"clear-all-filters-btn\" 
                        class="text-red-600 hover:text-red-800 text-sm font-medium ml-2">
                    Clear All
                </button>
            ` : ''}
        </div>
    `;
    activeFiltersContainer.innerHTML = Utils.sanitizeHTML(activeHTML);
    // Delegate click handlers
    activeFiltersContainer.onclick = (e) => {
        const removeBtn = e.target.closest('.remove-filter-btn');
        if (removeBtn && activeFiltersContainer.contains(removeBtn)) {
            const type = removeBtn.getAttribute('data-type');
            const value = removeBtn.getAttribute('data-value');
            removeFilter(type, decodeURIComponent(value || ''));
            return;
        }
        const clearBtn = e.target.closest('.clear-all-filters-btn');
        if (clearBtn && activeFiltersContainer.contains(clearBtn)) {
            clearAllFilters();
        }
    };
}

// Update pagination display
function updatePagination() {
    const paginationContainer = Utils.$('#pagination-container');
    if (!paginationContainer) return;
    
    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let paginationHTML = '<div class="flex justify-center items-center space-x-2">';
    
    // Previous button
    if (currentPage > 1) {
        paginationHTML += `
            <button onclick="changePage(${currentPage - 1})" 
                    class="px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <i class="fas fa-chevron-left mr-1"></i> Previous
            </button>
        `;
    }
    
    // Page numbers
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    // Adjust startPage if we're near the end
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // First page + ellipsis if needed
    if (startPage > 1) {
        paginationHTML += `
            <button onclick="changePage(1)" 
                    class="px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                1
            </button>
        `;
        if (startPage > 2) {
            paginationHTML += '<span class="px-2 py-2 text-gray-500">...</span>';
        }
    }
    
    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
        const isActive = i === currentPage;
        paginationHTML += `
            <button onclick="changePage(${i})" 
                    class="px-3 py-2 border rounded-lg transition-colors ${
                        isActive 
                            ? 'bg-primary-600 text-white border-primary-600' 
                            : 'bg-white border-gray-300 hover:bg-gray-50'
                    }">
                ${i}
            </button>
        `;
    }
    
    // Last page + ellipsis if needed
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            paginationHTML += '<span class="px-2 py-2 text-gray-500">...</span>';
        }
        paginationHTML += `
            <button onclick="changePage(${totalPages})" 
                    class="px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                ${totalPages}
            </button>
        `;
    }
    
    // Next button
    if (currentPage < totalPages) {
        paginationHTML += `
            <button onclick="changePage(${currentPage + 1})" 
                    class="px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Next <i class="fas fa-chevron-right ml-1"></i>
            </button>
        `;
    }
    
    paginationHTML += '</div>';
    
    // Add page info
    paginationHTML += `
        <div class="text-center mt-4 text-sm text-gray-600">
            Page ${currentPage} of ${totalPages}
        </div>
    `;
    
    paginationContainer.innerHTML = paginationHTML;
}

// Change page function
function changePage(page) {
    if (page < 1 || page > totalPages || page === currentPage) return;
    
    currentPage = page;
    loadOpportunities();
    
    // Scroll to top of opportunities
    const container = Utils.$('#opportunities-container');
    if (container) {
        container.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// --- Application Modal wiring ---
function setupApplicationModalHandlers() {
    const modal = Utils.$('#applicationModal');
    if (!modal) return;

    const closeBtn = Utils.$('#closeApplicationModal');
    const cancelBtn = Utils.$('#cancelApplication');
    const form = Utils.$('#applicationForm');
    const notes = Utils.$('#applicationNotes');
    const uploadArea = Utils.$('#documentUploadArea');
    const uploadInput = Utils.$('#documentUpload');
    const uploadedList = Utils.$('#uploadedFiles');

    const close = () => { modal.classList.add('hidden'); };

    closeBtn && closeBtn.addEventListener('click', close);
    cancelBtn && cancelBtn.addEventListener('click', close);

    // Drag/drop upload UX (optional)
    if (uploadArea && uploadInput && uploadedList) {
        const refreshFiles = () => {
            uploadedList.innerHTML = '';
            Array.from(uploadInput.files || []).forEach(file => {
                const item = document.createElement('div');
                item.className = 'flex items-center justify-between text-sm px-3 py-2 rounded border';
                item.style.borderColor = 'var(--slate-400)';
                item.innerHTML = `<span>${Utils.escapeHTML(file.name)}</span><span class="text-muted">${(file.size/1024/1024).toFixed(2)} MB</span>`;
                uploadedList.appendChild(item);
            });
        };
        uploadArea.addEventListener('click', () => uploadInput.click());
        uploadInput.addEventListener('change', refreshFiles);
        ['dragover','dragenter'].forEach(evt => uploadArea.addEventListener(evt, e => { e.preventDefault(); uploadArea.classList.add('ring'); }));
        ;['dragleave','drop'].forEach(evt => uploadArea.addEventListener(evt, e => { e.preventDefault(); uploadArea.classList.remove('ring'); }));
        uploadArea.addEventListener('drop', e => {
            const dt = e.dataTransfer;
            if (!dt) return;
            uploadInput.files = dt.files;
            refreshFiles();
        });
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = Utils.$('#submitApplication');
            const submitText = Utils.$('#submitButtonText');
            const spinner = Utils.$('#submitSpinner');
            try {
                submitBtn && (submitBtn.disabled = true);
                submitText && (submitText.textContent = 'Submitting...');
                spinner && spinner.classList.remove('hidden');

                if (typeof window.applyToOpportunity === 'function' && currentApplicationOpportunityId) {
                    await window.applyToOpportunity(currentApplicationOpportunityId);
                } else {
                    Utils.showToast('Application submitted (demo)', 'success');
                }
                modal.classList.add('hidden');
            } catch (err) {
                console.error('Application submit failed', err);
                Utils.showToast(err?.message || 'Failed to submit application', 'error');
            } finally {
                submitBtn && (submitBtn.disabled = false);
                submitText && (submitText.textContent = 'Submit Application');
                spinner && spinner.classList.add('hidden');
                notes && (notes.value = '');
                const uploadedList = Utils.$('#uploadedFiles');
                if (uploadedList) uploadedList.innerHTML = '';
                const uploadInput = Utils.$('#documentUpload');
                if (uploadInput) uploadInput.value = '';
            }
        });
    }
}

function toggleApplicationForm(opportunityId) {
    const modal = Utils.$('#applicationModal');
    if (!modal) return;
    currentApplicationOpportunityId = opportunityId;
    const titleEl = Utils.$('#opportunityTitle');
    const opp = (window.currentOpportunities || []).find(o => String(o.id) === String(opportunityId));
    const title = opp ? `${Utils.escapeHTML(opp.title || 'Opportunity')} — ${Utils.escapeHTML(opp.organization_name || opp.organization?.name || '')}` : 'Opportunity';
    if (titleEl) titleEl.textContent = title;

    // Load dynamic questions if API supports it (best-effort)
    const qContainer = Utils.$('#dynamicQuestions');
    if (qContainer) {
        qContainer.innerHTML = '<div class="text-sm text-gray-600">Preparing questions…</div>';
        (async () => {
            try {
                if (api?.opportunities?.getQuestions) {
                    const res = await api.opportunities.getQuestions(opportunityId);
                    const questions = Array.isArray(res?.results) ? res.results : (Array.isArray(res) ? res : []);
                    if (!questions.length) { qContainer.innerHTML = '<div class="text-sm text-gray-500">No additional questions.</div>'; return; }
                    qContainer.innerHTML = questions.map((q, idx) => {
                        const label = Utils.escapeHTML(q.label || q.text || `Question ${idx+1}`);
                        const name = Utils.escapeHTML(q.name || `q_${idx}`);
                        const required = q.required ? 'required' : '';
                        if ((q.type||'').toLowerCase() === 'textarea') {
                            return `<div><label class="block text-sm font-medium mb-1">${label}</label><textarea name="${name}" rows="4" class="w-full px-3 py-2 border border-gray-300 rounded-md" ${required}></textarea></div>`;
                        }
                        return `<div><label class="block text-sm font-medium mb-1">${label}</label><input name="${name}" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-md" ${required}/></div>`;
                    }).join('');
                } else {
                    qContainer.innerHTML = '<div class="text-sm text-gray-500">No additional questions.</div>';
                }
            } catch (e) {
                console.warn('Questions load failed', e);
                qContainer.innerHTML = '<div class="text-sm text-gray-500">No additional questions.</div>';
            }
        })();
    }

    modal.classList.remove('hidden');
}

// Setup user menu toggle
window.toggleUserMenu = () => {
    const dropdown = Utils.$('#user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
};

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const userBtn = e.target.closest('[onclick="toggleUserMenu()"]');
    if (!userBtn) {
        const userDropdown = Utils.$('#user-dropdown');
        if (userDropdown && !userDropdown.contains(e.target)) {
            userDropdown.classList.add('hidden');
        }
    }
});

// Initialize saved filters dropdown
updateSavedFiltersDropdown();

// IMMEDIATE TEST - This should run as soon as the script loads
console.log('🧪 OPPORTUNITIES.JS LOADED!');
console.log('🧪 Testing basic functionality...');

// Test if basic DOM selection works
setTimeout(() => {
    console.log('🧪 DELAYED TEST (after DOM might be ready)');
    const testElement = document.querySelector('.opportunity-filter');
    console.log('🧪 Found test filter element:', testElement);
    
    if (testElement) {
        console.log('🧪 Test element name:', testElement.name);
        console.log('🧪 Test element tagName:', testElement.tagName);
    } else {
        console.error('🧪 ❌ NO FILTER ELEMENTS FOUND IN DELAYED TEST!');
    }
}, 2000);

// Debug function to track filter changes and catch undefined values
function debugFilterState(context = '') {
    console.log(`🔍 FILTER DEBUG [${context}]:`, {
        currentFilters: JSON.stringify(currentFilters),
        keys: Object.keys(currentFilters),
        undefinedKeys: Object.keys(currentFilters).filter(key => currentFilters[key] === undefined),
        nullKeys: Object.keys(currentFilters).filter(key => currentFilters[key] === null),
        emptyKeys: Object.keys(currentFilters).filter(key => currentFilters[key] === '')
    });
    
    // Warn about problematic values
    Object.entries(currentFilters).forEach(([key, value]) => {
        if (value === undefined || value === null || value === '') {
            console.warn(`❌ PROBLEMATIC FILTER: ${key} = ${value} (type: ${typeof value})`);
        }
    });
}

// Aggressive filter cleanup - removes all problematic values
function cleanupFilters() {
    console.log('🧼 Starting aggressive filter cleanup');
    debugFilterState('before cleanup');
    
    const cleanedFilters = {};
    
    Object.entries(currentFilters).forEach(([key, value]) => {
        // Only keep values that are definitely valid
        if (value !== undefined && 
            value !== null && 
            value !== '' && 
            value !== 'undefined' &&  // Also exclude string 'undefined'
            !(typeof value === 'string' && value.trim() === '') &&
            !(typeof value === 'string' && value.trim() === 'undefined') &&  // Trim and check
            !(Array.isArray(value) && value.length === 0)) {
            cleanedFilters[key] = value;
            console.log(`✅ Kept filter: ${key} = ${value}`);
        } else {
            console.log(`🗑️ Removed problematic filter: ${key} = ${value} (type: ${typeof value})`);
        }
    });
    
    currentFilters = cleanedFilters;
    debugFilterState('after cleanup');
    
    return currentFilters;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeOpportunitiesPage();
});

// Make functions globally available
window.clearSearch = clearSearch;
window.applyQuickFilter = applyQuickFilter;
window.clearAllFilters = clearAllFilters;
window.removeFilter = removeFilter;
window.addSkill = addSkill;
window.removeSkill = removeSkill;
window.saveCurrentFilters = saveCurrentFilters;
window.selectSearchSuggestion = selectSearchSuggestion;
window.applyRecentSearch = applyRecentSearch;
window.toggleAdvancedFilters = toggleAdvancedFilters;
window.updateResultsCount = updateResultsCount;
window.handleFilterError = handleFilterError;
window.updateActiveFilters = updateActiveFilters;
window.updateFiltersUI = updateFiltersUI;
window.initializeEnhancements = initializeEnhancements;
window.updatePagination = updatePagination;
window.changePage = changePage;
window.viewOpportunity = viewOpportunity;
window.debugOpportunities = debugOpportunities;
window.exportCurrentFilters = exportCurrentFilters;
window.importFilters = importFilters;
window.showFilterAnalytics = showFilterAnalytics;
window.toggleApplicationForm = toggleApplicationForm;

// Setup skills filter functionality
function setupSkillsFilter() {
    console.log('🔧 Setting up skills filter...');
    
    const skillInput = Utils.$('#skills-input');
    if (skillInput) {
        skillInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const skill = skillInput.value.trim();
                if (skill) {
                    addSkill(skill);
                }
            }
        });
    }
    
    const addSkillBtn = Utils.$('#add-skill-btn');
    if (addSkillBtn) {
        addSkillBtn.addEventListener('click', () => {
            const skillInput = Utils.$('#skills-input');
            const skill = skillInput?.value.trim();
            if (skill) {
                addSkill(skill);
            }
        });
    }
}

// ----- UX helpers added to align with new UI -----
function updateViewModeButtons() {
    const gridBtn = Utils.$('#grid-view-btn');
    const listBtn = Utils.$('#list-view-btn');
    if (!gridBtn || !listBtn) return;
    if (currentViewMode === 'grid') {
        gridBtn.classList.add('active');
        listBtn.classList.remove('active');
    } else {
        listBtn.classList.add('active');
        gridBtn.classList.remove('active');
    }
}

function addSkill(skill) {
    const s = String(skill).trim();
    if (!s) return;
    if (!Array.isArray(currentFilters.skills)) currentFilters.skills = [];
    if (!currentFilters.skills.includes(s)) {
        currentFilters.skills.push(s);
        updateSkillsDisplay();
        currentPage = 1;
        loadOpportunities();
    }
    const input = Utils.$('#skills-input');
    if (input) input.value = '';
}

function removeSkill(skill) {
    const s = String(skill).trim();
    if (!Array.isArray(currentFilters.skills)) return;
    currentFilters.skills = currentFilters.skills.filter(x => x !== s);
    if (currentFilters.skills.length === 0) delete currentFilters.skills;
    updateSkillsDisplay();
    currentPage = 1;
    loadOpportunities();
}

function removeFilter(type, value) {
    switch (type) {
        case 'search':
            delete currentFilters.search;
            if (searchInput) searchInput.value = '';
            break;
        case 'location':
            delete currentFilters.location;
            break;
        case 'type':
            delete currentFilters.type;
            break;
        case 'opportunity_type':
            delete currentFilters.opportunity_type;
            break;
        case 'remote':
            delete currentFilters.isRemote;
            break;
        case 'deadline':
            delete currentFilters.deadline;
            break;
        case 'dateRange':
            delete currentFilters.dateRange;
            break;
        case 'skill':
            removeSkill(value);
            return;
        default:
            delete currentFilters[type];
    }
    updateActiveFiltersDisplay();
    currentPage = 1;
    loadOpportunities();
}

function saveCurrentFilters() {
    const sets = JSON.parse(localStorage.getItem('savedFilterSets') || '[]');
    const entry = { id: Date.now(), name: `Set ${sets.length + 1}`, filters: currentFilters };
    sets.push(entry);
    localStorage.setItem('savedFilterSets', JSON.stringify(sets));
    Utils.showToast('Filter set saved', 'success');
    updateSavedFiltersDropdown();
}

function updateSavedFiltersDropdown() {
    const select = Utils.$('#saved-filters');
    if (!select) return;
    const sets = JSON.parse(localStorage.getItem('savedFilterSets') || '[]');
    select.innerHTML = '<option value="">Select a saved filter set...</option>' +
        sets.map(s => `<option value="${s.id}">${Utils.escapeHTML(s.name)}</option>`).join('');
    select.onchange = () => {
        const id = Number(select.value);
        const chosen = sets.find(s => s.id === id);
        if (chosen) {
            currentFilters = { ...chosen.filters };
            updateFiltersUI();
            currentPage = 1;
            loadOpportunities();
        }
    };
}

async function exportCurrentFilters() {
    const data = JSON.stringify(currentFilters, null, 2);
    try { await navigator.clipboard.writeText(data); Utils.showToast('Filters copied', 'success'); }
    catch { prompt('Copy filters JSON:', data); }
}

async function importFilters() {
    const str = prompt('Paste filters JSON:');
    if (!str) return;
    try {
        const obj = JSON.parse(str);
        currentFilters = obj && typeof obj === 'object' ? obj : {};
        updateFiltersUI();
        loadOpportunities();
    } catch { Utils.showToast('Invalid JSON', 'error'); }
}

function showFilterAnalytics() {
    const analytics = JSON.parse(localStorage.getItem('filterAnalytics') || '{}');
    console.table(analytics);
    Utils.showToast('Analytics logged to console', 'info');
}

function debugOpportunities() {
    console.log('Filters:', currentFilters);
    console.log('Page:', currentPage, '/', totalPages);
    console.log('Cache keys:', Array.from(filterCache.keys()));
}
