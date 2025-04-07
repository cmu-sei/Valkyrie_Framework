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
import gzip
import logging
from click import progressbar
import pandas as pd
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import platform
from beacon_huntress.src.bin.datasource import load_ds_data

#####################################################################################
##  Logging
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
##  LOCAL FUNCTIONS
#####################################################################################

def _total_cnt(src_loc):

    ret_cnt = 0
    for root, dirs, files in os.walk(src_loc, topdown=False): 
        ret_cnt += len(files)

    return ret_cnt

#####################################################################################
##  FUNCTIONS
#####################################################################################

def build_raw(src_file, dest_parquet_file, ds_type = "conn", start_dte = "", end_dte = "", overwrite = False, verbose = False):
    """
    Build initial files

    Parameters:
    ===========
        src_file:
            Source file.
        dest_parquet_file:
            Destination parquet file.
        ds_type:
            Data Source Type.
        start_dte: DATETIME
            Filter start date and time.
        end_dte: DATETIME
            Filter end date and time.
        overwrite: BOOLEAN
            Overwrite existing data.
            Default = False
        verbose: BOOLEAN
            Verbose logging.
            Default = False

    Returns:
    ========
        Nothing
    """
    from pandas import json_normalize

    #####################################################################################
    ##  Logging
    #####################################################################################

    if verbose == True:
        lvl = logging.DEBUG
        for handler in logger.handlers:
            handler.setLevel(lvl)

    #####################################################################################
    ##
    #####################################################################################

    starttime = datetime.now()
    logger.debug("Starting Ingest process")

    # REMOVE DATA IF EXISTS & OVERWRITE = TRUE
    if overwrite == True:
        if os.path.exists(dest_parquet_file):
            os.remove(dest_parquet_file)
    elif overwrite == False:
        if os.path.exists(dest_parquet_file):
            logger.debug("Parquet file {} already exists, skipping file.".format(dest_parquet_file))

            endtime = datetime.now() - starttime
            logger.debug('Total Export process completed')
            logger.debug('Total runtime {}'.format(endtime))

            return

    #####################################################################################
    ##  READ FILE & CREATE JSON & PARQUET FILES
    #####################################################################################

    ext = str(Path(src_file).suffix).replace(".","").lower()
    #REMOVE
    #logger.info(f"SOURCE FILE: {src_file}")
    #logger.info(f"EXTENSION: {ext}")

    if ext == "json" or ext == "gz":
        df = pd.read_json(src_file, lines=True)
        #REMOVE
        #logger.info("READ JSON")
        #logger.info(len(df))
    elif ext == "parquet":
        print("PARQUET SECTION")
        df = pd.read_parquet(src_file)
    else:
        print("ERROR: Extension option {} does not exist for a Raw File type!".format(ext))

    print("RAW DATAFRAME LENGTH: {}".format(len(df)))

    # CHECK FOR DATES
    # START & END DATE
    if start_dte == "" and end_dte == "":
        logger.info("No dates entered skipping!!")
        pass
    elif start_dte != "" and end_dte != "":
        df = df.query("ts >= {} and ts <= {}".format(start_dte, end_dte))
    # ONLY START
    elif start_dte != "" and end_dte == "":
        df = df.query("ts >= {}".format(start_dte))
    # ONLY END
    elif start_dte == "" and end_dte != "":
        df = df.query("ts <= {}".format(end_dte))
    else:
        pass

    # PROCESS IF THERE IS DATA
    if df.empty:
        logger.warning("No data for file {}".format(dest_parquet_file))
    else:
        if ds_type == "conn":
            logger.info("Data Source = {}".format(ds_type))
            # READ JSON AND NORMALIZE IT
            # NORMALIZE JSON IF EVENTDATA TAG IS PRESENT
            if "eventdata" in df:
                nor_df = json_normalize(df["eventdata"])
                final_df = nor_df.query("proto == 'tcp'")
                new = final_df.copy()
                new["source_file"] = dest_parquet_file
                new["src_row_id"] = new.reset_index().index
                final_df = new
            else:
                nor_df = df
                final_df = nor_df.query("proto == 'tcp'")
                final_df = df.astype({"id.resp_p": int}, errors="raise")
                final_df["source_file"] = dest_parquet_file
                final_df["src_row_id"] = df.reset_index().index
        #BACKHERE
        elif ds_type == "http":
            logger.info(src_file)
            logger.info(df.info())
            logger.info("Data Source = {}".format(ds_type))
            # THIS IS NOT EFFICIENT FIX IT LATER
            final_df = load_ds_data(df,dest_parquet_file,"http","parquet")

            logger.info(final_df)

        logger.debug("Creating parquet file {}".format(dest_parquet_file))
        try:
            final_df.to_parquet(dest_parquet_file,compression="snappy")
        except BaseException as err:
            logger.error("Failure on file {}".format(dest_parquet_file))
            logger.error(err)

    #####################################################################################
    ##  FINAL RESULTS
    #####################################################################################

    endtime = datetime.now() - starttime
    logger.debug('Total export process completed')
    logger.debug('Total runtime {}'.format(endtime))

