# Generated migration - Add earnings tracking fields to WorkerProfile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0005_remove_workerprofile_experience_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerprofile',
            name='pending_earnings',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Earnings from completed but unpaid jobs', max_digits=12),
        ),
        migrations.AddField(
            model_name='workerprofile',
            name='available_earnings',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Earnings available for withdrawal after payment is confirmed', max_digits=12),
        ),
        migrations.AddField(
            model_name='workerprofile',
            name='withdrawn_earnings',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Total amount withdrawn by worker', max_digits=12),
        ),
    ]
