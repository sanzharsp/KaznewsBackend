# Generated by Django 4.0 on 2022-09-06 09:17

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsapp', '0003_refreshblacklistedtoken_refreshoutstandingtoken_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='context',
            field=ckeditor.fields.RichTextField(db_index=True, verbose_name='Краткое описание новости'),
        ),
    ]
