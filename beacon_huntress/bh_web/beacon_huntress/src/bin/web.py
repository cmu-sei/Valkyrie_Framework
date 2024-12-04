from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pathlib import Path
import os
import yaml
import beacon_huntress.src.beacon_huntress as bh
from settings.models import conf_general, conf_filter
from bh_execute.models import Agg, DBScan, DBScanVar, ByPacket, ByConnGroup, ByPConn
from beacon_huntress.src.beacon_huntress import main as beacon_huntress

# REMOVE THIS AFTER DONE
import sys

# BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

def _fix_list(lst):

    ret_lst = []
    cnt = 1

    try:
        for z in lst:
            print(z)
            if cnt < 2:
                val_1 = int(z.replace("[","").replace("]","").replace(",",""))
                cnt += 1
            else:
                val_2 = int(z.replace("[","").replace("]","").replace(",",""))
                lst = [ val_1, val_2 ]
                ret_lst.append(lst)
                cnt = 1
    except BaseException as err:
        # logger.error("Error with list parameter")
        # logger.error(err)  
        print(err)
    
    return ret_lst
            

def exe_bh(request,type):

    # Load Beacon Huntress Config
    conf = bh._load_config(os.path.join(BASE_DIR, "config", "config.conf"))
    db_conf = bh._load_config(os.path.join(BASE_DIR, "config", "dashboard.conf"))

    conf = load_settings(conf, "general")
    conf = load_settings(conf, "filter")
    #conf = load_settings(db_conf, "dashboard")
    conf = load_settings(conf, type)

    print(conf)

    with open("bh_run.yaml", "w") as file:
        yaml.dump(conf, file, sort_keys=False)

    # UNCOMMENT TO RUN THIS ALGO
    beacon_huntress("bh_run.yaml")

    # DELETE TEMP YAML
    os.remove("bh_run.yaml")

    # UNCOMMENT TO RENDER THE PAGE
    return render(request,os.path.join(Path(__file__).resolve().parent.parent.parent.parent, "bh_web", "pages", "Results.html"))


def load_settings(config, type):

    if type == "general":
        # GET THE DATA
        set_data = conf_general.objects.latest("row_id")

        # GET CURRENT RAW PATH TO BUILD THE BRONZE, SILVER, GOLD & FILTER LOCATIONS
        build_path = Path(config["general"]["raw_loc"])
        lst_path = list(build_path.parts[0:2])      
        
        #SET THE GENERAL DATA
        config["general"]["raw_loc"] = str(set_data.raw_loc)
        config["general"]["bronze_loc"] = os.path.join(lst_path[0], lst_path[1], "bronze", "data")
        config["general"]["silver_loc"] = os.path.join(lst_path[0], lst_path[1], "silver", "data")
        config["general"]["gold_loc"] = os.path.join(lst_path[0], lst_path[1], "gold", "data")        
        config["general"]["file_type"] = "parquet" if set_data.file_type == "1" else "csv"
        config["general"]["overwrite"] = set_data.overwrite
        config["general"]["verbose"] = set_data.verbose

    elif type == "filter":
        # GET THE DATA
        set_data = conf_filter.objects.latest("row_id")

        # GET CURRENT RAW PATH TO BUILD THE BRONZE, SILVER, GOLD & FILTER LOCATIONS
        build_path = Path(config["general"]["raw_loc"])
        lst_path = list(build_path.parts[0:2])       

        # #SET FILTER DATA
        config["general"]["filter"] = set_data.filter
        config["general"]["filter_loc"] = os.path.join(lst_path[0], lst_path[1], "bronze", "filtered")
        #config["filter"]["port"]["filter"] = set_data.port_filter.replace("\r","").replace("\n","").split(",")
        config["filter"]["port"]["filter"] = [int(x) for x in set_data.port_filter.split(",")]
        config["filter"]["port"]["exclude"] = set_data.port_exclude
        config["filter"]["source_ip"]["filter"] = [x for x in set_data.src_ip_filter.split(",")]
        config["filter"]["source_ip"]["exclude"] = set_data.src_ip_exclude
        config["filter"]["dest_ip"]["filter"] = [x for x in set_data.dest_ip_filter.split(",")]
        config["filter"]["dest_ip"]["exclude"] = set_data.dest_ip_exclude    

    elif type == "agg":
        #GET THE DATA
        set_data = Agg.objects.latest("row_id")

        #SET FILTER DATA
        config["general"]["cluster_type"] = "agg"
        config["beacon"]["agg"]["max_variance"] = (set_data.max_variance / 100)
        config["beacon"]["agg"]["min_records"] = set_data.min_records
        config["beacon"]["agg"]["cluster_factor"] = (set_data.cluster_factor / 100)
        config["beacon"]["agg"]["line_amounts"] = list(set_data.line_amounts)
        config["beacon"]["agg"]["min_delta_time"] = set_data.min_delta_time

    elif type == "dbscan":
        #GET THE DATA
        set_data = DBScan.objects.latest("row_id")

        #SET FILTER DATA

        # format the  list from django
        dbscan_spans = _fix_list(set_data.spans.split())

        config["general"]["cluster_type"] = "dbscan"
        config["beacon"]["dbscan"]["minimum_delta"] = set_data.minimum_delta
        # config["beacon"]["dbscan"]["spans"] = list(set_data.spans)
        config["beacon"]["dbscan"]["spans"] = dbscan_spans
        config["beacon"]["dbscan"]["minimum_points_in_cluster"] = set_data.minimum_points_in_cluster
        config["beacon"]["dbscan"]["minimum_likelihood"] = (set_data.minimum_likelihood /100)

    elif type == "dbscan_var":
        #GET THE DATA
        set_data = DBScanVar.objects.latest("row_id")

        #SET FILTER DATA
        config["general"]["cluster_type"] = "dbscan_var"
        config["beacon"]["dbscan_var"]["avg_delta"] = set_data.avg_delta
        config["beacon"]["dbscan_var"]["conn_cnt"] = set_data.conn_cnt
        config["beacon"]["dbscan_var"]["span_avg"] = set_data.span_avg
        config["beacon"]["dbscan_var"]["variance_per"] = set_data.variance_per
 
    elif type == "by_conn_group":
        #GET THE DATA
        set_data = ByConnGroup.objects.latest("row_id")

        #SET FILTER DATA
        config["general"]["cluster_type"] = "by_conn_group"
        config["beacon"]["by_conn_group"]["conn_cnt"] = set_data.conn_cnt
        config["beacon"]["by_conn_group"]["conn_group"] = set_data.conn_group
        config["beacon"]["by_conn_group"]["threshold"] = set_data.threshold

    elif type == "by_p_conn":
        #GET THE DATA
        set_data = ByPConn.objects.latest("row_id")

        #SET FILTER DATA
        config["general"]["cluster_type"] = "by_p_conn"
        config["beacon"]["by_p_conn"]["diff_time"] = set_data.diff_time
        config["beacon"]["by_p_conn"]["diff_type"] = set_data.diff_type       

    return config
