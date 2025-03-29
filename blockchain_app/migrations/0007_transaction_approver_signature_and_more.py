# Generated by Django 5.1.7 on 2025-03-25 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain_app', '0006_transaction_rejected_by_transaction_rejection_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='approver_signature',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='creator_signature',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='public_key',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
