'''
Valkyrie Framework
Copyright 2023 Carnegie Mellon University.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
DM23-0210
'''

import string
import sys
import os
import logging
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import time
from progress.bar import Bar


#####################################################################################
##  LOGGING
#####################################################################################

logger = logging.getLogger("logger")

if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s %(levelname)s:\t%(message)s',datefmt="%m-%d %H:%M:%S")
    logger.setLevel(logging.INFO)
    log_basic = logging.StreamHandler()
    log_basic.setLevel(logging.INFO)
    log_basic.setFormatter(formatter)
    logger.addHandler(log_basic)

#####################################################################################
##  CONSTAINTS
#####################################################################################

DB_CONF = os.path.join(os.path.abspath(os.path.join(os.getcwd(),"..")),"config","dashboard.conf")

def _config_hash(conf = DB_CONF, conf_hash = "", option = "get"):

    from sqlalchemy import create_engine
    import json

    starttime = datetime.now()
    logger.info("Deleting dashboard records from local db")

    try:
        logger.debug("Opening config {}".format(conf))

        with open(conf) as conf_file:
            conf_data = yaml.safe_load(conf_file)

    except BaseException as err:
        logger.error("Issue with config {}".format(conf))
        logger.error(err)

    #####################################################################################
    ##  
    #####################################################################################    

    my_conn = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(conf_data["conn"]["user"], conf_data["conn"]["pwd"], conf_data["conn"]["host"], conf_data["conn"]["port"], conf_data["conn"]["db"]))

    if option == "get":
        query = "select conf_hash from conf_hash where conf_hash = '{}'".format(conf_hash)
        rows = my_conn.connect().execute(query).fetchall()
        
        if len(rows) > 0:
            ret_val = True
        else:
            ret_val = False

    elif option == "add":
        query = "delete from conf_hash"
        my_conn.connect().execute(query)

        query = "insert into conf_hash(conf_hash) values ('{}')".format(conf_hash)
        my_conn.connect().execute(query)

        ret_val = None

    return ret_val

