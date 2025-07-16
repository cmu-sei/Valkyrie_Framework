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
##  FUNCTIONS
#####################################################################################

def _percentage(part, whole):
    return part/whole

def _find_beacons(y_hc, deltas, max_variance, min_records):
    clusters = {}
    curr = deltas[0][0]
    beacons = []
    for i in range(len(deltas)):
        new_id = deltas[i][0]
        if new_id != curr:
            for cluster in clusters:
                if curr not in beacons:
                    curr_list = clusters[cluster]
                    failed = False
                    if len(curr_list) >= min_records:
                        median = np.median(curr_list)                      
                        for number in curr_list:
                            if curr not in beacons:
                                if not abs(number - median) / median <= max_variance:
                                    failed = True
                        if not failed:
                            beacons.append(curr)
            curr = new_id
            clusters = {}
        cluster = y_hc[i]
        if cluster not in clusters:
            clusters[cluster] = []
        clusters[cluster].append(deltas[i][1])
    for cluster in clusters:
        if curr not in beacons:
            curr_list = clusters[cluster]
            failed = False
            if len(curr_list) >= min_records:
                median = np.median(curr_list)             
                for number in curr_list:
                    if curr not in beacons:
                        if not abs(number - median) / median <= max_variance:
                            failed = True
                if not failed:
                    beacons.append(curr)
    return beacons 

def _build_gold_beacons(delta_file, delta_column, gold_loc, beacon_conns, overwrite = False):

    #####################################################################################
    ##  
    #####################################################################################

    logger.info("Building gold file")

    # LOAD FULL DATASET (KEEP NULL DATES)
    dataset_full = pd.read_parquet(delta_file).sort_values(by=["connection_id"])

    # CREATE BEACON DATASET
    df_beacons = pd.DataFrame.from_dict(beacon_conns, orient='index')

    # GET BEACON DATA
    df_delta = pd.merge(dataset_full, df_beacons, how="inner", left_on=["connection_id"], right_on = ["connection_id"])

    # WINDOWS HAS A PROBLEM WITH SEARCHING FOR PATHS WITH \
    # ADDED FILE NAME COLUMN TO SEARCH BY FILE_NAME REGUARDLESS OF OS
    # df_delta["file_name"] = df_delta["source_file"].apply(lambda z: os.path.basename(z))
    df_delta["file_name"] = df_delta["source_file"].str.replace(chr(92),chr(47), regex=False)
    
    logger.debug("Total delta file records {}".format(len(df_delta)))

    # FINAL DATAFRAME
    final_gold_df = pd.DataFrame()
        
    # LOOP THROUGH ORIGINAL FILES FOR FULL DATA
    for x in df_delta["source_file"].unique():

        # REPLACE PATH FOR WINDOWS
        # MODIFIED FOR WINDOWS OS FILES
        # PANDAS TREATS \ AS AN ESCAPE CHARACTER
        fn_x = str(x).replace(chr(92),"/")

        logger.debug("Gathering beacon data from {}".format(x))

        # MODIFIED FOR WINDOWS OS FILES
        # PANDAS TREATS \ AS AN ESCAPE CHARACTER
        vals = df_delta[["src_row_id", "file_name", "datetime", "likelihood", "{}".format(delta_column)]].query("file_name == '{}'".format(fn_x))

        # IF SOURCE FILE DOES NOT EXIST SKIP
        if os.path.exists(x) == True:
            org_df = pd.read_parquet(x)

            # MODIFIED FOR WINDOWS OS FILES
            # PANDAS TREATS \ AS AN ESCAPE CHARACTER
            org_df["file_name"] = fn_x

            df_og = pd.merge(org_df,vals[["src_row_id", "file_name", "datetime", "likelihood", "{}".format(delta_column)]],how="inner", left_on=['src_row_id', 'file_name'], right_on=['src_row_id', 'file_name'])
            logger.debug("Total records found {} for file {}".format(len(df_og),x))
        else:
            logger.info("Source File {} does not exist...skipping".format(x))
            df_og = df_delta[["sip", "dip", "port", "src_row_id", "file_name", "datetime", "likelihood", "{}".format(delta_column)]].query("file_name == '{}'".format(fn_x))
            df_og[["uid", "id.orig_p", "id.resp_p", "proto", "service", "duration", "orig_bytes", "resp_bytes", "conn_state", "local_orig", "local_resp", "missed_bytes", "history", "orig_pkts", "orig_ip_bytes", "resp_pkts", "resp_ip_bytes", "community_id", "likelihood"]] = np.NaN
            df_og["ts"] = df_og["datetime"]
            df_og["id.resp_p"] = df_og["port"]
            df_og.drop("port", axis=1, inplace=True)

        final_gold_df = pd.concat([final_gold_df, df_og])

    if os.path.exists(gold_loc) and overwrite == True:
        shutil.rmtree(gold_loc)

    # DUMP GOLD DATA TO PARQUET
    Path(gold_loc).mkdir(parents=True, exist_ok=True)
    
    #GET EPOCH TIME
    epoch = int(time.time())
    
    gold_file = os.path.join(gold_loc, "beacon_{}.parquet".format(epoch))
    
    try:
        final_gold_df.sort_values(by=["id.orig_h", "id.resp_h", "ts"], inplace=True)
        final_gold_df.to_parquet(gold_file, compression="snappy", use_deprecated_int96_timestamps=True)
        logger.info("Gold file {} created".format(gold_file))
    except BaseException as err:
        logger.error(err)
        try:
            logger.warning("Source columns (id.orig_h, id.resp_h, ts) do not exist.")
            logger.warning("Trying renamed columns (sip, dip, datetime).")

            # NO NEED TO RENAME DATETIME
            final_gold_df.rename(columns={"sip": "id.orig_h", "dip": "id.resp_h"}, inplace = True)
            final_gold_df.sort_values(by=["id.orig_h", "id.resp_h", "ts"], inplace=True)

            final_gold_df.to_parquet(gold_file, compression="snappy", use_deprecated_int96_timestamps=True)
            logger.info("Gold file {} created".format(gold_file))
        except BaseException as err:
            logger.error("Failure to create gold parquet file {}".format(gold_file))
            logger.error("Columns for final dataframe {}".format(final_gold_df.columns))
            logger.error(err)    
    
    return gold_file

