'''
Valkyrie Framework
Copyright 2023 Carnegie Mellon University.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
DM23-0210
'''

import sys
import os
import json
import logging
import argparse
from datetime import datetime, timedelta, timezone
import time
import hashlib
import shutil
import yaml
from pathlib import Path
from progress.bar import Bar
import uuid
import pandas as pd
from django.utils import timezone

#####################################################################################
##  IMPORT BEACON HUNTRESS MODULES & SET BASE_DIR
#####################################################################################

sys.path.append(os.path.join(os.getcwd(),"bin"))

from beacon_huntress.src.bin import ingest
from beacon_huntress.src.bin import beacon
from beacon_huntress.src.bin import dash
from beacon_huntress.src.bin import data
from beacon_huntress.src.bin import datasource

# BASE DIRECTORY (BH_WEB)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

######################################################################################
###  LOAD CONFIG
######################################################################################

def _load_config(conf):

    try:
        abs_conf_path = os.path.abspath(conf)
        print("DEBUG: Opening config {} {}".format(conf, abs_conf_path))


        with open(conf) as conf_file:
            config = yaml.safe_load(conf_file)

    except BaseException as err:
        print("ERROR: Issue with config {}".format(conf))
        print("ERROR: {}".format(err))
        sys.exit(1)

    return config

#####################################################################################
##  LOCAL FUNCTIONS
#####################################################################################

def _config_changed(filter_path,config):

    config_change = False

    # GET CONFIG FILES
    filter_path_file = os.path.join(filter_path,"metadata.json")
    tmp_file = os.path.join(os.path.join(os.getcwd(),"tmp","metadata.json"))

    if os.path.exists(filter_path_file) == False:
        config_change = True
    else:
        f_meta = json.load(open(filter_path_file))

        port_filter = config["filter"]["port"]
        src_filter = config["filter"]["source_ip"]
        dest_filter = config["filter"]["dest_ip"]
        s_dns_filter = config["filter"]["source_dns"]
        d_dns_filter = config["filter"]["dest_dns"]
        match_filter = config["filter"]["dns_match"]

        # BUILD METADATA FILE
        if port_filter == None:
            port_filter = []

        if src_filter == None: 
            src_filter = []

        if dest_filter == None: 
            dest_filter = []

        if s_dns_filter == None: 
            s_dns_filter = []

        if d_dns_filter == None: 
            d_dns_filter = []

        if match_filter == None:
            match_filter = []

        json_data = {}
        json_data["Port_Filter"] = port_filter
        json_data["Source_IP_Filter"] = src_filter
        json_data["Destination_IP_Filter"] = dest_filter    
        json_data["Source_DNS_Filter"] = s_dns_filter
        json_data["Destination_DNS_Filter"] = d_dns_filter
        json_data["Match_Filter"] = match_filter

        if f_meta == json_data:
            config_change = False
        else:
            config_change = True

    return config_change    

def _delete_folders(folder,logger = ""):
    
    try:
        if isinstance(folder, list):
            for x in folder:
                if os.path.exists(str(x)):
                    shutil.rmtree(str(x))            
        else:
            if os.path.exists(folder):
                shutil.rmtree(folder)
    except BaseException as err:
        logger.error(err)

def _get_epoch_dte(dte):

    if dte != "" or len(dte) > 0:
        fix_dte = datetime.strptime(dte, "%Y-%m-%dT%H:%M")
        dte_utc = fix_dte.replace(tzinfo=timezone.utc)
        dte = int(dte_utc.timestamp())
    else:
        dte = ""
    
    return dte

#####################################################################################
##  FUNCTIONS
#####################################################################################

