# Generated by Django 4.2.2 on 2024-02-07 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agg',
            fields=[
                ('row_id', models.AutoField(primary_key=True, serialize=False)),
                ('max_variance', models.IntegerField(default=0)),
                ('min_records', models.IntegerField(default=0)),
                ('cluster_factor', models.IntegerField(default=0)),
                ('line_amounts', models.TextField(default='')),
                ('min_delta_time', models.IntegerField(default=0)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ByConnGroup',
            fields=[
                ('row_id', models.AutoField(primary_key=True, serialize=False)),
                ('conn_cnt', models.IntegerField(default=0)),
                ('conn_group', models.IntegerField(default=0)),
                ('threshold', models.IntegerField(default=0)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ByPacket',
            fields=[
                ('row_id', models.AutoField(primary_key=True, serialize=False)),
                ('avg_delta', models.IntegerField(default=0)),
                ('conn_cnt', models.IntegerField(default=0)),
                ('min_unique_percent', models.IntegerField(default=0)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ByPConn',
            fields=[
                ('row_id', models.AutoField(primary_key=True, serialize=False)),
                ('diff_time', models.IntegerField(default=0)),
                ('diff_type', models.CharField(default='mi', max_length=256)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DBScan',
            fields=[
                ('row_id', models.AutoField(primary_key=True, serialize=False)),
                ('minimum_delta', models.IntegerField(default=0)),
                ('spans', models.TextField(default='')),
                ('minimum_points_in_cluster', models.IntegerField(default=0)),
                ('minimum_likelihood', models.IntegerField(default=0)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DBScanVar',
            fields=[
                ('row_id', models.AutoField(primary_key=True, serialize=False)),
                ('avg_delta', models.IntegerField(default=0)),
                ('conn_cnt', models.IntegerField(default=0)),
                ('span_avg', models.IntegerField(default=0)),
                ('variance_per', models.IntegerField(default=0)),
                ('minimum_likelihood', models.IntegerField(default=0)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
