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
        Pandas data frame will all data

    """
    final_df = pd.DataFrame()

    # GATHER FILES
    for x in df["file_name"]:

        df_n = pd.read_parquet(x)

        df_n.reset_index(inplace=True)

        final_df = pd.concat([final_df, df_n])


    return final_df