def add_records(file_loc, conf = DB_CONF, verbose = False):
    '''
    Add values from a pandas dataframe into a mysql db to be used for a Grafana dashboard. Source files must be in parquet format.\n

    Parameters:
        file_loc - Source gold file. File must be parquest.\n
        conf - DB configuration file location. File must be json format.\n
            default = ../conf/mysql.json\n
        drop - Drop the table and recreate prior to inserting the data. True or False (case-sensistive).
            default = False\n
        verbose - Verbose logger.  True or False (case-sensistive). \n
            default = False

    Returns
        Nothing
    '''
    from sqlalchemy import create_engine
    import json

    starttime = datetime.now()
    logger.info("Loading dashboard records to local db")

    try:
        logger.debug("Opening config {}".format(conf))

        with open(conf) as conf_file:
            conf_data = yaml.safe_load(conf_file)

    except BaseException as err:
        logger.error("Issue with config {}".format(conf))
        logger.error(err)

    if conf_data["db"]["drop"] == True:
        exist = "replace"
    else:
        exist = "append"

    #####################################################################################
    ##  FAST LOAD OLD CODE KEEP FOR NOW
    ##
    ##  IF LOAD_TYPE == "FAST":
    ##  COLUMNS = ','.JOIN([STR(I) FOR I IN LIST(DF.COLUMNS)])
    ##  VALS = ','.JOIN([STR(I) FOR I IN LIST(DF.TO_RECORDS(INDEX=FALSE))])
    ##  QUERY = "INSERT IGNORE INTO `{}` ({}) VALUES {}".FORMAT(FILE_TYPE,COLUMNS,VALS)   
    ##  MY_CONN.CONNECT().EXECUTE(QUERY)  
    #####################################################################################    

    my_conn = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(conf_data["conn"]["user"], conf_data["conn"]["pwd"], conf_data["conn"]["host"], conf_data["conn"]["port"], conf_data["conn"]["db"]))

    for x in file_loc:

        logger.debug("Loading file {}".format(x))
        
        # LOAD BEACON DATA
        if "beacon" in os.path.basename(x):
            df = pd.read_parquet(x)
            file_type = "beacon"

            if len(df) > 0:
                logger.debug("Loading {} data".format(file_type))
                del_records(t_names = [file_type], conf = conf, verbose = verbose)

                df.rename(columns={"id.orig_h": "source_ip", "id.resp_h": "dest_ip", "id.resp_p": "port", "id.orig_p": "source_port", "datetime": "dt"}, inplace = True)

                # CREATE FINAL DATAFRAME
                # MIGHT NEED TO ADD BACK IN "resp_p", "s_dns", "d_dns", "delta_ms"
                final_df = df[["uid", "orig_bytes", "source_ip" , "source_port", "port", "dest_ip", "local_resp", "missed_bytes", "orig_pkts",
                "orig_ip_bytes", "community_id", "ts", "proto", "duration", "resp_ip_bytes", "local_orig", "service",
                "resp_pkts", "history", "resp_bytes", "conn_state", "source_file", "src_row_id",
                "delta_mins", "dt"]]
                
                final_df.to_sql(con = my_conn, name = file_type, if_exists = exist, index = False, chunksize= 50000)
            else:
                logger.debug("Nothing to load for {}".file_type)

        # LOAD DELTA DATA
        elif "delta" in os.path.basename(x):
            df = pd.read_parquet(x)
            file_type = "delta"        

            if len(df) > 0:
                logger.info("Loading {} data".format(file_type))
                del_records(t_names = [file_type], conf = conf, verbose = verbose)

                df.rename(columns={"id.orig_h": "source_ip", "id.resp_h": "dest_ip", "id.resp_p": "port", "id.orig_p": "source_port", "datetime": "dt"}, inplace = True)
                
                # CREATE FINAL DATAFRAME
                final_df = df[["connection_id", "sip", "dip", "port", "proto", "dt" , "delta_ms", "delta_mins", "source_file", "src_row_id"]]                           

                final_df.to_sql(con = my_conn, name = file_type, if_exists = exist, index = False, chunksize= 50000)   
            else:
                logger.debug("Nothing to load for {}".file_type)                
        
        # LOAD RAW DATA
        else:
            df = pd.read_parquet(x)
            file_type = "raw_source"        

            if len(df) > 0:
                logger.info("Loading {} data".format(file_type))
                del_records(t_names = [file_type], conf = conf, verbose = verbose)

                df_cnt = df['source_file'].value_counts()
                df_2 = pd.DataFrame(df_cnt).reset_index()
                df_2.rename(columns={"source_file": "count", "index": "source_file"}, inplace = True)

                # CREATE FINAL DATAFRAME
                final_df = df_2[["source_file", "count"]]                  

                final_df.to_sql(con = my_conn, name = file_type, if_exists = exist, index = False, chunksize= 50000)
            else:
                logger.debug("Nothing to load for {}".file_type)                

    # CLOSE ENGINE
    my_conn.dispose()

    endtime = datetime.now() - starttime
    logger.info("Dashboard data added")
    logger.info("Total runtime {}".format(endtime))

def del_records(t_names, conf = DB_CONF, verbose = False):
    '''
    Delete all records from a mysql table that are used for a Grafana dashboard. Truncate command is used. Truncate is not a logged operation.\n

    Parameters:
        t_name - Table names of tables you wish to delete all records from.  All option will only delete available table options.\n
            options\n
            =======\n
            all\n
            beacon\n
            conf_hash\n
            delta\n
            raw_source\n
        conf - DB configuration file location. File must be json format.\n
            default = ../conf/mysql.json\n
        verbose - Verbose logger.  True or False (case-sensistive). \n
            default = False

    Returns
        Nothing
    '''

    from sqlalchemy import create_engine
    import json

    starttime = datetime.now()
    logger.info("Deleting dashboard records from local db")

    try:
        logger.debug("Opening config {}".format(conf))

        with open(conf) as conf_file:
            conf_data = yaml.safe_load(conf_file)

    except BaseException as err:
        logger.error("Issue with config {}".format(conf))
        logger.error(err)

    #####################################################################################
    ##  
    #####################################################################################    

    my_conn = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(conf_data["conn"]["user"], conf_data["conn"]["pwd"], conf_data["conn"]["host"], conf_data["conn"]["port"], conf_data["conn"]["db"]))

    for x in t_names:

        if x in ["beacon", "conf_hash", "delta", "raw_source"]:
            logger.debug("Truncate table data {}".format(x))

            my_conn.execute("truncate table {}".format(x))
        else:
            logger.warning("Cannot delete {} as it is not an available option".format(x))

    # CLOSE ENGINE
    my_conn.dispose()

    endtime = datetime.now() - starttime
    logger.info("Dashboard data removed")
    logger.info("Total runtime {}".format(endtime))    

