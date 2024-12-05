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
from pathlib import Path
from datetime import datetime, timedelta
import time
import shutil

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


#FILTER_FILE = os.path.join(os.getcwd(),"lib","filter","filter.parquet")
FILTER_FILE = os.path.join("C:\\bit_bucket\\Valkyrie_Framework","beacon_huntress","src","lib","filter","filter.parquet")

#####################################################################################
##  FUNCTIONS
#####################################################################################

def _build_dict(values):
    data = {}

    for x in values:
        cols = x.split("=")

        # NO LIST FOR TRUE/FALSE VALUES & CONVERT TO BOOLEAN
        if cols[1].strip().replace('"','').replace("'","").lower() in ["true", "false"]:
            data["{}".format(cols[0].strip())] = eval(cols[1].strip().replace('"','').replace("'",""))
        else:
            data["{}".format(cols[0].strip())] = [cols[1].strip().replace('"','').replace("'","")]

    return data

def _build_where(cmd_list):
    ret_val = ""

    if cmd_list[2].lower() == "where":
        ret_val = cmd_list[3].replace("=","==").replace("==<","=<").replace("==>","=>")

    return ret_val    

def reset_filter():

    # PROMPT FOR RESETTING FILTERS
    while True:
        print("Filters will be reset to their original state, and all current features will be lost!")
        del_all = input("Do you wish to continue?  [Y]es or [N]o: ")

        if del_all.lower() in ["y", "yes", "n", "no"]:
            break
        else:
            print("Invaild option!  Try again!")
    
    # RESET FILTERS
    if del_all.lower() in ["y", "yes"]:
        try:
            epoch = int(time.time())

            data = {"key": ["dest_ip"],
                    "value": ["204.79.197.203"],
                    "exclude": True,
                    "create_date": epoch}

            df = pd.DataFrame(data)

            df.to_parquet(FILTER_FILE)
            print("Filters reset")
        except BaseException as err:
            print("ERROR: {}".format(err))

def get_filter(cmd="all"):

    if cmd.lower() == "all" or cmd.lower() == "*":
        df = pd.read_parquet(FILTER_FILE)
    else:
        df = pd.read_parquet(FILTER_FILE).query("{}".format(cmd))

    df.reset_index(inplace=True)
    return df

def add_filter(command):

    try:
        # BUILD DATAFRAME
        data = _build_dict(command)
        epoch = int(time.time())
        data["create_date"] = epoch
        df = pd.DataFrame(data)

        # FILTER FILE DATAFRAME
        df_f = pd.read_parquet(FILTER_FILE)
        
        # CHECK FOR EXISTANCE
        # DUPLICATE
        df_dup = pd.merge(df, df_f, how="inner",on=["key", "value", "exclude"])

        if len(df) == len(df_dup):
            print("ERROR: Value already exists!")
            return

        # UPSERT A RECORD
        df_dup = pd.merge(df_f, df, how="inner",on=["key", "value"])
        
        if len(df_dup) > 0:
            # ADD INDICATOR & OUTER JOIN TO MERGE
            # UPSERT THE DATA
            df_dup = pd.merge(df_f, df, how="outer",on=["key", "value"], indicator=True)
            df_dup = df_dup.loc[df_dup._merge == "left_only",["key", "value", "exclude_x", "create_date_x"]]
            df_dup.rename(columns={"exclude_x": "exclude", "create_date_x": "create_date"}, inplace = True)
            new_df = pd.concat([df_dup, df], ignore_index=True)
            new_df.to_parquet(FILTER_FILE)
        else:
            df.to_parquet(FILTER_FILE, engine="fastparquet", append=True)
    except Exception as err:
        print("ERROR: {}".format(err))

    # if type(value) == str:
    #     epoch = int(time.time())

    #     data = {"key": ["{}".format(key)],
    #         "value": ["{}".format(value)],
    #         "exclude": ["{}".format(exclude)],
    #         "create_date": epoch}
    # elif type(value) == list:
    #     print("HERE")
    #     epoch = int(time.time())

    #     data = {"key": ["{}".format(key)] * len(value),
    #         "value": value,
    #         "create_date": epoch}
    # else:
    #     print("ERROR: Invaild input either string or List")
    #     sys.exit(1)

    # df = pd.DataFrame(data)
    # df.to_parquet(FILTER_FILE, engine="fastparquet", append=True)

def del_filter(key, value):

    df = pd.read_parquet(FILTER_FILE)

    if key == "index":
        del_val = len(df.iloc[[value]])
        if del_val > 0:
            df.drop([df.index[int(value)]], inplace=True)

            df.to_parquet(FILTER_FILE, engine="fastparquet")
            print("{} row/s deleted".format(del_val))
        else:
            print("0 row/s deleted")        
    else:
        del_val = len(df[(df["key"] == key) & (df["value"] == value)].index)

        if del_val > 0:
            df.drop(
                df[
                    (df["key"] == key) & (df["value"] == value)
                ].index, inplace=True)
            
            df.to_parquet(FILTER_FILE, engine="fastparquet")
            print("{} row/s deleted".format(del_val))
        else:
            print("0 row/s deleted")

def run_cmd(cmd):

    try:
        # GET 
        if cmd[0].lower() == "get":
            # ALL
            if len(cmd) <= 2:
                df = get_filter("all")
            # RUN WHERE CLAUSE
            else:
                if cmd[2].lower() == "where":
                    w_cmd = _build_where(cmd)
                    df = get_filter(w_cmd)

            # PRINT RESULTS
            if len(df) > 0:
                print(df)
            print("{} row/s".format(len(df.index)))
        
        # DELETE
        elif cmd[0].lower() == "del":
            df = del_filter(key=cmd[2], value=cmd[3])

        # ADD
        # STRIP COMMAND COLUMNS
        elif cmd[0].lower() == "add" or cmd[0].lower() == "insert":
            add_filter(cmd[2].split(",",-1))
        
        # INIT FILE
        elif cmd[0].lower() == "reset":
            reset_filter()
    except BaseException as err:
        print("ERROR: {}".format(err))

