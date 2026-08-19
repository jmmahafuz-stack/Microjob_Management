# Generated migration - Add PayoutRequest model for worker withdrawals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_phase2_payment_updates'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PayoutRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('approved_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('payout_method', models.CharField(
                    choices=[
                        ('BANK', 'Bank Transfer'),
                        ('BKASH', 'BKash'),
                        ('NAGAD', 'Nagad'),
                        ('ROCKET', 'Rocket'),
                    ],
                    max_length=20
                )),
                ('payout_account_holder', models.CharField(max_length=255)),
                ('payout_account_number', models.CharField(max_length=100)),
                ('payout_bank_name', models.CharField(blank=True, max_length=255)),
                ('payout_branch', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(
                    choices=[
                        ('Requested', 'Requested'),
                        ('Approved', 'Approved'),
                        ('Rejected', 'Rejected'),
                        ('Processed', 'Processed'),
                    ],
                    default='Requested',
                    max_length=20
                )),
                ('admin_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('processed_at', models.DateTimeField(blank=True, null=True)),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='payoutrequest',
            index=models.Index(fields=['worker', 'status'], name='payments_payoutrequest_worker_status_idx'),
        ),
        migrations.AddIndex(
            model_name='payoutrequest',
            index=models.Index(fields=['status', '-created_at'], name='payments_payoutrequest_status_created_idx'),
        ),
        migrations.AddField(
            model_name='payment',
            name='worker_payout_status',
            field=models.CharField(
                choices=[
                    ('Pending', 'Pending - Awaiting Payment'),
                    ('Available', 'Available - Ready for Withdrawal'),
                    ('Withdrawn', 'Withdrawn'),
                ],
                default='Pending',
                max_length=20
            ),
        ),
    ]
