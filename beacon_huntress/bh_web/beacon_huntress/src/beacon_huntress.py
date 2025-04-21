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
import uuid
import pandas as pd
#from django.utils import timezone

#####################################################################################
##  IMPORT BEACON HUNTRESS MODULES & SET BASE_DIR
#####################################################################################

sys.path.append(os.path.join(os.getcwd(),"bin"))

# COMMENTED FOR CLI
# from beacon_huntress.src.bin import ingest
# from beacon_huntress.src.bin import beacon
# from beacon_huntress.src.bin import dash
# from beacon_huntress.src.bin import data
# from beacon_huntress.src.bin import Madmom as mm

# CLI
from bin import ingest
from bin import beacon
from bin import Madmom as mm


# BASE DIRECTORY (BH_WEB)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

######################################################################################
###  LOAD CONFIG
######################################################################################

def _load_config(conf):

    try:
        abs_conf_path = os.path.abspath(conf)
        #print("DEBUG: Opening config {} {}".format(conf, abs_conf_path))

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

def _get_ds_types(type_id):

    if type_id == 1:
        ds_name = "Zeek Connection Logs"
        ds_type = "Zeek Connection Logs"
    elif type_id == 2:
        ds_name = "HTTP File"
        ds_type = "HTTP File"
    elif type_id == 3:
        ds_name = "Delta File"
        ds_type = "Delta File"
    else:
        ds_name = ""
        ds_type = ""

    return ds_name, ds_type

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
    # COMMENTED FOR CLI
    #config = _load_config(conf)

    # CLI SPECIFIC
    config = conf

    # DASHBOARD CONFIG
    # COMMENTED FOR CLI
    #dash_config = _load_config(config["dashboard"]["conf"])

    # CLI SPECIFIC
    dash_config = _load_config(os.path.join("config","dashboard.conf"))

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

    # COMMENTED FOR CLI
    # IF OVERWRITE IS SELECTED REMOVE ALL RESULTS
    # if config["general"]["overwrite"] == True:
    #     data.del_data("detail","all")

    # DELTA & CONFIG HASH
    new_delta = False
    config_hash = hashlib.sha1(json.dumps(config, sort_keys=True).encode()).hexdigest()

    # GET A RESULT GROUP & ADD THE RUN CONFIG
    # COMMENTED FOR CLI
    #group_id = data.add_beacon_group(UID)
    #data.add_group_conf(UID,config)

    #CLI SPECIFIC
    group_id = UID

    # COMMENTED FOR CLI
    # ADD LOG FILE
    # data.add_group_log(group_id,os.path.basename(log_file))

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
    # CLI COMMENT
    #lst_path = list(build_path.parts[0:2])
    # CLI SPECIFIC
    lst_path = [os.path.join(Path.cwd().parent,"data"), str(group_id)]

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

    # GET FILTERS
    df_filter = pd.read_parquet("filter/filtered_ips.parquet")

    # CLI CHANGE
    df_bronze, is_new_bronze = beacon.build_bronze_ds(
        config = config,
        start_dte = start_dte,
        end_dte = end_dte,
        beacon_group = UID,
        filter_ds = df_filter,
        group_id = group_id,
        logger = logger)


    #####################################################################################
    ##  BRONZE LAYER
    #####################################################################################


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

        # COMMENTED FOR CLI
        # LOAD DASHBOARD DATA (DELTA)
        # if config["dashboard"]["dashboard"] == True:
            # dash.load_dashboard(
            #     file_loc = [max_delta_file],
            #     dash_config = config["dashboard"]["conf"],
            #     dash_type = "delta",
            #     is_new = is_new_bronze,
            #     group_id = group_id,
            #     overwrite = config["general"]["overwrite"],
            #     verbose = config["general"]["verbose"]
            # )

        #####################################################################################
        ##  BEACONS
        #####################################################################################

        # Default Score for MAD
        likelihood = ".50"

        # AGGLOMERATIVE CLUSTERING
        if config["general"]["cluster_type"] == "agg":
            # COMMENTED FOR CLI
            if config["dashboard"]["dashboard"] == True:
                pass
            #     if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:

            #         # Default Score for MAD
            #         likelihood = (config["beacon"]["agg"]["cluster_factor"] / 100)

            #         ret_gold_file = beacon.agglomerative_clustering(
            #             delta_file = max_delta_file,
            #             delta_column = config["beacon"]["delta_column"],
            #             max_variance = config["beacon"]["agg"]["max_variance"],
            #             min_records = config["beacon"]["agg"]["min_records"],
            #             cluster_factor = config["beacon"]["agg"]["cluster_factor"],
            #             line_amounts = config["beacon"]["agg"]["line_amounts"],
            #             min_delta_time = config["beacon"]["agg"]["min_delta_time"],
            #             gold_loc = config["general"]["gold_loc"],
            #             overwrite = config["general"]["overwrite"],
            #             verbose = config["general"]["verbose"]
            #         )

                    # if config["dashboard"]["dashboard"] == True:
                    #     dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                # else:
                #     logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     return
            else:

                # Default Score for MAD
                likelihood = (config["beacon"]["agg"]["cluster_factor"] / 100)

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
                pass
                # COMMENTED FOR CLI
                # if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:

                #     # Default Score for MAD
                #     likelihood = (config["beacon"]["dbscan"]["minimum_likelihood"] / 100)

                #     ret_gold_file = beacon.dbscan_clustering(
                #         delta_file = max_delta_file,
                #         delta_column = config["beacon"]["delta_column"],
                #         minimum_delta = config["beacon"]["dbscan"]["minimum_delta"],
                #         spans = config["beacon"]["dbscan"]["spans"],
                #         minimum_points_in_cluster = config["beacon"]["dbscan"]["minimum_points_in_cluster"],
                #         minimum_likelihood = config["beacon"]["dbscan"]["minimum_likelihood"],
                #         gold_loc = config["general"]["gold_loc"],
                #         overwrite = config["general"]["overwrite"],
                #         verbose = config["general"]["verbose"]
                #     )

                #     dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                # else:
                #     logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     return
            else:

                # Default Score for MAD
                likelihood = (config["beacon"]["dbscan"]["minimum_likelihood"] / 100)

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
                pass
                # COMMENTED FOR CLI
                # if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:

                #     # Default Score for MAD
                #     likelihood = (config["beacon"]["dbscan_var"]["minimum_likelihood"] / 100)

                #     ret_gold_file = beacon.dbscan_by_variance(
                #         delta_file = max_delta_file,
                #         delta_column = config["beacon"]["delta_column"],
                #         avg_delta = config["beacon"]["dbscan_var"]["avg_delta"],
                #         conn_cnt = config["beacon"]["dbscan_var"]["conn_cnt"],
                #         span_avg = config["beacon"]["dbscan_var"]["span_avg"],
                #         variance_per = config["beacon"]["dbscan_var"]["variance_per"],
                #         minimum_likelihood = config["beacon"]["dbscan_var"]["minimum_likelihood"],
                #         gold_loc = config["general"]["gold_loc"],
                #         overwrite = config["general"]["overwrite"],
                #         verbose = config["general"]["verbose"]
                #     )

                #     dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                # else:
                #     logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     return
            else:

                # Default Score for MAD
                likelihood = (config["beacon"]["dbscan_var"]["minimum_likelihood"] / 100)

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
                pass
                # COMMENTED FOR CLI
                # if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:
                #     ret_gold_file = beacon.packet(
                #         delta_file = max_delta_file,
                #         delta_column = config["beacon"]["delta_column"],
                #         avg_delta = config["beacon"]["by_packet"]["avg_delta"],
                #         conn_cnt = config["beacon"]["by_packet"]["conn_cnt"],
                #         min_unique_percent = config["beacon"]["by_packet"]["min_unique_percent"],
                #         gold_loc = config["general"]["gold_loc"],
                #         overwrite = config["general"]["overwrite"],
                #         verbose = config["general"]["verbose"]
                #         )

                #     dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                # else:
                #     logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     return
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
                pass
                # COMMENTED FOR CLI
                # if new_delta == True or dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "get") == False:
                #     ret_gold_file = beacon.cluster_conns(
                #         delta_file = max_delta_file,
                #         delta_column = config["beacon"]["delta_column"],
                #         conn_cnt = config["beacon"]["by_conn_group"]["conn_cnt"],
                #         conn_group = config["beacon"]["by_conn_group"]["conn_group"],
                #         threshold = config["beacon"]["by_conn_group"]["threshold"],
                #         gold_loc = config["general"]["gold_loc"],
                #         overwrite = config["general"]["overwrite"],
                #         verbose = config["general"]["verbose"]
                #         )

                #     dash._config_hash(conf = config["dashboard"]["conf"], conf_hash = config_hash, option = "add")
                # else:
                #     logger.warning("Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     print("\t* WARNING: Cluster options are the same, no need to rerun.  Please create a new delta file or change the configuration.")
                #     return
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

        ###########################################################
        ##  MAD ALGO
        ## MEDIAN AVG DEVIATION OF THE MEAN OF OBSERVATIONS MEANS
        ###########################################################

        logger.info("Running MAD algorithm")

        likelihood = 0.50
        df_mad = mm.run_mad(max_delta_file, likelihood)

        # FIX
        #df_mad["dns"] = ""

        if df_mad.empty:
            logger.warning("No results for Median Absolute Deviation!")
        else:
            pass
            # COMMENTED FOR CLI
            # if config["dashboard"]["dashboard"] == True:
            #     logger.info("Loading MAD results")
            #     dash.load_dashboard(
            #         dataframe = df_mad,
            #         dash_config = config["dashboard"]["conf"],
            #         dash_type = "mad",
            #         is_new = True,
            #         group_id = group_id,
            #         overwrite = config["general"]["overwrite"],
            #         verbose = config["general"]["verbose"]
            #     )

        # COMMENTED FOR CLI
        #df_mad.to_csv("/delta/rita.csv")

        ###########################################################
        ##  MAD ALGO
        ###########################################################

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

            # COMMENTED FOR CLI
            # dash.load_dashboard(
            #     file_loc = max_gold_file,
            #     dash_config = config["dashboard"]["conf"],
            #     dash_type = "beacon",
            #     is_new = True,
            #     group_id = group_id,
            #     overwrite = config["general"]["overwrite"],
            #     verbose = config["general"]["verbose"]
            # )

            # CHECK FOR RESULTS AND ADD BACK TO DICTIONARY
            if max_gold_file != None and os.path.exists(max_gold_file):
                df_rt = pd.read_parquet(max_gold_file)
                rt_cnt = len(df_rt)

                beacon_results["cnt"] = rt_cnt
                beacon_results["log_file"] = log_file_name
            else:
                beacon_results["cnt"] = 0
                beacon_results["log_file"] = log_file_name

        # FIX THIS LATER
        elif config["dashboard"]["dashboard"] == False and is_p_conn == False:

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

            # CHECK FOR RESULTS AND ADD BACK TO DICTIONARY
            if max_gold_file != None and os.path.exists(max_gold_file):
                df_rt = pd.read_parquet(max_gold_file)
                rt_cnt = len(df_rt)

                beacon_results["cnt"] = rt_cnt
                beacon_results["log_file"] = log_file_name
            else:
                df_rt = pd.DataFrame(columns=["id.orig_h", "id.resp_h", "id.resp_p", "id.orig_p", "datetime", "likelihood", "delta_mins"])
                beacon_results["cnt"] = 0
                beacon_results["log_file"] = log_file_name

    else:
        logger.warning("No data falls within the date range of {} & {}".format(config["general"]["start_dte"], config["general"]["end_dte"]))
        beacon_results["cnt"] = 0
        beacon_results["log_file"] = log_file_name

    #####################################################################################
    ##  Final Results
    #####################################################################################

    # GET FILTERS
    df_filter = pd.read_parquet("filter/filtered_ips.parquet")

    # GET DELTA FOR TOP TALKER
    df_delta = pd.read_parquet(max_delta_file)

    # CREATE CLI RESULTS DIRECTORY
    Path("cli_results/{}".format(group_id)).mkdir(parents=True, exist_ok=True)

    # WRITE FILES IF YOU HAVE RESULTS
    if df_rt.empty == False:
        # DNS FLIP & FILTER
        if conf["general"]["ds_type"] == "HTTP File":
            df_rt = df_rt.rename(columns={"id.resp_h": "host", "dns": "id.resp_h"}).rename(columns={"host": "dns"})
            #df_rt = df_rt[~df_rt["dns"].isin(df_filter["dns"])]

        #df_rt = df_rt[~df_rt["id.resp_h"].isin(df_filter["ip"])]
        df_rt.to_csv("cli_results/{}/cluster_results.csv".format(group_id))
    else:
        # CREATE EMPTY DATAFRAME AS THERE IS NO RESULTS
        df_rt = pd.DataFrame(columns=["source_ip", "dest_ip", "port", "source_port", "dt", "cluster_score", "dns", "delta_mins"])

    if df_mad.empty == False:
        # DNS FLIP & FILTER
        if conf["general"]["ds_type"] == "HTTP File":
            df_mad = df_mad.rename(columns={"dip": "host", "dns": "dip"}).rename(columns={"host": "dns"})
            #df_mad = df_mad.rename(columns={"id.resp_h": "host", "dns": "id.resp_h"}).rename(columns={"host": "dns"})
            #df_mad = df_mad[~df_mad["dns"].isin(df_filter["dns"])]

        #df_mad = df_mad[~df_mad["dip"].isin(df_filter["ip"])]
        df_mad.to_csv("cli_results/{}/mad_results.csv".format(group_id))
    else:
        # CREATE EMPTY DATAFRAME AS THERE IS NO RESULTS
        df_mad = pd.DataFrame(columns=["source_ip", "dest_ip", "port", "mad_score", "connection_count", "dns"])

    if df_delta.empty == False:
        df_delta = df_delta[~df_delta["dip"].isin(df_filter["ip"])]

        if conf["general"]["ds_type"] == "HTTP File":
            df_delta = df_delta.rename(columns={"dip": "host", "dns": "dip"}).rename(columns={"host": "dns"})
            #df_delta = df_delta[~df_delta["dns"].isin(df_filter["dns"])]

        # BUILD TOP TALKER
        df_delta = df_delta.groupby(["sip","dip","port", "dns"]).agg(
            count=("sip", "size"),
            min_time=("datetime","min"),
            max_time=("datetime","max")
        ).rename(columns={"sip": "source_ip", "dip": "dest_ip"}).sort_values("count",ascending=False).reset_index()

        df_delta.to_csv("cli_results/{}/top_talker_results.csv".format(group_id))

    # FINAL AGGREGATE RESULTS
    df_agg = beacon.cli_results(df_rt, df_mad)
    df_agg.to_csv("cli_results/{}/aggregate_results.csv".format(group_id))

    with open("cli_results/{}/run_conf.yaml".format(group_id), "w") as file:
        yaml.dump(config, file, sort_keys=False)

    #####################################################################################
    ##  DELETE BH CREATE FILES
    #####################################################################################

    if config["general"]["ds_type"] == "Delta File":
        "/delta/{}".format(UID)

    logger.debug("Deleting bronze, silver and gold files")

    bz_f = os.path.join(lst_path[0], lst_path[1], "bronze")
    sv_f = os.path.join(lst_path[0], lst_path[1], "silver")
    gd_f = os.path.join(lst_path[0], lst_path[1], "gold")

    # DELETE FILES
    if config["general"]["ds_type"] == "Delta File":
        _delete_folders(["/delta/{}".format(UID),
                         os.path.join(lst_path[0], lst_path[1], "bronze"),
                         os.path.join(lst_path[0], lst_path[1], "silver"),
                         os.path.join(lst_path[0], lst_path[1], "gold")],
                         logger)
    else:
        _delete_folders([os.path.join(lst_path[0], lst_path[1], "bronze"),
                     os.path.join(lst_path[0], lst_path[1], "silver"),
                     os.path.join(lst_path[0], lst_path[1], "gold"),
                     os.path.join(lst_path[0], lst_path[1])],
                     logger)

    endtime = datetime.now() - starttime
    logger.info("Beacon Huntress completed {}".format(endtime))
    logger.info("All export files are located in cli_results/{}".format(group_id))

    # MOVE LOG FILE
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    shutil.move(log_file,"cli_results/{}/{}".format(group_id,log_file_name))

    # RETURN RESULTS DICTIONARY
    return beacon_results