def _build_beacon_df(delta_file, beacons_conns, sort_by = "connection_count", pass_df = pd.DataFrame(), asc = False, avg_delta = 0):

    # LOAD FULL DATASET (KEEP NULL DATES)
    df_full = pd.read_parquet(delta_file).sort_values(by=["connection_id"])

    # CREATE BEACON DATASET
    df_beacons = pd.DataFrame.from_dict(beacons_conns, orient='index')

    # GET BEACON DATA
    df_delta = pd.merge(dataset_full, df_beacons, how="inner", left_on=["connection_id"], right_on = ["connection_id"])

    if sort_by == "connection_count":
        # LOAD FULL DATASET (KEEP NULL DATES)
        dataset_full = df_full

        # df_delta = dataset_full[dataset_full["connection_id"].isin(beacons_conns)].copy()
        df_delta.rename(columns={"sip": "source_ip", "dip": "dest_ip", "datetime": "dt"}, inplace = True)

        # BUILD AGGREGATIONS
        # ONLY INCLUDE DELTA WHEN USING ML ALGORITHMS
        if sort_by == "packet_unq_per" or sort_by == "group_count":
            df_delta = df_delta.groupby(["source_ip", "dest_ip", "port"]).agg(
                connection_count=("dt", "count"))            
        else:
            # REMOVE ZERO'S IF DELTA AVG CHECK IS >= 5
            # THIS ONLY APPLIES TO DBSCAN BY VARIANCE OPTION
            # EVERYTHING ELSE ZEROS WILL BE INCLUDED IN THE AVERAGE DELTA
            if avg_delta >= 5:
                df_delta.loc[df_delta["delta_mins"]< 2.0, "delta_mins"] = np.nan        

            df_delta = df_delta.groupby(["source_ip", "dest_ip", "port"]).agg(
                connection_count=("dt", "count"),
                avg_delta=("delta_mins", "mean"))  

        df2 = df_delta.reset_index()
        
    else:
        # LOAD FULL DATASET (KEEP NULL DATES)
        dataset_full = pd.merge(df_full[["connection_id", "sip", "dip", "datetime", "port"]], pass_df, how="inner", left_on=['connection_id'], right_on=['connection_id'])

        # GET BEACON DATA
        # df_delta = dataset_full[dataset_full["connection_id"].isin(beacons_conns)].copy()
        df_delta.rename(columns={"sip": "source_ip", "dip": "dest_ip", "datetime": "dt"}, inplace = True)

        # BUILD AGGREGATIONS
        # ONLY INCLUDE DELTA WHEN USING ML ALGORITHMS
        if sort_by == "packet_unq_per" or sort_by == "group_count":
            # BUILD DATAFRAME & REORDER
            df_delta = df_delta.groupby(["source_ip", "dest_ip", "port", "{}".format(sort_by)]).agg(
                connection_count=("dt", "count"))
            
            df_delta = df_delta.reset_index()
            df_delta = df_delta[["source_ip", "dest_ip", "port", "connection_count", "{}".format(sort_by)]]

            df2 = df_delta
        else:
            # REMOVE ZERO'S IF DELTA AVG CHECK IS >= 5
            # THIS ONLY APPLIES TO DBSCAN BY VARIANCE OPTION
            # EVERYTHING ELSE ZEROS WILL BE INCLUDED IN THE AVERAGE DELTA
            if avg_delta >= 5:
                df_delta.loc[df_delta["delta_mins"]< 2.0, "delta_mins"] = np.nan

            df_delta = df_delta.groupby(["source_ip", "dest_ip", "port"]).agg(
                connection_count=("dt", "count"),
                avg_delta=("delta_mins", "mean"))  

            df2 = df_delta.reset_index()

    if len(df2) != 0:
        # SORT DF BY SORT_BY
        if sort_by == "connection_count":
            df2.sort_values(["{}".format(sort_by), "dest_ip"], inplace=True, ascending=asc)
        else:
            df2.sort_values(["{}".format(sort_by), "connection_count", "dest_ip"], inplace=True, ascending=asc)

    return df2

def _non_gold_cli(delta_file, beacons_conns, sort_by = "connection_count", pass_df = pd.DataFrame(), asc = False, avg_delta = 0):

    # BUILD BEACON DATAFRAME
    df = _build_beacon_df(
        delta_file = delta_file, 
        beacons_conns = beacons_conns, 
        sort_by = sort_by, 
        pass_df = pass_df,
        asc = asc,
        avg_delta = avg_delta
        )

    # BUILD RESULTS
    if df.empty:
        print("X" * 50, " POTENTIAL BEACONS (0)", "X" * 50)
        print("NONE")
        print("X" * 121)  
    else:
        
        # GET NUMBER OF UNIQUE BEACONS
        num_b = df["dest_ip"].nunique()

        print("X" * 50, " POTENTIAL BEACONS ({})".format(num_b), "X" * 50)

        # DISPLAY ALL RESULTS
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            print(df)

        print("X" * 121)     

