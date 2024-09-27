from django import forms
from django.forms import ModelForm
from .models import Agg, DBScan, DBScanVar, ByConnGroup, ByPConn, ByPacket

# Execute agg clustering
class ExeAgg(ModelForm):
    class Meta:
        model = Agg
        fields = ['max_variance', 'min_records', 'cluster_factor', 'line_amounts', 'min_delta_time']
        labels = {'max_variance': 'Maximum Variance Percentage',
                  'min_records': 'Beacon Callback Count', 
                  'cluster_factor': 'Clustering Factor Percentage', 
                  'line_amounts': 'Process Lines', 
                  'min_delta_time': 'Minimum Callback Time (ms)'}
   
class ExeDBScan(ModelForm):
    class Meta:
        model = DBScan
        fields = ['minimum_delta', 'spans', 'minimum_points_in_cluster', 'minimum_likelihood']
        labels = {'minimum_delta': 'Minimum Delta Time',
                  'spans': 'Time Spans', 
                  'minimum_points_in_cluster': 'Minimum Cluster Points',
                  'minimum_likelihood': 'Likelihood Percentage'}
        
class ExeDBScanVar(ModelForm):
    class Meta:
        model = DBScanVar
        fields = ['avg_delta', 'conn_cnt', 'span_avg', 'variance_per', 'minimum_likelihood']
        labels = {'avg_delta': 'Average Delta Time',
                  'conn_cnt': 'Connection Count', 
                  'span_avg': 'Time Span Average',
                  'variance_per': 'Variance Percentage',
                  'minimum_likelihood': 'Minimum Likelihood Percentage'
                  }

class ExeByPacket(ModelForm):
    class Meta:
        model = ByPacket
        fields = ['avg_delta', 'conn_cnt', 'min_unique_percent']
        labels = {'avg_delta': 'Average Delta Time',
                  'conn_cnt': 'Connection Count', 
                  'min_unique_percent': 'Minimum Unique Percentage'
                  }

class ExeConnGroup(ModelForm):
    class Meta:
        model = ByConnGroup
        fields = ['conn_cnt', 'conn_group', 'threshold']
        labels = {'conn_cnt': 'Connection Count', 
                  'conn_group': 'Number of Connection Groups',
                  'threshold': 'Time Threshold'
                  }

class ExePConn(ModelForm):
    class Meta:
        model = ByPConn
        fields = ['diff_time', 'diff_type']
        labels = {'diff_time': 'Time Value', 
                  'diff_type': 'Time Type (HH, MI, SS)',
                  }
