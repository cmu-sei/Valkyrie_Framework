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
import eland as ed
from beacon_huntress.src.bin.data import add_data, get_data, ds_activate
from elasticsearch import Elasticsearch
from pathlib import Path
import logging

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

def safe_load(row):
    """
    Convert a row to JSON format.\n

    Parameters:
    ===========
        row: 
            Dictionary tuple.

    Returns:
    ========
        JSON value or None
    """    
    try:
        return json.loads(row)
    except json.JSONDecodeError:
        return None

def elastic_client(data):
    """
    Convert a row to JSON format.\n

    Parameters:
    ===========
        data: 
            Dictionary with elastic info.
            {host: "SERVER NAME", port: PORT_NUM, "api" "API KEY", "timeout": TIMEOUT_NUM_SS, "auth": "api"}

    Returns:
    ========
        Elastic client\
    """    
    if data["auth"] == "api":

        # SET DEFAULT TIME TO 900 SECONDS IF A TIMEOUT DOES NOT EXIST
        if "timeout" in data:
            # API KEY
            es = Elasticsearch(
                hosts="http://{}:{}".format(data["host"],data["port"]),
                api_key=data["api"],
                request_timeout=data["timeout"],
                verify_certs=False
                )
        else:
            # API KEY
            es = Elasticsearch(
                hosts="http://{}:{}".format(data["host"],data["port"]),
                api_key=data["api"],
                request_timeout=900,
                verify_certs=False
                )            

    return es

def elastic_index(client):
    """
    Get all elastic indicies for a client connection.\n

    Parameters:
    ===========
        client: 
            Elastic Client

    Returns:
    ========
        Pandas Data Frame
    """        

    df = pd.DataFrame(columns=["index_name", "cnt"])

    index = client.cat.indices(format="json")

    for x in index:
        df_2 = pd.DataFrame({"index_name": [x["index"]], "cnt": [x["docs.count"]]})
        df = pd.concat([df_2, df], ignore_index=True)

    df.sort_values("index_name",inplace=True, ignore_index=True)

    return df

def deprecated_get_elastic_data(client, data, start_dte = "", end_dte = ""):
    """
    Deprecated:
    ===========
    Get elastic data for a client

    Parameters:
    ===========
        client: 
            Elastic Client
        data: JSON
            Data related to elastic indicies
            data = {"data_type": elastic or secon,
                    "index": elastic indicies in list form
                    "ds_name": Data source name
                    "auth": Authenication method must be api
                    "max_records": Maximum records to pull from indicies, 0 for all records
                    }

    Returns:
    ========
        Pandas Data Frame
    """      
    query = {
            "query": {
                    "bool": {
                                "should": [
                                            {"match": {"container.id": "conn.log"}},
                                            #{"match": {"container.id": "dns.log"}},
                                ]
                            }
            }
    }

    # # START & END DATES
    # elif start_dte != "" and end_dte != "":
    #     query = {
    #         "query": {
    #             "bool": {
    #                 "must": [
    #                     {
    #                         "range": {
    #                             "ts": {
    #                                 "gte": start_dte,
    #                                 "lte": end_dte
    #                             }
    #                         }
    #                     }
    #                 ],
    #                 "should": [
    #                     {"match": {"container.id": "conn.log"}}
    #                     #{"match": {"container.id": "dns.log"}},
    #                 ]
    #             }
    #         }
    #     }        

    size = 10000
    total = 0
    time = "15m"

    print(data)

    if data["max_records"] == 0:
        max_rec = sys.maxsize
    else:
        max_rec = data["max_records"]

    response = client.search(index=data["index"], 
                        # BODY WILL BE DEPRECATED
                        #body=query,
                        size=size,
                        scroll=time) 

    scroll_id = response["_scroll_id"]
    vals = response["hits"]["hits"]
    conn_data = []

    for x in vals:
        # Check for Sec Onion or Elasic
        if data["data_type"] == "Elastic":
            conn_data.append({"data": x["_source"]["zeek"]})
        else:
            conn_data.append({"data": x["_source"]["message"]})

    total += size

    while len(vals) > 0:
        zeek = client.scroll(scroll_id=scroll_id, scroll=time)
        scroll_id = zeek["_scroll_id"]
        vals = zeek["hits"]["hits"]

        for x in vals:
            # Check for Sec Onion or Elasic
            # ELASTIC MAKE SURE ZEEK IS IN THE VALUE IF NOT SKIP
            if data["data_type"] == "Elastic":
                if "_source" in x and "zeek" in x["_source"]:
                    conn_data.append({"data": x["_source"]["zeek"]})
                else:
                    pass
            else:
                conn_data.append({"data": x["_source"]["message"]})

        total += size
        print(total)

        if total >= max_rec:
            print("Max Records...exiting scroll")
            break
            
    df = pd.json_normalize(conn_data)
    if df.empty:
        df_zeek = df
    else:
        if data["data_type"] == "Elastic":
            # remove data. columns
            df.columns = df.columns.str.replace('^data\.', '', regex=True)
            df_zeek = df
        else:
            df["data"] = df["data"].apply(safe_load)
            df = df.dropna(subset=["data"])
            df_zeek = pd.json_normalize(df["data"])

        # CHECK DATES 
        # TEMPORARY CHANGE TO ELASTIC QUERY IN THE FUTURE
        if start_dte != "" and end_dte != "":
            df_zeek = df_zeek.query("ts >= {} and ts <= {}".format(start_dte, end_dte))
        # ONLY START
        elif start_dte != "" and end_dte == "":
            df_zeek = df_zeek.query("ts >= {}".format(start_dte))
        # ONLY END
        elif start_dte == "" and end_dte != "":
            df_zeek = df_zeek.query("ts <= {}".format(end_dte))
        else:
            pass        

    return df_zeek

