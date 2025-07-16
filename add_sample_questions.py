#!/usr/bin/env python3
"""
Add sample additional questions to opportunities
"""

import os
import sys
import django

# Add the project root to the Python path
sys.path.append('/home/mirzosharif/MVP/chinor_id_new/opportuni_backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opportuni.settings.development')
django.setup()

from apps.opportunities.models import Opportunity, OpportunityQuestion

def add_sample_questions():
    """Add sample questions to existing opportunities"""
    
    print("🔧 Adding sample questions to opportunities...")
    
    # Get all opportunities
    opportunities = Opportunity.objects.all()
    
    if not opportunities.exists():
        print("❌ No opportunities found. Please create some opportunities first.")
        return False
    
    # Sample question sets for different opportunity types
    question_sets = {
        'internship': [
            {
                'question': 'What programming languages are you most comfortable with?',
                'question_type': 'textarea',
                'is_required': True,
                'placeholder': 'List your programming languages and proficiency levels',
                'help_text': 'Be specific about your experience level with each language',
                'order': 1
            },
            {
                'question': 'Are you available to work full-time during the internship period?',
                'question_type': 'select',
                'is_required': True,
                'options': ['Yes, full-time', 'Part-time only', 'Flexible schedule needed'],
                'order': 2
            },
            {
                'question': 'Upload a portfolio or code samples (optional)',
                'question_type': 'file',
                'is_required': False,
                'help_text': 'Please upload a PDF portfolio or links to your GitHub projects',
                'order': 3
            }
        ],
        'scholarship': [
            {
                'question': 'Describe your academic achievements and goals',
                'question_type': 'textarea',
                'is_required': True,
                'placeholder': 'Tell us about your GPA, awards, and future academic plans',
                'min_length': 200,
                'order': 1
            },
            {
                'question': 'What is your current GPA?',
                'question_type': 'number',
                'is_required': True,
                'placeholder': '3.50',
                'order': 2
            },
            {
                'question': 'Do you have any financial need for this scholarship?',
                'question_type': 'select',
                'is_required': True,
                'options': ['High financial need', 'Moderate financial need', 'No financial need'],
                'order': 3
            }
        ],
        'competition': [
            {
                'question': 'Describe your project idea or submission',
                'question_type': 'textarea',
                'is_required': True,
                'placeholder': 'Provide a detailed description of what you plan to create or submit',
                'min_length': 150,
                'order': 1
            },
            {
                'question': 'Will you be participating individually or as part of a team?',
                'question_type': 'select',
                'is_required': True,
                'options': ['Individual', 'Team of 2', 'Team of 3-5', 'Team of 6+'],
                'order': 2
            },
            {
                'question': 'Upload supporting documents (optional)',
                'question_type': 'file',
                'is_required': False,
                'help_text': 'Upload any relevant documents, designs, or prototypes',
                'order': 3
            }
        ],
        'volunteer': [
            {
                'question': 'Why are you interested in volunteering with our organization?',
                'question_type': 'textarea',
                'is_required': True,
                'placeholder': 'Share your motivation and what you hope to contribute',
                'min_length': 100,
                'order': 1
            },
            {
                'question': 'How many hours per week can you commit to volunteering?',
                'question_type': 'select',
                'is_required': True,
                'options': ['1-5 hours', '6-10 hours', '11-20 hours', '20+ hours'],
                'order': 2
            },
            {
                'question': 'Do you have any relevant volunteer experience?',
                'question_type': 'textarea',
                'is_required': False,
                'placeholder': 'Describe any previous volunteer work or community service',
                'order': 3
            }
        ]
    }
    
    # Default questions for any opportunity type not covered above
    default_questions = [
        {
            'question': 'Why are you interested in this opportunity?',
            'question_type': 'textarea',
            'is_required': True,
            'placeholder': 'Tell us what motivates you to apply for this opportunity',
            'min_length': 100,
            'order': 1
        },
        {
            'question': 'What relevant skills or experience do you bring?',
            'question_type': 'textarea',
            'is_required': True,
            'placeholder': 'Highlight your most relevant qualifications',
            'order': 2
        }
    ]
    
    questions_added = 0
    
    for opportunity in opportunities:
        print(f"\n📝 Adding questions to: {opportunity.title}")
        
        # Skip if questions already exist
        if opportunity.additional_questions.exists():
            print(f"   ℹ️  Questions already exist for this opportunity")
            continue
        
        # Get question set based on opportunity type
        questions = question_sets.get(opportunity.opportunity_type, default_questions)
        
        for question_data in questions:
            question = OpportunityQuestion.objects.create(
                opportunity=opportunity,
                **question_data
            )
            print(f"   ✅ Added: {question.question[:50]}...")
            questions_added += 1
    
    print(f"\n✅ Successfully added {questions_added} questions to opportunities!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ADDING SAMPLE QUESTIONS TO OPPORTUNITIES")
    print("=" * 60)
    
    success = add_sample_questions()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Sample questions added successfully!")
        print("🌐 You can now test the opportunity details page with custom questions")
        print("🔗 Visit: http://localhost:8080/opportunity-details.html?id=1")
    else:
        print("❌ Failed to add sample questions!")
    print("=" * 60)