def add_dns(src_file, dest_loc, file_type, dns_file = "", dns_df = "", verbose = False):
    """
    Add all DNS entries to files.

    Parameters:
    ===========
        src_file:
            Source file/s directory location.
        dest_loc:
            Destination file/s directory location.
        file_type:
            Destination file type (csv or parquet).
        dns_file:
            Source DNS lookup file (must be in parquet format).
        dns_df:
            Source DNS Pandas DataFrame.
        verbose: BOOLEAN
            Verbose logging.
            Default = False

    Returns:
    ========
        Nothing
    """

    #####################################################################################
    ##  Logging
    #####################################################################################

    if verbose == True:
        lvl = logging.DEBUG
        for handler in logger.handlers:
            handler.setLevel(lvl)

    #####################################################################################
    ##  SEARCH FOR IPS DNS
    #####################################################################################

    starttime = datetime.now()

    logger.debug("Building Dataframes")

    # REMOVE - Values 
    if len(dns_file) > 0:
        df_ips = pd.read_parquet(dns_file)
        df_ips = df_ips[df_ips["wildcard_ip"].str.contains("-") == False]
        df_ips[["oct1", "oct2", "oct3", "oct4"]] = df_ips['whitelist_ip'].str.split('.', expand=True).replace("X","0").astype("int32")
    elif len(dns_df) > 0:
        df_ips = dns_df
    else:
        logger.error("Missing dns file or dns dataframe")


    df = pd.read_parquet(src_file)
    df.rename(columns={"id.orig_h": "sip", "id.resp_h": "dip", "id.resp_p": "port"}, inplace=True)   

    # GET EXPORT FILE NAME & ADD IT TO THE SOURCE DATAFRAME
    if file_type == "csv":   
        new_file_name = os.path.basename(src_file).replace(".parquet.gz",".csv").replace(".parquet",".csv")
        new_file = os.path.join(dest_loc,new_file_name)
    else:
        new_file_name = os.path.basename(src_file).replace(".parquet.gz",".parquet")
        new_file = os.path.join(dest_loc,new_file_name)

    #####################################################################################
    ##  BUILD DATAFRAME OCTETS
    #####################################################################################

    logger.debug("Splitting Octets for Dataframes")

    # SPLIT OCTETS
    df[["s_oct1", "s_oct2", "s_oct3", "s_oct4"]] = df['sip'].str.split('.', expand=True).replace("X","0").astype("int32")
    df[["d_oct1", "d_oct2", "d_oct3", "d_oct4"]] = df['dip'].str.split('.', expand=True).replace("X","0").astype("int32")

    #####################################################################################
    ##  SEARCH FOR IPS DNS
    #####################################################################################

    logger.debug("Searching for IPs")

    for x in ["s", "d"]:

        if x == "s":
            t_name = "source"
            full_name = "source"
            logger.debug("Searching by source IPs")
        else:
            t_name = "dest"
            full_name = "destination"
            logger.debug("Searching by destination IPs")
        
        # SEARCH SOURCE DNS BY OCTETS (4 - 1)
        # OCTET 4 (X.X.X.X)
        '''
        # NO LONGER NEED TO SEARCH BY 4 OCTETS
        logger.debug("Searching by octet 4 (X.X.X.X)")
        df_oct4 = pd.merge(df[["{}ip".format(x), "{}_oct1".format(x), "{}_oct2".format(x), "{}_oct3".format(x), "{}_oct4".format(x)]], 
            df_ips, 
            how='inner', 
            left_on = ["{}_oct1".format(x), "{}_oct2".format(x), "{}_oct3".format(x), "{}_oct4".format(x)], 
            right_on = ["oct1", "oct2", "oct3", "oct4"])[["{}ip".format(x), "dns"]]
        '''

        # OCTET 3 (X.X.X*)
        logger.debug("Searching by octet 3 (X.X.X*)")
        df_oct3 = pd.merge(df[["{}ip".format(x), "{}_oct1".format(x), "{}_oct2".format(x), "{}_oct3".format(x), "{}_oct4".format(x)]], 
            df_ips.query("oct4 == 0"), 
            how='inner', 
            left_on = ["{}_oct1".format(x), "{}_oct2".format(x), "{}_oct3".format(x)], 
            right_on = ["oct1", "oct2", "oct3"])[["{}ip".format(x), "dns"]]

        logger.debug("Searching by octet position 1 & 3 (X.0.X*)")
        df_oct13 = pd.merge(df[["{}ip".format(x), "{}_oct1".format(x), "{}_oct2".format(x), "{}_oct3".format(x), "{}_oct4".format(x)]], 
            df_ips.query("oct4 == 0 and oct2 == 0"), 
            how='inner', 
            left_on = ["{}_oct3".format(x), "{}_oct1".format(x)], 
            right_on = ["oct3", "oct1"])[["{}ip".format(x), "dns"]]        

        # OCTET 2 (X.X*)
        logger.debug("Searching by octet 2 (X.X*)")        
        df_oct2 = pd.merge(df[["{}ip".format(x), "{}_oct1".format(x), "{}_oct2".format(x), "{}_oct3".format(x), "{}_oct4".format(x)]], 
            df_ips.query("oct4 == 0 and oct3 == 0"), 
            how='inner', 
            left_on = ["{}_oct1".format(x), "{}_oct2".format(x)], 
            right_on = ["oct1", "oct2"])[["{}ip".format(x), "dns"]]

        # OCTET 1 (X*)
        logger.debug("Searching by octet 1 (X*)")        
        df_oct1 = pd.merge(df[["{}ip".format(x), "{}_oct1".format(x), "{}_oct2".format(x), "{}_oct3".format(x), "{}_oct4".format(x)]], 
            df_ips.query("oct4 == 0 and oct3 == 0 and oct2 == 0"), 
            how='inner', 
            left_on = ["{}_oct1".format(x)], 
            right_on = ["oct1"])[["{}ip".format(x), "dns"]]

        # DELETION ORDER
        # 4 > 3 
        # 2 > 3_1
        # 2 > 1
        # 3_1 > 1
     
        # OPTIMIZE THIS CODE LATER
        # DELETE OCTET_2 DUPLICATES
        logger.debug("Deleting duplicates")
        df_oct2 = df_oct2[~df_oct2["{}ip".format(x)].isin(df_oct3["{}ip".format(x)])]
        
        # DELETE OCTET_1_3 DUPLICATES
        df_oct13 = df_oct13[~df_oct13["{}ip".format(x)].isin(df_oct3["{}ip".format(x)])]
        df_oct13 = df_oct13[~df_oct13["{}ip".format(x)].isin(df_oct2["{}ip".format(x)])]

        # DELETE OCTET_1 DUPLICATES
        df_oct1 = df_oct1[~df_oct1["{}ip".format(x)].isin(df_oct3["{}ip".format(x)])]
        df_oct1 = df_oct1[~df_oct1["{}ip".format(x)].isin(df_oct13["{}ip".format(x)])]
        df_oct1 = df_oct1[~df_oct1["{}ip".format(x)].isin(df_oct2["{}ip".format(x)])]

        # MERGE
        # NO LONGER NEED OCTET 4
        #df_final_src = pd.concat([df_oct4, df_oct3, df_oct2, df_oct1], ignore_index=True)
        df_final_src = pd.concat([df_oct3, df_oct13, df_oct2, df_oct1], ignore_index=True)
        df_final_src.rename(columns={"{}ip".format(x): "{}_ip".format(t_name)}, inplace=True)
        df_final_src.drop_duplicates(inplace=True)

        df_final_src =  df_final_src.groupby("{}_ip".format(t_name))["dns"].apply(list)

        logger.debug("Adding dns records for {}".format(full_name))

        df = pd.merge(df,df_final_src,how = "left", left_on = ["{}ip".format(x)], right_on = ["{}_ip".format(t_name)])
        df.rename(columns={"dns": "{}_dns".format(x)}, inplace=True)

        logger.debug("Deleting dataframes")
        #del [[df_oct4, df_oct3, df_oct2, df_oct1, df_final_src]]
        del [[ df_oct3, df_oct13, df_oct2, df_oct1, df_final_src]]

    #####################################################################################
    ##  Export file
    #####################################################################################

    # RENAME COLUMNS BACK TO ORIGINAL NAMES
    df.rename(columns={"sip": "id.orig_h", "dip": "id.resp_h", "port": "id.resp_p"}, inplace=True)

    # CREATE FINAL DATAFRAME
    final_df = df[["uid", 
        "orig_bytes", "id.orig_h", "id.orig_p", "id.resp_h", "local_resp", "missed_bytes", "orig_pkts", 
        "orig_ip_bytes", "community_id", "ts", "proto", "duration", "resp_ip_bytes", 
        "local_orig", "service", "resp_pkts", "history", "resp_bytes", "id.resp_p", "conn_state", 
        "s_dns", "d_dns", "source_file", "src_row_id"]]

    # DUMP FILE AS CSV OR PARQUET
    if file_type == "csv":   
        new_file.replace(".parquet",".csv")
        final_df.to_csv(new_file)
    else:
        final_df.to_parquet(new_file, compression= "snappy")

    logger.debug("{} file {} is completed".format(file_type, new_file))
    endtime = datetime.now() - starttime
    logger.debug('Total runtime {}'.format(endtime))

