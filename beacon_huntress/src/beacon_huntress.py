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
from datetime import datetime, timedelta
import time
import hashlib
import shutil
import yaml
from pathlib import Path
from progress.bar import Bar
from art import *

#####################################################################################
##  LOGGING
#####################################################################################

log_dir = os.path.join(os.getcwd(),"log")
Path(log_dir).mkdir(parents=True, exist_ok=True)

log_file = os.path.join(log_dir,"log_{}".format(datetime.now().strftime("%Y%m%d")))
logger = logging.getLogger("logger")

if not logger.handlers:
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s:\t%(message)s',datefmt="%m-%d %H:%M:%S")

    # FILE LOG HANDLER
    log_fh = logging.FileHandler(log_file)
    log_fh.setLevel(logging.INFO)
    log_fh.setFormatter(formatter)

    # ADD LOG HANDLERS
    #logger.addHandler(log_basic)
    logger.addHandler(log_fh)
    logger.propagate = False

#####################################################################################
##  IMPORT BEACON HUNTRESS MODULES
#####################################################################################

sys.path.append(os.path.join(os.getcwd(),"bin"))

import ingest
import beacon
import dash

#####################################################################################
##  LOAD CONFIG
#####################################################################################

def _load_config(conf):

    try:
        logger.debug("Opening config {}".format(conf))

        with open(conf) as conf_file:
            config = yaml.safe_load(conf_file)

    except BaseException as err:
        logger.error("Issue with config {}".format(conf))
        logger.error(err)
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

#####################################################################################
##  FUNCTIONS
#####################################################################################

def pipeline(conf):

    logger.info("Beacon Huntress Pipeline Process Started")
    starttime = datetime.now()

    #####################################################################################
    ##  LOAD CONFIGURATION & LOCAL VARIABLES
    #####################################################################################
    
    # LOAD CONFIG
    config = _load_config(conf)
    new_delta = False
    config_hash = hashlib.sha1(json.dumps(config, sort_keys=True).encode()).hexdigest()

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
    ##  CHECK OVERWRITE & REMOVE
    #####################################################################################

    if config["general"]["overwrite"] == True:
        # DELETE BRONZE LAYER
        if os.path.exists(config["general"]["bronze_loc"]):
            shutil.rmtree(config["general"]["bronze_loc"])
        
        # DELETE SILVER LAYER
        if os.path.exists(config["general"]["silver_loc"]):
            shutil.rmtree(config["general"]["silver_loc"])

        # DELETE GOLD LAYER
        if os.path.exists(config["general"]["gold_loc"]):
            shutil.rmtree(config["general"]["gold_loc"])

        # DELETE FILTER LOCATION
        if os.path.exists(config["general"]["filter_loc"]):
            shutil.rmtree(config["general"]["filter_loc"])

    #####################################################################################
    ##  DASHBOARD
    #####################################################################################

    # IF DASHBOARD = TRUE 
    # CLI_RESULTS = FALSE
    if config["dashboard"]["dashboard"] == True:
        print("\t* Dashboard Enabled")
        dash_config = _load_config(config["dashboard"]["conf"])

        # CLEAR BEACON FILTERS
        if dash_config["dashboard"]["clear_beacon_filter"] == True:
            dash.beacon_filter(
                ips = None, 
                f_type = "clear", 
                conf = config["dashboard"]["conf"], 
                verbose = config["general"]["verbose"])  

        # DELETE DASHBOARD DATA (EVERYTIME)
        if config["general"]["overwrite"] == True:
            dash.del_records(
                t_names = ["beacon", "delta", "raw_source", "conf_hash"], 
                conf = config["dashboard"]["conf"], 
                verbose = config["general"]["verbose"])

        cli_return = False
    else:
        cli_return = True

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
    ##  BRONZE LAYER
    #####################################################################################

    if len(os.listdir(config["general"]["raw_loc"])) == 0:
        print("\t* ERROR: {} files located at {}!  Please use another location!".format(len(os.listdir(config["general"]["raw_loc"])), config["general"]["raw_loc"]))
        logger.error("{} files located at {}!  Please use another location!".format(len(os.listdir(config["general"]["raw_loc"])), config["general"]["raw_loc"]))
        sys.exit(1)

    # BUILD BRONZE LAYER
    is_new_bronze = ingest.build_bronze_layer(
        src_loc=config["general"]["raw_loc"], 
        bronze_loc=config["general"]["bronze_loc"],
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
            overwrite = config["general"]["overwrite"],
            verbose = config["general"]["verbose"]
        )

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
            src_loc = config["general"]["filter_loc"],
            delta_file_loc = config["general"]["silver_loc"],
            delta_file_type = config["general"]["file_type"],
            overwrite =  config["general"]["overwrite"]
            )

            new_delta = True
        else:
            print("\t* WARNING: Bronze Files and Filters are the same.  Running with old delta file ({}).".format(config["beacon"]["delta_file"]))
            logger.warning("Bronze Files and Filters are the same.  Running with old delta file ({}).".format(config["beacon"]["delta_file"]))
            new_delta = False

    else:
        # ONLY BUILD A NEW DELTA FILE IF THERE IS A NEW FILTER FILE OR NEW BRONZE FILE
        if is_new_filter == True or is_new_bronze == True:
            # BUILD DELTA FILE
            ingest.build_delta_files(
            src_loc = config["bronze"]["bronze_loc"],
            delta_file_loc = config["general"]["silver_loc"],
            delta_file_type = config["general"]["file_type"],
            overwrite =  config["general"]["overwrite"]
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
            overwrite = config["general"]["overwrite"],
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
                    cli_return = cli_return,
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
                cli_return = cli_return,
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
                    cli_return = cli_return,
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
                cli_return = cli_return,
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
                    cli_return = cli_return,
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
                cli_return = cli_return,
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
                    cli_return = cli_return,
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
                cli_return = cli_return,
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
                    cli_return = cli_return,
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
                    cli_return = cli_return,
                    overwrite = config["general"]["overwrite"],
                    verbose = config["general"]["verbose"]
                )

    # LOAD DB DATA FOR DASHBOARD
    if config["dashboard"]["dashboard"] == True:

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
            overwrite = config["general"]["overwrite"],
            verbose = config["general"]["verbose"]
        )                    

    endtime = datetime.now() - starttime
    logger.info("Beacon Huntress completed {}".format(endtime))
    print("Beacon Huntress completed {}".format(endtime))            

#####################################################################################
##  MAIN
#####################################################################################

def main(conf):

    print("Beacon Huntress starting the hunt!")
    config = _load_config(conf)

    if config["general"]["refresh_rate"] == 0:
        logger.debug("Running a single process")
        logger.debug("Set refresh rate >= 5 to run as a continuous process")
        pipeline(conf = conf)
    elif config["general"]["refresh_rate"] < 5:
        logger.debug("Minimum refresh rate is 5 secs")
        logger.debug("Running a single pipeline instance")
        pipeline(conf = conf)
    else:
        while True:
            pipeline(conf = conf)
            time.sleep(config["general"]["refresh_rate"])

#####################################################################################
##  RUN FROM COMMAND LINE
##  default = os.path.join(os.path.abspath(os.path.join(os.getcwd(),"..")),"config","config.json"))
#####################################################################################

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--conf",
        help = "Pipeline configuration file", 
        default = os.path.join(os.getcwd(),"config", "config.conf")
    )
    
    args = parser.parse_args()
    if not vars(args):
        parser.print_help()
        parser.exit(1)
        sys.exit(1)

    tprint("Beacon Huntress")
    # RUN THE MAIN PROCESS
    main(
        conf = args.conf
        )