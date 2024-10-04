# Create your views here.
from pathlib import Path
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages

import os
import time
import pandas as pd
from settings.models import conf_general, conf_filter
from beacon_huntress.src.bin.data import get_data, del_data, add_data, get_run_conf, get_group_id
from beacon_huntress.src.bin.beacon import get_dns

# BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

def _get_context(df):
    df_html = df.to_html(escape=False, 
                         index=False, 
                         #justify="left",
                         classes="table table-striped", 
                         table_id="grid"
                         )

    # replace dataframe class
    df_html = df_html.replace('class="dataframe ', 'class="')
    df_html = df_html.replace('<tr class="text-end">','<tr>')
    context = {"files": df_html}

    return context

def _get_file_size(path):

    # GET FILE SIZE BYTES
    file_size = os.path.getsize(path)

    # CONVERT
    if file_size == 0:
        pass
    else:
        if file_size < 1024:
            file_size = 1
        else:
            file_size = file_size % 1024

    return file_size

def index(request):
    
    return render(request, os.path.join(BASE_DIR, "index.html"))

def log_view(request):

    df = pd.DataFrame()
    cnt = 0

    # WALK DIR
    context = walk_dir(os.path.join(BASE_DIR, "log"),"LogDetails")

    return render(request, os.path.join(BASE_DIR, "bh_web", "pages", "Logs.html"), context)

def log_detail_view(request):

    fname = request.GET.get("filename")
    with open(os.path.join(BASE_DIR, "log", fname), "r") as f:
        log_txt = f.read()

    context = {"file_content": log_txt}
    return render(request, os.path.join(BASE_DIR, "bh_web", "pages", "LogDetails.html"), context)
    
def walk_dir(walk_dir,page):

    df = pd.DataFrame()
    cnt = 0

    # WALK DIR FOR GOLD FILES
    for root, dir, dir_f in os.walk(walk_dir):
        # NESTED LOOP FOR FILES
        for fname in dir_f:

            # CREATED DATE
            c_date = os.path.getctime(os.path.join(root,fname))
            c_date = time.ctime(c_date)

            #FILESIZE
            file_size = _get_file_size(os.path.join(root,fname))

            row = [[fname, c_date, file_size]]

            df2 = pd.DataFrame(row, columns=["File Name", "Created Date", "File Size (KB)"])
            df = pd.concat([df, df2])

    if df.empty:
        df = pd.DataFrame(columns=["ID", "File Name", "Created Date", "File Size (KB)", "Option"])
    else:
        # # ADD HYPER LINK FOR THE LOG FILENAME & DELETE FILE
        df["Option"] = df["File Name"].apply(lambda x: '<a href="/DelFile?log={}"><i class="fa-regular fa-trash-can"></i></a>'.format(x))
        df["File Name"] = df["File Name"].apply(lambda x: '<a href="{1}.html?filename={0}">{0}</a>'.format(x,page))
        df["Created Date"] = pd.to_datetime(df["Created Date"])

        # REORDER BY LOG CREATED DATE & REINDEX
        df.sort_values(by=["Created Date"], ascending=False, inplace=True)
        df = df.reset_index(drop=True)
        df["ID"] = (df.index) + 1
        df = df[["ID", "File Name", "Created Date", "File Size (KB)", "Option"]]

    context = _get_context(df)

    return context