def get_elastic_data(client, data):
    """
    Get all elastic indicies for a client connection.\n

    Parameters:
    ===========
        client: 
            Elastic Client
        data: JSON
            Data related to elastic indicies
            data = {"index": elastic indicies in list form
                    }            

    Returns:
    ========
        Pandas Data Frame
    """    

    e_df = ed.DataFrame(client, es_index_pattern=data["index"],
        columns = ['zeek.community_id', 'zeek.conn_state', 'zeek.duration',
        'zeek.history', 'zeek.id.orig_h', 'zeek.id.orig_p', 'zeek.id.resp_h',
        'zeek.id.resp_p', 'zeek.local_orig', 'zeek.local_resp',
        'zeek.missed_bytes', 'zeek.orig_bytes', 'zeek.orig_ip_bytes',
        'zeek.orig_mac_oui', 'zeek.orig_pkts', 'zeek.proto', 'zeek.resp_bytes',
        'zeek.resp_ip_bytes', 'zeek.resp_pkts', 'zeek.service', 'zeek.ts',
        'zeek.uid'])

    df = e_df.to_pandas(True)

    df.columns = df.columns.str.strip("zeek.")

    return df

def chunk_data(df,loc,filename,chunk_type="num",chunk=10000):
    """
    Create local parquet files for data source.\n

    Parameters:
    ===========
        df: 
            Pandas data frame
        loc:
            Destination location for files
        chunk_type: STRING
            How to chunk the data
                num: # of rows
        chunk: INT
            The number of rows per file

    Returns:
    ========
        File locations: LIST
    """  
    cnt = 0
    chunk_lst = []

    Path(loc).mkdir(parents=True, exist_ok=True)

    if chunk_type == "num":
        for x in range(0, len(df), chunk):
            cnt += 1
            chk = df[x:x+ chunk].copy()

            p_file = filename + "_{}.parquet".format(cnt)
            
            f_name = os.path.join(loc,p_file)

            chk["source_file"] = f_name
            chk["src_row_id"] = range(1,len(chk)+1)

            chk.to_parquet(f_name,compression="snappy")
            chunk_lst.append(p_file)

            # DELETE DATAFRAME TO PREVENT ISSUES
            del chk
    
    return chunk_lst

