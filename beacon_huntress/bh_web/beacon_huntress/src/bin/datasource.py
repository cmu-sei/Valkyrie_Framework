'''
Valkyrie Framework
Copyright 2023 Carnegie Mellon University.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
DM23-0210
'''

import pandas as pd
import json
import sys
import os
import uuid
from pathlib import Path
import logging

#from beacon_huntress.src.bin.data import add_data, get_data, ds_activate
#from bin.data import add_data, get_data, ds_activate

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
##  FUNCTIONS
#####################################################################################


def get_file_data(df):

    """
    Get a single Pandas data frame for the chunked elastic data.\n

    Parameters:
    ===========
        df: 
            Pandas data frame with all file names

    Returns:
    ========
        Pandas data frame with all data

    """
    final_df = pd.DataFrame()

    # GATHER FILES
    for x in df["file_name"]:

        df_n = pd.read_parquet(x)

        df_n.reset_index(inplace=True)

        final_df = pd.concat([final_df, df_n])


    return final_df

def check_delta_columns(df):

    df.rename(columns={"source_ip":	"id.orig_h", "destination_ip": "id.resp_h", "port": "id.resp_p","datetime": "ts"},inplace=True)

    if "source_bytes" not in df:
        df["orig_ip_bytes"] = 0
    else:
        df.rename(columns={"source_bytes": "orig_ip_bytes"},inplace = True)

    if "destination_bytes" not in df:
        df["resp_ip_bytes"] = 0
    else:
        df.rename(columns={"destination_bytes":"resp_ip_bytes"}, inplace = True)

    # ADD MISSING ZEEK COLUMNS
    df["uid"] = df.index + 1
    df["id.orig_p"] = 0
    df["id.orig_p"] = 0
    df["proto"] = ""
    df["service"] = ""
    df["duration"] = 0    
    df["orig_bytes"] = 0
    df["resp_bytes"] = 0
    df["conn_state"] = ""
    df["local_orig"] = False
    df["local_resp"] = False
    df["missed_bytes"] = 0    
    df["history"] = ""
    df["orig_pkts"] = 0
    df["resp_pkts"] = 0
    df["community_id"] = ""
    df["orig_mac_oui"] = ""

    return df

def load_delta_data(fname, ftype = "csv"):

    """
    Get a delta file data .\n
    Column names must be 

    Parameters:
    ===========
        fname: 
            File name
        ftype:
            File type
            CSV or Parquet


    Returns:
    ========
        Pandas data frame will all data
    """

    try:
        if ftype.lower() == "csv":
            df = pd.read_csv(fname)
            df["source_file"] = fname
            df["src_row_id"] = df.index

            # GET THE CORRECT COLUMNS
            df = check_delta_columns(df)
        elif ftype.lower() == "parquet":
            df = pd.read_parquet(fname)

            df["source_file"] = fname
            df["src_row_id"] = df.index

            # GET THE CORRECT COLUMNS
            df = check_delta_columns(df)
        else:
            print("ERROR: Invaild delta file type must be either csv or parquet!")
            df = pd.DataFrame(columns=["ts","uid","id.orig_h","id.orig_p","id.resp_h",
                    "id.resp_p","proto","service","duration","orig_bytes",
                    "resp_bytes","conn_state","local_orig","local_resp",
                    "missed_bytes","history","orig_pkts","orig_ip_bytes",
                    "resp_pkts","resp_ip_bytes","community_id","orig_mac_oui",
                    "source_file","src_row_id"
                    ])

    except Exception as err:
        print("ERROR: {}".format(str(err)))
        df = pd.DataFrame(columns=["ts","uid","id.orig_h","id.orig_p","id.resp_h",
                "id.resp_p","proto","service","duration","orig_bytes",
                "resp_bytes","conn_state","local_orig","local_resp",
                "missed_bytes","history","orig_pkts","orig_ip_bytes",
                "resp_pkts","resp_ip_bytes","community_id","orig_mac_oui",
                "source_file","src_row_id"
                ])

    return df

