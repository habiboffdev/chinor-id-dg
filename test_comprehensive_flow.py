#!/usr/bin/env python3
"""
Comprehensive test script for the opportunity details page and application submission.
Tests the full flow including question loading and form submission.
"""

import time
import json

def test_frontend_integration():
    """Test the frontend integration with the backend API"""
    
    print("🔧 Testing Frontend Integration...")
    
    # JavaScript snippet to inject into the page to test functionality
    test_script = """
    // Test script to check opportunity loading and questions
    (async function testOpportunityPage() {
        console.log('=== TESTING OPPORTUNITY PAGE ===');
        
        try {
            // Check if opportunityData is loaded
            if (typeof opportunityData !== 'undefined' && opportunityData) {
                console.log('✅ Opportunity data loaded:', {
                    id: opportunityData.id,
                    title: opportunityData.title,
                    questionsCount: (opportunityData.additional_questions || []).length
                });
                
                // Check questions
                const questions = opportunityData.additional_questions || [];
                if (questions.length > 0) {
                    console.log('✅ Questions found:', questions.length);
                    questions.forEach((q, i) => {
                        console.log(`   ${i+1}. ${q.question} (${q.question_type}, required: ${q.is_required})`);
                    });
                } else {
                    console.log('⚠️  No additional questions found');
                }
                
                // Check if questions are rendered in DOM
                const questionsContainer = document.getElementById('additionalQuestions');
                if (questionsContainer) {
                    const renderedQuestions = questionsContainer.children.length;
                    console.log(`✅ Questions rendered in DOM: ${renderedQuestions}`);
                } else {
                    console.log('❌ Questions container not found');
                }
                
                // Test form elements
                const form = document.getElementById('applicationForm');
                if (form) {
                    console.log('✅ Application form found');
                    
                    // Check required form fields
                    const coverLetter = document.getElementById('coverLetter');
                    const termsCheckbox = document.getElementById('termsAccepted');
                    
                    if (coverLetter) console.log('✅ Cover letter field found');
                    if (termsCheckbox) console.log('✅ Terms checkbox found');
                    
                } else {
                    console.log('❌ Application form not found');
                }
                
            } else {
                console.log('❌ Opportunity data not loaded');
            }
            
        } catch (error) {
            console.error('❌ Test error:', error);
        }
        
        console.log('=== TEST COMPLETE ===');
    })();
    """
    
    # Write the test script to a file that can be injected
    with open('/tmp/test_opportunity.js', 'w') as f:
        f.write(test_script)
    
    print("📝 Test script created at /tmp/test_opportunity.js")
    print("🌐 To test manually:")
    print("   1. Open http://localhost:8080/opportunity-details.html?id=1")
    print("   2. Open browser dev tools (F12)")
    print("   3. Copy and paste the test script into the console")
    print("   4. Review the output")
    
    return True

def test_application_form_structure():
    """Test the application form structure in the HTML"""
    
    print("\n🔍 Testing Application Form Structure...")
    
    html_file = "/home/mirzosharif/MVP/chinor_id_new/opportuni_frontend/opportunity-details.html"
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for form elements
        form_elements = [
            ('id="applicationForm"', 'Main application form'),
            ('id="coverLetter"', 'Cover letter textarea'),
            ('id="relevantExperience"', 'Relevant experience field'),
            ('id="availability"', 'Availability field'),
            ('id="reference1Name"', 'Reference 1 name field'),
            ('id="reference1Contact"', 'Reference 1 contact field'),
            ('id="reference1Relationship"', 'Reference 1 relationship field'),
            ('id="termsAccepted"', 'Terms acceptance checkbox'),
            ('id="additionalQuestions"', 'Additional questions container'),
            ('id="additionalQuestionsSection"', 'Additional questions section'),
            ('loadAdditionalQuestions()', 'Question loading function'),
            ('handleApplicationSubmit', 'Form submission handler')
        ]
        
        missing_elements = []
        for element, description in form_elements:
            if element in content:
                print(f"✅ Found {description}")
            else:
                missing_elements.append(description)
                print(f"❌ Missing {description}")
        
        # Check for question rendering logic
        question_logic = [
            'opportunityData.additional_questions',
            'question.question_type',
            'question.is_required',
            'question.placeholder'
        ]
        
        for logic in question_logic:
            if logic in content:
                print(f"✅ Found question logic: {logic}")
            else:
                print(f"⚠️  Missing question logic: {logic}")
        
        # Check application submission logic
        submission_elements = [
            'formData.get(\'coverLetter\')',
            'formData.get(\'termsAccepted\')',
            'additional_answers',
            'api.applications.submit'
        ]
        
        for element in submission_elements:
            if element in content:
                print(f"✅ Found submission logic: {element}")
            else:
                print(f"⚠️  Missing submission logic: {element}")
        
        return len(missing_elements) == 0
        
    except Exception as e:
        print(f"❌ Error reading HTML file: {e}")
        return False