def build_null_files(src_loc, dest_loc, overwrite = False, file_type = "parquet"):
    """
    Create files with Null DNS entries

    Parameters:
    ===========
        src_file:
            Source file/s directory location.
        dest_loc:
            Destination file/s directory location.
        overwrite: BOOLEAN
            Overwrite existing file/s.
            Default = False
        file_type: STRING
            Destination file type (csv or parquet).
            Default = parquet
    Returns:
    ========
        Nothing
    """

    #####################################################################################
    ##  
    #####################################################################################

    overall_start = datetime.now()
    logger.info("Starting filter process")

    # CREATE STRUCTURE
    Path(dest_loc).mkdir(parents=True, exist_ok=True)

    logger.debug("Checking directory {}".format(src_loc))

    # WALK DIR
    for filename in os.listdir(src_loc):

        starttime = datetime.now()
        f = os.path.join(src_loc, filename)

        if os.path.isfile(f):
            raw_name = os.path.join(src_loc,str(os.path.basename(f)))
            dest_name = os.path.join(dest_loc,str(os.path.basename(f)))

        #CHECK IF FILE ALREADY EXISTS
        if overwrite == False and os.path.exists(dest_name) == True:
            logger.debug("File {} already exists, skipping".format(dest_name))
            continue
        elif overwrite == True and os.path.exists(dest_name) == True:
            os.remove(dest_name)

        logger.debug("Building Dataframes")

        df = pd.read_parquet(raw_name)

        logger.debug("Checking for nulls")
        s_dns = df[df["s_dns"].isnull()]
        d_dns = df[df["d_dns"].isnull()]

        final_df = pd.concat([s_dns, d_dns])

        # DUMP FILE AS CSV OR PARQUET
        if file_type == "csv":   
            final_df.to_csv(dest_name, headers = True)
        else:
            final_df.to_parquet(dest_name, compression= "snappy")    

        logger.debug("{} file {} is completed".format(file_type, dest_name))
        endtime = datetime.now() - starttime
        logger.debug('File filter runtime {}'.format(endtime))

    endtime = datetime.now() - overall_start
    logger.info('Total runtime {}'.format(endtime))    

