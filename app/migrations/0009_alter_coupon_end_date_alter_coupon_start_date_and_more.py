# Generated by Django 4.2 on 2023-05-17 08:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_rename_oder_item_id_orderitem_order_item_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 200367)),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 200367)),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 197375)),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='like',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='feedbackimage',
            name='name',
            field=models.ImageField(upload_to='feedback/'),
        ),
        migrations.AlterField(
            model_name='feedbackrespone',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 197375)),
        ),
        migrations.AlterField(
            model_name='notification',
            name='create_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 200367)),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 198372)),
        ),
        migrations.AlterField(
            model_name='product',
            name='time_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 195380)),
        ),
        migrations.AlterField(
            model_name='productsale',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 196385)),
        ),
        migrations.AlterField(
            model_name='productsale',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 196385)),
        ),
        migrations.AlterField(
            model_name='tracking',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 17, 15, 29, 7, 199373)),
        ),
    ]
