# Generated by Django 4.2.9 on 2024-08-09 15:11

from django.db import migrations

def add_defaults(apps, schema_editor):

    conf_filter = apps.get_model('settings','conf_filter')

    conf_filter.objects.create(
        filter = True,
        port_filter = '80,443',
        port_exclude = False,
        src_ip_filter = '127.0.0.1',
        src_ip_exclude = True,
        dest_ip_filter = '127.0.0.1',
        dest_ip_exclude = True
    )

    gen = apps.get_model('settings','conf_general')

    gen.objects.create(
        raw_loc = '/tmp/raw/data',
        file_type = 'Parquet',
        overwrite = False,
        verbose = False
    )

  

class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_defaults)
    ]