def filter_dataframe(df, filter_vals, filter_column, filter_exclude = True, data_type = "int", ret_org = False, verbose = False):
    """
    Filter a zeke pandas dataframe.

    Parameters:
    ===========
        df:
            Source pandas dataframe.
        filter_vals:
            List values you wish to filter for.  This is ends with (default) or wildcard (*) only, can be mixed mode.
            * for a wildcard search
                example ends with : ["facebook.com", "twitter.com"]
                example wildcard with : ["facebook*", "*twitter"]
        filter_column:
            Dataframe column you want to search.
        filter_exclude: BOOLEAN
            Filter by exclusion.
                Default = True
        data_type: STRING
            Datatype for your filter
                int = integer
                string = string
                match = matching values (source and destination DNS values)
            Default = int
        ret_org: BOOLEAN
            Return original dataframe if no results gathered.
            Default = False
        verbose: BOOLEAN
            Verbose logging
            Default = False        
    Returns:
    ========
        Pandas DataFrame
    """

    #####################################################################################
    ##  Logging
    #####################################################################################

    if verbose == True:
        lvl = logging.DEBUG
        for handler in logger.handlers:
            handler.setLevel(lvl)

    #####################################################################################
    ##  
    #####################################################################################

    logger.debug("Filtering for {} in filter_column {}".format(data_type,filter_column))
    final_df = pd.DataFrame()

    #####################################################################################
    ##  
    #####################################################################################

    # SKIP NO VALUES
    if len(filter_vals) == 0:
        logger.warning("No filter for {}".format(data_type))
        final_df = pd.concat([final_df, df])
    # SKIP DNS VALUES IF DNS COLUMN IS NOT AVAILABLE
    elif ((filter_column == "sip" or filter_column == "dip") and "{}".format(filter_column) not in df.columns):
        logger.warning("Parameter {}_filter was selected but {} column does not exist!".format(filter_column, filter_column))
        logger.warning("Check source location file and run add_dns() to add dns entries!")
        final_df = pd.concat([final_df, df])
    # SKIP MATCH VALUES IF DNS COLUMN IS NOT AVAILABLE
    elif data_type == "match" and "s_dns" not in df.columns:
        logger.warning("Parameter match was selected but dns columns does not exist!")
        logger.warning("Check source location file and run add_dns() to add dns entries!")
        final_df = pd.concat([final_df, df])
    # SKIP IF YOU HAVE DNS COLUMN THAT IS NOT AVAILABLE
    elif filter_column == "s_dns" and "s_dns" not in df.columns:
        logger.warning("Parameter {} was selected but {} column does not exist!".format(filter_column, filter_column))
        logger.warning("Check source location file and run add_dns() to add dns entries!")
        final_df = pd.concat([final_df, df])
    # SKIP IF YOU HAVE DNS COLUMN THAT IS NOT AVAILABLE
    elif filter_column == "d_dns" and "d_dns" not in df.columns:
        logger.warning("Parameter {} was selected but {} column does not exist!".format(filter_column, filter_column))
        logger.warning("Check source location file and run add_dns() to add dns entries!")
        final_df = pd.concat([final_df, df])
    # VALID SEARCH
    else:
        # CHECK INTEGER VALUES
        if str(data_type).lower() == "int":
            # INCLUSIVE INT VALUEs
            if filter_exclude == False:
                filter_df = df[df[filter_column].isin(filter_vals)]
            # EXCLUSIVE INT VALUEs
            else:
                filter_df = df[~df[filter_column].isin(filter_vals)]
            
            final_df = pd.concat([final_df, filter_df])
            logger.debug("Found {} values for {}".format(len(filter_df.index),filter_vals))

        # CHECK SOURCE IP OR DESTINATION IP
        elif str(data_type).lower() == "string" and (filter_column == "sip" or filter_column == "dip"):
            for z in filter_vals:
                if "*" in z:
                    logger.debug("Wildcard search selected")
                    z = str(z).replace("*","")
                    filter_df = pd.DataFrame(df["{}".format(filter_column)].str.contains("{}".format(z))).query("{} == {}".format(filter_column, filter_exclude))    
                else:
                    filter_df = df.query("{} == '{}'".format(filter_column,z))

                final_df = pd.concat([final_df, filter_df])
                logger.debug("Found {} values for {}".format(len(filter_df.index),z))

        # CHECK SOURCE DNS OR DESTINATION DNS
        elif str(data_type).lower() == "string" and (filter_column != "sip" and filter_column != "dip"):
            for z in filter_vals:
                if "*" in z:
                    logger.debug("Wildcard search selected")
                    z = str(z).replace("*","")
                    filter_df = pd.DataFrame(df["{}".format(filter_column)].explode().str.contains("{}".format(z))).query("{} == {}".format(filter_column, filter_exclude))
                else:
                    filter_df = pd.DataFrame(df["{}".format(filter_column)].explode().str.endswith("{}".format(z))).query("{} == {}".format(filter_column, filter_exclude))
                          
                final_df = pd.concat([final_df, filter_df])
                logger.debug("Found {} values for {}".format(len(filter_df.index),z))    

        # CHECK MATCH
        elif str(data_type).lower() == "match":
            for z in filter_vals:
                logger.debug("Search for matches for {}".format(z))
                
                for y in filter_vals:
                    if "*" in z:
                        logger.debug("Wildcard search selected")
                        z = str(z).replace("*","")
                        f_src = pd.DataFrame(df["s_dns"].explode().str.contains("{}".format(z))).query("s_dns == {}".format(filter_exclude))
                        f_dest = pd.DataFrame(df["d_dns"].explode().str.contains("{}".format(y))).query("d_dns == {}".format(filter_exclude))
                    else:
                        f_src = pd.DataFrame(df["s_dns"].explode().str.contains("{}".format(z))).query("s_dns == {}".format(filter_exclude))
                        f_dest = pd.DataFrame(df["d_dns"].explode().str.endswith("{}".format(y))).query("d_dns == {}".format(filter_exclude))    

                    filter_df = pd.merge(f_src,f_dest,
                        how="inner", 
                        left_index = True, 
                        right_index = True)
                    
                    logger.debug("Found {} for match {} = {}".format(len(filter_df.index), z, y))
                    final_df = pd.concat([final_df, filter_df])

    if ret_org == True and len(final_df.index) == 0:
        logger.warning("No values found and ret_org = True")
        logger.warning("Returning original DataFrame")
        final_df = pd.concat([final_df, df])  

    logger.debug("Total values {} for filter type {}".format(len(final_df.index),filter_column)) 
    return final_df

def convert_parquet_to_csv(par_file, csv_file):
    """
    Create a csv file from a parquet file.

    Parameters:
    ===========
        par_file:
            Parquet file/s location.
        csv_file:
            Destination csv file.
    Returns:
    ========
        Nothing
    """
    df = pd.read_parquet(par_file)
    df.to_csv(csv_file)

