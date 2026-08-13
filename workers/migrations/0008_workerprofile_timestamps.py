# Generated migration - Add timestamp fields to WorkerProfile

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('workers', '0007_workerprofile_payout_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workerprofile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
