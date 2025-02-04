# Generated by Django 5.1.1 on 2024-09-17 20:10

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Whois",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("end_address", models.CharField(max_length=255)),
                ("handle", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                ("org_handle", models.CharField(blank=True, max_length=255, null=True)),
                ("start_address", models.CharField(max_length=255)),
                ("ref", models.CharField(blank=True, max_length=255, null=True)),
                ("city", models.CharField(blank=True, max_length=255, null=True)),
                ("code2", models.CharField(blank=True, max_length=2, null=True)),
                ("code3", models.CharField(blank=True, max_length=3, null=True)),
                (
                    "customer_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("e164", models.CharField(blank=True, max_length=255, null=True)),
                ("customer", models.CharField(blank=True, max_length=255, null=True)),
                ("postal_code", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "registration_date",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("state", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "street_address",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("update_date", models.CharField(blank=True, max_length=50, null=True)),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "referral_server",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "parent_org_handle",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("updated", models.DateTimeField(default=datetime.datetime.utcnow)),
            ],
        ),
        migrations.CreateModel(
            name="Mapping",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("query", models.CharField(max_length=255)),
                ("answer", models.CharField(max_length=255)),
                ("timestamp", models.FloatField(blank=True, null=True)),
                ("uid", models.CharField(blank=True, max_length=100, null=True)),
                ("orig_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("orig_port", models.IntegerField(blank=True, null=True)),
                ("resp_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("resp_port", models.IntegerField(blank=True, null=True)),
                ("proto", models.CharField(blank=True, max_length=10, null=True)),
                ("query_type", models.CharField(blank=True, max_length=50, null=True)),
                ("query_class", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "response_code",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("rtt", models.FloatField(null=True)),
                ("rejected", models.BooleanField(blank=True, default=False, null=True)),
                ("AA", models.BooleanField(blank=True, default=False, null=True)),
                ("TC", models.BooleanField(blank=True, default=False, null=True)),
                ("RD", models.BooleanField(blank=True, default=True, null=True)),
                ("RA", models.BooleanField(blank=True, default=False, null=True)),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("handle", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "start_address",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("end_address", models.CharField(blank=True, max_length=50, null=True)),
                ("created", models.DateTimeField(auto_now=True, null=True)),
                ("updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "answer_whois",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="mappings_as_answer",
                        to="ipmaven_www.whois",
                    ),
                ),
                (
                    "query_whois",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="mappings_as_query",
                        to="ipmaven_www.whois",
                    ),
                ),
            ],
        ),
    ]