def download_s3_folder(s3_loc, loc_dest, profile = "default"):
    """
    Download a AWS s3 folder to a local folder.
    Must have a AWS CLI Profile setup.

    Parameters:
    ===========
        s3_loc:
            S3 file location. No trailing /.
                example: s3://bucketname/folder
        loc_dest:
            Local destination.
        profile:
            AWS CLI Profile name
            Default = default
    Returns:
    ========
        Nothing
    """

    import boto3

    # LOCAL VARIABLES FOR BUCKET & BUCKET FOLDERS
    bucket_name = s3_loc.split("/")[2]
    bucket_folder= s3_loc.replace("s3://{}/".format(bucket_name),"")

    #####################################################################################
    ##  BOTO PROFILE LOAD
    #####################################################################################

    profname = boto3.session.Session(profile_name=profile)
    s3 = profname.client("s3")

    #####################################################################################
    ##  DOWNLOAD FILES
    #####################################################################################

    page = s3.get_paginator('list_objects_v2')
    all_obj = page.paginate(Bucket=bucket_name,Prefix=bucket_folder)

    for x in all_obj:
        for y in x['Contents']:
            if y != bucket_folder and y != "{}/".format(bucket_folder):
                if y["Key"] != "{}/".format(bucket_folder):
                    f_name = str(y["Key"]).replace(bucket_folder,"")
                    final_loc = "{}{}".format(loc_dest,f_name)

                    logger.info("Downloading {} to {}".format(f_name, final_loc))
                    s3.download_file(bucket_name,y['Key'],final_loc)