def agglomerative_clustering(delta_file, delta_column, max_variance, min_records, cluster_factor, line_amounts, min_delta_time, gold_loc = "", overwrite = False, verbose = False):
    """
    Run an agglormerative clustering algorithm against a delta file to identify cluster points to be used to find a beacon.\n

    Parameters:
    ===========
    delta_file:
        Source delta file.\n
    delta_column: 
        Source delta column. \n
    max_variance:
        Variance threshold for any potential beacons.\n
    min_records:
        Minimum number of delta records to search.\n
    cluster_factor:
        Cluster factor percentage.\n
    line_amounts:
        Line amounts to process at a time, in list format.\n
    min_delta_time:
        Minimum delta time to search by, in milliseconds.\n
    gold_loc: STRING
        Results file location. Blank string ("") for no result file.\n
        Default: "" \n
    overwrite: BOOLEAN 
        Overwrite existing location.  True or False (case-sensistive). \n
        Default: False \n
    verbose: BOOLEAN 
        Verbose logger.\n
        default = False                               

    Returns:
    =======
    Gold File Path: STRING
    """
    from sklearn.cluster import AgglomerativeClustering

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
    start = time.time()

    # LOAD DATASET
    dataset = pd.read_parquet(delta_file).sort_values(by=["connection_id"])
    X = dataset.iloc[:, np.r_[0,6]].values
    Y = dataset.iloc[:, np.r_[0:3,6]].values

    logger.info("{} deltas found and sorted in {} seconds".format(len(X), time.time() - start))
    logger.info("Looking for beacons using a maximum variance of {}% across at least {} deltas.".format(max_variance,min_records))

    bar = Bar("\t* Searching for Beacons (Agglomerative Clustering)", max=len(line_amounts), suffix="%(index)d/%(max)d connections | %(elapsed_td)s")

    for max_lines in line_amounts:
        start = time.time()
        bar.next()
        curr_deltas = []
        calculations = 0
        beacons = []

        # DO NOTHING IF YOU HAVE NO VALUES
        if len(X) == 0:
            logger.info("{} deltas found!  Try changing the parameters!".format(len(X), time.time() - start))
            break
        else:
            curr_id = X[0][0]
        
        for i in range(len(X)):
            delta = X[i]
            new_id = delta[0]

            if delta[0] != curr_id or (i == len(X) - 1):
                if (len(curr_deltas) >= int(max_lines) and len(curr_deltas) >= int(min_records)):
                    
                    num_clusters = round(cluster_factor * len(curr_deltas)) + 1

                    # RUN THE CLUSTERING
                    hc = AgglomerativeClustering(n_clusters = num_clusters, affinity = 'euclidean', linkage = 'single')
                    y_hc = hc.fit_predict(curr_deltas)
                    calculations += 1
                    new_beacons = _find_beacons(y_hc, curr_deltas, max_variance, min_records)

                    print(new_beacons)

                    if len(new_beacons) > 0:
                        beacons += new_beacons
                        logger.warning("Possible Beacon: \n\
                        Session # {} \n\
                        Src:    {} \n\
                        Dst:    {}".format(Y[i-1][0], Y[i-1][1], Y[i-1][2]))
                    
                    # CLEAR THE VARIABLES FOR NEW CLUSTERING
                    curr_deltas = []
                    curr_id = new_id
            if delta[1] >= min_delta_time:
                curr_deltas.append(delta)
        
        logger.info("{}s to process dataset using {} lines at a time ({} total calculations)".format(time.time() - start, max_lines, calculations))

    logger.debug("Beacon connection_id/s {}".format(beacons))

    # OVERWRITE DELETE GOLD FILES
    if overwrite == True:
        if os.path.exists(gold_loc) and overwrite == True:
            shutil.rmtree(gold_loc)        

    # BUILD GOLD FILE
    if len(gold_loc) > 0 and len(beacons) > 0:
        gold_file = _build_gold_beacons(
            delta_file = delta_file,
            delta_column = delta_column,
            gold_loc = gold_loc,
            beacon_conns = beacons,
            overwrite = overwrite
        )
    else:
        gold_file = None

    bar.finish()
    
    endtime = datetime.now() - starttime
    logger.info("Found {} possible beacons".format(len(beacons)))
    logger.info("Total runtime {}".format(endtime))

    return gold_file

