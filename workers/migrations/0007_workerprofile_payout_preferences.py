# Generated migration - Add payout preference fields to WorkerProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0006_workerprofile_earnings_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerprofile',
            name='payout_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Bank Account', 'Bank Account'),
                    ('BKash', 'BKash'),
                    ('Nagad', 'Nagad'),
                    ('Rocket', 'Rocket'),
                ],
                default='Bank Account',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='workerprofile',
            name='payout_account_holder',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='workerprofile',
            name='payout_account_number',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='workerprofile',
            name='payout_bank_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='workerprofile',
            name='payout_branch',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
