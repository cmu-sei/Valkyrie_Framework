# Create your views here.  
from pathlib import Path
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ExeAgg, ExeDBScan, ExeDBScanVar, ExeByPacket, ExeConnGroup, ExePConn
from .models import Agg, DBScan, DBScanVar, ByPacket, ByConnGroup, ByPConn
import os
from beacon_huntress.src.bin.web import exe_bh
from bh_web.views import context_results_grid
from beacon_huntress.src.bin.data import get_data, data_to_json

BASE_DIR = Path(__file__).resolve().parent.parent

def AggView(request):

    if request.method == "POST":
        form = ExeAgg(request.POST)

        if form.is_valid():
            send = form.save(commit=False)
            send.save()

            # RUN BEACON HUNTRESS
            ret_val = exe_bh(request,"agg")

            if ret_val["cnt"] == 0:
                messages.info(request, 'No potential beacons! See log file <a href=/LogDetails.html?filename={0}>{0}</a> for more details!'.format(ret_val["log_file"]))

            return redirect("/Results.html")
    else:
        try:
            # GATHER DROP LIST ITEMS & CONVERT TO JSON
            df = get_data("data_sources")
            options = data_to_json(df)

            ds = Agg.objects.latest("row_id")
        except Agg.DoesNotExist:
            print("NO VALUE")
        
        form = ExeAgg(instance=ds)

    return render(request, os.path.join(BASE_DIR, "bh_execute", "pages", "ExeAgg.html"), context={'form': form, "options": options})

def DBScanView(request):

    if request.method == "POST":
        form = ExeDBScan(request.POST)

        if form.is_valid():
            send = form.save(commit=False)
            send.save()

            # RUN BEACON HUNTRESS
            ret_val = exe_bh(request,"dbscan")

            if ret_val["cnt"] == 0:
                messages.info(request, 'No potential beacons! See log file <a href=/LogDetails.html?filename={0}>{0}</a> for more details!'.format(ret_val["log_file"]))

            # REDIRECT TO RESULTS PAGE
            return redirect("/Results.html")
    else:
        try:
            # GATHER DROP LIST ITEMS & CONVERT TO JSON
            df = get_data("data_sources")
            options = data_to_json(df)

            ds = DBScan.objects.latest("row_id")
        except DBScan.DoesNotExist:
            print("NO VALUE")
        
        form = ExeDBScan(instance=ds)

    return render(request, os.path.join(BASE_DIR, "bh_execute", "pages", "ExeDBScan.html"), context={'form': form, "options": options})

def DBScanVarView(request):

    if request.method == "POST":
        form = ExeDBScanVar(request.POST)

        if form.is_valid():
            send = form.save(commit=False)
            send.save()

            # RUN BEACON HUNTRESS
            ret_val = exe_bh(request,"dbscan_var")

            if ret_val["cnt"] == 0:
                messages.info(request, 'No potential beacons! See log file <a href=/LogDetails.html?filename={0}>{0}</a> for more details!'.format(ret_val["log_file"]))

            # REDIRECT TO RESULTS PAGE
            return redirect("/Results.html")
    else:
        try:
            # GATHER DROP LIST ITEMS & CONVERT TO JSON
            df = get_data("data_sources")
            options = data_to_json(df)

            ds = DBScanVar.objects.latest("row_id")
        except DBScanVar.DoesNotExist:
            print("NO VALUE")
        
        form = ExeDBScanVar(instance=ds)

        return render(request, os.path.join(BASE_DIR, "bh_execute", "pages", "ExeDBScanVar.html"), context={'form': form, "options": options})

def ByPacketView(request):

    if request.method == "POST":
        form = ExeByPacket(request.POST)

        if form.is_valid():
            send = form.save(commit=False)
            send.save()

            # RUN BEACON HUNTRESS
            ret_val = exe_bh(request,"by_packet")

            if ret_val["cnt"] == 0:
                messages.info(request, 'No potential beacons! See log file <a href=/LogDetails.html?filename={0}>{0}</a> for more details!'.format(ret_val["log_file"]))

            # REDIRECT TO RESULTS PAGE
            return redirect("/Results.html")
    else:
        try:
            ds = ByPacket.objects.latest("row_id")
        except ByPacket.DoesNotExist:
            print("NO VALUE")
        
        form = ExeByPacket(instance=ds)

    return render(request, os.path.join(BASE_DIR, "bh_execute", "pages", "ExeByPacket.html"), {'form': form})

def ByConnGroupView(request):

    if request.method == "POST":
        form = ExeConnGroup(request.POST)

        if form.is_valid():
            send = form.save(commit=False)
            send.save()

            # RUN BEACON HUNTRESS
            ret_val = exe_bh(request,"by_conn_group")

            if ret_val["cnt"] == 0:
                messages.info(request, 'No potential beacons! See log file <a href=/LogDetails.html?filename={0}>{0}</a> for more details!'.format(ret_val["log_file"]))

            # REDIRECT TO RESULTS PAGE
            return redirect("/Results.html")
    else:
        try:
            ds = ByConnGroup.objects.latest("row_id")
        except ByConnGroup.DoesNotExist:
            print("NO VALUE")
        
        form = ExeConnGroup(instance=ds)

    return render(request, os.path.join(BASE_DIR, "bh_execute", "pages", "ExeConnGroup.html"), {'form': form})

def ByPConnView(request):

    if request.method == "POST":
        form = ExePConn(request.POST)

        if form.is_valid():
            send = form.save(commit=False)
            send.save()

            # RUN BEACON HUNTRESS
            ret_val = exe_bh(request,"by_p_conn")

            if ret_val["cnt"] == 0:
                messages.info(request, 'No potential beacons! See log file <a href=/LogDetails.html?filename={0}>{0}</a> for more details!'.format(ret_val["log_file"]))

            # REDIRECT TO RESULTS PAGE
            return redirect("/Results.html")            
    else:
        try:
            ds = ByPConn.objects.latest("row_id")
        except ByPConn.DoesNotExist:
            print("NO VALUE")
        
        form = ExePConn(instance=ds)

    return render(request, os.path.join(BASE_DIR, "bh_execute", "pages", "ExePConn.html"), {'form': form})