def load_ds_data(df, fname, dstype = "delta", ftype = "csv"):

    """
    Get a delta file data .\n

    Parameters:
    ===========
        fname:
            File name
        ftype:
            File type
            CSV or Parquet


    Returns:
    ========
        Pandas data frame will all data
    """

    try:
        # if ftype.lower() == "csv":
        #     df = pd.read_csv(fname)

        #     df["source_file"] = fname
        #     df["src_row_id"] = df.index

        #     col_check = True
        # elif ftype.lower() == "parquet":
        #     df = pd.read_parquet(fname)

        #     df["source_file"] = fname
        #     df["src_row_id"] = df.index

        #     col_check = True
        if df.empty:
            logger.warning("Empty file {}!".format(fname))
            df = pd.DataFrame(columns=["ts","uid","id.orig_h","id.orig_p","id.resp_h",
                    "id.resp_p","proto","service","duration","orig_bytes",
                    "resp_bytes","conn_state","local_orig","local_resp",
                    "missed_bytes","history","orig_pkts","orig_ip_bytes",
                    "resp_pkts","resp_ip_bytes","community_id","orig_mac_oui",
                    "source_file","src_row_id", "dns"
                    ])
            col_check = False
        else:
            df["source_file"] = fname
            df["src_row_id"] = df.index

            col_check = True

        if col_check:
            df = check_ds_columns(df, dstype)

    except Exception as err:
        print("ERROR: {}".format(str(err)))
        df = pd.DataFrame(columns=["ts","uid","id.orig_h","id.orig_p","id.resp_h",
                "id.resp_p","proto","service","duration","orig_bytes",
                "resp_bytes","conn_state","local_orig","local_resp",
                "missed_bytes","history","orig_pkts","orig_ip_bytes",
                "resp_pkts","resp_ip_bytes","community_id","orig_mac_oui",
                "source_file","src_row_id","dns"
                ])

    return df

def check_ds_columns(df, dstype = "delta"):

    if dstype.lower() == "delta":
        df.rename(columns={"source_ip":	"id.orig_h", "destination_ip": "id.resp_h", "port": "id.resp_p","datetime": "ts"},inplace=True)

        if "source_bytes" not in df:
            df["orig_ip_bytes"] = 0
        else:
            df.rename(columns={"source_bytes": "orig_ip_bytes"},inplace = True)

        if "destination_bytes" not in df:
            df["resp_ip_bytes"] = 0
        else:
            df.rename(columns={"destination_bytes":"resp_ip_bytes"}, inplace = True)

        df_new = df.copy()

        # ADD MISSING ZEEK COLUMNS
        df_new["uid"] = df.index + 1
        df_new["id.orig_p"] = 0
        df_new["proto"] = ""
        df_new["service"] = ""
        df_new["duration"] = 0
        df_new["orig_bytes"] = 0
        df_new["resp_bytes"] = 0
        df_new["conn_state"] = ""
        df_new["local_orig"] = False
        df_new["local_resp"] = False
        df_new["missed_bytes"] = 0
        df_new["history"] = ""
        df_new["orig_pkts"] = 0
        df_new["resp_pkts"] = 0
        df_new["community_id"] = ""
        df_new["orig_mac_oui"] = ""
        # NEW FOR CLI
        df_new["dns"] = ""

    elif dstype.lower() == "http":
        # FIGURE OUT WHAT TO DO WITH HOST

        # OVERWRITE DATASOURCE PULL ONLY NEEDED FIELDS
        df = df[["ts","uid","id.orig_h","id.orig_p","id.resp_h","id.resp_p","source_file","src_row_id","host"]].rename(columns={"host": "dns"})

        df_new = df.copy()

        # ADD MISSING ZEEK COLUMNS
        df_new["proto"] = ""
        df_new["service"] = ""
        df_new["duration"] = 0
        df_new["orig_ip_bytes"] = 0
        df_new["resp_ip_bytes"] = 0
        df_new["conn_state"] = ""
        df_new["local_orig"] = False
        df_new["local_resp"] = False
        df_new["missed_bytes"] = 0
        df_new["history"] = ""
        df_new["orig_pkts"] = 0
        df_new["resp_pkts"] = 0
        df_new["community_id"] = ""
        df_new["orig_mac_oui"] = ""

    elif dstype.lower() == "dns":
        # FIGURE OUT WHAT TO DO WITH TTLs & Query
        # TWO RECORDS PER

        # OVERWRITE DATASOURCE PULL ONLY NEEDED FIELDS
        df = df[["ts","uid","id.orig_h","id.orig_p","id.resp_h","id.resp_p", "proto","source_file","src_row_id"]]

        df_new = df.copy()

        # ADD MISSING ZEEK COLUMNS
        df_new["service"] = ""
        df_new["duration"] = 0
        df_new["orig_ip_bytes"] = 0
        df_new["resp_ip_bytes"] = 0
        df_new["conn_state"] = ""
        df_new["local_orig"] = False
        df_new["local_resp"] = False
        df_new["missed_bytes"] = 0
        df_new["history"] = ""
        df_new["orig_pkts"] = 0
        df_new["resp_pkts"] = 0
        df_new["community_id"] = ""
        df_new["orig_mac_oui"] = ""
        # NEW FOR CLI
        df_new["dns"] = ""
    else:
        print("ERROR: Data Source Type {} does not exist!".format(str(dstype)))
        sys.exit(1)

    return df_new
