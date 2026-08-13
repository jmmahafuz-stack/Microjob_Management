# Generated Phase 2 Migration - ServiceRequest, JobApplication, Job Models

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_category'),
        ('bookings', '0002_bookingmessage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Brief title of the service needed', max_length=200)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('preferred_date', models.DateField()),
                ('preferred_time_start', models.TimeField(blank=True, null=True)),
                ('preferred_time_end', models.TimeField(blank=True, null=True)),
                ('budget_min', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('budget_max', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(choices=[('OPEN', 'Open - Accepting Applications'), ('REVIEWING', 'Reviewing Applications'), ('ASSIGNED', 'Worker Assigned'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='OPEN', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to=settings.AUTH_USER_MODEL)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to='services.service')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proposed_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estimated_duration', models.DurationField(help_text='Estimated time to complete the job')),
                ('proposal_message', models.TextField(help_text="Why you're the best choice for this job")),
                ('can_start_date', models.DateField(help_text='When you can start working')),
                ('worker_rating_at_application', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('worker_completed_jobs', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('PENDING', 'Pending Review'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('WITHDRAWN', 'Withdrawn by Worker')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('service_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to='bookings.servicerequest')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('service_request', 'worker')},
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('proposed_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estimated_duration', models.DurationField()),
                ('scheduled_date', models.DateField()),
                ('scheduled_time_start', models.TimeField(blank=True, null=True)),
                ('scheduled_time_end', models.TimeField(blank=True, null=True)),
                ('location', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('status', models.CharField(choices=[('CONFIRMED', 'Confirmed'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='CONFIRMED', max_length=20)),
                ('actual_start_time', models.DateTimeField(blank=True, null=True)),
                ('actual_end_time', models.DateTimeField(blank=True, null=True)),
                ('actual_price', models.DecimalField(blank=True, decimal_places=2, help_text='Final price if different from proposed', max_digits=10, null=True)),
                ('completion_notes', models.TextField(blank=True, help_text='Notes from worker after completion')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs_as_customer', to=settings.AUTH_USER_MODEL)),
                ('job_application', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='job', to='bookings.jobapplication')),
                ('service_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='job', to='bookings.servicerequest')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs_as_worker', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='servicerequest',
            index=models.Index(fields=['customer', '-created_at'], name='bookings_se_custome_idx'),
        ),
        migrations.AddIndex(
            model_name='servicerequest',
            index=models.Index(fields=['status', '-created_at'], name='bookings_se_status_idx'),
        ),
        migrations.AddIndex(
            model_name='servicerequest',
            index=models.Index(fields=['preferred_date'], name='bookings_se_preferr_idx'),
        ),
        migrations.AddIndex(
            model_name='jobapplication',
            index=models.Index(fields=['service_request', 'status'], name='bookings_jo_service_idx'),
        ),
        migrations.AddIndex(
            model_name='jobapplication',
            index=models.Index(fields=['worker', 'status'], name='bookings_jo_worker_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['customer', 'status'], name='bookings_job_custome_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['worker', 'status'], name='bookings_job_worker_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['scheduled_date'], name='bookings_job_schedul_idx'),
        ),
    ]
