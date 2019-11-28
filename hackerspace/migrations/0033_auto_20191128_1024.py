# Generated by Django 2.2.6 on 2019-11-28 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hackerspace', '0032_auto_20191127_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='many_hosts',
            field=models.ManyToManyField(blank=True, null=True, related_name='m_persons', to='hackerspace.Person', verbose_name='Hosts'),
        ),
        migrations.AlterField(
            model_name='event',
            name='str_location',
            field=models.CharField(default='Noisebridge<br>2169 Mission St<br94110, San Francisco, CA, US', max_length=250, verbose_name='Location'),
        ),
    ]