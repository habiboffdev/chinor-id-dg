"""
🔴 CRITICAL: Application Validation Audit
Django management command to audit application validation compliance
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from apps.applications.models import Application, ApplicationAnswer
from apps.opportunities.models import OpportunityQuestion


def format_table(data, headers):
    """Simple table formatter"""
    if not data:
        return "No data"
    
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Create separator
    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    
    # Format header
    header_row = '|' + '|'.join(f' {str(h):<{col_widths[i]}} ' for i, h in enumerate(headers)) + '|'
    
    # Format rows
    rows = []
    for row in data:
        row_str = '|' + '|'.join(f' {str(cell):<{col_widths[i]}} ' for i, cell in enumerate(row)) + '|'
        rows.append(row_str)
    
    # Combine
    result = [separator, header_row, separator]
    result.extend(rows)
    result.append(separator)
    
    return '\n'.join(result)


class Command(BaseCommand):
    help = '🔴 Audit application validation - find invalid applications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            default='summary',
            choices=['summary', 'detailed', 'recent', 'by-opportunity', 'all'],
            help='Type of audit to run'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to look back (for recent mode)'
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Export results to CSV file'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        days = options['days']
        
        self.stdout.write(self.style.SUCCESS('\n🔍 Application Validation Audit'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if mode == 'summary' or mode == 'all':
            self.run_summary_audit()
        
        if mode == 'detailed' or mode == 'all':
            self.run_detailed_audit()
        
        if mode == 'recent' or mode == 'all':
            self.run_recent_audit(days)
        
        if mode == 'by-opportunity':
            self.run_opportunity_audit()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Audit complete\n'))

    def run_summary_audit(self):
        """Run summary statistics"""
        self.stdout.write(self.style.WARNING('\n📊 Summary Statistics'))
        self.stdout.write('-' * 60)
        
        # Total applications
        total_apps = Application.objects.count()
        
        # Applications with missing required answers
        invalid_apps = self.find_invalid_applications()
        
        # Applications with empty answers
        empty_answers = self.find_empty_answers()
        
        # Calculate percentages
        invalid_percent = (len(invalid_apps) / total_apps * 100) if total_apps > 0 else 0
        
        summary_data = [
            ['Total Applications', total_apps],
            ['Invalid Applications (missing answers)', len(invalid_apps)],
            ['Applications with empty answers', len(empty_answers)],
            ['Validation Compliance Rate', f'{100 - invalid_percent:.2f}%'],
        ]
        
        self.stdout.write(tabulate(summary_data, headers=['Metric', 'Value'], tablefmt='grid'))
        
        if len(invalid_apps) > 0:
            self.stdout.write(self.style.ERROR(f'\n⚠️  Found {len(invalid_apps)} invalid applications!'))
            self.stdout.write(self.style.WARNING('Run with --mode=detailed for more information'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ All applications are valid!'))

    def run_detailed_audit(self):
        """Show detailed list of invalid applications"""
        self.stdout.write(self.style.WARNING('\n📋 Detailed Invalid Applications'))
        self.stdout.write('-' * 60)
        
        invalid_apps = self.find_invalid_applications()
        
        if not invalid_apps:
            self.stdout.write(self.style.SUCCESS('✅ No invalid applications found!'))
            return
        
        detailed_data = []
        for app_data in invalid_apps[:50]:  # Limit to 50 for readability
            detailed_data.append([
                app_data['id'],
                app_data['student_name'],
                app_data['opportunity_title'][:40],
                app_data['required_questions'],
                app_data['answered_questions'],
                app_data['missing_answers'],
                app_data['applied_at'].strftime('%Y-%m-%d')
            ])
        
        headers = ['ID', 'Student', 'Opportunity', 'Req.', 'Ans.', 'Miss.', 'Date']
        self.stdout.write(tabulate(detailed_data, headers=headers, tablefmt='grid'))
        
        if len(invalid_apps) > 50:
            self.stdout.write(self.style.WARNING(f'\n... and {len(invalid_apps) - 50} more'))

    def run_recent_audit(self, days):
        """Audit recent applications"""
        self.stdout.write(self.style.WARNING(f'\n📅 Recent Applications (last {days} days)'))
        self.stdout.write('-' * 60)
        
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_apps = Application.objects.filter(applied_at__gte=cutoff_date)
        total_recent = recent_apps.count()
        
        if total_recent == 0:
            self.stdout.write(self.style.WARNING(f'No applications in the last {days} days'))
            return
        
        invalid_recent = []
        for app in recent_apps:
            if self.is_application_invalid(app):
                invalid_recent.append(app)
        
        compliance_rate = ((total_recent - len(invalid_recent)) / total_recent * 100) if total_recent > 0 else 100
        
        recent_data = [
            ['Total Recent Applications', total_recent],
            ['Invalid Applications', len(invalid_recent)],
            ['Compliance Rate', f'{compliance_rate:.2f}%'],
        ]
        
        self.stdout.write(tabulate(recent_data, headers=['Metric', 'Value'], tablefmt='grid'))
        
        if len(invalid_recent) > 0:
            self.stdout.write(self.style.ERROR(f'\n⚠️  {len(invalid_recent)} invalid applications in last {days} days!'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✅ All recent applications are valid!'))

    def run_opportunity_audit(self):
        """Audit by opportunity"""
        self.stdout.write(self.style.WARNING('\n🎯 Audit by Opportunity'))
        self.stdout.write('-' * 60)
        
        from django.db.models import Count
        from apps.opportunities.models import Opportunity
        
        opportunities = Opportunity.objects.annotate(
            app_count=Count('applications')
        ).filter(app_count__gt=0)
        
        opp_data = []
        for opp in opportunities:
            apps = opp.applications.all()
            required_questions = opp.additional_questions.filter(is_required=True).count()
            
            invalid_count = sum(1 for app in apps if self.is_application_invalid(app))
            
            opp_data.append([
                opp.id,
                opp.title[:40],
                len(apps),
                required_questions,
                invalid_count,
                f'{((len(apps) - invalid_count) / len(apps) * 100):.1f}%' if len(apps) > 0 else 'N/A'
            ])
        
        headers = ['ID', 'Opportunity', 'Apps', 'Req. Q', 'Invalid', 'Valid %']
        self.stdout.write(tabulate(opp_data, headers=headers, tablefmt='grid'))

    def find_invalid_applications(self):
        """Find all applications with missing required answers"""
        invalid_apps = []
        
        for app in Application.objects.select_related('student__user', 'opportunity').all():
            required_questions = app.opportunity.additional_questions.filter(is_required=True)
            
            if not required_questions.exists():
                continue
            
            answered_question_ids = set(
                app.answers.values_list('question_id', flat=True)
            )
            required_question_ids = set(
                required_questions.values_list('id', flat=True)
            )
            
            missing_ids = required_question_ids - answered_question_ids
            
            if missing_ids:
                invalid_apps.append({
                    'id': app.id,
                    'student_name': app.student.user.get_full_name(),
                    'opportunity_title': app.opportunity.title,
                    'required_questions': len(required_question_ids),
                    'answered_questions': len(answered_question_ids),
                    'missing_answers': len(missing_ids),
                    'applied_at': app.applied_at,
                    'application': app
                })
        
        return invalid_apps

    def find_empty_answers(self):
        """Find applications with empty/whitespace answers to required questions"""
        empty_answers = []
        
        for answer in ApplicationAnswer.objects.select_related('question', 'application').all():
            if not answer.question.is_required:
                continue
            
            if not answer.answer_text or not answer.answer_text.strip():
                empty_answers.append({
                    'application_id': answer.application.id,
                    'question': answer.question.question,
                    'answer_text': answer.answer_text
                })
        
        return empty_answers

    def is_application_invalid(self, app):
        """Check if a single application is invalid"""
        required_questions = app.opportunity.additional_questions.filter(is_required=True)
        
        if not required_questions.exists():
            return False
        
        answered_question_ids = set(
            app.answers.exclude(answer_text='').exclude(answer_text__isnull=True)
            .values_list('question_id', flat=True)
        )
        required_question_ids = set(
            required_questions.values_list('id', flat=True)
        )
        
        return len(answered_question_ids) < len(required_question_ids)