def build_filter_files(src_loc, dest_file = "", port_filter = None, port_exclude = False, src_filter = None, src_exclude = True, 
dest_filter  = None, dest_exclude = True, s_dns_filter = None, s_dns_exclude = True, d_dns_filter  = None, d_dns_exclude = True, 
match_filter = None, match_exclude = True, file_type = "parquet", overwrite = False, verbose = False):
    """
    Create filtered files. A default metadata.json will be created for historical filter identification purposes.

    Parameters:
    ===========
        src_loc: STRING
            Source folder location. No trailing slash.
                Example: /bronze/parquet/raw/2022/04/20
        dest_file: STRING
            Destination folder location for all filtering.
                Use a new folder name at the end.
                Data folder to be appended to the end
                Must have a file location.
            Example: /bronze/filtered/my_filter_name            
        port_filter: LIST
            Ports you want to filter on in list format.
            Example: [80, 443]
        port_exclude: BOOLEAN
            Exclusive or inclusive search on port_filter values.
                Exclusive = True (not in)
                Inclusive = False (in)
            Default: False
        src_filter: LIST
            Source IP filters you want to search for in list format.
                Will search for filters ending in unless a wildcard (*) is used.
                Wildcard location does not matter.
            Example w/o wildcard: ["127.0.0.1", "9.9.9.9"]
            Example with wildcard: ["127.*", "9.9.*"]
        src_exclude: TRUE
            Exclusive or inclusive search on src_filter values.
                Exclusive = True (not in)
                Inclusive = False (in)
            Default: True
        dest_filter: LIST
            Destination IP filters you want to search for in list format.
                Will search for filters ending in unless a wildcard (*) is used.
                Wildcard location does not matter.
            Example w/o wildcard: ["127.0.0.1", "9.9.9.9"]
            Example with wildcard: ["127.*", "9.9.*"]
        dest_exclude: BOOLEAN
            Exclusive or inclusive search on dest_filter values.
                Exclusive = True (not in)
                Inclusive = False (in)
            Default: True
        s_dns_filter: LIST
            Source DNS filters you want to search for in list format.
                Will search for filters ending in unless a wildcard (*) is used.
                Wildcard location does not matter.
            Example w/o wildcard: ["google.com", "facebook.com"]
            Example with wildcard: ["*google", "*facebook"]
        src_exclude: BOOLEAN
            Exclusive or inclusive search on s_dns_filter values.
                Exclusive = True (not in)
                Inclusive = False (in)
            Default: True
        d_dns_filter: LIST
            Destination IP filters you want to search for in list format.
                Will search for filters ending in unless a wildcard (*) is used.
                Wildcard location does not matter.
            Example w/o wildcard: ["google.com", "facebook.com"]
            Example with wildcard: ["*google", "*facebook"]
        d_dns_exclude: BOOLEAN
            Exclusive or inclusive search on dest_filter values.
                Exclusive = True (not in)
                Inclusive = False (in)
            Default: True 
        match_filter: LIST
            Source & Destination DNS filters you want to match for in list format.
                In order for a match to filter objects must be in both source and destination.
                The matching is for the entire list, and can match on any item in the list.
                Will search for filters ending in unless a wildcard (*) is used.
                Wildcard location does not matter.
            Example w/o wildcard: ["google.com", "facebook.com"]
            Example with wildcard: ["*google", "*facebook"] 
        match_exclude: BOOLEAN
            Exclusive or inclusive search on match_filter values.
                Exclusive = True (not in)
                Inclusive = False (in)
            Default: True
        file_type: STRING
            Destination file types. Parquet or CSV
            Example: parquet or csv
            Default: parquet
        overwrite: BOOLEAN
            Overwrite existing location.
            Example: False
            Default: False
    Returns:
    ========
        BOOLEAN: New file create 
    """ 

    #####################################################################################
    ##  Logging
    #####################################################################################

    if verbose == True:
        lvl = logging.DEBUG
        for handler in logger.handlers:
            handler.setLevel(lvl)

    #####################################################################################
    ##  SET DEFAULT LIST IF A FILTER PARAMETER IS NONE
    #####################################################################################

    logger.info("Starting filter process")

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

    if dest_file == "":
        logger.error("Must pass a dest_file parameter!")

    #####################################################################################
    ##  BUILD METADATA FILE
    #####################################################################################

    is_new = False
    overall_start = datetime.now()
    json_data = {}
    json_data["Port_Filter"] = {"exclude": port_exclude, "filter": port_filter}
    json_data["Source_IP_Filter"] = {"exclude": src_exclude, "filter": src_filter}
    json_data["Destination_IP_Filter"] = {"exclude": dest_exclude, "filter": dest_filter}
    json_data["Source_DNS_Filter"] = {"exclude": s_dns_exclude, "filter": s_dns_filter}
    json_data["Destination_DNS_Filter"] = {"exclude": d_dns_exclude, "filter": d_dns_filter}
    json_data["Match_Filter"] = {"exclude": match_exclude, "filter": match_filter}

    # CREATE STRUCTURE
    if len(dest_file) > 0:
        Path(dest_file).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(dest_file,"metadata.json"), "w") as f:
            json.dump(json_data, f)    
        
        dest_file = os.path.join(dest_file,"data")
        Path(dest_file).mkdir(parents=True, exist_ok=True)

    #####################################################################################
    ##  START FILTER PROCESS
    #####################################################################################

    tot_files = _total_cnt(src_loc)
    per_cnt = tot_cnt = int((0.10 * tot_files))
    log_cnt = 0
    tot_cnt = 0
    logger.debug("Processing {} files from {}".format(tot_files, src_loc))

    # WALK DIR
    for root, dir, dir_f in os.walk(src_loc):
        # NESTED LOOP FOR FILES
        for fname in dir_f:
            filename = os.path.join(root,fname)
            base_folder = os.path.basename(root)

            # INCREMENTAL BAR & VARIABLES
            tot_cnt += 1
            log_cnt += 1

            if log_cnt == per_cnt or tot_cnt == 1:
                logger.debug("Processed {} of {}".format(tot_cnt, tot_files))
                log_cnt = 0        

            starttime = datetime.now()
            logger.debug("Starting filter process for {}".format(filename))

            f = filename

            # BUILD DIRECTORY
            if os.path.isfile(f):
                
                raw_name = f
                dest_name = os.path.join(dest_file,base_folder,str(os.path.basename(f)))
                
                Path(os.path.join(dest_file,base_folder)).mkdir(parents=True, exist_ok=True)

            #CHECK IF FILE ALREADY EXISTS
            if overwrite == False and os.path.exists(dest_name) == True:
                logger.debug("File {} already exists, skipping".format(dest_name))
                continue
            elif overwrite == True:
                if os.path.exists(dest_name):
                    os.remove(dest_name)                           

            logger.debug("Building Dataframe/s")
            df = pd.read_parquet(raw_name)

            # RENAMING TO PREVENT ERRORS
            df.rename(columns={"id.orig_h": "sip", "id.resp_h": "dip", "id.resp_p": "port"}, inplace=True)

            is_new = True

            #####################################################################################
            ##  FILTERS
            #####################################################################################

            if len(port_filter) > 0:
                port_df = filter_dataframe(df = df, 
                    filter_vals = port_filter, 
                    filter_column = "port",
                    data_type = "int",
                    filter_exclude = port_exclude,
                    ret_org = False,
                    verbose = verbose)
            else:
                port_df = pd.DataFrame()

            if len(src_filter) > 0:
                src_df = filter_dataframe(df = port_df, 
                    filter_vals = src_filter, 
                    filter_column = "sip",
                    data_type = "string",
                    filter_exclude = src_exclude,
                    ret_org = False,
                    verbose = verbose)
            else:
                src_df = pd.DataFrame()

            if len(dest_filter) > 0:
                dest_df = filter_dataframe(df = port_df, 
                    filter_vals = dest_filter, 
                    filter_column = "dip",
                    data_type = "string",
                    filter_exclude = dest_exclude,
                    ret_org = False,
                    verbose = verbose)
            else:
                dest_df = pd.DataFrame()            

            if len(s_dns_filter) > 0:
                s_dns_df = filter_dataframe(df = port_df, 
                    filter_vals = s_dns_filter, 
                    filter_column = "s_dns",
                    data_type = "string",
                    filter_exclude = s_dns_exclude,
                    ret_org = False,
                    verbose = verbose)
            else:
                s_dns_df = pd.DataFrame()

            if len(d_dns_filter) > 0: 
                d_dns_df = filter_dataframe(df = port_df, 
                    filter_vals = d_dns_filter, 
                    filter_column = "d_dns",
                    data_type = "string",
                    filter_exclude = d_dns_exclude,
                    ret_org = False,
                    verbose = verbose)
            else:
                d_dns_df = pd.DataFrame()

            if len(match_filter) > 0: 
                match_df = filter_dataframe(df = port_df, 
                    filter_vals = match_filter, 
                    filter_column = "",
                    data_type = "match",
                    filter_exclude = match_exclude,
                    ret_org = False,
                    verbose = verbose)
            else:
                match_df = pd.DataFrame()

            #####################################################################################
            ##  FILTER FOR SOURCE, DESTINATION AND MATCH
            #####################################################################################

            filter_df = pd.concat([src_df, dest_df, s_dns_df, d_dns_df, match_df])

            df_match = port_df[port_df.index.isin(filter_df.index)]
            df_nomatch = port_df.drop(df_match.index)

            # SET COLUMNS BACK TO ORIGINAL FORMAT
            df_nomatch.rename(columns={"sip": "id.orig_h", "dip": "id.resp_h", "port": "id.resp_p"}, inplace=True)

            logger.debug("Exporting for filters")

            # DUMP FILE AS CSV OR PARQUET
            if df_nomatch.empty == True:
                logger.debug("No filtered data for {}".format(fname))
            else:
                if file_type == "csv":
                    df_nomatch.to_csv(str(dest_name).replace(".parquet",".csv"), header = True)
                else:
                    df_nomatch.to_parquet(dest_name, compression= "snappy")   

            del [df, src_df, dest_df, match_df, s_dns_df, d_dns_df, filter_df, df_match, df_nomatch]

            logger.debug("{} file {} is completed".format(file_type, dest_name))
            endtime = datetime.now() - starttime
            logger.debug('File filter runtime {}'.format(endtime))

            #####################################################################################
            ##  
            #####################################################################################

    endtime = datetime.now() - overall_start
    logger.info('Filter process complete {}'.format(endtime))

    return is_new