def dbscan_clustering(delta_file, delta_column, minimum_delta, spans = [], minimum_points_in_cluster = 4, minimum_likelihood = .70, gold_loc = "", overwrite = False, verbose = False):
    """
    Run a DBSCAN cluster algorithm against a delta file to identify cluster points to be used to find a beacon.\n

    Parameters:
    ===========
    delta_file:
        Source delta file.\n
    delta_column:
        Source delta column. \n
    minimum_delta:
        Minimum number of delta records to search using your delta column.\n
    spans: LIST 
        Spans you wish to search, in list format. Minimum number of delta records to search using your delta column.\n
        Example: [[0, 5], [5, 10]] (Will search two spans 0-5 and 5-10).
        Default = []\n
    minimum_points_in_cluster: INT
        Minimum points needed for a cluster.\n
        Default = 4\n
    minimum_likelihood: FLOAT
        Minimum likelihood value to identify a beacon.\n
        Default = .70\n
    gold_loc: STRING
        Results file location. Blank string ("") for no result file.\n
        Default = ""\n
    overwrite: BOOLEAN
        Overwrite existing location.\n
        Example: False \n
        Default: False \n
    verbose - Verbose logger.\n
        Default = False

    Returns:
    ========
    Gold File Location: STRING
    """

    from sklearn.cluster import DBSCAN
    from scipy.spatial.distance import cdist
    from sklearn import metrics
    from numpy import unique
    from numpy import where

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

    ds = pd.read_parquet(delta_file).query("{} > {}".format(delta_column, minimum_delta))
    ds.rename(columns={"Unnamed: 0": "id"}, inplace=True)

    # convert delta ms to minutes
    ds["delta"] = ds["{}".format(delta_column)]
    ds.head(10)

    # get unique connection_ids {sip, dip, port, proto}
    start_time = time.time()
    connection_ids = ds.connection_id.unique()
    logger.info("{} unique connection_ids found ({}) seconds".format(len(connection_ids), (time.time()-start_time)))
    beacons = {}
    beacon_num = 1
    dbl_break = False

    starttime = datetime.now()
    start_time = time.time()

    id = time.strftime('%Y%m%d-%H%M%S')
    start_time = time.time()
    connection_count = 0
    log_cnt = 0
    tot_cnt = int((0.10 * len(connection_ids)))

    logger.info("Searching for beacons")
    bar = Bar("\t* Searching for Beacons (DBScan)", max=len(connection_ids), suffix="%(index)d/%(max)d connections | %(elapsed_td)s")

    if len(connection_ids) == 0:
        logger.warning("No connections found for DBScan")
        print("\t* WARNING: No connections found for DBScan")

    for connection_id in connection_ids:
        connection_count += 1
        log_cnt += 1
        bar.next()

        # GET ALL OF THE RECORDS FROM THE DELTA FILE WITH THIS CONNECTION_ID
        f = ds.query("connection_id == {}".format(connection_id))

        # PRINT MESSAGE AFTER 10% PERCENT COMPLETE
        if log_cnt == tot_cnt or connection_count == 1:
            log_cnt = 0
            logger.info("Evaluation #{} of {} ID: {}: {} original records...".format(connection_count, len(connection_ids), connection_id, len(f)))
        
        # NEED AT LEAST N DELTA RECORDS TO MAKE IT INTERESTING
        if len(f) <= minimum_points_in_cluster:  
            continue

        #X = f.iloc[:, [1, 7]]  # X = [connection_id, delta time in milliseconds]
        X = f[["connection_id","delta"]]

        # HERE WE DBSCAN CLUSTER OVER SEVERAL DIFFERENT EPSILON VALUES CALCULATED FROM TIME_SPANS
        # WE PICKED ARBITRARY SPANS OF TIME IN MINUTES, BUT THEY HAVE SERVED US WELL IN THE RESULTS
        span_count = 0
        for span in spans:
            span_count += 1
            #logger.info("Evaluating {} span {}...".format(connection_id, span))
            eps = ((span[1] - span[0]) / 2) * .10 # this is our eps calculation: take a span's difference, and halve it, then multiply by .10
        
            t_time = time.time()
            # RUN DBSCAN CLUSTERING MODEL...
            dbscan = DBSCAN(eps=eps, min_samples=minimum_points_in_cluster).fit(X)
            core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
            core_samples_mask[dbscan.core_sample_indices_] = True

            (unique, counts) = np.unique(dbscan.labels_, return_counts=True)
            frequencies = np.asarray((unique, counts)).T
            
            dbscan_cluster_data = pd.DataFrame()
            dbscan_cluster_data['delta'] = f["delta"]
            dbscan_cluster_data['cluster'] = dbscan.labels_
            dbscan_cluster_data = dbscan_cluster_data.groupby(["cluster"])["cluster"].count().reset_index(name="count")
            
            # CALCULATE LIKELIHOOD OF EACH CLUSTER
            likelihood = _percentage(dbscan_cluster_data['count'], dbscan_cluster_data['count'].sum())
            
            # // TODO: NEED TO EXPAND UPON LIKELIHOOD CALCULATION
            # COULD WE ADD THIS NUMBER OF ITEMS IN THE CLUSTER VS THE LARGEST CLUSTER OVERALL?
            # VS THE LARGEST CLUSTER IN THIS TIME SPAN?
            dbscan_cluster_data["likelihood"] = likelihood

            if dbscan_cluster_data["likelihood"].any() > minimum_likelihood:
                cols = [col for col in dbscan_cluster_data.columns if col == 'likelihood']
                dbscan_cluster_data.loc[dbscan_cluster_data['cluster'] == -1, cols] = 0
                for index, row in dbscan_cluster_data.iterrows():
                    if row['cluster'] > -1:
                        if row["likelihood"] > minimum_likelihood:
                            
                            logger.warning("Possible Beacon: \n\
                            Session # {} \n\
                            Src:    {} \n\
                            Dst:    {} \n\
                            Likelihood {}".format(f["connection_id"].iloc[0], f["sip"].iloc[0], f["dip"].iloc[0], row["likelihood"]))

                            beacons[beacon_num] = {}
                            beacons[beacon_num]["connection_id"] = connection_id
                            beacons[beacon_num]["likelihood"] = row["likelihood"] * 100
                            beacon_num +=1                            
                            
                            #beacons.append(f["connection_id"].iloc[0])

                            # POSSIBLE BEACON FOUND NO NEED TO CONTINUE
                            # SET A DOUBLE BREAK VARIABLE
                            dbl_break = True

            # BREAK THE ORIGINAL FOR LOOP FOR THE CONNECTION                
            if dbl_break == True:
                dbl_break = False
                break                        
    
    logger.debug("Beacon connection_id/s {}".format(beacons))

    # OVERWRITE DELETE GOLD FILES
    if overwrite == True:
        if os.path.exists(gold_loc) and overwrite == True:
            shutil.rmtree(gold_loc)        

    # BUILD GOLD FILE
    if len(gold_loc) > 0 and len(beacons) > 0:
        gold_file = _build_gold_beacons(
            delta_file = delta_file,
            delta_column = delta_column,
            gold_loc = gold_loc,
            beacon_conns = beacons,
            overwrite = overwrite
        )
    else:
        gold_file = None

    bar.finish()

    endtime = datetime.now() - starttime
    logger.info("{} clusters processed".format(connection_count))
    logger.info("Found {} possible beacons".format(len(beacons)))
    logger.info("Total runtime {}".format(endtime))

    return gold_file

