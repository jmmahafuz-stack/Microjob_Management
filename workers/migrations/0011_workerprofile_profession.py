from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('workers', '0010_alter_workerprofile_bkash_number_and_more')]
    operations = [
        migrations.AddField(
            model_name='workerprofile',
            name='profession',
            field=models.CharField(blank=True, help_text='Primary profession, e.g. Electrician', max_length=100),
        ),
    ]
