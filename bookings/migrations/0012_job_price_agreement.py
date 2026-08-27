from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0011_alter_booking_status_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='price_agreed',
            field=models.BooleanField(
                default=False,
                help_text='Whether the customer has accepted the current price',
            ),
        ),
        migrations.AddField(
            model_name='job',
            name='price_agreed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]