def dbscan_by_variance(delta_file, delta_column, avg_delta, conn_cnt = 5, span_avg = 15, variance_per = 10, minimum_likelihood = 70, gold_loc = "", overwrite = False, verbose = False):
    """
    Run a DBSCAN cluster by filtering out records by delta variance percentage and average delta time. Source delta file must be in parquet format.\n

    Parameters:
    ===========
    delta_file:
        Source delta file.\n
    delta_column:
        Source delta column. \n
    avg_delta:
        Average delta time to include in the search using your delta column. Greater than equal (>=).\n
    conn_cnt: INTEGER
        Total connection count for filtering. Greater than equal (>=).\n
        Default = 4\n
    span_avg:
        The percentage to increase and decrease from the connections total delta span.\n
        Example: 15\n
            15 will decrease 15% from the minimum and maximum delta span.\n
            min delta = 5\n
            max delta = 10\n
            span min = 4.25 (5 - (5 * 15%))\n
            span max = 11.5 (10 + (10 * 15%))\n
        Default = 15\n
    variance_per: INTEGER
        Total variance perctage for filtering. Greater than equal (>=).
        Default = 4\n           
    gold_loc: STRING
        Results file location. Blank string ("") for no result file.\n
        Default = ""\n
    overwrite: BOOLEAN
        Overwrite existing location.\n
        Example: False \n
        Default: False \n
    verbose: BOOLEAN
        Verbose logger.\n
        Default = False

    Returns:
    ========
    Gold File Location: STRING
    """

    from sklearn.cluster import DBSCAN
    from scipy.spatial.distance import cdist
    from sklearn import metrics
    from numpy import unique
    from numpy import where

    from sklearn.cluster import AgglomerativeClustering

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

    # BUILD DATASET BASED UPON THE DELTA AVG
    if avg_delta >= 5:
        df = pd.read_parquet(delta_file).query("delta_ms >= 120000")
        df["avg_time"] = df.groupby(["connection_id"])["{}".format(delta_column)].transform("mean")
        df["avg_low"] = df["avg_time"] - (df["avg_time"] * (span_avg / 100))
        df["avg_high"] = df["avg_time"] + (df["avg_time"] * (span_avg / 100))

        df["variance"] = df.groupby(["connection_id"])["{}".format(delta_column)].transform("var")

        # NEW VARIANCE IS BASED UPON PERCENTAGE OF CHANGE
        df["per_cnt"] = df.query("delta_ms >= 60000".format(delta_column)).groupby(["connection_id"])["{}".format(delta_column)].pct_change()
        df["variance_per"] = df.groupby(["connection_id"])["per_cnt"].transform("mean") * 100
    else:
        df = pd.read_parquet(delta_file)
        df["avg_time"] = df.groupby(["connection_id"])["{}".format(delta_column)].transform("mean")
        df["avg_low"] = df["avg_time"] - (df["avg_time"] * (span_avg / 100))
        df["avg_high"] = df["avg_time"] + (df["avg_time"] * (span_avg / 100))

        df["variance"] = df.groupby(["connection_id"])["{}".format(delta_column)].transform("var")
        df["variance_per"] = (df["variance"] / df["avg_time"]) * 100

    # SLOW (>= 8 hrs) OR FAST BEACON (< 8 hrs)
    if avg_delta >= 480:
        logger.info("Slow Beacon Search")
        df_conns = df.query("avg_time >= {} and variance_per <= {}".format(avg_delta,variance_per))
    else:
        logger.info("Fast Beacon Search")
        df_conns = df.query("avg_time <= {} and variance_per <= {}".format(avg_delta,variance_per))

    # GET CONNECTION COUNTS
    df_conns = df.query("avg_time <= {} and variance_per <= {}".format(avg_delta,variance_per))
    df_conns = df_conns[df_conns["{}".format(delta_column)].notna()]
    df_conns["conn_cnt"] = df_conns.groupby("connection_id")["connection_id"].transform("count")
    df_conns = df_conns.query("conn_cnt >= {}".format(conn_cnt))

    # FINAL DATAFRAME OF VALUES TO SCAN
    ds = df[df["connection_id"].isin(df_conns["connection_id"])].copy()

    # SET DELTA COLUMN
    ds["delta"] = ds["{}".format(delta_column)]
    ds.head(10)

    #####################################################################################
    ##
    #####################################################################################

    # GET UNIQUE CONNECTION_IDS {SIP, DIP, PORT, PROTO}
    start_time = time.time()
    connection_ids = ds.connection_id.unique()
    logger.info("{} unique connection_ids found ({}) seconds".format(len(connection_ids), (time.time()-start_time)))
    beacons = {}
    beacon_num = 1
    dbl_break = False

    starttime = datetime.now()
    start_time = time.time()

    id = time.strftime('%Y%m%d-%H%M%S')
    start_time = time.time()
    connection_count = 0
    log_cnt = 0
    tot_cnt = int((0.10 * len(connection_ids)))

    logger.info("Searching for beacons")

    bar = Bar("\t* Searching for Beacons (DBScan by Variance)", max=len(connection_ids), suffix="%(index)d/%(max)d connections | %(elapsed_td)s")

    if len(connection_ids) == 0:
        logger.warning("No connections found for {}% variance".format(variance_per))
        print("\t* WARNING: No connections found for {}% variance".format(variance_per))

    for connection_id in connection_ids:
        connection_count += 1
        log_cnt += 1
        bar.next()

        # GET ALL OF THE RECORDS FROM THE DELTA FILE WITH THIS CONNECTION_ID
        f = ds.query("connection_id == {}".format(connection_id))
        f = f.dropna()
        
        # PRINT MESSAGE AFTER 10% PERCENT COMPLETE
        if log_cnt == tot_cnt or connection_count == 1:
            log_cnt = 0
            logger.info("Evaluation #{} of {} ID: {}: {} original records...".format(connection_count, len(connection_ids), connection_id, len(f)))
        
        X = f[["connection_id","delta"]]

        # DBSCAN CLUSTER OVER AVG SPAN CONFIGURED
        avg_high = int(max(f["avg_high"]))
        avg_low = int(min(f["avg_low"]))

        # EPS IS AVG_HIGH - AVG_LOW / 2 * 10%
        eps = ((avg_high - avg_low ) / 2) * .10 # this is our eps calculation: take a span's difference, and halve it, then multiply by .10
        
        # MIN PTS IN CLUSTER IS LENGTH SET * LIKELIHOOD
        min_pts = len(X) * (minimum_likelihood / 100)

        logger.debug("EPS = {}".format(eps))
        logger.debug("Min Pts = {}".format(min_pts))
        
        # EPS = 0 DO NOT SCAN
        if eps == 0.0:
            continue

        t_time = time.time()
        # RUN DBSCAN CLUSTERING MODEL...
        dbscan = DBSCAN(eps=eps, min_samples=min_pts).fit(X)
        core_samples_mask = np.zeros_like(dbscan.labels_, dtype=bool)
        core_samples_mask[dbscan.core_sample_indices_] = True

        (unique, counts) = np.unique(dbscan.labels_, return_counts=True)
        frequencies = np.asarray((unique, counts)).T
        
        dbscan_cluster_data = pd.DataFrame()
        dbscan_cluster_data['delta'] = f["delta"]
        dbscan_cluster_data['cluster'] = dbscan.labels_
        dbscan_cluster_data = dbscan_cluster_data.groupby(["cluster"])["cluster"].count().reset_index(name="count")

        # CALCULATE LIKELIHOOD OF EACH CLUSTER
        likelihood = _percentage(dbscan_cluster_data['count'], dbscan_cluster_data['count'].sum())
        dbscan_cluster_data["likelihood"] = likelihood

        logger.debug("Connection = {}".format(connection_id))
        logger.debug("Likelihood = {}".format(likelihood))
        logger.debug("Cluster Data = {}".format(dbscan_cluster_data))
        logger.debug("Cluster PTS = {}".format(dbscan.labels_))

        if dbscan_cluster_data["likelihood"].any() > (minimum_likelihood / 100):

            logger.warning("Possible Beacon: \n\
            Session # {} \n\
            Src:    {} \n\
            Dst:    {} \n\
            Likelihood: {}".format(connection_id, max(f["sip"]), max(f["dip"]),max(likelihood)))

            beacons[beacon_num] = {}
            beacons[beacon_num]["connection_id"] = connection_id
            beacons[beacon_num]["likelihood"] = max(likelihood) * 100
            beacon_num +=1

    logger.info("Beacon dictionary {}".format(beacons))
    logger.debug("Beacon connection_id/s {}".format(beacons))    

    # OVERWRITE DELETE GOLD FILES
    if overwrite == True:
        if os.path.exists(gold_loc) and overwrite == True:
            shutil.rmtree(gold_loc)        

    # BUILD GOLD FILE
    if len(gold_loc) > 0 and len(beacons) > 0:
        gold_file = _build_gold_beacons(
            delta_file = delta_file,
            delta_column = delta_column,
            gold_loc = gold_loc,
            beacon_conns = beacons,
            overwrite = overwrite
        )
    else:
        gold_file = None

    bar.finish() 

    endtime = datetime.now() - starttime
    logger.info("{} clusters processed".format(connection_count))
    logger.info("Found {} possible beacons".format(len(beacons)))
    logger.info("Total runtime {}".format(endtime))
    
    return gold_file

