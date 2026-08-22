from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0008_bookingmessage_attachment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='problem_photo',
            field=models.ImageField(blank=True, null=True, upload_to='booking_problem_photos/'),
        ),
    ]