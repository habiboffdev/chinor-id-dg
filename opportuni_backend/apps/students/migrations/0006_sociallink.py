from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_studentprofile_bio_studentprofile_date_of_birth_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('github', 'GitHub'), ('linkedin', 'LinkedIn'), ('twitter', 'Twitter/X'), ('website', 'Website'), ('instagram', 'Instagram'), ('facebook', 'Facebook'), ('youtube', 'YouTube'), ('tiktok', 'TikTok'), ('medium', 'Medium'), ('devto', 'Dev.to'), ('stackoverflow', 'Stack Overflow'), ('kaggle', 'Kaggle'), ('behance', 'Behance'), ('dribbble', 'Dribbble'), ('telegram', 'Telegram'), ('custom', 'Custom')], max_length=32)),
                ('label', models.CharField(blank=True, max_length=50)),
                ('url', models.URLField()),
                ('is_public', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_links', to='students.studentprofile')),
            ],
            options={
                'ordering': ['sort_order', 'platform'],
                'unique_together': {('student', 'platform')},
            },
        ),
    ]