def get_dns(ip):
    """
    Lookup DNS record for an IP.\n

    Parameters:
    ===========
    ip:
        IP you want to lookup DNS entry.\n

    Returns:
    ========
    DNS record: STRING
    """

    import socket

    try:
        val = socket.getfqdn(ip)

        # IF RETURNED SAME IP THEN SET TO UNKNOWN
        if val == ip:
            val = "UNKNOWN"
        
        ret_val = val
    except BaseException as err:
        ret_val = "UNKNOWN" 

    return ret_val

def cli_results(gold_file, file_type = "parquet", avg_delta = 0):
    """
    Display the results of a gold file in the Command Line Interface (CLI).\n

    Parameters:
    ===========
    gold_file:
        IP you want to lookup DNS entry.\n
    file_type: STRING (Options = csv or parquet)
        Destination file type (csv or parquet)\n
        Default = parquet\n
    avg_delta: INTEGER
        Default = 0

    Returns:
    ========
    Nothing
    """

    if file_type == "CSV":
        df = pd.read_csv(gold_file)
    else:
        df = pd.read_parquet(gold_file)

    df.rename(columns={"id.orig_h": "source_ip", "id.resp_h": "dest_ip", "id.resp_p": "port", "id.orig_p": "source_port", "datetime": "dt"}, inplace = True)

    # REMOVE ZERO'S IF DELTA AVG CHECK IS >= 5
    # THIS ONLY APPLIES TO DBSCAN BY VARIANCE OPTION
    # EVERYTHING ELSE ZEROS WILL BE INCLUDED IN THE AVERAGE DELTA
    if avg_delta >= 5:
        df.loc[df["delta_mins"]< 2.0, "delta_mins"] = np.nan

    # BUILD AGGREGATIONS
    df = df.groupby(["source_ip", "dest_ip", "port"]).agg(
        connection_count=("dt", "count"),
        avg_delta=("delta_mins", "mean"))

    # BUILD DISPLAY DATAFRAME
    df2 = df.reset_index()
    
    # DISPLAY RESULTS
    if len(df2) != 0:
        df2.sort_values(by=["connection_count", "dest_ip"], inplace=True, ascending=False)
        num_b = df2["dest_ip"].nunique()

        print("X" * 50, " POTENTIAL BEACONS ({})".format(num_b), "X" * 50)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            print(df2)
        print("X" * 121)
    else:
        print("X" * 50, " POTENTIAL BEACONS (0)", "X" * 50)
        print("NONE")
        print("X" * 121)        

def packet(delta_file, delta_column, avg_delta, conn_cnt = 5, min_unique_percent = 5, gold_loc = "", overwrite = False, verbose = False):
    """
    Run a Beacon search by packet size uniqueness.\n

    Parameters:
    ===========
    delta_file:
        Source delta file.\n
    delta_column:
        Source delta column. \n
    avg_delta:
        Average delta time to include in the search using your delta column. Greater than equal (>=).\n
    conn_cnt: INTEGER
        Total connection count for filtering. Greater than equal (>=).\n
        Default = 4\n
    min_unique_percent: INTEGER 
        Lowest packet uniqueness in percentage. For instance if you have 10 connections with 9 of them being the same packet size,\nyour unique package size is 10%.\n
        Default = 5\n           
    gold_loc:
        Results file location. Blank string ("") for no result file.\n
        Default = ""\n
    overwrite: BOOLEAN
        Overwrite existing location.
        Default: False \n
    verbose - Verbose logger.  True or False (case-sensistive). \n
        Default = False

    Returns:
    ========
    Gold File Location: STRING
    """
    
    starttime = datetime.now()

    # BUILD DATASET BASED UPON THE DELTA AVG
    if avg_delta >= 5:
        df = pd.read_parquet(delta_file).query("delta_ms >= 120000")
        df["avg_time"] = df.groupby(["connection_id"])["{}".format(delta_column)].transform("mean")
        df["conn_cnt"] = df.groupby("connection_id")["connection_id"].transform("count")
    else:
        df = pd.read_parquet(delta_file)
        df["conn_cnt"] = df.groupby("connection_id")["connection_id"].transform("count")
        df["avg_time"] = df.groupby(["connection_id"])["{}".format(delta_column)].transform("mean")

    w_df = df.query("avg_time <= {} and conn_cnt >= {}".format(avg_delta,conn_cnt))

    connection_count = w_df.connection_id.unique()
    final_df = pd.DataFrame()

    logger.info("Searching for beacons")
    bar = Bar("\t* Searching for Beacons (Packet Uniqueness)", max=4, suffix="%(index)d/%(max)d Steps | %(elapsed_td)s")    
    bar.next()

    for x in w_df["source_file"].unique():
        
        # REPLACE PATH FOR WINDOWS
        # MODIFIED FOR WINDOWS OS FILES
        # PANDAS TREATS \ AS AN ESCAPE CHARACTER
        fn_x = str(x).replace(chr(92),"/")

        # IF SOURCE FILE DOES NOT EXIST SKIP
        # GET THE PACKETS
        if os.path.exists(x) == True:
            org_df = pd.read_parquet(x)

            df_og = pd.merge(org_df[["src_row_id", "source_file", "orig_pkts", "resp_pkts", "orig_bytes", "resp_bytes"]], w_df,how="inner", left_on=['src_row_id', 'source_file'], right_on=['src_row_id', 'source_file'])
            logger.debug("Total records found {} for file {}".format(len(df_og),x))

            final_df = pd.concat([final_df, df_og])
        else:
            logger.info("Source File {} does not exist...skipping".format(x))

    #####################################################################################
    ##  
    #####################################################################################

    bar.next()

    # GATHER PACKET UNIQUENESS
    final_df["pkt_cnt"] = final_df.groupby(["connection_id", "orig_pkts","resp_pkts"])["connection_id"].transform("count")
    uni_counts = final_df.groupby("connection_id")["pkt_cnt"].value_counts(normalize=True) * 100
    final_df = final_df.join(uni_counts.rename("pkt_unique"), on=["connection_id", "pkt_cnt"])

    # UNIQUE PACKET SIZE DATAFRAME
    uni_df = final_df.query("pkt_unique <= {}".format(min_unique_percent))
    bar.next()

    # CLI OUTPUT DATAFRAME
    uni_df = uni_df[["connection_id", "pkt_unique"]]
    uni_df.rename(columns={"pkt_unique": "packet_unq_per"}, inplace = True)

    # GET CONNECTIONS
    beacons = []

    for z in uni_df["connection_id"].unique():
        beacons.append(z)

    logger.debug("Beacon connection_id/s {}".format(beacons))
    bar.next()

    #####################################################################################
    ##  
    #####################################################################################

    # OVERWRITE DELETE GOLD FILES
    if overwrite == True:
        if os.path.exists(gold_loc) and overwrite == True:
            shutil.rmtree(gold_loc)        

    # BUILD GOLD FILE
    if len(gold_loc) > 0 and len(beacons) > 0:
        gold_file = _build_gold_beacons(
            delta_file = delta_file,
            delta_column = delta_column,
            gold_loc = gold_loc,
            beacon_conns = beacons,
            overwrite = overwrite
        )
    else:
        gold_file = None        

    bar.finish()

    endtime = datetime.now() - starttime
    logger.info("Found {} possible beacons".format(len(beacons)))
    logger.info("Total runtime {}".format(endtime))
    
    return gold_file

