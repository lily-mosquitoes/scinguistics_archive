# Generated by Django 3.2.5 on 2021-07-03 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_alter_student_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['date_and_time']},
        ),
    ]
