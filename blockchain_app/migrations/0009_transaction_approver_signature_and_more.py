# Generated by Django 5.1.7 on 2025-03-29 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain_app', '0008_remove_transaction_approver_signature_and_more'),
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
    ]