def beacon_filter(ips = None, f_type = "add", conf = DB_CONF, verbose = False ):
    '''
    Add/Remove record to filter a beacon in the Grafana Dashboard.\n

    Parameters:
        ips - IPs you wish to un/filter in list format.\n
            default = None
        f_type - Filter type options.\n
            options\n
            =======\n
            add\n
            clear\n
            del\n

            default = add\n
        conf - DB configuration file location. File must be json format.\n
            default = ../conf/mysql.json\n
        verbose - Verbose logger.  True or False (case-sensistive). \n
            default = False

    Returns
        Nothing
    '''
    from sqlalchemy import create_engine
    import json

    starttime = datetime.now()
    logger.info("{} option for ip/s {}".format(f_type, ips))

    try:
        logger.debug("Opening config {}".format(conf))

        with open(conf) as conf_file:
            #conf_data = json.load(conf_file)
            conf_data = yaml.safe_load(conf_file)

    except BaseException as err:
        logger.error("Issue with config {}".format(conf))
        logger.error(err)

    #####################################################################################
    ##  
    #####################################################################################   

    if ips == None:
        ips = []

    t_name = "beacon_filter"

    my_conn = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(conf_data["conn"]["user"], conf_data["conn"]["pwd"], conf_data["conn"]["host"], conf_data["conn"]["port"], conf_data["conn"]["db"]))

    if f_type == "add":
        for x in ips:
            my_conn.execute("insert ignore into {} (ip) value ('{}')".format(t_name,x))
    elif f_type == "del":
        for x in ips:
            my_conn.execute("delete from {} where ip = '{}'".format(t_name,x))
    elif f_type == "clear":
        logger.debug("Truncate table data {}".format(t_name))

        my_conn.execute("truncate table {}".format(t_name))

def load_dashboard(file_loc, dash_config, dash_type, is_new = False, overwrite = False, verbose = False):

    # DELETE DASHBOARD DATA OR SKIP ALREADY LOADED DATA
    if dash_type == "raw_source" or dash_type == "all":
        if is_new == False and overwrite != True:
            logger.warning("No new bronze data to add to dashboard")
        else:
            bar = Bar("\t* Loading Dashboard (Bronze)", max=2, suffix="%(elapsed_td)s")
            bar.next()

            add_records(
                file_loc = file_loc,
                conf = dash_config,
                verbose = verbose
                )
            bar.next()            
            bar.finish()
    
    elif dash_type == "delta" or dash_type == "all":
        if is_new == False and overwrite != True:
            logger.warning("No new delta data to add to dashboard")
        else:
            bar = Bar("\t* Loading Dashboard (Delta)", max=2, suffix="%(elapsed_td)s")
            bar.next()
            add_records(
                file_loc = file_loc,
                conf = dash_config,
                verbose = verbose
                )
            bar.next()
            bar.finish()

    elif dash_type == "beacon" or dash_type == "all":
        if is_new == False and overwrite != True:
            logger.warning("No new beacon data to add to dashboard")        
        else:
            # DELETE DASHBOARD DATA
            bar = Bar("\t* Loading Dashboard (Gold/Beacons)", max=3, suffix="%(elapsed_td)s")
            bar.next()                
            del_records(
                t_names = ["beacon"], 
                conf = dash_config, 
                verbose = verbose
                )

            # NO GOLD FILE FINISH
            # GOLD FILE CONTINUE THE PROCESS
            if file_loc == None or file_loc == "":
                logger.warning("No gold file!")
                bar.next()
                bar.next()
                bar.finish()
            else:
                # ALL BEACON DATA
                bar.next()
                add_records(
                    file_loc = [file_loc],
                    conf = dash_config,
                    verbose = verbose)
                bar.next()
                bar.finish()            