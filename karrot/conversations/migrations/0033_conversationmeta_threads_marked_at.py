# Generated by Django 2.2.1 on 2019-05-18 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0032_auto_20190518_1358'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversationmeta',
            name='threads_marked_at',
            field=models.DateTimeField(null=True),
        ),
    ]