def build_delta_files(src_loc, delta_file_loc, delta_file_type = "parquet", overwrite = False):
    """
    Create a delta file from a parquet folder location or file.
    Current unit of measurement is milliseconds and minutes.

    Parameters:
    ===========
        src_loc: STRING
            Parquet folder or single file location.  Must be a parquet files!
            Folder example: /bronze/filtered/filterloc
            File example: /bronze/filtered/filterloc/single_file.parquet
        delta_file_loc: STRING
            Destination of delta file.
            Example: /silver/parquet/foldername
        delta_file_type: STRING
            Destination file types. Parquet or CSV
            Example: parquet or csv
            Default: parquet
        overwrite: BOOLEAN
            Overwrite existing location.
            Example: False
            Default: False
    Returns:
    ========
        Nothing
    """

    # Delta time measures
    unit_measure_ms = "milliseconds"
    unit_measure_mi = "minutes"

    #####################################################################################
    ##  Main Process
    #####################################################################################

    starttime = datetime.now()
    logger.info("Starting Delta process")

    # LOOP FOR BAR ONLY
    for i in range(5):
        if os.path.exists(delta_file_loc) and overwrite == True:
            shutil.rmtree(delta_file_loc) 

        Path(delta_file_loc).mkdir(parents=True, exist_ok=True)

        logger.debug("Loading Parquet/s from {}".format(src_loc))

        try:
            df = pd.read_parquet(src_loc, columns=["id.orig_h", "id.resp_h", "id.resp_p", "proto", "ts", "orig_ip_bytes", "resp_ip_bytes", "source_file", "src_row_id"])
            df.rename(columns={"id.orig_h": "sip", "id.resp_h": "dip", "id.resp_p": "port", "orig_ip_bytes": "src_bytes", "resp_ip_bytes": "dest_bytes"}, inplace=True)
        except:
            logger.debug("columns (id.orig_h, id.resp_h, id.resp_p, proto, ts) not found.  Trying renamed columns (sip, dip, port, proto, ts)")
            try:
                df = pd.read_parquet(src_loc, columns=["sip", "dip", "port", "proto", "ts", "src_bytes", "dest_bytes", "source_file", "src_row_id"])
            except BaseException as err:
                logger.error("Failure to load parquet files in folder {}".format(src_loc))
                logger.error(err)
                sys.exit(1)

        if df.empty == True:
            logger.error("No records for file {}".format(src_loc))
            logger.error("Cannot create a delta file")
            sys.exit(1)

        #####################################################################################
        ##  CONFIGURE DATAFRAME
        #####################################################################################

        logger.debug("Configuring DataFrame")

        # BUILD ROWID, CONNECTION_ID, DATETIME & RENAME COLUMNS
        df.drop_duplicates(inplace=True, keep="first")
        df['rowid'] = df.reset_index().index

        # CREATE DATETIME
        try:
            df["datetime"] = pd.to_datetime(df["ts"], unit="s")
        except:
            try:
                logger.warning("Unable to convert to second/s trying millisecond/s")
                df["datetime"] = pd.to_datetime(df["ts"].astype('datetime64[ns]'), unit="ms")
            except BaseException as err:
                logger.error("Error with date conversion")
                logger.error(err)
        
        df["connection_id"] = df.groupby(["sip", "dip",	"port", "proto"]).ngroup() 
        df.sort_values(["connection_id", "datetime"], inplace=True)

        logger.debug("Configuring Delta/s")

        #####################################################################################
        ##  BUILD FEATURESET
        #####################################################################################

        logger.debug("Building Delta/s")
        st_fm_tm = datetime.now()

        df["delta"] = df.groupby("connection_id")["datetime"].diff()
        
        # FIX FOR PANDAS 2.0
        #df["delta_ms"] = df["delta"].astype("timedelta64[ms]").astype(float)
        df["delta_ms"] = df["delta"].dt.total_seconds() * 1000
        df["delta_mins"] = df["delta_ms"] / 60000

        #GET EPOCH TIME
        epoch = int(time.time())

        # DUMP FILE AS CSV OR PARQUET
        if delta_file_type == "csv":   
            delta_file = os.path.join(delta_file_loc,"delta_{}.csv".format(epoch))
            df.to_csv(delta_file, columns = ["connection_id", "sip", "dip", "port", "proto", "datetime", "src_bytes", "dest_bytes", "delta_ms", "delta_mins", "source_file", "src_row_id"])
        else:
            delta_file = os.path.join(delta_file_loc,"delta_{}.parquet".format(epoch))
            export_df = df[["connection_id", "sip", "dip","port", "proto", "datetime", "src_bytes", "dest_bytes", "delta_ms", "delta_mins", "source_file", "src_row_id"]]
            # MIGHT HAVE TO ENABLE AT A LATER TIME
            #export_df.to_parquet(delta_file, compression= "snappy", allow_truncated_timestamps=True)
            export_df.to_parquet(delta_file, compression= "snappy", use_deprecated_int96_timestamps=True)

        break

    logger.debug("Delta File {} is completed".format(delta_file))
    endtime = datetime.now() - starttime
    logger.info('Delta process is completed {}'.format(endtime))

