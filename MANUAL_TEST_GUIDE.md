
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