#####################################################################################
##  CLI
#####################################################################################

def cli():

    print(""" ____                                     _   _                _
| __ )   ___   __ _   ___   ___   _ __   | | | | _   _  _ __  | |_  _ __   ___  ___  ___ 
|  _ \  / _ \ / _` | / __| / _ \ | '_ \  | |_| || | | || '_ \ | __|| '__| / _ \/ __|/ __|
| |_) ||  __/| (_| || (__ | (_) || | | | |  _  || |_| || | | || |_ | |   |  __/\__ \\__ \\
|____/  \___| \__,_| \___| \___/ |_| |_| |_| |_| \__,_||_| |_| \__||_|    \___||___/|___/""")

    print("\n")

    while True:
        print("Menu")
        print("="*10)
        print("1. Run Beacon Huntress")
        print("2. Filtered IPs")
        print("3. Results")
        print("4. Quit\n")

        option = int(input("Enter option [1-4]: "))

        if option in [1, 2, 3, 4]:
            break
        else:
            print("\nERROR: Invaild option!\n")

    return option

def cli_run():

    # LOAD BEACON HUNTRESS CONFIG
    conf = _load_config(os.path.join("config", "config.conf"))
    db_conf = _load_config(os.path.join("config", "dashboard.conf"))

    # INPUTS
    raw_log = input("Log file folder location: ")

    while True:
        log_type = int(input("Log file type [1 = Zeek Conn, 2 = HTTP, 3 = Delta File]: "))
        if log_type in [1, 2, 3]:
            break
        else:
            print("Incorrect value! Values must be [1 = Zeek Conn, 2 = HTTP, 3 = Delta File]")

    while True:
        algo = int(input("Algorithm [1 = Quick Cluster Search, 2 = Cluster Search]: "))
        if algo in [1, 2]:
            break
        else:
            print("Incorrect value! Values must be [1 = Quick Cluster Search, 2 = Cluster Search]")

    avg_delta = int(input("Average Delta Time in Minutes: "))
    conn_cnt = int(input("Minimum Callback Count: "))
    minimum_likelihood = int(input("Likelihood Percentage (e.g. 70): "))


    if algo == 1:
        conf["general"]["cluster_type"] = "dbscan_var"
        conf["beacon"]["dbscan_var"]["avg_delta"] = avg_delta
        conf["beacon"]["dbscan_var"]["conn_cnt"] = conn_cnt
        conf["beacon"]["dbscan_var"]["span_avg"] = 15
        conf["beacon"]["dbscan_var"]["variance_per"] = 15
        conf["beacon"]["dbscan_var"]["minimum_likelihood"] = minimum_likelihood
    elif algo == 2:
        conf["general"]["cluster_type"] = "dbscan"
        conf["beacon"]["dbscan"]["minimum_delta"] = avg_delta
        conf["beacon"]["dbscan"]["spans"] = [[0, 5], [2, 15], [15, 35], [30, 60], [60, 120], [480, 1440]]
        conf["beacon"]["dbscan"]["minimum_points_in_cluster"] = conn_cnt
        conf["beacon"]["dbscan"]["minimum_likelihood"] = minimum_likelihood

    ds_name, ds_type = _get_ds_types(log_type)
    conf["general"]["raw_loc"] = raw_log
    conf["general"]["ds_name"] = ds_name
    conf["general"]["ds_type"] = ds_type
    conf["general"]["start_dte"] = ""
    conf["general"]["end_dte"] = ""

    return conf

