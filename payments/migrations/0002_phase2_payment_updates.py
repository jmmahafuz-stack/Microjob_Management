# Generated Phase 2 Migration - Payment model updates for Job and Commission

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_phase2_workflow_models'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='job',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='bookings.job'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='booking',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_legacy', to='bookings.booking'),
        ),
        migrations.AddField(
            model_name='payment',
            name='customer_amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Total amount customer pays', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='worker_amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Amount worker receives', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='platform_commission',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Platform commission/fee', max_digits=10),
        ),
        migrations.AddField(
            model_name='payment',
            name='commission_rate',
            field=models.DecimalField(decimal_places=2, default=10, help_text='Commission percentage (e.g., 10 for 10%)', max_digits=5),
        ),
        migrations.AddField(
            model_name='payment',
            name='commission_calculated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='refund_reason',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='payment',
            name='refunded_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(choices=[('Cash', 'Cash'), ('Mobile Banking', 'Mobile Banking'), ('Card', 'Card'), ('Digital Wallet', 'Digital Wallet')], default='Cash', max_length=25),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed'), ('Refunded', 'Refunded')], default='Pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Legacy: single amount field', max_digits=10, null=True),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['payment_status', 'payment_date'], name='payments_pa_payment_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['job'], name='payments_pa_job_idx'),
        ),
    ]
