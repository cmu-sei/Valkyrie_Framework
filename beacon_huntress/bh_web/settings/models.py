from django.db import models
import datetime

class conf_general(models.Model):

    option_ft = (("1", "Parquet"), ("2", "CSV"))

    row_id = models.AutoField(primary_key=True)
    raw_loc = models.CharField(max_length=256)
    # bronze_loc = models.CharField(max_length=256)
    # silver_loc = models.CharField(max_length=256)
    # gold_loc = models.CharField(max_length=256)
    file_type = models.CharField(max_length=256, choices=option_ft, default=1)
    overwrite = models.BooleanField(default=False)
    verbose = models.BooleanField(default=False)
    update_date = models.DateTimeField(auto_now_add=True, blank=False)

    # def __str__(self):
    #     return self.name

class conf_filter(models.Model):

    row_id = models.AutoField(primary_key=True)
    filter = models.BooleanField(default=True)
    # filter_loc = models.CharField(max_length=256)
    port_filter = models.TextField(default="",blank=True)
    port_exclude = models.BooleanField(default=False)
    src_ip_filter = models.TextField(default="",blank=True)
    src_ip_exclude = models.BooleanField(default=True)
    dest_ip_filter = models.TextField(default="",blank=True)
    dest_ip_exclude = models.BooleanField(default=True)
    update_date = models.DateTimeField(auto_now_add=True, blank=False)

