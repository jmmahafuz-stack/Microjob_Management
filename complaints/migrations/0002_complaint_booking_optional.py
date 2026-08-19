import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='booking',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='complaints',
                to='bookings.booking',
            ),
        ),
    ]