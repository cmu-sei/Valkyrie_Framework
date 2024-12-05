![Beacon Huntress](../images/beacon_huntress.png)
#
## __Table of Contents__

>   * [Home](../../../readme.md)
>   * [Overview](#overview)
>   * [beacon.py](#beaconpy)
>       * [agglomerative_clustering()](#agglomerativeclustering)
>       * [cli_results()](#cliresults)
>       * [cluster_conns()](#clusterconn)
>       * [dbscan_clustering()](#dbscanclustering)
>       * [dbscan_by_variance()](#dbscanbyvariance)
>       * [get_dns()](#getdns)
>       * [packet()](#packet)
>   * [ingest.py](#ingestpy)
>       * [add_dns()](#adddns)
>       * [build_bronze_layer()](#buildbronzelayer)
>       * [build_delta_files()](#builddeltafiles)
>       * [build_filter_files()](#buildfilterfiles)
>       * [build_null_files()](#buildnullfiles)
>       * [build_raw()](#buildraw)
>       * [convert_parquet_to_csv()](#convertparquettocsv)
>       * [download_s3_folder()](#downloads3folder)
>       * [filter_dataframe()](#filterdataframe)
>       * [get_latest_file()](#getlatestfile)
>       * [unzip()](#unzip)

#
# __Overview__

There are two main modules that can be used for the beacon detection data pipeline: beacon.py and ingest.py.<br>
Beacon.py is used for beacon detection. Ingest.py is used for creating the data pipeline.  <b><i>Modules should only be used in a Juypter Notebook environment</b></i>.

# __beacon.py__

The Beacon module is used to run various beacon detection algorithms against an ingest-created delta file. Currently all delta files used within this module must be in Parquet format.<br>

> ### __Note__<br>
> Ensure that you have the `__pycache__` directory in the same location as the beacon.py file.<br>


### __Import Module__
```python
import beacon
```

These are the available methods:

* [agglomerative_clustering()](#agglomerativeclustering)
* [cli_results()](#cliresults)
* [cluster_conns()](#clusterconn)
* [dbscan_clustering()](#dbscanclustering)
* [dbscan_by_variance()](#dbscanbyvariance)
* [get_dns()](#getdns)

> ### __Note__<br>
> Any changes made to the beacon.py module within __JuypterLab__ will require a reload of the beacon.py module.<br>
> Use the code below to reload the beacon.py module.

### __Reload Module__
```python
import importlib
imported_module = importlib.import_module("beacon")
importlib.reload(imported_module)
import beacon
```

# 
## <a name="agglomerativeclustering"></a>__agglomerative_clustering(**kwargs)__

Run an agglomerative clustering algorithm against a delta file to identify cluster points to be used to find a beacon.<br>

### __Request Syntax__
```python
import beacon

request = beacon.agglomerative_clustering(
    delta_file = "string",
    delta_column = "string",
    max_variance = float,
    min_records = int,
    cluster_factor = float,
    line_amounts = [ int, ],
    min_delta_time = int,
    gold_loc = "string",
    cli_return = True|False,
    overwrite = True|False,
    verbose = True|False
)
```

### __Parameters__
* __delta_file__ <i>(string)</i> -- __[REQUIRED]__<br>
Source delta file.<br>

* __delta_column__ <i>(string)</i><br>
Source delta column that you want to search.  Options (below) are ms = milliseconds and mins = minutes<br>
__Options__
    * delta_ms
    * delta_mins

* __max_variance__ <i>(float)</i> -- __[REQUIRED]__<br>
Variance threshold for any potential beacons.<br>

* __min_records__ <i>(int)</i> -- __[REQUIRED]__<br>
Minimum number of delta records to search.<br>

* __cluster_factor__ <i>(float)</i> -- __[REQUIRED]__<br>
The likelihood percentage for a cluster.<br>

* __line_amounts__ <i>(list)</i> -- __[REQUIRED]__<br>
Line amounts to process at a time, in list format.<br>

* __min_delta_time__ <i>(string)</i> -- __[REQUIRED]__<br>
Minimum delta time to search by, in milliseconds.<br>

* __gold_loc__ <i>(string)</i> <br>
Results file location.  Blank string ("") for no result file<br>
__Default__ = ""<br>

* __cli_return__ <i>(boolean)</i> <br>
Return Command Line Interface (CLI) results.  Will display as a print statement and not a return variable.<br>
__Default__ = True<br>

* __overwrite__ <i>(boolean)</i> <br>
Overwrite existing files. __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i> <br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
Gold file (string)

### __Example Run__
```python
import beacon

gold_file = beacon.agglomerative_clustering(
    delta_file = "/tmp/delta/delta_file.parquet",
    max_variance = 0.01,
    min_records = 10,
    cluster_factor = 0.2,
    line_amounts = [1],
    min_delta_time = 300000,
    gold_loc = "/tmp/gold/beacon/agg_cluster",
    cli_return = False
)

print(gold_file)
```

# 
## <a name="cliresults"></a>__cli_results(**kwargs)__

Return Command Line Interface (CLI) results from a gold file.  Results will be printed to the screen.

### __Request Syntax__
```python
import beacon

request = beacon.cli_results(
    gold_file = "string",
    file_type = "string
)
```

### __Parameters__
* __gold_file__ <i>(string)</i> --__[REQUIRED]__<br>
Gold file location.<br>

* __file_type__ <i>(string)</i> --__[REQUIRED]__<br>
Gold file type (CSV or Parquet).<br>
__Default__ = "parquet"<br>

### __Returns__
None

### __Example Run__
```python
import beacon

beacon.cli_results(
    gold_file = "/tmp/gold/data/12345678.parquet"
)
```

# 
## <a name="clusterconn"></a>__cluster_conns(**kwargs)__

Return Command Line Interface (CLI) results from a gold file.  Results will be printed to the screen.

### __Request Syntax__
```python
import beacon

request = beacon.cluster_conns(
    delta_file = "string",
    delta_column = "string",
    conn_cnt = int,
    conn_group = int,
    threshold = int,
    gold_loc = "string",
    cli_return = True|False,
    overwrite = True|False,
    verbose = True|False
)
```

### __Parameters__
* __delta_file__ <i>(string)</i> -- __[REQUIRED]__<br>
Source delta file.<br>

* __delta_column__ <i>(string)</i> --__[REQUIRED]__<br>
Source delta column that you want to search.<br>

* __conn_cnt__ <i>(int)</i><br>
Total connection count for a group. Greater than or equal (>=).<br>
__Default__ = 10<br>

* __conn_group__ <i>(int)</i><br>
Total number of connection groups. Greater than or equal (>=).<br>
__Default__ = 5<br>

* __threshold__ <i>(int)</i><br>
The time threshold in minutes when determining connection groups.<br>
__Default__ = 60<br>

* __gold_loc__ <i>(string)</i><br>
Results file location.  Blank string ("") for no result file<br>
__Default__ = ""<br>

* __cli_return__ <i>(boolean)</i> <br>
Return Command Line Interface (CLI) results.  Will display as a print statement and not a return variable.<br>
__Default__ = True<br>

* __overwrite__ <i>(boolean)</i><br>
Overwrite existing files. __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>


### __Returns__
Gold file (string)

### __Example Run__
```python
import beacon

gold_file = beacon.cluster_conns(
    delta_file = "/tmp/delta/delta_file.parquet",
    delta_column = "delta_mins",
    conn_cnt = 10,
    conn_group = 5,
    threshold = 60,
    gold_loc = "/tmp/gold/beacon/dbscan",
    cli_return = False,
    overwrite = False,
    verbose = False
)

print(gold_file)
```

# 
## <a name="dbscanclustering"></a>__dbscan_clustering(**kwargs)__

Run a DBSCAN cluster algorithm against a delta file to identify cluster points to be used to find a beacon.

### __Request Syntax__
```python
import beacon

request = beacon.dbscan_clustering(
    delta_file = "string",
    delta_column = "string",
    minimum_delta = int,
    spans = [[ int, int ], [ int, int], ],
    minimum_points_in_cluster = int,
    minimum_likelihood = float,
    gold_loc = "string",
    cli_return = True|False,
    overwrite = True|False,
    verbose = True|False    
)
```

### __Parameters__
* __delta_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source delta file.<br>

* __delta_column__ <i>(string)</i> --__[REQUIRED]__<br>
Source delta column that you want to search.<br>

* __minimum_delta__ <i>(int)</i> --__[REQUIRED]__<br>
Minimum number of delta records to search using your delta column.<br>

* __spans__ <i>(list)</i> <br>
Spans of time that you wish to search, in list format.<br>
<i>Example: Will search within two time spans, 0-5 min and 5-10 min.<br>
    <t>[[0, 5], [5, 10]]</i><br>
__Default__ = []<br>

* __minimum_points_in_cluster__ <i>(int)</i><br>
Destination file type (CSV or Parquet).<br>
__Default__ = 4<br>

* __minimum_likelihood__ <i>(float)</i> <br>
Likelihood value (threshold) used to identify a potential beacon.<br>
__Default__ = .70<br>

* __gold_loc__ <i>(string)</i><br>
Results file location.  Blank string ("") for no result file<br>
__Default__ = ""<br>

* __cli_return__ <i>(boolean)</i> <br>
Return Command Line Interface (CLI) results.  Will display as a print statement and not a return variable.<br>
__Default__ = True<br>

* __overwrite__ <i>(boolean)</i><br>
Overwrite existing files. __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
Gold file (string)

### __Example Run__
```python
import beacon

gold_file = beacon.dbscan_clustering(
    delta_file = "/tmp/delta/delta_file.parquet",
    delta_column = "delta_mins",
    minimum_delta = 1,
    spans = [[0, 5], [2, 15], [15, 35], [30, 60]],
    minimum_points_in_cluster = 4,
    minimum_likelihood = 0.70,
    gold_loc = "/tmp/gold/beacon/dbscan",
    cli_return = False  
)

print(gold_file)
```

#
## <a name="dbscanbyvariance"></a>__dbscan_by_variance(**kwargs)__

Run a DBSCAN cluster by filtering out records by delta variance percentage and average delta time.  Source delta file must be in Parquet format.

### __Request Syntax__
```python
import beacon

request = beacon.dbscan_by_variance(
    delta_file = "string",
    delta_column = "string",
    avg_delta = int,
    conn_cnt = int,
    span_avg = int,
    variance_per = int,
    minimum_likelihood = float,
    gold_loc = "string",
    cli_return = True|False,
    overwrite = True|False,
    verbose = True|False    
)
```

### __Parameters__
* __delta_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source delta file.<br>

* __delta_column__ <i>(string)</i> --__[REQUIRED]__<br>
Source delta column that you want to search.<br>

* __avg_delta__ <i>(int)</i> --__[REQUIRED]__<br>
Average delta time to include in the search using your delta column. Less than or equal (<=).<br>

* __conn_cnt__ <i>(int)</i><br>
Total connection count for filtering. Greater than or equal (>=).<br>
__Default__ = 4<br>

* __span_avg__ <i>(int)</i> <br>
The percentage to increase and decrease from the connections total delta span.<br>
<i>Example: 15 will increase/decrease the minimum and maximum of the delta span by 15%.<br>
    <t>delta min = 5<br>
    <t>delta max = 10<br>
    <t>span min = 4.25 (5 - (5 * 15%))<br>
    <t>span max = 11.5 (10 + (10 * 15%))</i><br>
__Default__ = 15<br>

* __variance_per__ <i>(int)</i><br>
Total variance percentage for filtering. Greater than or equal (>=).<br>
__Default__ = 4<br>

* __gold_loc__ <i>(string)</i><br>
Results file location.  Blank string ("") for no result file<br>
__Default__ = ""<br>

* __cli_return__ <i>(boolean)</i> <br>
Return Command Line Interface (CLI) results. Will display as a print statement and not a return variable.<br>
__Default__ = True<br>

* __overwrite__ <i>(boolean)</i> <br>
Overwrite existing files. __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
Gold file (string)

### __Example Run__
```python
import beacon

gold_file = beacon.dbscan_by_variance(
    delta_file = "/tmp/delta/delta_file.parquet",
    delta_column = "delta_mins",
    avg_delta = 10,
    conn_cnt = 5,
    span_avg = 15,
    variance_per = 10,
    minimum_likelihood = 0.70,
    gold_loc = "/tmp/gold/beacon/dbscan_var",
    cli_return = False
)

print(gold_file)
```

# 
## <a name="getdns"></a>__get_dns(**kwargs)__

Look up a DNS record for an IP.

### __Request Syntax__
```python
import beacon

request = beacon.get_dns(
    ip = "string"
)
```

### __Parameters__
* __ip__ <i>(list)</i> --__[REQUIRED]__<br>
IP for which you want to look up a DNS entry.<br>
__Default__ = None<br>

### __Returns__
DNS Value (string)

### __Example Run__
```python
import beacon

dns = beacon.get_dns(
    ip = "127.0.0.1"
)

print(dns)
```

# 
## <a name="packet"></a>__packet(**kwargs)__

Run a Beacon search by packet size uniqueness.

### __Request Syntax__
```python
import beacon

request = beacon.packet(
    delta_file = "string",
    delta_column = "string",
    avg_delta = int,
    conn_cnt = int,
    min_unique_percent = int,
    gold_loc = "string",
    cli_return = True|False,
    overwrite = True|False,
    verbose = True|False
)
```

### __Parameters__
* __delta_file__ <i>(string)</i> -- __[REQUIRED]__<br>
Source delta file.<br>

* __delta_column__ <i>(string)</i> --__[REQUIRED]__<br>
Source delta column that you want to search.<br>

* __avg_delta__ <i>(int)</i> --__[REQUIRED]__<br>
Average delta time to include in the search using your delta column. Less than or equal (<=).<br>

* __conn_cnt__ <i>(int)</i><br>
Total connection count for a group. Greater than or equal (>=).<br>
__Default__ = 5<br>

* __min_unique_percent__ <i>(int)</i><br>
Lowest packet uniqueness as a percentage. For instance, if you have 10 connections with 9 of them being the same packet size, your unique package size is 10%.<br>
__Default__ = 5<br>

* __threshold__ <i>(int)</i><br>
The time threshold in minutes for determining connection groups.<br>
__Default__ = 60<br>

* __gold_loc__ <i>(string)</i><br>
Results file location.  Blank string ("") for no result file<br>
__Default__ = ""<br>

* __cli_return__ <i>(boolean)</i> <br>
Return Command Line Interface (CLI) results.  Will display as a print statement and not a return variable.<br>
__Default__ = True<br>

* __overwrite__ <i>(boolean)</i><br>
Overwrite existing files. __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>


### __Returns__
Gold file (string)

### __Example Run__
```python
import beacon

gold_file = beacon.packet(
    delta_file = "/tmp/delta/delta_file.parquet",
    delta_column = "delta_mins",
    avg_delta = 15,
    conn_cnt = 5,
    min_unique_percent = 5,
    gold_loc = "/tmp/gold/beacon/dbscan",
    cli_return = False,
    overwrite = False,
    verbose = False
)

print(gold_file)
```


# **ingest.py**

Below are the steps for loading the ingest.py module. Ensure that you have the `__pycache__` directory in the same location as the ingest.py file.

```python
import ingest
```

Any changes done to the ingest.py module within JuypterLab will require a reload of the ingest.py module.  Use the code below to reload the ingest.py module.

```python
import importlib
imported_module = importlib.import_module("ingest")
importlib.reload(imported_module)
import ingest
```

These are the available methods:

* [add_dns()](#adddns)
* [build_bronze_layer()](#buildbronzelayer)
* [build_delta_files()](#builddeltafiles)
* [build_filter_files()](#buildfilterfiles)
* [build_null_files()](#buildnullfiles)
* [build_raw()](#buildraw)
* [convert_parquet_to_csv()](#convertparquettocsv)
* [download_s3_folder()](#downloads3folder)
* [filter_dataframe()](#filterdataframe)
* [get_latest_file()](#getlatestfile)
* [unzip()](#unzip)


#
## <a name="adddns"></a>__add_dns(**kwargs)__

Add source and destination DNS entries to file(s) based upon a whitelist Parquet file or Pandas DataFrame. Both the source and destination files need to be in Parquet format.

### __Request Syntax__
```python
import ingest

request = ingest.add_dns(
    src_file = "string",
    dest_loc = "string",
    file_type = "string",
    dns_file = "string" 
    dns_df = Pandas_DataFrame,
    verbose = True|False
)
```

### __Parameters__
* __src_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source folder or file location.<br>

* __dest_loc__ <i>(string)</i> --__[REQUIRED]__<br>
Destination folder or file location.<br>

* __file_type__ <i>(string)</i> --__[REQUIRED]__<br>
Destination file type (CSV or Parquet).<br>
<i>Parquet format recommended!</i>

* __dns_file__ <i>(string)</i> <br>
Source DNS lookup file. A blank string is the default. The lookup file must be in Parquet format.<br>
__Default__ = ""<br>

* __dns_df__ <i>(Pandas DataFrame)</i> <br>
Source DNS Pandas DataFrame. A blank string is the default.<br>
__Default__ = ""<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
None

### __Example Run__
```python
import ingest

# Folder Location
ingest.add_dns(
    src_file = "/tmp/source_files",
    dest_loc = "/tmp/dest_files",
    dns_file = "/tmp/whitelist/whitelist_ip.parquet" 
)

# Single File
ingest.add_dns(
    src_file = "/tmp/source_files/source_file.parquet",
    dest_loc = "/tmp/dest_files",
    dns_file = "/tmp/whitelist/whitelist_ip.parquet" 
)
```

#
## <a name="buildbronzelayer"></a>__build_bronze_layer(**kwargs)__

Create a bronze data layer for a source folder location. Bronze data will contain TCP data only and will include both source and destination DNS.

### __Request Syntax__
```python
import ingest

request = ingest.build_bronze_layer(
    src_loc = "string", 
    bronze_loc = "string",
    dns_file = "string",
    overwrite = True|False,
    verbose = True|False
)
```

### __Parameters__
* __src_file__ <i>(string)</i> --__[REQUIRED]__<br>
Raw source folder location.<br>

* __bronze_loc__ <i>(string)</i> --__[REQUIRED]__<br>
Bronze layer folder location. The destination location for all bronze files.<br>

* __dns_file__ <i>(string)</i> <br>
Source DNS lookup file. The lookup file must be in Parquet format.<br>

* __overwrite__ (boolean) <br>
Overwrite existing files. __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
None

### __Example Run__

```python
import ingest

ingest.build_bronze_layer(
    src_loc="/tmp/source/", 
    bronze_loc="/tmp/bronze/zeek/raw/parquet/2022/04/22",
    dns_file = "/tmp/whitelist/whitelist_ip.parquet" 
    )
```

#
## <a name="builddeltafiles"></a>__build_delta_files(**kwargs)__

Create a delta file from a Parquet folder location or file. Current units of measurement are milliseconds and minutes. Source and destination files must be in Parquet format. <br>

> __Note__<br>
> Destination files are named <i>delta_epochtime.parquet</i>.

### __Request Syntax__
```python
import ingest

request = ingest.build_delta_files(
    src_loc = "string",
    delta_file_loc = "string",
    delta_file_type = "string",
    overwrite = True|False,
    )
```

### __Parameters__
* __src_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source folder or file location.<br>

* __delta_file_loc__ <i>(string)</i> --__[REQUIRED]__<br>
Destination folder or file location for delta files.<br>

* __delta_file_type__ <i>(string)</i><br>
Destination file type (CSV or Parquet).<br>
<i>Parquet format is recommended!</i><br>
__Default__ = parquet<br>

* __overwrite__ <i>(boolean)</i> <br>
Overwrite existing files. __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
None

### __Example Run__
```python
import ingest

ingest.build_delta_files(
    src_loc = "/tmp/filtered/",
    delta_file_loc = "/tmp/delta"
    )
```

#
## <a name="buildfilterfiles"></a>__build_filter_files(**kwargs)__

Create filtered files by searching for Ports, Source/Destination IPs or DNS entries. A default metadata.json will be created for historical filter identification purposes.  

### __Request Syntax__
```python
import ingest

request = ingest.build_filter_files(
    src_loc = "string",
    dest_file = "string",
    port_filter = [ int, ],
    port_exclude = True|False,
    src_file = [ "string", ],
    src_exclude = True|False,
    dest_filter = [ "string", ],
    dest_exclude = True|False,
    s_dns_filter = [ "string", ],
    s_dns_exclude = True|False,
    d_dns_filter = [ "string", ],
    d_dns_exclude = True|False,
    match_filter = [ "string", ],
    match_exclude = True|False,
    file_type = "string",
    overwrite = True|False,
    verbose = True|False    
    )
```

### __Parameters__
* __src_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source folder location.<br>

* __dest_file__ <i>(string)</i><br>
Destination file location for filters.<br>
Use a unique folder name at the end to identify your filter - a data folder will be appended automatically.<br>
__Default__ = ""<br>

* __port_filter__ <i>(list)</i><br>
Ports that you want to filter by, in a list format.  __Inclusive results only__.<br>
__Default__ = None<br>

* __port_exclude__ <i>(boolean)</i><br>
Exclusive or inclusive search on port_filter values.  __True or False (case-sensitive)__.<br>
Exclusive = True (not in)<br>
Inclusive = False (in)<br>
__Default__ = False<br>

* __src_filter__ <i>(list)</i><br>
Source IP that you want to filter by, in a list format.<br>
__Default search__ will look for items equal to match.<br>
Use of a wildcard (*) will perform a wildcard search.<br>
__Default__ = None<br>

* __src_exclude__ <i>(boolean)</i><br>
Exclusive or inclusive search on src_filter values.  __True or False (case-sensitive)__.<br>
Exclusive = True (not in)<br>
Inclusive = False (in)<br>
__Default__ = True<br>

* __dest_filter__ <i>(list)</i><br>
Destination DNS that you want to filter by, in a list format.<br>
__Default search__ will look for items equal to match.<br>
Use of a wildcard (*) will perform a wildcard search.<br>
__Default__ = None<br>

* __dest_exclude__ <i>(boolean)</i><br>
Exclusive or inclusive search on dest_filter values.  __True or False (case-sensitive)__.<br>
Exclusive = True (not in)<br>
Inclusive = False (in)<br>
__Default__ = True<br>

* __s_dns_filter__ <i>(list)</i><br>
Source DNS that you want to filter by, in a list format.<br>
__Default search__ will look for items equal to match.<br>
Use of a wildcard (*) will perform a wildcard search.<br>
__Default__ = None<br>

* __s_dns_exclude__ <i>(boolean)</i><br>
Exclusive or inclusive search on s_dns_filter values.  __True or False (case-sensitive)__.<br>
Exclusive = True (not in)<br>
Inclusive = False (in)<br>
__Default__ = True<br>

* __d_dns_filter__ <i>(list)</i><br>
Destination DNS that you want to filter by, in a list format.<br>
__Default search__ will look for items equal to match.<br>
Use of a wildcard (*) will perform a wildcard search.<br>
__Default__ = None<br>

* __d_dns_exclude__ <i>(boolean)</i><br>
Exclusive or inclusive search on d_dns_filter values.  __True or False (case-sensitive)__.<br>
Exclusive = True (not in)<br>
Inclusive = False (in)<br>
__Default__ = True<br>

* __match_filter__ <i>(list)</i><br>
Source and Destination DNS that you want to filter by, in a list format.<br>
__Default search__ will look for items equal to match.<br>
Use of a wildcard (*) will perform a wildcard search.<br>
__In order to match, objects must be in both source and destination__.<br>
__Default__ = None<br>

* __match_exclude__ <i>(boolean)</i><br>
Exclusive or inclusive search on match_filter values.  __True or False (case-sensitive)__.<br>
Exclusive = True (not in)<br>
Inclusive = False (in)<br>
__Default__ = True<br>

* __file_type__ <i>(string)</i> <br>
Destination file types. Parquet or CSV.<br>
<i>Parquet format is recommended!</i><br>
__Default__ = parquet<br>

* __overwrite__ <i>(boolean)</i> <br>
Overwrite existing location.  __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
None

### __Example Run__
```python
import ingest

# NO INCLUDE FILE
# ONLY PORTS 80 & 443 WILL BE INCLUDED.
# EXAMPLE IPS WILL BE REMOVED.
ingest.build_filter_files(
    src_loc = "/tmp/source",
    dest_file = "/tmp/dest/filtered/test_filter" 
    port_filter = [80, 443],
    src_filter = ["127.0.0.1", "9.9.9.9"],
    dest_filter = ["127.0.0.1", "9.9.9.9"])
```

#
## <a name="buildnullfiles"></a>__build_null_files(**kwargs)__

Create filter files with NULL DNS entries.

### __Request Syntax__
```python
import ingest

request = ingest.build_null_files(
    src_loc = "string",
    dest_loc = "string",
    overwrite = True|False,
    file_type = "string"
    )
```

### __Parameters__
* __src_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source folder or file location.<br>

* __dest_loc__ <i>(string)</i> --__[REQUIRED]__<br>
Destination folder location.<br>

* __overwrite__ <i>(boolean)</i> <br>
Overwrite existing location.  __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __file_type__ <i>(string)</i> <br>
Destination file types. Parquet or CSV.<br>
<i>Parquet format is recommended!</i><br>
__Default__ = parquet<br>

### __Returns__
None

### __Example Run__
```python
import ingest

ingest.build_null_files(
    src_loc = "/tmp/source",
    dest_loc = "/tmp/filtered/no_match")
```

#
## <a name="buildraw"></a>__build_raw(**kwargs)__

Build initial Parquet file from raw JSON Zeek file. To be used only for single files. Use [build_bronze_layer()](#buildbronzelayer) for folder-level processing.

### __Request Syntax__
```python
import ingest

ingest.build_raw(
    src_loc = "string",
    dest_loc = "string",
    overwrite = True|False,
    verbose = True|False
    )
```

### __Parameters__
* __src_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source file.<br>

* __dest_parquet_file__ <i>(string)</i> --__[REQUIRED]__<br>
Destination Parquet file.<br>

* __overwrite__ <i>(boolean)</i> <br>
Overwrite existing files. __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
None

### __Example Run__
```python
import ingest

ingest.build_raw(
    src_loc = "/tmp/source/test.json",
    dest_loc = "/tmp/raw/test.parquet"
    )
```

#
## <a name="convertparquettocsv"></a>__convert_parquet_to_csv(**kwargs)__

Create a CSV file from a Parquet file.

### __Request Syntax__
```python
import ingest

request = ingest.convert_parquet_to_csv(
    par_file = "string",
    csv_file = "string"
    )
```

### __Parameters__
* __par_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source Parquet file.<br>

* __csv_file__ <i>(string)</i> --__[REQUIRED]__<br>
Destination CSV file.<br>

### __Returns__
None

### __Example Run__
```python
import ingest

ingest.convert_parquet_to_csv(
    par_file = "/tmp/source/test.parquet",
    csv_file = "/tmp/dest/test.csv"
    )
```

#
## <a name="downloads3folder"></a>__download_s3_folder(**kwargs)__

Download an AWS S3 folder to a local folder.  <i>__Must have an AWS CLI Profile configured__</i>.<br>

### __Example Run__
```python
import ingest

request = ingest.download_s3_folder(
    s3_loc = "string",
    csv_file = "string",
    profile = "string"
    )
```

### __Parameters__
* __s3_loc__ <i>(string)</i> --__[REQUIRED]__<br>
S3 folder location.<br>

* __local_dest__ <i>(string)</i> --__[REQUIRED]__<br>
Local destination folder.<br>

* __profile__ <i>(string)</i><br>
AWS CLI Profile name.<br>
__Default__ = default<br>

### __Returns__
None

### __Example Run__
```python
import ingest

ingest.download_s3_folder(
    s3_loc = "s3://bucket/foldername",
    csv_file = "/tmp/bucketname/foldername")
```

#
## <a name="filterdataframe"></a>__filter_dataframe(**kwargs)__

Filter a Zeek Pandas Dataframe for matching values. Returns a Pandas Dataframe.<br>

### __Request Syntax__
```python
import ingest

request = ingest.filter_dataframe(
    df = Pandas_DataFrame, 
    filter_vals = [ "string", ], 
    filter_column = "string", 
    filter_type = "string",
    ret_org = True|False,
    verbose = True|False
    )

```

### __Parameters__
* __df__ <i>(pandas dataframe)</i> --__[REQUIRED]__<br>
Pandas Dataframe.<br>

* __filter_vals__ <i>(list)</i> --__[REQUIRED]__<br>
Values that you want to filter by, in a list format.<br>

    __String values search types:__<br>
    __Default search__ will look for items equal to match.<br>
    Use of a wildcard (*) will perform a wildcard search.<br>

* __filter_column__ <i>(string)</i> --__[REQUIRED]__<br>
Pandas DataFrame column that you want to search by.  __Case sensitive__.<br>

    __Valid Options__<br>
        * community_id <br>
        * conn_state <br>
        * duration <br>
        * history <br>
        * id.orig_h <br>
        * id.orig_p <br>
        * id.resp_h <br>
        * id.resp_p <br>
        * local_orig <br>
        * local_resp <br>
        * missed_bytes <br>
        * orig_bytes <br>
        * orig_ip_bytes <br>
        * orig_pkts <br>
        * proto <br>
        * resp_bytes <br>
        * resp_ip_bytes <br>
        * resp_pkts <br>
        * service <br>
        * ts <br>
        * uid <br>
<br>
* __filter_type__ <i>(string)</i> --__[REQUIRED]__<br>
The type of filter that you are using.<br>
__Valid Options__<br>
    * int (integer)<br>
    * string (string)<br>
    * match (matching Source and Destination DNS values)<br>

* __ret_org__ <i>(boolean)</i><br>
Return original dataframe if no results gathered.  __True or False (case-sensitive)__.<br>
__Default__ = False<br>

* __verbose__ <i>(boolean)</i><br>
Verbose logging.   __True or False (case-sensitive)__.<br>
__Default__ = False<br>

### __Returns__
Pandas Dataframe

### __Example Run__
```python
import ingest
import pandas as pd

src_df = pd.read_parquet("/tmp/dest/test.parquet")

new_df = ingest.filter_dataframe(
    df = src_df, 
    filter_vals = ["127.0.0.1", "localhost"], 
    filter_column = "id.orig_h", 
    filter_type = "string"
    )

print(new_df)
```

#
## <a name="getlatestfile"></a>__get_latest_file(**kwargs)__

Get the most recent file from a folder location.  Method is used to grab the latest delta or gold file.  Returns a full path.<br>

### __Request Syntax__
```python
import ingest

request = ingest.get_latest_file(
    folder_loc = "string", 
    file_type = "string"
    )

```

### __Parameters__
* __folder_loc__ <i>(string)</i> --__[REQUIRED]__<br>
Source folder location.<br>

* __file_type__ <i>(string)</i> <br>
Destination file type that you want to search for. Parquet or CSV.<br>
<i>Parquet format is recommended!</i><br>
__Default__ = parquet<br>

### __Example Run__
```python
import ingest

# PULL LATEST DELTA FILE
max_file = ingest.filter_dataframe(
    folder_loc = "/tmp/delta/"
    )

print(max_file)
```

#
## <a name="unzip"></a>__unzip(**kwargs)__

Unzip a raw source file.  Only tar files are available for unzipping.<br>

### __Request Syntax__
```python
import ingest

request = ingest.unzip(
    zip_file = "string", 
    dest_loc = "string",     
    file_type = "string"
    )

```

### __Parameters__
* __zip_file__ <i>(string)</i> --__[REQUIRED]__<br>
Source zip file.<br>

* __dest_loc__ <i>(string)</i> --__[REQUIRED]__<br>
Destination folder where the zip file will be extracted.<br>
<i>Parquet format is recommended!</i><br>
__Default__ = parquet<br>

* __dest_loc__ <i>(string)</i> <br>
Zip file type.<br>
<i>Currently the only valid option is tar</i><br>
__Valid Options__<br>
    * tar<br>
__Default__ = tar<br>

```python
import ingest

ingest.unzip(
    zip_file = "/tmp/aw_data_file.tar", 
    dest_loc = "/tmp/raw/data"
    )
```

#
Valkyrie Framework<br>
Copyright 2023 Carnegie Mellon University.<br>
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.<br>
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.<br>
DM23-0210<br>