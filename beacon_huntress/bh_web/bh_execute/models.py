from django.db import models


class Agg(models.Model):

    row_id = models.AutoField(primary_key=True)
    max_variance = models.IntegerField(default=0)
    min_records = models.IntegerField(default=0)
    cluster_factor = models.IntegerField(default=0)
    line_amounts = models.TextField(default="")
    min_delta_time = models.IntegerField(default=0)
    update_date = models.DateTimeField(auto_now_add=True, blank=False)

    # def __str__(self):
    #     return self.row_id

class DBScan(models.Model):

    row_id = models.AutoField(primary_key=True)
    minimum_delta = models.IntegerField(default=0)
    spans = models.TextField(default="")
    minimum_points_in_cluster = models.IntegerField(default=0)
    minimum_likelihood = models.IntegerField(default=0)
    update_date = models.DateTimeField(auto_now_add=True, blank=False)

class DBScanVar(models.Model):

    row_id = models.AutoField(primary_key=True)
    avg_delta = models.IntegerField(default=0)
    conn_cnt = models.IntegerField(default=0)
    span_avg = models.IntegerField(default=0)
    variance_per = models.IntegerField(default=0)
    minimum_likelihood = models.IntegerField(default=0)
    update_date = models.DateTimeField(auto_now_add=True, blank=False)    

class ByPacket(models.Model):

    row_id = models.AutoField(primary_key=True)
    avg_delta = models.IntegerField(default=0)
    conn_cnt = models.IntegerField(default=0)
    min_unique_percent = models.IntegerField(default=0)
    update_date = models.DateTimeField(auto_now_add=True, blank=False)    

class ByConnGroup(models.Model):
    
    row_id = models.AutoField(primary_key=True)
    conn_cnt = models.IntegerField(default=0)
    conn_group = models.IntegerField(default=0)
    threshold = models.IntegerField(default=0)
    update_date = models.DateTimeField(auto_now_add=True, blank=False)    

class ByPConn(models.Model):

    row_id = models.AutoField(primary_key=True)
    diff_time = models.IntegerField(default=0)
    diff_type = models.CharField(default="mi", max_length=256)
    update_date = models.DateTimeField(auto_now_add=True, blank=False)    
