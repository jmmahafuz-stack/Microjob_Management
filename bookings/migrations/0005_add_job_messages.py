# Generated migration for BookingMessage job field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_rename_bookings_job_custome_idx_bookings_jo_custome_3c5273_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookingmessage',
            name='booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='bookings.booking'),
        ),
        migrations.AddField(
            model_name='bookingmessage',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='bookings.job'),
        ),
    ]