def build_bronze_layer(src_loc, bronze_loc, start_dte = "", end_dte = "", dns_file = "", ds_type = "conn", overwrite = False, verbose = False):
    """
    Create a bronze data layer for a source folder location.  
    Bronze data will only use tcp data and will include source and destination DNS.

    Parameters:
    ===========
        src_loc: STRING 
            Source raw data folder.
            Folder example: /source/       
        bronze_loc: STRING
            Bronze folder location. Files will be parquet format.
            Example: /bronze/raw/parquet
        start_dte: DATETIME
            Filter start date and time.
        end_dte: DATETIME
            Filter end date and time.
        dns_file:
            Source DNS lookup file (must be in parquet format).
        overwrite:
            Overwrite existing files.
            Default = False
        verbose:
            Verbose logger.
            Default = False        
    Returns:
    ========
        BOOLEAN: Is a new file
    """ 

    starttime = datetime.now()
    logger.debug("Starting Bronze Layer Process")
    is_new = False

    # CREATE STRUCTURE
    Path(src_loc).mkdir(parents=True, exist_ok=True)
    Path(bronze_loc).mkdir(parents=True, exist_ok=True)

    # BUILD DNS DATA IF SPECIFIED
    logger.debug("Building DNS dataframe")
    if dns_file == "":
        logger.warning("No dns_file selected.")
        logger.warning("Will skip DNS identification process")
        is_dns = False
    else:
        dns_df = pd.read_parquet(dns_file)
        dns_df = dns_df[dns_df["wildcard_ip"].str.contains("-") == False]
        dns_df[["oct1", "oct2", "oct3", "oct4"]] = dns_df['whitelist_ip'].str.split('.', expand=True).replace("X","0").astype("int32")    
        is_dns = True

    #tot_files = len(os.listdir(src_loc))
    tot_files = _total_cnt(src_loc)
    per_cnt = tot_cnt = int((0.10 * tot_files))
    log_cnt = 0
    tot_cnt = 0
    logger.info("Processing {} files from {}".format(tot_files, src_loc))

    # NO FILES EXIT THE PROCESS
    if tot_files == 0:
        logger.error("{} files located at {}!  Please use another location!".format(tot_files, src_loc))
        sys.exit(1)

    # WALK DIR
    #for filename in os.listdir(src_loc):
    for root, dir, dir_f in os.walk(src_loc):
        for fname in dir_f:
            f = os.path.join(root,fname)

            tot_cnt += 1
            log_cnt += 1

            if log_cnt == per_cnt or tot_cnt == 1:
                logger.debug("Processed {} of {}".format(tot_cnt, tot_files))
                log_cnt = 0

            if os.path.isfile(f):
                raw_name = os.path.join(bronze_loc,os.path.basename(root),str(os.path.basename(f)))
                fold_name = os.path.join(bronze_loc,os.path.basename(root))
                par_name = os.path.join(bronze_loc,os.path.basename(root),str(os.path.basename(f).replace(".txt",".parquet").replace(".parquet.gz",".parquet").replace(".log.gz",".parquet")))
                dest_loc = os.path.dirname(par_name)

                # SKIP FILE IF THE FILE EXISTS AND OVERWRITE = False
                if overwrite == False:
                    if os.path.exists(par_name):
                        logger.debug("Parquet file {} already exists, skipping file.".format(par_name))
                        continue
                try:
                    is_new = True

                    Path(fold_name).mkdir(parents=True, exist_ok=True)

                    build_raw(src_file = f,
                        dest_parquet_file = par_name,
                        ds_type = ds_type,
                        start_dte = start_dte,
                        end_dte = end_dte,
                        overwrite = overwrite,
                        verbose = verbose)

                    if is_dns == True:
                        add_dns(src_file = par_name, 
                        dest_loc = dest_loc, 
                        file_type = "parquet",
                        dns_df = dns_df,
                        verbose = verbose)

                except BaseException as err:
                    logger.error("Failure on file {}".format(f))
                    logger.error(err)
    
    endtime = datetime.now() - starttime
    logger.info("Bronze file process completed {}".format(endtime))

    return is_new

def unzip(zip_file, dest_loc, zip_type = "tar"):
    """
    Unzip a source raw file. Only tar files are available for unzipping.

    Parameters:
    ===========
        zip_file: STRING
            Source zip file location.
            Folder example: /temp/file.tar
        dest_loc: STRING
            Destination folder location where the file will unzip.
            Example: /temp/raw
        zip_type: STRING
            Type of zip file.
            Example: "tar" 
            Default = "tar"

    Returns:
    ========
        Nothing
    """   
    import tarfile

    if zip_type == "tar":
        logger.info("Unzipping file {} to {}".format(zip_file, dest_loc))

        try:
            Path(dest_loc).mkdir(parents=True, exist_ok=True)

            # WINDOWS CANNOT ACCEPT COLONS (:)
            # REPLACE WITH UNDERSCORE (_)
            if platform.system() == "Windows":
                f = tarfile.open(zip_file)
                for x in f:
                    x.name = x.name.replace(":","_")

                f.extractall(dest_loc)
                f.close()
            else:
                f = tarfile.open(zip_file)
                f.extractall(dest_loc)
                f.close()

            logger.info("Successfully unzipped files")
        except BaseException as err:
            logger.error(err)
    
def get_latest_file(folder_loc, file_type = "parquet"):
    """
    Get latest file file from a folder location and file type.

    Parameters:
    ===========
        folder_loc: STRING
            Source zip file location.
            Folder example: /temp/silver/delta
        delta_file_type: STRING
            Type of delta file. CSV or Parquet.
            Default = "parquet"
    Returns:
    ========
        File
    """     
    import glob

    if file_type == "log":
        final_src = os.path.join(folder_loc,"log_*")
        file_lst = glob.glob(final_src)
    else:
        final_src = os.path.join(folder_loc,"*.{}".format(file_type))
        file_lst = glob.glob(final_src)
    
    try:
        max_file = max(file_lst, key=os.path.getctime)
    except BaseException as err:
        logger.error("Failure finding file in {}".format(folder_loc))
        logger.error(err)
        max_file = None


    return max_file