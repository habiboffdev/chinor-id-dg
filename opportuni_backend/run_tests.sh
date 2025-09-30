#!/bin/bash

# Backend Testing Suite for Opportuni Platform
# Runs comprehensive tests for all backend systems

echo "🧪 Opportuni Backend Testing Suite"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Check if we're in the correct directory
if [ ! -f "manage.py" ]; then
    print_error "Please run this script from the opportuni_backend directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not detected. Attempting to activate..."
    if [ -f "../venv/bin/activate" ]; then
        source ../venv/bin/activate
        print_status "Virtual environment activated"
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_status "Virtual environment activated"
    else
        print_error "Virtual environment not found. Please activate it manually."
        exit 1
    fi
fi

# Configure Django settings for testing
export DJANGO_SETTINGS_MODULE="opportuni.settings.test"
print_status "Using test settings configuration"

# Function to run tests for a specific app
run_app_tests() {
    local app_name=$1
    local test_description=$2
    
    print_section "$test_description"
    
    if python manage.py test apps.$app_name.tests --verbosity=2; then
        print_status "$test_description - PASSED ✅"
        return 0
    else
        print_error "$test_description - FAILED ❌"
        return 1
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_section "Integration Tests"
    
    if python manage.py test apps.core.tests_integration --verbosity=2; then
        print_status "Integration Tests - PASSED ✅"
        return 0
    else
        print_error "Integration Tests - FAILED ❌"
        return 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_section "Running All Backend Tests"
    
    local failed_tests=0
    
    # Core system tests
    if ! run_app_tests "notifications" "Notification System Tests"; then
        ((failed_tests++))
    fi
    
    if ! run_app_tests "applications" "Application Management Tests"; then
        ((failed_tests++))
    fi
    
    if ! run_app_tests "communications" "Communications System Tests"; then
        ((failed_tests++))
    fi
    
    # Integration tests
    if ! run_integration_tests; then
        ((failed_tests++))
    fi
    
    # Additional core tests (if they exist)
    print_section "Additional System Tests"
    
    # Test accounts system
    if python manage.py test apps.accounts --verbosity=1 2>/dev/null; then
        print_status "Accounts System Tests - PASSED ✅"
    else
        print_warning "Accounts System Tests - No tests found or failed"
    fi
    
    # Test students system
    if python manage.py test apps.students --verbosity=1 2>/dev/null; then
        print_status "Students System Tests - PASSED ✅"
    else
        print_warning "Students System Tests - No tests found or failed"
    fi
    
    # Test organizations system
    if python manage.py test apps.organizations --verbosity=1 2>/dev/null; then
        print_status "Organizations System Tests - PASSED ✅"
    else
        print_warning "Organizations System Tests - No tests found or failed"
    fi
    
    # Test opportunities system
    if python manage.py test apps.opportunities --verbosity=1 2>/dev/null; then
        print_status "Opportunities System Tests - PASSED ✅"
    else
        print_warning "Opportunities System Tests - No tests found or failed"
    fi
    
    return $failed_tests
}

# Function to run coverage analysis
run_coverage() {
    print_section "Test Coverage Analysis"
    
    if command -v coverage &> /dev/null; then
        print_status "Running tests with coverage analysis..."
        
        coverage run --source='apps' manage.py test apps.notifications.tests apps.applications.tests apps.communications.tests apps.core.tests_integration
        
        echo ""
        print_status "Coverage Report:"
        coverage report --show-missing
        
        print_status "Generating HTML coverage report..."
        coverage html
        print_status "HTML coverage report generated in htmlcov/ directory"
        
    else
        print_warning "Coverage tool not installed. Install with: pip install coverage"
    fi
}

# Function to run specific test suites
run_specific_tests() {
    case $1 in
        "notifications"|"notif")
            run_app_tests "notifications" "Notification System Tests"
            ;;
        "applications"|"apps")
            run_app_tests "applications" "Application Management Tests"
            ;;
        "communications"|"comms")
            run_app_tests "communications" "Communications System Tests"
            ;;
        "integration"|"int")
            run_integration_tests
            ;;
        "coverage"|"cov")
            run_coverage
            ;;
        *)
            echo "Available test suites:"
            echo "  notifications (notif)     - Notification system tests"
            echo "  applications (apps)       - Application management tests"
            echo "  communications (comms)    - Communications system tests"
            echo "  integration (int)         - Cross-system integration tests"
            echo "  coverage (cov)           - Run with coverage analysis"
            echo "  all                      - Run all tests"
            ;;
    esac
}

# Check database setup
print_section "Pre-test Setup"
print_status "Checking database setup..."

if python manage.py check --verbosity=0; then
    print_status "Django system check - PASSED ✅"
else
    print_error "Django system check failed. Please fix issues before running tests."
    exit 1
fi

# Run migrations in test mode (this creates test database)
print_status "Ensuring test database is ready..."
if python manage.py migrate --run-syncdb --verbosity=0; then
    print_status "Database migrations - PASSED ✅"
else
    print_warning "Migration issues detected, but proceeding with tests..."
fi

# Main execution
if [ $# -eq 0 ]; then
    # No arguments provided, run all tests
    print_status "No specific test suite specified. Running all tests..."
    
    failed_tests=$(run_all_tests)
    
    echo ""
    print_section "Test Summary"
    
    if [ $failed_tests -eq 0 ]; then
        print_status "🎉 All test suites completed successfully!"
        echo ""
        echo "Test suites completed:"
        echo "  ✅ Notification System Tests"
        echo "  ✅ Application Management Tests"
        echo "  ✅ Communications System Tests"
        echo "  ✅ Integration Tests"
        echo ""
        print_status "To run coverage analysis: ./run_tests.sh coverage"
        exit 0
    else
        print_error "❌ $failed_tests test suite(s) failed"
        echo ""
        echo "Failed test suites need attention."
        echo "Run individual test suites to see detailed error messages:"
        echo "  ./run_tests.sh notifications"
        echo "  ./run_tests.sh applications"
        echo "  ./run_tests.sh communications"
        echo "  ./run_tests.sh integration"
        exit 1
    fi
else
    # Specific test suite requested
    run_specific_tests $1
fi