def pipeline(conf):

    # Return Dictionary
    beacon_results = {}

    #####################################################################################
    ##  LOAD CONFIGURATIONS
    #####################################################################################  

    # LOAD GENERAL CONFIG
    config = _load_config(conf)

    # DASHBOARD CONFIG
    dash_config = _load_config(config["dashboard"]["conf"])
        
    #####################################################################################
    ##  LOGGING
    #####################################################################################  

    build_path = Path(config["general"]["raw_loc"])
    lst_path = list(build_path.parts[0:2])

    # SET BH LOG DIRECTORY
    # LOCATION FOR THE SERVICE
    log_dir = os.path.join(BASE_DIR,"log")
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    epoch = int(time.time())
    # LOCATION FOR THE SERVICE
    log_file_name = "log_{}".format(epoch)
    log_file = os.path.join(log_dir,"{}".format(log_file_name))

    logger = logging.getLogger("logger")

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s:\t%(message)s',datefmt="%m-%d %H:%M:%S")

    # FILE LOG HANDLER
    log_fh = logging.FileHandler(log_file)
    log_fh.setLevel(logging.INFO)
    log_fh.setFormatter(formatter)

    # ADD LOG HANDLERS
    logger.addHandler(log_fh)
    logger.propagate = False    

    #####################################################################################
    ##  LOAD CONSTANTS & LOCAL VARIABLES
    #####################################################################################  

    # RUN BEACON GROUP UUID
    UID = uuid.uuid4()

    beacon_results["beacon_group"] = UID

    print("Beacon Huntress starting the hunt!")
    logger.info("Beacon Huntress starting the hunt!")
    starttime = datetime.now()

    # IF OVERWRITE IS SELECTED REMOVE ALL RESULTS
    if config["general"]["overwrite"] == True:
        data.del_data("detail","all")

    # DELTA & CONFIG HASH
    new_delta = False
    config_hash = hashlib.sha1(json.dumps(config, sort_keys=True).encode()).hexdigest()

    # GET A RESULT GROUP & ADD THE RUN CONFIG
    group_id = data.add_beacon_group(UID)
    data.add_group_conf(UID,config)

    # ADD LOG FILE
    data.add_group_log(group_id,os.path.basename(log_file))

    #####################################################################################
    ##  DNS VALUES
    ##  NOT AVAILABLE IN THIS VERSION EXIT THE PROGRAM TO PREVENT ANY ISSUES
    #####################################################################################

    if config["bronze"]["dns_file"] != "":
        print("\t* ERROR: dns_file option is not available in this version of Beacon Huntress!")
        print("\t* ERROR: Reconfigure the dns_file option to \"\" ")
        # LOGGER
        logger.error("DNS File option is not available in this version of Beacon Huntress!")
        logger.error("Reconfigure the DNS File option to \"\" in ")

        # EXIT BEACON HUNTRESS
        sys.exit(1)

    #####################################################################################
    ##  SET THE BRONZE_LOC, SILVER_LOC, GOLD_LOC & FILTER_LOC
    #####################################################################################

    build_path = Path(config["general"]["raw_loc"])
    lst_path = list(build_path.parts[0:2])

    config["general"]["bronze_loc"] = os.path.join(lst_path[0], lst_path[1], "bronze", "data")
    config["general"]["silver_loc"] = os.path.join(lst_path[0], lst_path[1], "silver", "data")
    config["general"]["gold_loc"] = os.path.join(lst_path[0], lst_path[1], "gold", "data")
    config["general"]["filter_loc"] = os.path.join(lst_path[0], lst_path[1], "bronze", "filtered")

    #####################################################################################
    ##  DELETE EXISTING FILES
    #####################################################################################

    # DELETE BRONZE, SILVER, GOLD & FILTERS LAYERS
    logger.info("Deleting previous folder/s")
    _delete_folders([config["general"]["bronze_loc"],
                     config["general"]["silver_loc"],
                     config["general"]["gold_loc"],
                     config["general"]["filter_loc"]
                     ],
                     logger)

    #####################################################################################
    ##  ZIP
    #####################################################################################

    # UNZIP
    if config["zip"]["unzip"] == True:
        ingest.unzip(
            zip_file = config["zip"]["zip_loc"],
            dest_loc = config["general"]["raw_loc"]
        )

    #####################################################################################
    ##  CONVERT START & END DATE TO UTC THEN EPOCH
    #####################################################################################  

    start_dte = _get_epoch_dte(config["general"]["start_dte"])
    end_dte = _get_epoch_dte(config["general"]["end_dte"])
    
    logger.info("Start Date >= {} and End Date <= {}".format(config["general"]["start_dte"], config["general"]["end_dte"]))

    #####################################################################################
    ##  BRONZE LAYER
    #####################################################################################

    # RAW ZEEK LOGS
    if config["general"]["ds_type"] == "Zeek Connection Logs":
        if len(os.listdir(config["general"]["raw_loc"])) == 0:
            print("\t* ERROR: {} files located at {}!  Please use another location!".format(len(os.listdir(config["general"]["raw_loc"])), config["general"]["raw_loc"]))
            logger.error("{} files located at {}!  Please use another location!".format(len(os.listdir(config["general"]["raw_loc"])), config["general"]["raw_loc"]))
            sys.exit(1)

        # BUILD BRONZE LAYER
        is_new_bronze = ingest.build_bronze_layer(
            src_loc=config["general"]["raw_loc"], 
            bronze_loc=config["general"]["bronze_loc"],
            start_dte = start_dte,
            end_dte = end_dte,
            dns_file=config["bronze"]["dns_file"],
            overwrite = config["general"]["overwrite"], 
            verbose = config["general"]["verbose"]
            )

        if config["dashboard"]["dashboard"] == True:

            dash.load_dashboard(
                file_loc = [config["general"]["bronze_loc"]],
                dash_config = config["dashboard"]["conf"],
                dash_type = "raw_source",
                is_new = is_new_bronze,
                group_id = group_id,
                overwrite = config["general"]["overwrite"],
                verbose = config["general"]["verbose"]
            )

        # CHECK BRONZE
        df_bronze = pd.read_parquet(config["general"]["bronze_loc"])

    # ELASTIC DATASOURCE
    elif config["general"]["ds_type"] in ["Elastic", "Security Onion"]:

        try:
            es_starttime = datetime.now()

            # VARIABLE INIT
            is_new_bronze = True

            logger.info("Elastic datasource selected")

            logger.info("Gather file location")
            df_files = data.get_data("ds_files_name", config["general"]["ds_name"])
            df_files = df_files[["file_name"]]

            df_bronze = datasource.get_file_data(df_files)

            logger.info("Elastic data collected ({})".format(len(df_bronze)))

            # FILTER BY DATES
            if start_dte != "" and end_dte != "":
                df_bronze = df_bronze.query("ts >= {} and ts <= {}".format(start_dte, end_dte))
            # ONLY START
            elif start_dte != "" and end_dte == "":
                df_bronze = df_bronze.query("ts >= {}".format(start_dte))
            # ONLY END
            elif start_dte == "" and end_dte != "":
                df_bronze = df_bronze.query("ts <= {}".format(end_dte))
            else:
                pass  

            # #df_bronze["source_file"] = "/elastic/elastic.parquet"
            #df_bronze["source_file"] = os.path.join(config["general"]["bronze_loc"], "elastic_{}.parquet".format(epoch))
            #df_bronze["src_row_id"] = df_bronze.index

            Path(config["general"]["bronze_loc"]).mkdir(parents=True, exist_ok=True)

            df_bronze.to_parquet(os.path.join(config["general"]["bronze_loc"], "elastic_{}.parquet".format(epoch)))     

            endtime = datetime.now() - es_starttime
            logger.info("Elastic runtime {}".format(endtime))
        except BaseException as err:
            logger.error("{} issue.".format(config["general"]["ds_type"]))
            logger.error(err)
            
            beacon_results["cnt"] = 0
            beacon_results["log_file"] = log_file_name

            return beacon_results

    # IF DATA FALLS IN THE DATE RANGE CONTINUE
    if len(df_bronze) > 0:

        #####################################################################################
        ##  FILTER FILES
        #####################################################################################

        # CREATE FILTERED & DELTA FILES
        if config["general"]["filter"] == True: 

            # CHECK FOR CONFIG FILTER CHANGE
            conf_changed = _config_changed(config["general"]["filter_loc"],config)

            # IF CONFIG FILTER CHANGED REFILTER BRONZE LAYER
            if conf_changed == True and config["general"]["overwrite"] == False:
                # OVERWRITE IF CONFIG FILTER CHANGED
                print("\t* WARNING: Filter configuration changed. Refiltering bronze layer.".format(config["beacon"]["delta_file"]))
                logger.warning("Filter configuration changed. Refiltering bronze layer.")

                is_new_filter = ingest.build_filter_files(
                    src_loc = config["general"]["bronze_loc"],
                    dest_file = config["general"]["filter_loc"],
                    port_filter = config["filter"]["port"]["filter"],
                    port_exclude = config["filter"]["port"]["exclude"],
                    src_filter = config["filter"]["source_ip"]["filter"],
                    src_exclude = config["filter"]["source_ip"]["exclude"],
                    dest_filter = config["filter"]["dest_ip"]["filter"],
                    dest_exclude = config["filter"]["dest_ip"]["exclude"],
                    # DNS FEATURE CURRENTLY NOT AVAILABLE FOR BEACON HUNTRESS
                    # s_dns_filter = config["filter"]["source_dns"]["filter"],
                    # s_dns_exclude = config["filter"]["source_dns"]["exclude"],
                    # d_dns_filter = config["filter"]["dest_dns"]["filter"],
                    # d_dns_exclude = config["filter"]["dest_dns"]["exclude"],
                    # match_filter = config["filter"]["dns_match"]["filter"],
                    # match_exclude = config["filter"]["dns_match"]["exclude"],
                    file_type = config["general"]["file_type"],
                    overwrite = True, 
                    verbose = config["general"]["verbose"]
                    )            
            else:        
                is_new_filter = ingest.build_filter_files(
                    src_loc = config["general"]["bronze_loc"],
                    dest_file = config["general"]["filter_loc"],
                    port_filter = config["filter"]["port"]["filter"],
                    port_exclude = config["filter"]["port"]["exclude"],
                    src_filter = config["filter"]["source_ip"]["filter"],
                    src_exclude = config["filter"]["source_ip"]["exclude"],
                    dest_filter = config["filter"]["dest_ip"]["filter"],
                    dest_exclude = config["filter"]["dest_ip"]["exclude"],
                    # DNS FEATURE CURRENTLY NOT AVAILABLE FOR BEACON HUNTRESS
                    # s_dns_filter = config["filter"]["source_dns"]["filter"],
                    # s_dns_exclude = config["filter"]["source_dns"]["exclude"],
                    # d_dns_filter = config["filter"]["dest_dns"]["filter"],
                    # d_dns_exclude = config["filter"]["dest_dns"]["exclude"],
                    # match_filter = config["filter"]["dns_match"]["filter"],
                    # match_exclude = config["filter"]["dns_match"]["exclude"],
                    file_type = config["general"]["file_type"],
                    overwrite = config["general"]["overwrite"], 
                    verbose = config["general"]["verbose"]
                    )

            # ONLY BUILD A NEW DELTA FILE IF THERE IS A NEW FILTER FILE OR NEW BRONZE FILE
            if is_new_filter == True or is_new_bronze == True:
                # BUILD DELTA FILE FOR FILTERED LOCATION
                ingest.build_delta_files(
                #src_loc = config["general"]["filter_loc"],
                src_loc = os.path.join(config["general"]["filter_loc"],"data"),
                delta_file_loc = config["general"]["silver_loc"],
                delta_file_type = config["general"]["file_type"],
                overwrite =  config["general"]["overwrite"]
                )

                new_delta = True
            else:
                print("\t* WARNING: Bronze Files and Filters are the same.  Running with old delta file ({}).".format(config["beacon"]["delta_file"]))
                logger.warning("Bronze Files and Filters are the same.  Running with old delta file ({}).".format(config["beacon"]["delta_file"]))
                new_delta = False

        #BACKHERE
        #ADDED BY HUFF ON 05/03/2023
        # CREATE FILTERED & DELTA FILES
        elif config["general"]["filter"] == False:
            print("\t* WARNING: No Filters selected.")
            logger.warning("No Filters selected.")

            # BUILD DELTA FILE
            ingest.build_delta_files(
            src_loc = config["general"]["bronze_loc"],
            delta_file_loc = config["general"]["silver_loc"],
            delta_file_type = config["general"]["file_type"],
            overwrite =  config["general"]["overwrite"]
            )

            new_delta = False
        else:
            # ONLY BUILD A NEW DELTA FILE IF THERE IS A NEW FILTER FILE OR NEW BRONZE FILE
            if is_new_filter == True or is_new_bronze == True:
                # BUILD DELTA FILE
                ingest.build_delta_files(
                src_loc = config["general"]["bronze_loc"],
                delta_file_loc = config["general"]["silver_loc"],
                delta_file_type = config["general"]["file_type"],
                #overwrite =  config["general"]["overwrite"]
                overwrite = False
                )
                
                new_delta = True
            else:
                print("\t* WARNING: Bronze Files and Filters are the same.  Running with old delta file ({}).".format(config["beacon"]["agg"]["delta_file"]))
                logger.warning("Bronze Files and Filters are the same.  Running with old delta file ({}).".format(config["beacon"]["agg"]["delta_file"]))
                new_delta = False   

        #####################################################################################
        ##  DELTA
        #####################################################################################

        if config["beacon"]["delta_file"] == "latest":
            max_delta_file = ingest.get_latest_file(folder_loc = config["general"]["silver_loc"], file_type = config["general"]["file_type"])
        else:
            max_delta_file = config["beacon"]["delta_file"]

        if max_delta_file == None:
            logger.error("No delta file!")
            sys.exit(1)

        # LOAD DASHBOARD DATA (DELTA)
        if config["dashboard"]["dashboard"] == True:
            dash.load_dashboard(
                file_loc = [max_delta_file],
                dash_config = config["dashboard"]["conf"],
                dash_type = "delta",
                is_new = is_new_bronze,
                group_id = group_id,
                overwrite = config["general"]["overwrite"],
                # overwrite = False,
                verbose = config["general"]["verbose"]
            )

        #####################################################################################
        ##  BEACONS
        #####################################################################################

        # AGGLOMERATIVE CLUSTERING
        if config["general"]["cluster_type"] == "agg":        
            if config["dashboard"]["dashboard"] == True: 
                if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:
                    ret_gold_file = beacon.agglomerative_clustering(
                        delta_file = max_delta_file,
                        delta_column = config["beacon"]["delta_column"],
                        max_variance = config["beacon"]["agg"]["max_variance"],
                        min_records = config["beacon"]["agg"]["min_records"],
                        cluster_factor = config["beacon"]["agg"]["cluster_factor"],
                        line_amounts = config["beacon"]["agg"]["line_amounts"],
                        min_delta_time = config["beacon"]["agg"]["min_delta_time"],
                        gold_loc = config["general"]["gold_loc"],
                        overwrite = config["general"]["overwrite"],
                        verbose = config["general"]["verbose"]
                    )

                    if config["dashboard"]["dashboard"] == True:
                        dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                else:
                    logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    return
            else:
                ret_gold_file = beacon.agglomerative_clustering(
                    delta_file = max_delta_file,
                    delta_column = config["beacon"]["delta_column"],
                    max_variance = config["beacon"]["agg"]["max_variance"],
                    min_records = config["beacon"]["agg"]["min_records"],
                    cluster_factor = config["beacon"]["agg"]["cluster_factor"],
                    line_amounts = config["beacon"]["agg"]["line_amounts"],
                    min_delta_time = config["beacon"]["agg"]["min_delta_time"],
                    gold_loc = config["general"]["gold_loc"],
                    overwrite = config["general"]["overwrite"],
                    verbose = config["general"]["verbose"]
                )            

        # DBSCAN 
        if config["general"]["cluster_type"] == "dbscan":
            if config["dashboard"]["dashboard"] == True: 
                if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:
                    ret_gold_file = beacon.dbscan_clustering(
                        delta_file = max_delta_file,
                        delta_column = config["beacon"]["delta_column"],
                        minimum_delta = config["beacon"]["dbscan"]["minimum_delta"],
                        spans = config["beacon"]["dbscan"]["spans"],
                        minimum_points_in_cluster = config["beacon"]["dbscan"]["minimum_points_in_cluster"],
                        minimum_likelihood = config["beacon"]["dbscan"]["minimum_likelihood"],
                        gold_loc = config["general"]["gold_loc"],
                        overwrite = config["general"]["overwrite"],
                        verbose = config["general"]["verbose"]
                    )

                    dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                else:
                    logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    return
            else:
                ret_gold_file = beacon.dbscan_clustering(
                    delta_file = max_delta_file,
                    delta_column = config["beacon"]["delta_column"],
                    minimum_delta = config["beacon"]["dbscan"]["minimum_delta"],
                    spans = config["beacon"]["dbscan"]["spans"],
                    minimum_points_in_cluster = config["beacon"]["dbscan"]["minimum_points_in_cluster"],
                    minimum_likelihood = config["beacon"]["dbscan"]["minimum_likelihood"],
                    gold_loc = config["general"]["gold_loc"],
                    overwrite = config["general"]["overwrite"],
                    verbose = config["general"]["verbose"]
                )            

        # DBSCAN BY VARIANCE
        if config["general"]["cluster_type"] == "dbscan_var":
            if config["dashboard"]["dashboard"] == True:
                if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:
                    ret_gold_file = beacon.dbscan_by_variance(
                        delta_file = max_delta_file,
                        delta_column = config["beacon"]["delta_column"],
                        avg_delta = config["beacon"]["dbscan_var"]["avg_delta"],
                        conn_cnt = config["beacon"]["dbscan_var"]["conn_cnt"],
                        span_avg = config["beacon"]["dbscan_var"]["span_avg"],
                        variance_per = config["beacon"]["dbscan_var"]["variance_per"],
                        minimum_likelihood = config["beacon"]["dbscan_var"]["minimum_likelihood"],
                        gold_loc = config["general"]["gold_loc"],
                        overwrite = config["general"]["overwrite"],
                        verbose = config["general"]["verbose"]
                    )

                    dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                else:
                    logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    return
            else:
                ret_gold_file = beacon.dbscan_by_variance(
                    delta_file = max_delta_file,
                    delta_column = config["beacon"]["delta_column"],
                    avg_delta = config["beacon"]["dbscan_var"]["avg_delta"],
                    conn_cnt = config["beacon"]["dbscan_var"]["conn_cnt"],
                    span_avg = config["beacon"]["dbscan_var"]["span_avg"],
                    variance_per = config["beacon"]["dbscan_var"]["variance_per"],
                    minimum_likelihood = config["beacon"]["dbscan_var"]["minimum_likelihood"],
                    gold_loc = config["general"]["gold_loc"],
                    overwrite = config["general"]["overwrite"],
                    verbose = config["general"]["verbose"]
                )

        # BY PACKET
        if config["general"]["cluster_type"] == "by_packet":
            if config["dashboard"]["dashboard"] == True:
                if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:
                    ret_gold_file = beacon.packet(
                        delta_file = max_delta_file,
                        delta_column = config["beacon"]["delta_column"],
                        avg_delta = config["beacon"]["by_packet"]["avg_delta"],
                        conn_cnt = config["beacon"]["by_packet"]["conn_cnt"],
                        min_unique_percent = config["beacon"]["by_packet"]["min_unique_percent"],
                        gold_loc = config["general"]["gold_loc"],
                        overwrite = config["general"]["overwrite"],
                        verbose = config["general"]["verbose"]
                        )

                    dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                else:
                    logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    return
            else:
                ret_gold_file = beacon.packet(
                    delta_file = max_delta_file,
                    delta_column = config["beacon"]["delta_column"],
                    avg_delta = config["beacon"]["by_packet"]["avg_delta"],
                    conn_cnt = config["beacon"]["by_packet"]["conn_cnt"],
                    min_unique_percent = config["beacon"]["by_packet"]["min_unique_percent"],
                    gold_loc = config["general"]["gold_loc"],
                    overwrite = config["general"]["overwrite"],
                    verbose = config["general"]["verbose"]
                    )

        # BY CONNECTION GROUP
        if config["general"]["cluster_type"] == "by_conn_group":
            if config["dashboard"]["dashboard"] == True:
                if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:
                    ret_gold_file = beacon.cluster_conns(
                        delta_file = max_delta_file,
                        delta_column = config["beacon"]["delta_column"],
                        conn_cnt = config["beacon"]["by_conn_group"]["conn_cnt"],
                        conn_group = config["beacon"]["by_conn_group"]["conn_group"],
                        threshold = config["beacon"]["by_conn_group"]["threshold"],
                        gold_loc = config["general"]["gold_loc"],
                        overwrite = config["general"]["overwrite"],
                        verbose = config["general"]["verbose"]
                        )

                    dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                else:
                    logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                    return
            else:
                ret_gold_file = beacon.cluster_conns(
                        delta_file = max_delta_file,
                        delta_column = config["beacon"]["delta_column"],
                        conn_cnt = config["beacon"]["by_conn_group"]["conn_cnt"],
                        conn_group = config["beacon"]["by_conn_group"]["conn_group"],
                        threshold = config["beacon"]["by_conn_group"]["threshold"],
                        gold_loc = config["general"]["gold_loc"],
                        overwrite = config["general"]["overwrite"],
                        verbose = config["general"]["verbose"]
                    )

        # PERSISTENT CONNECTIONS
        # ADDED IS_P_CONN FOR NOW AS PERSISTENT CONNECTIONS HAVE NO DASHBOARD
        is_p_conn = False
        if config["general"]["cluster_type"] == "by_p_conn":
            is_p_conn = True
            beacon.p_conns(
                delta_file = max_delta_file,
                diff_time = config["beacon"]["by_p_conn"]["diff_time"], 
                diff_type = config["beacon"]["by_p_conn"]["diff_type"]
                )


        # LOAD DB DATA FOR DASHBOARD 
        # ADDED IS_P_CONN FOR NOW AS PERSISTENT CONNECTIONS HAVE NO DASHBOARD
        if config["dashboard"]["dashboard"] == True and is_p_conn == False:

            # GRAB THE LATEST GOLD FILE IF SELECTED
            if dash_config["db"]["file_loc"] == "latest" and dash_config["dashboard"]["last_gold_file"] == True:
                logger.warning("Latest Gold File will be loaded")
                print("\t* WARNING: Latest Gold File will be loaded")
                if ret_gold_file != None and ret_gold_file != "":
                    max_gold_file = ret_gold_file
                else:
                    max_gold_file = ingest.get_latest_file(folder_loc = config["general"]["gold_loc"], file_type = config["general"]["file_type"])
            elif dash_config["db"]["file_loc"] == "latest" and dash_config["dashboard"]["last_gold_file"] == False:
                max_gold_file = ret_gold_file
            else:
                max_gold_file = dash_config["db"]["file_loc"]

            dash.load_dashboard(
                file_loc = max_gold_file,
                dash_config = config["dashboard"]["conf"],
                dash_type = "beacon",
                is_new = True,
                group_id = group_id,
                overwrite = config["general"]["overwrite"],
                verbose = config["general"]["verbose"]
            )

            # CHECK FOR RESULTS AND ADD BACK TO DICTIONARY
            if max_gold_file != None and os.path.exists(max_gold_file):
                df_rt = pd.read_parquet(max_gold_file)
                rt_cnt = len(df_rt)
            
                beacon_results["cnt"] = rt_cnt
                beacon_results["log_file"] = log_file_name
            else:
                beacon_results["cnt"] = 0
                beacon_results["log_file"] = log_file_name
    else:
        logger.warning("No data falls within the date range of {} & {}".format(config["general"]["start_dte"], config["general"]["end_dte"]))
        beacon_results["cnt"] = 0
        beacon_results["log_file"] = log_file_name

    #####################################################################################
    ##  DELETE BH CREATE FILES
    #####################################################################################

    logger.info("Deleting bronze, silver and gold files")

    bz_f = os.path.join(lst_path[0], lst_path[1], "bronze")
    sv_f = os.path.join(lst_path[0], lst_path[1], "silver")
    gd_f = os.path.join(lst_path[0], lst_path[1], "gold")
    
    _delete_folders([os.path.join(lst_path[0], lst_path[1], "bronze"),
                     os.path.join(lst_path[0], lst_path[1], "silver"),
                     os.path.join(lst_path[0], lst_path[1], "gold")
                     ],logger)

    endtime = datetime.now() - starttime
    logger.info("Beacon Huntress completed {}".format(endtime))
    print("Beacon Huntress completed {}".format(endtime))
    
    # RETURN RESULTS DICTIONARY
    return beacon_results

#####################################################################################
##  MAIN
#####################################################################################

def main(conf):

    config = _load_config(conf)

    ret_val = pipeline(conf = conf)

    return ret_val