def cli_filter(option,is_dns):

    df_fil_ips = pd.read_parquet("filter/filtered_ips.parquet")

    if is_dns:
        print("For multiples values use a list (e.g. [microsoft.com, amazon.com])")
    else:
        print("For multiples values use a list (e.g. [127.0.0.1, 255.255.255.255])")

    # SHOW FILTERED IPS
    if option == 3:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
            print(df_fil_ips)
    # ADD OR DELETE VALUES
    else:
        if is_dns:
            vals = input("Enter DNS: ")
        else:
            vals = input("Enter IPs: ")

        # CONVERT TO LIST
        vals = [str(x) for x in vals.strip("[]").split(",")]

        # OPTION 1 IS ADD
        if option == 1:
            opt = "added"
            if isinstance(vals,list):
                for x in vals:
                    if is_dns:
                        new_val = {"dns": x, "ip": ""}
                    else:
                        new_val = {"dns": "", "ip": x}
                    df_fil_ips = pd.concat([df_fil_ips, pd.DataFrame([new_val])], ignore_index=True)
            else:
                print("\nERROR: Invaild Type!\n")

        elif option == 2:
            opt = "deleted"
            if isinstance(vals,list):
                for x in vals:
                    if is_dns:
                        df_fil_ips = df_fil_ips[df_fil_ips["dns"] != x]
                    else:
                        df_fil_ips = df_fil_ips[df_fil_ips["ip"] != x]
            else:
                print("\nERROR: Invaild Type!\n")

        # ADD THE VALUES
        df_fil_ips.to_parquet("filter/filtered_ips.parquet")
        print("Value/s {}!".format(opt))