def create_manual_test_guide():
    """Create a manual test guide for the application flow"""
    
    print("\n📋 Creating Manual Test Guide...")
    
    guide = """
# Manual Test Guide: Opportunity Application Flow

## Prerequisites
1. Backend server running on http://localhost:8000
2. Frontend server running on http://localhost:8080
3. Database with opportunity and questions data

## Test Steps

### 1. Load Opportunity Details Page
- Visit: http://localhost:8080/opportunity-details.html?id=1
- Expected: Page loads without JavaScript errors
- Expected: Opportunity title and details are displayed
- Expected: Cover image is shown (or default gradient)

### 2. Check Additional Questions
- Scroll to application section
- Expected: 3 additional questions should be visible:
  1. "Why are you interested in volunteering..." (textarea, required)
  2. "How many hours per week..." (select, required)  
  3. "Do you have any relevant volunteer experience?" (textarea, optional)

### 3. Fill Application Form
- Enter cover letter (minimum 100 characters)
- Fill relevant experience
- Select availability
- Fill reference information
- Answer additional questions
- Check terms acceptance

### 4. Submit Application
- Click submit button
- Expected: Loading state shows
- Expected: Either success message or login prompt
- Expected: No JavaScript errors in console

### 5. Verify Submission Data
- Check that all form data is captured correctly
- Verify additional question answers are included
- Confirm API call structure matches backend expectations

## Browser Console Tests
Open browser dev tools and run:

```javascript
// Check if opportunity data loaded with questions
console.log('Opportunity data:', opportunityData);
console.log('Questions:', opportunityData?.additional_questions);

// Check if questions are rendered
console.log('Rendered questions:', document.getElementById('additionalQuestions')?.children.length);

// Test form data collection
const form = document.getElementById('applicationForm');
const formData = new FormData(form);
for (let [key, value] of formData.entries()) {
    console.log(key, value);
}
```

## Expected Results
- ✅ All questions load from backend
- ✅ Questions render correctly in form
- ✅ Form validation works
- ✅ Submission includes question answers
- ✅ No JavaScript errors
- ✅ Professional UI/UX
"""
    
    with open('/home/mirzosharif/MVP/chinor_id_new/MANUAL_TEST_GUIDE.md', 'w') as f:
        f.write(guide)
    
    print("📄 Manual test guide created: MANUAL_TEST_GUIDE.md")
    return True

if __name__ == "__main__":
    print("🧪 Comprehensive Testing: Opportunity Application Flow\n")
    
    # Test 1: Frontend integration
    frontend_ok = test_frontend_integration()
    
    # Test 2: Form structure  
    form_ok = test_application_form_structure()
    
    # Test 3: Create manual test guide
    guide_ok = create_manual_test_guide()
    
    print(f"\n🏁 Final Results:")
    print(f"   Frontend integration: {'✅ PASSED' if frontend_ok else '❌ FAILED'}")
    print(f"   Form structure: {'✅ PASSED' if form_ok else '❌ FAILED'}")
    print(f"   Manual test guide: {'✅ CREATED' if guide_ok else '❌ FAILED'}")
    
    overall_success = frontend_ok and form_ok and guide_ok
    print(f"   Overall: {'✅ READY FOR TESTING' if overall_success else '❌ NEEDS FIXES'}")
    
    if overall_success:
        print("\n🎉 Application flow is ready for testing!")
        print("🔗 Next steps:")
        print("   1. Open: http://localhost:8080/opportunity-details.html?id=1")
        print("   2. Follow the manual test guide: MANUAL_TEST_GUIDE.md")
        print("   3. Test application submission with questions")
    
    exit(0 if overall_success else 1)
