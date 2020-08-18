# Generated by Django 3.0.9 on 2020-08-16 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0020_set_initial_activity_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='typus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='activities.ActivityType'),
        ),
    ]
