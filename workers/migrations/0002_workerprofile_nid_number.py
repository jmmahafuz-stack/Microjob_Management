from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("workers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="workerprofile",
            name="nid_number",
            field=models.CharField(
                blank=True,
                help_text="National ID number",
                max_length=30,
                null=True,
            ),
        ),
    ]
