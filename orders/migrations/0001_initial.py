# Generated by Django 5.2 on 2025-05-02 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0011_remove_orders_products_remove_orders_user_and_more'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price_at_time', models.DecimalField(decimal_places=2, max_digits=10)),
                ('line_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='products.products')),
            ],
            options={
                'verbose_name': 'Order Item',
                'verbose_name_plural': 'Order Items',
            },
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('tax_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='pending', max_length=10)),
                ('products', models.ManyToManyField(related_name='orders', through='orders.OrderProduct', to='products.products')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='users.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='orders.orders'),
        ),
    ]
