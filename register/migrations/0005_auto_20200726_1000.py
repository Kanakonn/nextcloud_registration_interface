# Generated by Django 3.0.8 on 2020-07-26 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0004_auto_20200725_1842'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invitecode',
            old_name='group',
            new_name='groups'
        ),
        migrations.AlterField(
            model_name='invitecode',
            name='groups',
            field=models.CharField(blank=True, max_length=191, null=True, verbose_name='Groups'),
        )
    ]
