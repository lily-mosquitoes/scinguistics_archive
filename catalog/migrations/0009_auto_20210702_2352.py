# Generated by Django 3.2.5 on 2021-07-02 23:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0008_auto_20210702_2106"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lesson",
            name="student",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="catalog.student",
            ),
        ),
        migrations.AlterField(
            model_name="lesson",
            name="teacher",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="catalog.teacher",
            ),
        ),
    ]
