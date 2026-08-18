from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0006_workerresponse'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapplication',
            name='agreed_to_schedule',
            field=models.BooleanField(
                default=False,
                help_text="Worker agrees to the customer's requested date and time",
            ),
        ),
    ]