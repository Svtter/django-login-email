# Generated by Django 5.0.4 on 2024-04-06 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_login_email', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emaillogin',
            name='sault',
            field=models.CharField(default='', max_length=100, verbose_name='Sault'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emaillogin',
            name='validated',
            field=models.BooleanField(default=False, verbose_name='Login Token validated'),
        ),
        migrations.AlterField(
            model_name='emaillogin',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email'),
        ),
    ]