def result_grid_group(request):

    # GET Results Group
    df = get_data("group")

    # DELETE NULL VALUES OR MISSING VALUES
    df.dropna(inplace=True)

    #df["Dashboard"] =  df["uid"].apply(lambda x: '<a href="/Dashboard.html?uid={}"><i class="fas fa-chart-line"></i></a>'.format(x))
    df["Dashboard"] =  df["uid"].apply(lambda x: '<a href="http://127.0.0.1:3000/d/UK-8Ve_7z/beacon?orgId=1&var-uid={}&from=now-2y&to=now&refresh=5s" target="_blank"><i class="fas fa-chart-line"></i></a>'.format(x))
    df["Config"] = df["uid"].apply(lambda x: '<a href="/RunConfig?uid={}"><i class="fa-solid fa-gears"></i></a>'.format(x))
    df["log_file"] = df["log_file"].apply(lambda x: '<a href="/LogDetails.html?filename={}"><i class="fas fa-file"></i></a>'.format(x))
    df["Delete"] = df["uid"].apply(lambda x: '<a href="/DelDetail?uid={}"><i class="fa-regular fa-trash-can"></i></a>'.format(x))
    df["uid"] = df["uid"].apply(lambda x: '<a href="{1}.html?uid={0}">{0}</a>'.format(x,"ResultDetails"))

    df = df[["uid", "dt", "beacons", "Dashboard", "log_file", "Config", "Delete"]].rename(columns={"uid": "Group ID", "dt": "Date", "beacons": "Beacon Count", "log_file": "Log File"})

    context = _get_context(df)

    return render(request, os.path.join(BASE_DIR, "bh_web", "pages", "Results.html"), context)

def result_detail_view(request):

    uid = request.GET.get("uid")

    df = get_data("detail",uid)

    df["Filter"] = df["dest_ip"].apply(lambda x: '<a href="/FilterBeacon?dest_ip={}&uid={}"><i class="fa-solid fa-filter"></i></a> '.format(x,uid))

    # SET LOOKUP FOR UNKNOWN DNS
    df.loc[df["dns"] == "UNKNOWN", "dns"] = df["dest_ip"].apply(lambda x: '<a href="/LookupDNS?dest_ip={}&uid={}" onclick="document.body.style.cursor=\'wait\'"><i class="fa-solid fa-magnifying-glass"></i></a> '.format(x,uid)) + " UNKNOWN"

    # REORDER BY SCORE & REINDEX
    df.sort_values(by=["score", "conn_cnt"], ascending=False, inplace=True)
    df = df.reset_index(drop=True)
    df["ID"] = (df.index) + 1

    df = df[["ID", "source_ip", "dest_ip", "port", "score", "dns", "conn_cnt", "min_dt", "max_dt", "Filter"]].rename(columns={"source_ip": "Source IP", "port": "Port", "dest_ip": "Destination IP", "score": "Score", "dns": "DNS", "conn_cnt": "Connection Count", "min_dt": "First Occurrence", "max_dt": "Last Occurrence"})

    context = _get_context(df)
    return render(request, os.path.join(BASE_DIR, "bh_web", "pages", "ResultDetails.html"), context)

def doc_view(request):

    return render(request, os.path.join(BASE_DIR, "bh_web", "pages", "Documentation.html"))

def del_log(request):

    log = request.GET.get("log")

    full_path = os.path.join(BASE_DIR, "log", log)

    if os.path.exists(full_path):
        os.remove(full_path)
    else:
        print("File {} does not exist".format(full_path))

    # RELOAD LOG VIEW
    return HttpResponseRedirect("/Logs.html")
    
def del_result(request):
    uid = request.GET.get("uid")

    del_data("detail",uid)
    
    # RELOAD RESULTS VIEW
    return HttpResponseRedirect("/Results.html")    

def filter_beacon(request):
    dest_ip = request.GET.get("dest_ip")
    uid = request.GET.get("uid")

    add_data("beacon",dest_ip)

    # RELOAD RESULTS VIEW
    return HttpResponseRedirect("/ResultDetails.html?uid={}".format(uid))