def cluster_conns(delta_file, delta_column, conn_cnt = 5, conn_group = 5, threshold = 60, gold_loc = "", overwrite = False, verbose = False):
    """
    Run a Beacon search by clusters of connections per a threshold.\n

    Parameters:
    ===========
    delta_file:
        Source delta file.\n
    delta_column:
        Source delta column. \n
    conn_cnt: INTEGER
        Total connection count for a group. Greater than equal (>=).\n
        Default = 4\n
    conn_group: INTEGER
        Total number of connections groups. Greater than equal (>=).\n
    threshold: INTEGER
        The time threshold in minutes when determining connection groups.\n
    gold_loc: STRING
        Results file location. Blank string ("") for no result file.\n
        Default = ""\n        
    overwrite: BOOLEAN
        Overwrite existing location.\n
        Default: False \n
    verbose: BOOLEAN
        Verbose logger.\n
        Default = False

    Returns
    Gold File Location: STRING
    """
    
    starttime = datetime.now()

    # BUILD DATASET BASED UPON THE DELTA AVG
    og_df = pd.read_parquet(delta_file)
    og_df["avg_time"] = og_df.groupby(["connection_id"])["{}".format(delta_column)].transform("mean")
    og_df["conn_cnt"] = og_df.groupby("connection_id")["connection_id"].transform("count")

    # GET ALL CONNECTIONS
    og_df = og_df.query("conn_cnt >= {}".format(conn_cnt * conn_group))

    logger.info("Scanning {} connection groups".format(len(og_df["connection_id"].unique())))

    logger.info("Searching for beacons")
    bar = Bar("\t* Scanning for clustered connection groups", max=len(og_df["connection_id"].unique()), suffix="%(index)d/%(max)d Groups | %(elapsed_td)s")

    # VARIABLES FOR COUNTERS & PROGRESS
    complete_cnt = 0
    log_cnt = 1
    tot_cnt = int((0.10 * len(og_df["connection_id"].unique())))
    connection_count = len(og_df["connection_id"].unique())
    org_cnt = connection_count

    # FINAL COUNT DATAFRAME
    final_cnt = pd.DataFrame()

    # FINAL BEACON LIST
    beacons = []

    # LOOP THROUGH EACH CONNECTION_ID
    for z in list(og_df["connection_id"].unique()):

        # CREATE NEW DATAFRAME
        df = og_df.query("connection_id == {}".format(z))
        
        # RANGE & COUNTER VARIABLE
        rng = pd.date_range(df["datetime"].min(), og_df["datetime"].max(), freq="{}min".format(threshold))
        y = 0

        # DATAFRAME VARIABLES IN THE FOR LOOP
        cnts = pd.DataFrame()
        dict = []

        # LOOP THROUGH EACH DATE RANGE FOR EACH CONNECTION
        for x in range(len(rng)):

            # ENDING INDEX POSITION
            y += 1

            # USE MAX DT VALUE FOR LAST RANGE
            if x == len(rng)-1:
                if True in df["datetime"].between(rng[x], df["datetime"].max()).value_counts():
                    val_cnt = df["datetime"].between(rng[x],df["datetime"].max()).value_counts()[True]
                    dict = {"connection_id": [z], "begin_date": [rng[x]], "end_date": [df["datetime"].max()], "count": [val_cnt]}
                    cnts = pd.concat([cnts, pd.DataFrame(data=dict)])

            # ELSE USE THE RANGE
            else:
                if True in df["datetime"].between(rng[x], rng[y]).value_counts():
                    val_cnt = df["datetime"].between(rng[x], rng[y]).value_counts()[True]
                    dict = {"connection_id": [z], "begin_date": [rng[x]], "end_date": [df["datetime"].max()], "count": [val_cnt]}
                    cnts = pd.concat([cnts, pd.DataFrame(data=dict)])

        complete_cnt += 1
        
        # PRINT MESSAGE AFTER 10% PERCENT COMPLETE
        if log_cnt == tot_cnt:
            log_cnt = 0
            logger.info("Completed {} of {}".format(complete_cnt,org_cnt))
        else:
            log_cnt += 1

        # CHECK FOR FOUND GROUPS
        if len(cnts) == 0:
            pass
        elif ((cnts["count"] >= conn_cnt).sum() >= conn_group) == True:
            dict = {"connection_id": [z], "group_count": [(cnts["count"] >= conn_cnt).sum()]}
            final_cnt = pd.concat([final_cnt, pd.DataFrame(dict)])
            beacons.append(z)

        else:
            pass

        bar.next()

    logger.debug("Beacon connection_id/s {}".format(beacons))

    #####################################################################################
    ##  
    #####################################################################################

    # OVERWRITE DELETE GOLD FILES
    if overwrite == True:
        if os.path.exists(gold_loc) and overwrite == True:
            shutil.rmtree(gold_loc)        

    # BUILD GOLD FILE
    if len(gold_loc) > 0 and len(beacons) > 0:
        gold_file = _build_gold_beacons(
            delta_file = delta_file,
            delta_column = delta_column,
            gold_loc = gold_loc,
            beacon_conns = beacons,
            overwrite = overwrite
        )
    else:
        gold_file = None

    bar.finish()

    endtime = datetime.now() - starttime
    logger.info("{} connections processed".format(connection_count))
    logger.info("Found {} possible beacons".format(len(beacons)))
    logger.info("Total runtime {}".format(endtime))
    
    return gold_file

