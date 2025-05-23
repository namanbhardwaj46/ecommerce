# Generated by Django 5.2 on 2025-04-29 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_category_user_alter_products_created_at_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrderItems',
            new_name='OrderProduct',
        ),
        migrations.AddField(
            model_name='orders',
            name='order_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=10),
        ),
    ]
