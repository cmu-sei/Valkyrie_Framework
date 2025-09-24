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
import argparse
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

    if not dte:
        return ""

    try:
        # CONVERT DTE & TIME (HH:MM:SS)
        fix_dte = datetime.strptime(dte, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # CONVERT DTE & TIME (HH:MM)
            fix_dte = datetime.strptime(dte, "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                # CONVERT JUST DTE
                fix_dte = datetime.strptime(dte, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"Invalid date format: '{dte}'. Expected 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'.")

    dte_utc = fix_dte.replace(tzinfo=timezone.utc)
    dte = int(dte_utc.timestamp())

    return dte

def _get_ds_types(type):

    # if type_id == 1:
    #     ds_name = "Zeek Connection Logs"
    #     ds_type = "Zeek Connection Logs"
    # elif type_id == 2:
    #     ds_name = "HTTP File"
    #     ds_type = "HTTP File"
    # elif type_id == 3:
    #     ds_name = "Delta File"
    #     ds_type = "Delta File"
    # else:
    #     ds_name = ""
    #     ds_type = ""
    if type.lower() in ["c", "conn"]:
        ds_name = "Zeek Connection Logs"
        ds_type = "Zeek Connection Logs"
    elif type.lower() in ["h", "http"]:
        ds_name = "HTTP File"
        ds_type = "HTTP File"
    elif type.lower() in ["d", "delta"]:
        ds_name = "HTTP File"
        ds_type = "HTTP File"
    else:
        ds_name = ""
        ds_type = ""

    return ds_name, ds_type

def _str_arg_bool(val):

    if isinstance(val, bool):
        return val

    if val.lower() in ["yes", "y", "true", "t", "1"]:
        return True
    elif val.lower() in ["no", "n", "false", "f", "0"]:
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected!")

#####################################################################################
##  CLASS
#####################################################################################

class BeaconHuntress:
    """
    Methods
    -------
    run() -> dict
        - Run Beacon Huntress
    """
    def __init__self(self):
        self

    def run(self,
            algo: str,
            log_type: str,
            log_dir: str,
            delta: int,
            call_back: int,
            percent: int,
            spans: list = [[0, 5], [2, 15], [15, 35], [30, 60], [60, 120], [480, 1440]],
            span_avg: int = 15,
            variance: int = 15,
            mad_score: int = 50,
            burst: bool = False,
            burst_pct: int = 300,
            start_dte = '',
            end_dte = '',
            write_file: bool = False,
            write_file_type: str = 'csv',
            zip: bool = False,
            verbose: bool = False,
            show_results: bool = False):
        """
        Run Beacon Huntress

        Parameters
        -----------
        **algo**: str
            Beacon Algorithm
            - Quick Cluster Search = q or quick
            - Cluster Search = c or cluster
            - Agglomerative Clustering = a or agg
        **log_type**: str
            Log File Type
            - Zeek Connection = conn or c
            - Http = http or h
            - Delta File = delta or d
        **log_dir**: str
            Raw Log Directory
            - Example: '/tutorial'
        **delta**: int
            Average Delta time in minutes
            - Example: 25
        **call_back**: int
            Number of Beacon Callbacks
            - Example: 10
        **percent**: int
            Likelihood Percentage Filter *ONLY CLUSTERING ALGOS*
            - Example: 85
        **spans**: list
            Spans you wish to search in list format. Minimum number of delta records to search using your delta column. *ONLY CLUSTER SEARCH (c/cluster)*
            - Example: [[0, 5], [2, 15], [15, 35], [30, 60], [60, 120], [480, 1440]]
            - Default: [[0, 5], [2, 15], [15, 35], [30, 60], [60, 120], [480, 1440]]
        **span_avg**: int
            The percentage to increase and decrease from the connections total delta span *ONLY QUICK CLUSTER SEARCH ONLY (q/quick).
            - Example: 15
                - 15 will decrease 15% from the minimum and maximum delta span.
            - Default: 15
        **variance**: int
            The amount of allowed variance or jitter in percentage *ONLY QUICK CLUSTER SEARCH (q/quick)*
            - Default: 15
        **mad_score**: int
            Median Absolute Deviation (MAD) score filter. The minmuim percentage to show the results. Enter as integer value.
            - Default: 50
        **burst**: boolean
            Run the Burst algorithm. Burst algorithm is based on the mean change in connections per delta minute.
            - Default: False
        **burst_pct**: int
            The Burst percentage needed for Burst Report. Burst percentage is calculated based on the mean change in connections per delta minute. Enter as integer value.
            - Default: 300
        **start_dte**:
            Start Date for filters. Date or datetime in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' or blank('') for no filter.
            - Default: ''
        **end_dte**:
            End Date for filters. Date or datetime in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' or blank('') for no filter.
            - Default: ''
        **write_file**: bool
            Write results to files (True/False)
            - Default: False
        **write_file_type**: str
            Write results files as either CSV or Parquet
            - Default: CSV
        **zip**: bool
            Log/s are zip files (True/False)
            - Default: False"
        **verbose**: bool
            Enable Verbose logging (True/False)
            - Default: False
        **show_results**: bool
            Show results (True/False)
            - Default: True

        Returns
        -------
        dict
            Beacon Huntress results as a dictionary
        """
        val = pipeline(algo,
                       log_type,
                       log_dir,
                       delta,
                       call_back,
                       percent,
                       spans,
                       span_avg,
                       variance,
                       mad_score,
                       burst,
                       burst_pct,
                       start_dte,
                       end_dte,
                       write_file,
                       write_file_type,
                       zip,
                       verbose,show_results
                       )

        return val

#####################################################################################
##  FUNCTIONS
#####################################################################################


def parse_arg_date(dte):

    if dte == "":
        return ""

    for fmt_dte in ('%Y-%m-%d %H:%M', '%Y-%m-%d'):
        try:
            return datetime.strptime(dte,fmt_dte)
        except ValueError:
            continue

    raise argparse.ArgumentTypeError(
        "Invalid date/time: '{}'. Expected 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' or blank.".format(dte)
    )

def write_results(df,group_id,write_file,file_name,write_file_type):

    # WRITE FILE
    if write_file:
        if write_file_type.lower() == "parquet":
            df.to_parquet("cli_results/{}/{}.parquet".format(group_id,file_name))
        else:
            df.to_csv("cli_results/{}/{}.csv".format(group_id,file_name))

def pipeline(algo,log_type,log_dir,delta,call_back,percent,spans,span_avg,variance,mad_score,burst,burst_pct,start_dte,end_dte,write_file,write_file_type,zip,verbose,show_results):

    # Return Dictionary
    beacon_results = {}

    #####################################################################################
    ##  SET DEFAULTS
    #####################################################################################

    config = {}

    for x in ["general", "filter", "dashboard", "beacon", "bronze", "zip"]:
        config[x] = {}

        if x == "filter":
            config[x]["port"] = {}

    config["general"]["filter"] = True
    config["general"]["file_type"] = "parquet"
    config["general"]["overwrite"] = False
    config["filter"]["port"]["exclude"] = False
    config["filter"]["port"]["filter"] = [80, 443]
    config["dashboard"]["dashboard"] = False
    config["bronze"]["dns_file"] = ""
    config["beacon"]["delta_file"] = "latest"
    config["beacon"]["delta_column"] = "delta_mins"

    for x in ["source_ip", "dest_ip", "source_dns","dest_dns","dns_match"]:
        config["filter"][x] = {}
        config["filter"][x]["exclude"] = True
        config["filter"][x]["filter"] = []

    # DISABLE DASHBOARD
    dash_config = {}
    dash_config["dashboard"] = {}
    dash_config["db"] = {}

    dash_config["dashboard"]["last_gold_file"] = False
    dash_config["dashboard"]["clear_beacon_filter"] = False
    dash_config["db"]["build_at_startup"] = True
    dash_config["db"]["file_loc"] = "latest"
    dash_config["db"]["drop"] = False

    #####################################################################################
    ##  LOAD RUN SETTINGS
    #####################################################################################

    ds_name, ds_type = _get_ds_types(log_type)

    config["general"]["raw_loc"] = log_dir
    config["general"]["ds_name"] = ds_name
    config["general"]["ds_type"] = ds_type
    config["general"]["mad_score"] = mad_score
    config["general"]["start_dte"] = str(start_dte)
    config["general"]["end_dte"] = str(end_dte)
    config["general"]["verbose"] = verbose
    config["zip"]["unzip"] = zip
    config["zip"]["zip_loc"] = log_dir

    if algo.lower() in ["q", "quick"]:
        config["beacon"]["dbscan_var"] = {}
        config["general"]["cluster_type"] = "dbscan_var"
        config["beacon"]["dbscan_var"]["avg_delta"] = delta
        config["beacon"]["dbscan_var"]["conn_cnt"] = call_back
        config["beacon"]["dbscan_var"]["span_avg"] = span_avg
        config["beacon"]["dbscan_var"]["variance_per"] = variance
        config["beacon"]["dbscan_var"]["minimum_likelihood"] = percent
    elif algo.lower() in ["c", "cluster"]:
        config["general"]["cluster_type"] = "dbscan"
        config["beacon"]["dbscan"] = {}
        config["beacon"]["dbscan"]["minimum_delta"] = delta
        config["beacon"]["dbscan"]["spans"] = spans
        config["beacon"]["dbscan"]["minimum_points_in_cluster"] = call_back
        config["beacon"]["dbscan"]["minimum_likelihood"] = percent

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

    # LOGGER LEVELS
    logger = logging.getLogger("logger")

    if config["general"]["verbose"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s:\t%(message)s',datefmt="%m-%d %H:%M:%S")

    if write_file:
        # FILE LOG HANDLER
        log_fh = logging.FileHandler(log_file)
        log_fh.setFormatter(formatter)

        # ADD LOG HANDLER
        logger.addHandler(log_fh)
        logger.propagate = False

    #####################################################################################
    ##  LOAD CONSTANTS & LOCAL VARIABLES
    #####################################################################################

    logger.debug("Step 1: Create Beacon Group")

    # RUN BEACON GROUP UUID
    UID = uuid.uuid4()

    beacon_results["beacon_group"] = UID

    logger.info("Beacon Huntress starting the hunt!")
    starttime = datetime.now()

    # DELTA & CONFIG HASH
    new_delta = False
    config_hash = hashlib.sha1(json.dumps(config, sort_keys=True).encode()).hexdigest()

    #CLI SPECIFIC
    group_id = UID

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
                ds_type =  config["general"]["ds_type"],
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
            ds_type =  config["general"]["ds_type"],
            overwrite =  config["general"]["overwrite"]
            )

            new_delta = False
        else:
            # ONLY BUILD A NEW DELTA FILE IF THERE IS A NEW FILTER FILE OR NEW BRONZE FILE
            # BACKHERE
            if is_new_filter == True or is_new_bronze == True:
                # BUILD DELTA FILE
                ingest.build_delta_files(
                src_loc = config["general"]["bronze_loc"],
                delta_file_loc = config["general"]["silver_loc"],
                delta_file_type = config["general"]["file_type"],
                ds_type =  config["general"]["ds_type"],
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

        #####################################################################################
        ##  BEACONS
        #####################################################################################

        # PLACE HOLDER FOR FINAL CONNECTION COUNT
        final_conn_count = 1

        # AGGLOMERATIVE CLUSTERING
        if config["general"]["cluster_type"] == "agg":

            # NO DASHBOARD FOR CLI
            if config["dashboard"]["dashboard"] == True:
                logger.warning("Dashboard is not available for CLI version!")
                config["dashboard"]["dashboard"] == False

            # ALGO FILTERS
            likelihood = (config["beacon"]["agg"]["cluster_factor"] / 100)
            final_conn_count = config["beacon"]["agg"]["min_records"]

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

            # NO DASHBOARD FOR CLI
            if config["dashboard"]["dashboard"] == True:
                logger.warning("Dashboard is not available for CLI version!")
                config["dashboard"]["dashboard"] == False

            # ALGO FILTERS
            likelihood = (config["beacon"]["dbscan"]["minimum_likelihood"] / 100)
            final_conn_count = config["beacon"]["dbscan"]["minimum_points_in_cluster"]

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

            # NO DASHBOARD FOR CLI
            if config["dashboard"]["dashboard"] == True:
                logger.warning("Dashboard is not available for CLI version!")
                config["dashboard"]["dashboard"] == False

            # ALGO FILTERS
            likelihood = (config["beacon"]["dbscan_var"]["minimum_likelihood"] / 100)
            final_conn_count = config["beacon"]["dbscan_var"]["conn_cnt"]

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

            # NO DASHBOARD FOR CLI
            if config["dashboard"]["dashboard"] == True:
                logger.warning("Dashboard is not available for CLI version!")
                config["dashboard"]["dashboard"] == False

            # ALGO FILTERS
            final_conn_count = config["beacon"]["by_packet"]["conn_cnt"]

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

            # NO DASHBOARD FOR CLI
            if config["dashboard"]["dashboard"] == True:
                logger.warning("Dashboard is not available for CLI version!")
                config["dashboard"]["dashboard"] == False

            # ALGO FILTERS
            final_conn_count = config["beacon"]["by_conn_group"]["conn_cnt"]

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
        ## MEDIAN ABSOLUTE DEVIATION OF THE MEAN OF OBSERVATIONS MEANS
        ###########################################################

        logger.info("Running MAD algorithm")

        mad_score = config["general"]["mad_score"] / 100
        df_mad = mm.run_mad(max_delta_file, mad_score)

        if df_mad.empty:
            logger.warning("No results for Median Absolute Deviation!")

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
        max_delta_file = None

    #####################################################################################
    ##  Running Burst Algorithm
    #####################################################################################

    if burst:
        logger.info("Running Burst algorithm")

        df_burst = beacon.burst_algo(max_delta_file,burst_pct,ds_type)

        if df_burst.empty:
            logger.warning("No results for Burst algorithm!")
    else:
        df_burst = pd.DataFrame()
        logger.debug("Burst algorithm skipped")

    #####################################################################################
    ##  FINAL RESULTS
    #####################################################################################

    logger.info("Gathering final results!")

    # GET FILTERS
    df_filter = pd.read_parquet("filter/filtered_ips.parquet")

    # CREATE CLI RESULTS DIRECTORY IF NECESSARY
    if write_file:
        Path("cli_results/{}".format(group_id)).mkdir(parents=True, exist_ok=True)

    # GET RESULTS
    if max_delta_file is None:
        if show_results:
            print("X" * 50, " POTENTIAL BEACONS (0)", "X" * 50)
            print("NONE")
            print("X" * 121)
    else:
        # GET DELTA FOR TOP TALKER
        df_delta = pd.read_parquet(max_delta_file)

        # WRITE FILES IF YOU HAVE RESULTS
        if df_rt.empty == False:
            # DNS FLIP & FILTER
            if config["general"]["ds_type"] == "HTTP File":
                df_rt = df_rt.rename(columns={"id.resp_h": "host", "dns": "id.resp_h"}).rename(columns={"host": "dns"})

            # WRITE FILE
            write_results(df_rt,group_id,write_file,"cluster_results",write_file_type)

        else:
            # CREATE EMPTY DATAFRAME AS THERE IS NO RESULTS
            df_rt = pd.DataFrame(columns=["source_ip", "dest_ip", "port", "source_port", "dt", "cluster_score", "dns", "delta_mins"])

        if df_mad.empty == False:
            # FILTER BASED UPON THE USERS FINAL CONNECTION COUNT
            df_mad = df_mad[df_mad["conn_count"] >= final_conn_count]

            # DNS FLIP & FILTER
            if config["general"]["ds_type"] == "HTTP File":
                df_mad = df_mad.rename(columns={"dip": "host", "dns": "dip"}).rename(columns={"host": "dns"})

            # WRITE FILE
            write_results(df_mad,group_id,write_file,"mad_results",write_file_type)
        else:
            # CREATE EMPTY DATAFRAME AS THERE IS NO RESULTS
            df_mad = pd.DataFrame(columns=["source_ip", "dest_ip", "port", "mad_score", "connection_count", "dns"])

        if df_delta.empty == False:
            df_delta = df_delta[~df_delta["dip"].isin(df_filter["ip"])]

            if config["general"]["ds_type"] == "HTTP File":
                df_delta = df_delta.rename(columns={"dip": "host", "dns": "dip"}).rename(columns={"host": "dns"})

            # BUILD TOP TALKER
            df_delta = df_delta.groupby(["sip","dip","port", "dns"]).agg(
                count=("sip", "size"),
                min_time=("datetime","min"),
                max_time=("datetime","max")
            ).rename(columns={"sip": "source_ip", "dip": "dest_ip"}).sort_values("count",ascending=False).reset_index()

            beacon_results["top_talkers"] = df_delta.head(30).to_dict(orient="records")

            # WRITE FILE
            write_results(df_delta,group_id,write_file,"top_talker_results",write_file_type)

        if df_burst.empty:
            beacon_results["burst"] = {}

            if burst == False:
                logger.warning("No results for Burst algorithm!")
        else:
            beacon_results["burst"] = df_burst.to_dict(orient="records")

        # FINAL AGGREGATE RESULTS
        df_agg = beacon.cli_results(df_rt, df_mad, final_conn_count, display_results=show_results)

        # WRITE FILE
        write_results(df_agg,group_id,write_file,"top_talker_results",write_file_type)

    # RUN CONFIG
    # WRITE FILE
    if write_file:
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

    # BACKHERE
    df_rt = beacon.cli_add_mad_scr(df_rt, df_mad)

    # RETURN RESULTS DICTIONARY
    beacon_results["results"] = df_rt.to_dict(orient="records")

    # WRITE FILE (LOG & MESSAGE)
    if write_file:
        logger.info("All export files are located in cli_results/{}".format(group_id))
        beacon_results["results_dir"] = "cli_results/{}".format(group_id)

    # CLOSE HANDLER
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    # MOVE LOG FILE
    if write_file:
        shutil.move(log_file,"cli_results/{}/{}".format(group_id,log_file_name))

    return beacon_results

#####################################################################################
##  MAIN
#####################################################################################

def main(algo,log_type,log_dir,delta,call_back,percent,spans,span_avg,variance,mad_score,burst,burst_pct,start_dte,end_dte,write_file,write_file_type,zip,verbose,show_results):

    # RUN VIA ARGS
    ret_val = pipeline(algo,
                       log_type,
                       log_dir,
                       delta,
                       call_back,
                       percent,
                       spans,
                       span_avg,
                       variance,
                       mad_score,
                       burst,
                       burst_pct,
                       start_dte,
                       end_dte,
                       write_file,
                       write_file_type,
                       zip,
                       verbose,
                       show_results)

    return ret_val

# RUN VIA ARGS
if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Beacon Huntress Help Menu")

    parser.add_argument("-a", "--algo",type=str,
        help = "Beacon Algorithm \nQuick Cluster Search = q or quick\nCluster Search = c or cluster\nAgglomerative Clustering = a or agg\n"
    )
    parser.add_argument("-lt", "--log_type",type=str,
        help = "Log File Type \nZeek Connection = conn or c\nHttp = http or h\nDelta File = delta or d"
    ),
    parser.add_argument("-ld", "--log_dir",type=str,
        help = "Log Directory \nExample: --log_dir '/tutorial'"
    ),
    parser.add_argument("-d", "--delta",type=int,
        help = "Average Delta time in minutes \nExample: 25"
    ),
    parser.add_argument("-c", "--call_back", type=int,
        help = "Number of Beacon Callbacks\nExample: --call_back 10"
    ),
    parser.add_argument("-p", "--percent", type=int,
        help = "Likelihood Percentage Filter (Clustering Only)\nExample: --percent 85"
    ),
    parser.add_argument("-s", "--spans", type=list, default=[[0, 5], [2, 15], [15, 35], [30, 60], [60, 120], [480, 1440]],
        help = "CLUSTER SEARCH ONLY(c/cluster) Spans you wish to search, in list format. Minimum number of delta records to search using your delta column.\nEnter spans as a list \nExample: [[0, 5], [2, 15], [15, 35], [30, 60], [60, 120], [480, 1440]]"
    ),
    parser.add_argument("-sa", "--span_avg", type=int, default=15,
        help = "QUICK CLUSTER SEARCH ONLY(q/quick) The percentage to increase and decrease from the connections total delta span.\nExample: 15\n15 will decrease 15%% from the minimum and maximum delta span.\nDefault: 15"
    ),
    parser.add_argument("-vp", "--variance", type=int, default=15,
        help = "QUICK CLUSTER SEARCH ONLY(q/quick) The amount of allowed variance or jitter in percentage.\nDefault: 15"
    ),
    parser.add_argument("-ms", "--mad_score", type=int, default=50,
        help = "Median Absolute Deviation (MAD) score filter. The minmuim percentage to show the results. Enter as integer value.\nDefault: 50"
    ),
    parser.add_argument("-b", "--burst", type=_str_arg_bool, default=False,
        help="Run Burst algorithm (True/False)\nDefault: False"
    )
    parser.add_argument("-bp", "--burst_pct", type=int, default=300,
        help = "The Burst percentage needed for Burst Report. Burst percentage is calculated based on the mean change in connections per delta minute. Enter as integer value.\nDefault: 300"
    ),
    parser.add_argument("-sd", "--start_dte",
        type=parse_arg_date,
        default='',
        help="Start Date for filters\nDate or datetime in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM', or blank('').\nDefault: ''"
    ),
    parser.add_argument("-ed", "--end_dte",
        type=parse_arg_date,
        default='',
        help="End Date for filters\nDate or datetime in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM', or blank('').\nDefault: ''"
    ),
    parser.add_argument("-wf", "--write_file", type=_str_arg_bool, default=True,
        help="Write results to files (True/False)\nDefault: True"
    ),
    parser.add_argument("-wt", "--write_file_type", type=str, default='csv',
        help="Write results to files (True/False)\nDefault: CSV"
    ),
    parser.add_argument("-z", "--zip", type=_str_arg_bool, default=False,
        help="Log/s zip files (True/False)\nDefault: False"
    ),
    parser.add_argument("-v", "--verbose", type=_str_arg_bool, default=False,
        help="Enable Verbose logging (True/False)\nDefault: False"
    ),
    parser.add_argument("-sr", "--show_results", type=_str_arg_bool, default=True,
        help="Show results (True/False)\nDefault: True"
    )

    args = parser.parse_args()
    if not vars(args):
        parser.print_help()
        parser.exit(1)
        sys.exit(1)

    main(algo = args.algo,
         log_type = args.log_type,
         log_dir = args.log_dir,
         delta = args.delta,
         call_back = args.call_back,
         percent = args.percent,
         spans = args.spans,
         span_avg = args.span_avg,
         variance = args.variance,
         mad_score = args.mad_score,
         burst = args.burst,
         burst_pct = args.burst_pct,
         start_dte = args.start_dte,
         end_dte = args.end_dte,
         write_file = args.write_file,
         write_file_type = args.write_file_type,
         zip = args.zip,
         verbose = args.verbose,
         show_results = args.show_results)