def p_conns(delta_file, diff_time = 60, diff_type = "mi"):
    """
    Run a persistent connection search.\n

    Parameters:
    ===========
    delta_file:
        Source delta file.\n
    diff_time:
        The time difference interval you want to search by (<=0). \n
    diff_type: STRING
        What time interval type.\n
        Options
            Days = dd, days or day\n
            Hours = hh, hr or hours\n
            Minutes = mi, mins or minutes\n
            Seconds = ss, sec or seconds\n
            Minutes = mi, mins or minutes\n
            Milliseconds = ms, milli or milliseconds\n
        default = mi\n

    Returns:
    ========
    Printed Pandas DataFrame
    """

    df = pd.read_parquet(delta_file)
    df_pc = df[["connection_id", "sip", "dip", "port", "proto", "datetime"]].copy().reset_index()

    # GENERATE HASHES & COUNTS
    df_pc["hash"] = df_pc.apply(lambda x: hash(tuple(x)), axis = 1)
    df_pc["conn_cnt"] = df_pc.groupby(["sip", "dip", "port", "proto"])["dip"].transform("count")
    df_pc["hash_cnt"] = df_pc.groupby(["sip", "dip", "port", "proto", "hash"])["hash"].transform("nunique")

    # GET DATE DIFFS
    # NEED TO CLEAN THIS UP A BIT
    df_pc["min_dte"] = df_pc.groupby(["sip", "dip", "port", "proto"])["datetime"].transform("min")
    df_pc["max_dte"] = df_pc.groupby(["sip", "dip", "port", "proto"])["datetime"].transform("max")
    df_pc["cur_dte"] = pd.Timestamp.today()
    df_pc["active_conn"] = False

    # GET THE DATE DIFF
    # NEED TO CLEAN THIS UP A BIT
    col_val = ""
    if diff_type.lower() == "day" or diff_type.lower() == "dd" or diff_type.lower() == "days":
        col_val = "days"
        df_pc["date_diff_{}".format(col_val)] = ((df_pc.max_dte - df_pc.min_dte) / pd.Timedelta(days=1))
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "active_conn"] = True
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "date_diff_{}".format(col_val)] = (df_pc.cur_dte - df_pc.min_dte) / pd.Timedelta(days=1)
    elif diff_type.lower() == "hr" or diff_type.lower() == "hh" or diff_type.lower() == "hours":
        col_val = "hrs"
        df_pc["date_diff_{}".format(col_val)] = ((df_pc.max_dte - df_pc.min_dte) / pd.Timedelta(hours=1))
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "active_conn"] = True
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "date_diff_{}".format(col_val)] = (df_pc.cur_dte - df_pc.min_dte) / pd.Timedelta(hours=1)
    elif diff_type.lower() == "min" or diff_type.lower() == "mi" or diff_type.lower() == "minutes":
        col_val = "mins"
        df_pc["date_diff_{}".format(col_val)] = ((df_pc.max_dte - df_pc.min_dte) / pd.Timedelta(minutes=1))
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "active_conn"] = True
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "date_diff_{}".format(col_val)] = (df_pc.cur_dte - df_pc.min_dte) / pd.Timedelta(minutes=1)
    elif diff_type.lower() == "sec" or diff_type.lower() == "ss" or diff_type.lower() == "seconds":
        col_val = "secs"
        df_pc["date_diff_{}".format(col_val)] = ((df_pc.max_dte - df_pc.min_dte) / pd.Timedelta(seconds=1))
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "active_conn"] = True
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "date_diff_{}".format(col_val)] = (df_pc.cur_dte - df_pc.min_dte) / pd.Timedelta(seconds=1)
    elif diff_type.lower() == "milli" or diff_type.lower() == "ms" or diff_type.lower() == "milliseconds":
        col_val = "ms"
        df_pc["date_diff_{}".format(col_val)] = ((df_pc.max_dte - df_pc.min_dte) / pd.Timedelta(milliseconds=1))
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "active_conn"] = True
        df_pc.loc[df_pc["date_diff_{}".format(col_val)] == 0.0, "date_diff_{}".format(col_val)] = (df_pc.cur_dte - df_pc.min_dte) / pd.Timedelta(milliseconds=1)
    else:
        logger.error("diff_type {} does not exist! Must be either (dd, hh, mi, ss or ms)!".format(diff_type))
        print("diff_type {} does not exist! Must be either (dd, hh, mi, ss or ms)!".format(diff_type))
        sys.exit(1)

    # SET NULL MAX_DTE FOR ACTIVE CONNECTIONS
    df_pc.loc[df_pc["active_conn"] == True, "max_dte"] = np.nan

    df_new_pc = pd.merge(
        left = df, 
        right = df_pc[["connection_id", "conn_cnt", "hash_cnt", "min_dte", "max_dte", "active_conn", "date_diff_{}".format(col_val)]], 
        how = "inner",
        on= "connection_id")

    # Currently Open
    # CREATE FINAL DF WILL PRINT RESULTS
    df_new_pc = df_new_pc.query("(hash_cnt == 1 and conn_cnt > 1) or (date_diff_{} >= {})".format(col_val,diff_time))
    df_new_pc = df_new_pc.drop_duplicates(subset=["connection_id", "sip", "dip", "port", "proto"])
    df_new_pc.rename(columns={"sip": "source_ip", "dip": "dest_ip", "datetime": "dt"}, inplace = True)

    # BUILD RESULTS
    if len(df_new_pc) != 0:
        # GET NUMBER OF UNIQUE BEACONS
        num_b = df_new_pc["dest_ip"].nunique()

        print("X" * 50, " PRESISTENT CONNECTIONS ({})".format(num_b), "X" * 50)

        # DISPLAY ALL RESULTS
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.expand_frame_repr', False):  # more options can be specified also
            print(df_new_pc[["source_ip", "dest_ip", "port", "min_dte", "max_dte", "date_diff_{}".format(col_val), "active_conn"]])

        print("X" * 129)
    else:
        print("X" * 50, " PRESISTENT CONNECTIONS  (0)", "X" * 50)
        print("NONE")
        print("X" * 129)