def filtered_beacons(request):

    df = get_data("filtered_beacons")

    # SET LOOKUP FOR UNKNOWN DNS
    df.loc[df["dns"] == "UNKNOWN", "dns"] = df["ip"].apply(lambda x: '<a href="/FilteredLookupDNS?dest_ip={}" onclick="document.body.style.cursor=\'wait\'"><i class="fa-solid fa-magnifying-glass"></i></a> '.format(x)) + " UNKNOWN"

    df["Option"] = df["ip"].apply(lambda x: '<a href="/DelFilteredBeacon?ip={}"><i class="fa-regular fa-trash-can"></i></a> '.format(x))

    # REORDER BY FILTERED DATE & REINDEX
    df.sort_values(by=["dt"], ascending=False, inplace=True)
    df = df.reset_index(drop=True)
    df["ID"] = (df.index) + 1
    df = df[["ID", "ip", "dns", "short_desc", "dt", "Option"]]

    df = df[["ID", "ip", "dns", "short_desc", "dt", "Option"]].rename(columns={"rowid": "Row ID", "ip": "IP", "dns": "DNS", "short_desc": "Description", "dt": "Filtered Date"})

    context = _get_context(df)
    return render(request, os.path.join(BASE_DIR, "bh_web", "pages", "FilteredHosts.html"), context)    

def del_fil_beacon(request):
    ip = request.GET.get("ip")

    del_data("beacon",ip)

    # RELOAD LOG VIEW
    return HttpResponseRedirect("/FilteredHosts.html")

def get_config(request):

    uid = request.GET.get("uid")

    df = get_run_conf(uid)

    context = _get_context(df)

    return render(request, os.path.join(BASE_DIR, "bh_web", "pages", "RunConfig.html"), context)

def context_results_grid():

    # GET Results Group
    df = get_data("group")

    # DELETE NULL VALUES OR MISSING VALUES
    df.dropna(inplace=True)

    #df["Dashboard"] =  df["uid"].apply(lambda x: '<a href="/Dashboard.html?uid={}"><i class="fa-solid fa-gauge"></i></a>'.format(x))
    df["Dashboard"] =  df["uid"].apply(lambda x: '<a href="http://127.0.0.1:3000/d/UK-8Ve_7z/beacon?orgId=1&var-uid={}&from=now-2y&to=now&refresh=5s" target="_blank"><i class="fas fa-chart-line"></i></a>'.format(x))
    df["Config"] = df["uid"].apply(lambda x: '<a href="/RunConfig?uid={}"><i class="fa-solid fa-gears"></i></a>'.format(x))
    df["log_file"] = df["log_file"].apply(lambda x: '<a href="/LogDetails.html?filename={}"><i class="fas fa-file"></i></a>'.format(x))
    df["Delete"] = df["uid"].apply(lambda x: '<a href="/DelDetail?uid={}"><i class="fa-regular fa-trash-can"></i></a>'.format(x))
    df["uid"] = df["uid"].apply(lambda x: '<a href="{1}.html?uid={0}">{0}</a>'.format(x,"ResultDetails"))

    df = df[["uid", "dt", "beacons", "Dashboard", "log_file", "Config", "Delete"]].rename(columns={"uid": "Group ID", "dt": "Date", "beacons": "Beacon Count", "log_file": "Log File"})

    context = _get_context(df)

    return context

def lookup_dns(request):

    dest_ip = request.GET.get("dest_ip")
    uid = request.GET.get("uid")

    val = get_dns(dest_ip)

    if val.lower() != "unknown":
        add_data("dns", [dest_ip,val])
    else:
        messages.info(request, "Cannot find a DNS Name for {}! Please use another method!".format(dest_ip))
        # NEED MSGBOX HERE!
        print(val)

    return HttpResponseRedirect("/ResultDetails.html?uid={}".format(uid))

def filter_lookup_dns(request):

    dest_ip = request.GET.get("dest_ip")

    val = get_dns(dest_ip)

    if val.lower() != "unknown":
        add_data("dns", [dest_ip,val])
    else:
        messages.info(request, "Cannot find a DNS Name for {}! Please use another method!".format(dest_ip))
        # NEED MSGBOX HERE!
        print(val)

    return HttpResponseRedirect("/FilteredHosts.html")