def cli_results_files(path):
    folders = []
    dates = []

    for dir in os.listdir(path):
        full_dir = os.path.join(path, dir)
        folders.append(dir)
        folder_dte = os.path.getctime(full_dir)
        dates.append(datetime.fromtimestamp(folder_dte))

    df = pd.DataFrame({"Group_ID": folders, "Run_Date": dates})
    df["Run_ID"] = df.index + 1
    df = df[["Run_ID", "Group_ID", "Run_Date"]]
    #df.index.name = "Run_ID"

    return df

def cli_view_results(df_results):


    while True:
        run_id = int(input("Enter Run_ID: "))
        run_guid = df_results.loc[df_results["Run_ID"] == run_id]["Group_ID"].iloc[0]
        while True:
            v_or_d = int(input("View or Delete [1 = View, 2 = Delete]: "))

            if v_or_d == 1:
                break
            elif v_or_d == 2:
                _delete_folders([os.path.join("cli_results",run_guid)])
                print("Results deleted!!")
                return

        option = int(input("Enter result option [1 = Aggregrate, 2 = Clustered Results, 3 = MAD Results, 4 = Top Talker Results, 5 = Run Configuration, 6 = Log File]"))

        # BACKHER
        if option == 1:
            path = os.path.join("cli_results",run_guid,"aggregate_results.csv")
            opt = "Aggregate Results"
            break
        elif option == 2:
            path = os.path.join("cli_results",run_guid,"cluster_results.csv")
            opt = "Cluster Results"
            break
        elif option == 3:
            path = os.path.join("cli_results",run_guid,"mad_results.csv")
            opt = "MAD Results"
            break
        elif option == 4:
            path =  os.path.join("cli_results",run_guid,"top_talker_results.csv")
            opt = "Top Talker Results"
            break
        elif option == 5:
            path = os.path.join("cli_results",run_guid,"run_conf.csv")
            opt = "Run Config"
            break

    if os.path.exists(path):
        df_view = pd.read_csv(path)

        if df_view.empty:
            print("X" * 100)
            print("No Results!!")
            print("X" * 100)
        else:
            with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
                print("X" * 50, f"{opt}", "X" * 50)
                print(df_view.reset_index())
                print("X" * (100 + len(opt)+2))
    else:
        print("X" * 100)
        print("No Results!!")
        print("X" * 100)