def load_elastic_data(client, data, chunk_size=100000):
    """
    Get elastic data, chunk the data to parquet files and load data into beacon huntress db. This function is used in the async processing\n

    Parameters:
    ===========
        client: 
            Elastic client
        data: JSON
            Data related to elastic indicies
            data = {"data_type": elastic or secon,
                    "index": elastic indicies in list form
                    "ds_name": Data source name
                    "auth": Authenication method must be api 
                    "max_records": Maximum records to pull from indicies, 0 for all records
                    }            
        chunk_size: INT
            The number of rows per file

    Returns:
    ========
        File locations: LIST

    """
    group_id = uuid.uuid4()

    try:
        # GATHER THE DATA FOR ELASTIC
        df = get_elastic_data(client, data)

        print("INFO: Chunking data")

        # CREATE THE FILES
        f_lst = chunk_data(
            df = df,
            loc = "/elastic/{}".format(group_id),
            filename = "elastic_{}".format(group_id),
            chunk_type = "num",
            chunk=chunk_size
            )
        
        # GET THE DS_ID TO BE USED FOR INSERT
        df_ds = get_data('ds_by_name',data["ds_name"])

        print("INFO: Add created files")
        # LOAD FILES
        for x in f_lst:
            add_data("ds_files",[group_id,df_ds["rowid"][0],"/elastic/{}/{}".format(group_id,x)])

        print("INFO: Activating the Data Souce")
        # UPDATE THE DATASOURCE TO ACTIVE
        ds_activate(data["ds_name"])

    except Exception as err:
        print("ERROR: {}".format(str(err)))
        f_lst = ""

    return f_lst

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

            print("RAW FILE: {}".format(len(fname)))
            print("LOAD DELTA SIZE: {}".format(len(df)))
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
                    "source_file","src_row_id"
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
                "source_file","src_row_id"
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

        # ADD MISSING ZEEK COLUMNS
        df["uid"] = df.index + 1
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

    elif dstype.lower() == "http":
        # FIGURE OUT WHAT TO DO WITH HOST

        # OVERWRITE DATASOURCE PULL ONLY NEEDED FIELDS
        df = df[["ts","uid","id.orig_h","id.orig_p","id.resp_h","id.resp_p","source_file","src_row_id"]]

        # ADD MISSING ZEEK COLUMNS
        df["proto"] = ""
        df["service"] = ""
        df["duration"] = 0
        df["orig_ip_bytes"] = 0
        df["resp_ip_bytes"] = 0
        df["conn_state"] = ""
        df["local_orig"] = False
        df["local_resp"] = False
        df["missed_bytes"] = 0
        df["history"] = ""
        df["orig_pkts"] = 0
        df["resp_pkts"] = 0
        df["community_id"] = ""
        df["orig_mac_oui"] = ""

    elif dstype.lower() == "dns":
        # FIGURE OUT WHAT TO DO WITH TTLs & Query
        # TWO RECORDS PER

        # OVERWRITE DATASOURCE PULL ONLY NEEDED FIELDS
        df = df[["ts","uid","id.orig_h","id.orig_p","id.resp_h","id.resp_p", "proto","source_file","src_row_id"]]

        # ADD MISSING ZEEK COLUMNS
        df["service"] = ""
        df["duration"] = 0
        df["orig_ip_bytes"] = 0
        df["resp_ip_bytes"] = 0
        df["conn_state"] = ""
        df["local_orig"] = False
        df["local_resp"] = False
        df["missed_bytes"] = 0
        df["history"] = ""
        df["orig_pkts"] = 0
        df["resp_pkts"] = 0
        df["community_id"] = ""
        df["orig_mac_oui"] = ""
    else:
        print("ERROR: Data Source Type {} does not exist!".format(str(dstype)))
        sys.exit(1)

    return df
