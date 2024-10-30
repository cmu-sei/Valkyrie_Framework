'''
Valkyrie Framework
Copyright 2023 Carnegie Mellon University.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
DM23-0210
'''

import os
import logging
import pandas as pd
import yaml
from datetime import datetime
from sqlalchemy import create_engine
import json
import platform
from pathlib import Path

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

def _get_parent_dir(path, levels=1):

    for x in range(levels):
        path = os.path.dirname(path)

    return path

#####################################################################################
##  CONSTAINTS, LOADING CONFIG AND SETTING CONNECTION STRING
#####################################################################################

CONF = os.path.join(_get_parent_dir(os.path.abspath(__file__),2),"config","dashboard.conf")

#####################################################################################
##  
#####################################################################################

def get_conn_str(conf = CONF, conf_hash = "", option = "get"):

    starttime = datetime.now()

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

    return my_conn

def data_to_json(df):
    # CONVERT TO 
    #df_json = df.to_json(orient="records", lines=True)
    df_json = df.to_json(orient="records")
    df_json = json.loads(df_json)

    return df_json

def get_data(type,value = None):
    
    #####################################################################################
    ##  
    #####################################################################################    

    my_conn = get_conn_str(CONF)

    if type == "group":
        df = pd.read_sql("select * from vw_beacon_group order by dt desc;", my_conn)
    elif type == "filtered_beacons":
        df = pd.read_sql("select * from vw_filtered_beacons", my_conn)
    elif type == "data_sources":
        if value == None:
            df = pd.read_sql("select * from vw_datasources", my_conn)
        else:
            df = pd.read_sql("select * from vw_datasources where rowid = {}".format(value), my_conn)
    elif type == "data_type":
        df = pd.read_sql("select * from ds_type order by ds_type", my_conn)
    else:
        if value == None:
            df = pd.read_sql("select * from vw_beacon", my_conn)
        else:
            df = pd.read_sql("select * from vw_beacon where uid = '{}'".format(value), my_conn)

    return df

def add_data(type,value=None):
    
    my_conn = get_conn_str(CONF)

    if type == "beacon":
        query = "insert into beacon_filter (ip) values('{}')".format(value)
        my_conn.connect().execute(query)
    elif type == "dns":
        query = "insert into dns (ip,dns) values('{}','{}')".format(value[0],value[1])
        my_conn.connect().execute(query)
    elif type == "ds":
        query = "insert into datasource (ds_name,ds_type_id,data) values('{}','{}','{}')".format(value[0],value[1],value[2])
        my_conn.connect().execute(query)

    return None

def del_data(type,value=None):
        
    my_conn = get_conn_str(CONF)

    table_lst = ["delta", "raw_source", "beacon_run_conf", "beacon_log", "beacon", "beacon_group"]

    if type == "detail" and value == "all":
        my_conn.connect()

        for x in table_lst:
            query = "delete from {}".format(x)
            my_conn.execute(query)

    elif type == "detail":
        my_conn.connect()

        for x in table_lst:
            if x == "beacon_group" or x == "beacon_run_conf":
                query = "delete from {} where uid = '{}'".format(x,value)
                my_conn.execute(query)
            else:
                query = "delete from {} where group_id in (select distinct group_id from beacon_group where uid = '{}')".format(x,value)
                my_conn.execute(query)

    elif type == "beacon":
        query = "delete from beacon_filter where ip = '{}'".format(value)
        my_conn.connect().execute(query)

    elif type == "data_source":
        if int(value) != 1:
            query = "delete from datasource where rowid = {}".format(value)
            my_conn.connect().execute(query)

    return None

def del_logfile(request,dir):
    
    log = request.GET.get("log")

    full_path = os.path.join(dir, "log", log)

    if os.path.exists(full_path):
        os.remove(full_path)
    else:
        print("File {} does not exist".format(full_path))

def get_run_conf(uid):

    pd.set_option('display.max_colwidth', None)

    my_conn = get_conn_str(CONF)

    query = "select * from beacon_run_conf where uid = '{}'".format(uid)

    df = pd.read_sql(query, my_conn)

    if df.empty == True:
        ret_val = ""
    else:
        wrk_val = df.config.to_string(index=False)
        val = yaml.safe_load(wrk_val)

        # REMOVE BRONZE, DASHBOARD, FILTER & ZIP (NOT SELECTED)
        del val["dashboard"]
        del val["bronze"]

        # REMOVE FILTER OR ZIP
        if val["general"]["filter"] == False:
            del val["filter"]
        elif val["zip"]["unzip"] == False:
            del val["zip"]

        # GET USED BEACON ALGO & REMOVE OTHERS
        b_val = val["beacon"]["{}".format(val["general"]["cluster_type"])]
        del val["beacon"]
        val["beacon"] = b_val

        ret_val = pd.json_normalize(val).melt().rename(columns={"variable": "Setting", "value": "Value"})

    return ret_val

