import os
import time
import pandas as pd
import numpy as np
import json
from pathlib import Path
from beacon_huntress.src.bin.data import get_data, del_data, add_data, del_data, get_conn_str

# BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

def get_results(uid):

    df = get_data("detail",uid)

    # REORDER BY SCORE & REINDEX
    df.sort_values(by=["score", "conn_cnt"], ascending=False, inplace=True)
    df = df.reset_index(drop=True)
    df["ID"] = (df.index) + 1

    df = df[["ID", "source_ip", "dest_ip", "port", "score", "dns", "conn_cnt", "min_dt", "max_dt"]].rename(columns={"source_ip": "Source IP", "port": "Port", "dest_ip": "Destination IP", "score": "Score", "dns": "DNS", "conn_cnt": "Connection Count", "min_dt": "First Occurrence", "max_dt": "Last Occurrence"})

    return df.to_dict(orient="records")

def result_grid_group():

    # GET Results Group
    df = get_data("group")

    # FINAL DATAFRAME
    df = df[["uid", "dt", "beacons", "log_file"]].rename(columns={"uid": "beacon_group", "dt": "date", "beacons": "beacon_count"})

    return df.to_dict(orient="records")

def log_detail_view(log_file):

    full_path = os.path.join(BASE_DIR, "log", log_file)

    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            log_txt = f.read()

        ret_json = {"file_content": log_txt}
    else:
        ret_json = {"file_content": "{} does not exist!".format(full_path)}

    return ret_json


def del_result(uid):

    try:
        # GET Results Group
        df = get_data("group",uid)

        # DELETE DATA
        del_data("detail",uid)
        data_json = {"Deleted": True, "Message": "Data deleted for {}".format(uid)}

        if df.empty:
            # DELETE LOG FILE
            log_json = {"Deleted": False, "Message": "No log associated with {}".format(uid)}
        else:
            log_json = del_log_file(df["log_file"][0])

        # DELETE LOGS
        ret_json = {"Data": data_json, "Log": log_json}
    except BaseException as err:
        ret_json =  {"Data": {"Deleted": False, "Message": err}, "Log": {}}

    return ret_json

def del_log_file(log_file):

    try:
        # DELETE LOG FILE
        full_path = os.path.join(BASE_DIR, "log", log_file)

        if os.path.exists(full_path):
            os.remove(full_path)
            ret_json = {"Deleted": True, "Message": "File {} is deleted".format(full_path)}
        else:
            ret_json = {"Deleted": False, "Message": "File {} does not exist".format(full_path)}

    except BaseException as err:
        ret_json = {"Deleted": False, "Message": err}

    return ret_json

def filter_beacon(ip):

    try:
        add_data("beacon",ip)
        ret_json = {"Filtered": True, "Message": "{} is filtered from beacon results".format(ip)}
    except BaseException as err:
        ret_json = {"Filtered": False, "Message": err}

    return ret_json

def del_fil_beacon(ip):

    try:
        del_data("beacon",ip)
        ret_json = {"Deleted": True, "Message": "{} has been removed from the filtered beacons".format(ip)}
    except BaseException as err:
        ret_json = {"Deleted": False, "Message": err}

    return ret_json