#####################################################################################
##  MAIN
#####################################################################################

def main(conf):

    # COMMENTED FOR CLI
    #config = _load_config(conf)

    ret_val = pipeline(conf = conf)

    return ret_val

if __name__ == "__main__":

    while True:
        option = cli()

        #CLI RUN
        if option == 1:
            conf = cli_run()
            main(conf)
        # FILTER
        elif option == 2:
            while True:
                fil_opt = int(input("Enter filter option [1 = Add, 2 = Delete, 3 = View]: "))
                if fil_opt in [1, 2]:
                    while True:
                        fil_type = int(input("Enter filter type [1 = DNS, 2 = IPs]: "))
                        if fil_type in [1,2]:
                            if fil_type == 1:
                                is_dns = True
                            else:
                                is_dns = False
                            break
                    break
                elif fil_opt == 3:
                    is_dns = False
                    break
                elif fil_opt == 0:
                    break
                else:
                    print("Invaild filter option! Must be [1 = Add, 2 = Delete, 3 = View]!")

            if fil_opt != 0:
                cli_filter(fil_opt,is_dns)
        elif option == 3:
            df_results = cli_results_files("cli_results")
            print(df_results.to_string(index=False))

            cli_view_results(df_results)

            #break
        elif option == 4:
            print("\nGoodbye!\n")
            break
        else:
            print("\nERROR: Invaild option!!\n")