def add_beacon_group(uid):
    
    group_id = []
    my_conn = get_conn_str(CONF)

    query = "insert into beacon_group (uid) values('{}')".format(uid)
    my_conn.connect()
    
    my_conn.execute(query)

    query = "select group_id from beacon_group where uid = '{}'".format(uid)

    df = pd.read_sql(query, my_conn)

    return int(df.group_id.to_string(index=False))

def add_group_conf(uid, config):

    my_conn = get_conn_str(CONF)

    query = "insert into beacon_run_conf (uid,config) values('{}','{}')".format(uid, str(config).replace("'","''"))
    my_conn.connect().execute(query)

def get_group_id(uid):

    my_conn = get_conn_str(CONF)

    query = "select group_id from beacon_group where uid = '{}'".format(uid)

    df = pd.read_sql(query, my_conn)

    return int(df.group_id.to_string(index=False))

def add_group_log(group_id,log_file):

    my_conn = get_conn_str(CONF)

    query = "insert into beacon_log (group_id,log_file) values('{}','{}')".format(group_id,log_file)
    my_conn.connect().execute(query)

def add_dns(http_log_dir):

    #####################################################################################
    ##  GATHER HTTP LOG DIR
    #####################################################################################   

    first = True

    for root, dir, dir_f in os.walk(http_log_dir):
        for fname in dir_f:
            f = os.path.join(root,fname)

            # GET FILE
            if os.path.isfile(f):
                raw_name = f

            print("Processing {}".format(raw_name))

            if first == True:
                final_df = pd.read_json(raw_name, lines=True)
                first = False
            else:
                df = pd.read_json(raw_name, lines=True)
                final_df = pd.concat([final_df,df])

    load_df = final_df[["id.resp_h", "host"]].copy().reset_index(drop=True)
    load_df.rename(columns={"id.resp_h": "ip", "host": "dns"},inplace=True)
    load_df.dropna(inplace=True)
    load_df.drop_duplicates(inplace=True)
    
    #####################################################################################
    ##  
    #####################################################################################    

    my_conn = get_conn_str(CONF)

    # QUICK LOAD TEMP TABLE
    load_df.to_sql(con = my_conn, name = "tmp_dns", if_exists = "replace", index = False, chunksize= 50000)

    query = "insert into dns \
            (ip,dns) \
            select distinct t.ip,t.dns \
            from tmp_dns t \
            left join dns d on \
                t.ip = d.ip and \
                t.dns = d.dns \
            where d.ip is null and d.dns is null \
            and t.ip != t.dns; \
            \
            drop table tmp_dns;"
    
    my_conn.connect().execute(query)

def add_ds(post_data):

    print(post_data)

    if post_data["data_type"] == "Zeek Connection Logs":
        data = {"raw_log_loc": post_data["raw_log_loc"]}

        query = "insert into datasource \
                (ds_name,ds_type_id,data) \
                select distinct '{}',{},'{}'".format(post_data["ds_name"], int(post_data["ds_type_name"]), str(data).replace("'","''"))
        
    elif post_data["data_type"] == "Security Onion":
        data = {"host": post_data["es_host"], "port": post_data["es_port"], "api_key": post_data["api_key"]}

        query = "insert into datasource \
                (ds_name,ds_type_id,data) \
                select distinct '{}',{},'{}'".format(post_data["ds_name"], int(post_data["ds_type_name"]), str(data).replace("'","''"))
    elif post_data["data_type"] == "Elastic":
        data = {"host": post_data["es_host"], "port": post_data["es_port"], "api_key": post_data["api_key"], "index": post_data["es_index"]}

        query = "insert into datasource \
                (ds_name,ds_type_id,data) \
                select distinct '{}',{},'{}'".format(post_data["ds_name"], int(post_data["ds_type_name"]), str(data).replace("'","''"))
    else:
        pass


    my_conn = get_conn_str(CONF)
    my_conn.connect().execute(query)

def upd_ds(post_data):

    data = {}

    # BUILD DATA JSON
    for key, value in post_data.POST.items():
        if key in ["rowid", "csrfmiddlewaretoken"]:
            pass
        elif key == "ds_name":
            ds_name = value
        else:
            data[key] = value

    query = "update datasource \
        set ds_name = '{}',\
        data = '{}'\
        where rowid = {}".format(ds_name,str(data).replace("'","''"),post_data.GET.get("rowid"))
        
    my_conn = get_conn_str(CONF)
    my_conn.connect().execute(query)    
