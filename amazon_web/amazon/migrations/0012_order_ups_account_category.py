# Generated by Django 4.1.5 on 2023-04-25 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amazon', '0011_order_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ups_account',
            field=models.TextField(default='ups_huidan'),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('Product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amazon.product')),
            ],
        ),
    ]
