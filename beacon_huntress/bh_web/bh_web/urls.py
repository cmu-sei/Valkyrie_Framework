"""
URL configuration for bh_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from pathlib import Path
from . import views
from bh_execute.views import AggView, DBScanView, DBScanVarView, ByPacketView, ByConnGroupView, ByPConnView
from settings.views import setting_view, filter_view, get_datasources, new_ds, del_ds, edit_ds, get_elasticindex
import os

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    # BLANK FOR A HOME PAGE
    path('', views.index),
    path('index/', views.index),
    path('admin/', admin.site.urls),
    path('GenSettings.html', setting_view),
    path('FilterSettings.html', filter_view),
    path('ExeAgg.html', AggView),
    path('ExeDBScan.html', DBScanView),
    path('ExeDBScanVar.html', DBScanVarView),
    path('ExeByPacket.html', ByPacketView),
    path('ExeConnGroup.html', ByConnGroupView),
    path('ExePConn.html', ByPConnView), 
    path('Logs.html', views.log_view),
    path('LogDetails.html', views.log_detail_view),
    path('Results.html', views.result_grid_group),
    path('ResultDetails.html', views.result_detail_view),
    path('Documentation.html', views.doc_view),
    path('FilteredHosts.html',views.filtered_beacons),
    path('DelFile', views.del_log),
    path('DelDetail', views.del_result),
    path('FilterBeacon', views.filter_beacon),
    path('DelFilteredBeacon', views.del_fil_beacon),
    path('RunConfig', views.get_config),
    path('LookupDNS', views.lookup_dns),
    path('FilteredLookupDNS', views.filter_lookup_dns),
    path('DataSources.html', get_datasources),
    path('NewDataSource.html', new_ds),
    path('DelDS', del_ds),
    path('EditDS', edit_ds),
    path('GetIndex', get_elasticindex)

]
