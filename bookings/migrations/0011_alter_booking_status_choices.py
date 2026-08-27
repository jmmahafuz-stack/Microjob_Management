from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('bookings', '0010_alter_jobapplication_proposal_message')]
    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('Pending', 'Pending'),
                    ('Open', 'Open'),
                    ('Confirmed', 'Confirmed'),
                    ('Accepted', 'Accepted'),
                    ('Assigned', 'Assigned'),
                    ('In Progress', 'In Progress'),
                    ('Completed', 'Completed'),
                    ('Cancelled', 'Cancelled'),
                ],
                default='Pending',
            ),
        ),
    ]
