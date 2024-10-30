from django import forms
from django.forms import ModelForm
from .models import conf_general, conf_filter

# GENERAL CONFIG SETTINGS CLASS
class bh_settings_general(ModelForm):
    raw_loc = forms.FileInput()
    class Meta:
        model = conf_general

        fields = ['raw_loc', 'file_type', 'overwrite', 'verbose']
        labels = {'raw_loc': 'Raw Log Location',
                'file_type': 'Working File Type',
                'overwrite': 'Overwrite Existing Data',
                'verbose': 'Verbose Logging'}        

# GENERAL CONFIG SETTINGS CLASS
class bh_filter_settings(ModelForm):
    class Meta:
        model = conf_filter
        
        fields = ['filter', 'port_filter', 'port_exclude', 'src_ip_filter', 'src_ip_exclude', 'dest_ip_filter', 'dest_ip_exclude']
        labels = {'filter': 'Filter',
                'port': 'Port Filter',
                'port_exclude': 'Port Filter Exclusive',
                'src_ip_filter': 'Source IP Filter',
                'src_ip_exclude': 'Source IP Filter Exclusive',
                'dest_ip_filter': 'Destination IP Filter',
                'dest_ip_exclude': 'Destination IP Filter Exclusive'}        

# DATASOURCES
class bh_datasources(ModelForm):
    data_type = forms.CharField(max_length=100)
    ds_name = forms.CharField(max_length=100)