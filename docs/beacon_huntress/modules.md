# Beacon Huntress Modules

There are two main modules that can be used for beacon detection data pipeline beacon.py and ingest.py.<br>
Beacon.py is used for beacon detection. Ingest.py is used for creating the data pipeline. <b><i>Modules should only be used in a Juypter Notebook environment</b></i>.

## **beacon.py**

Beacon module is used to run various beacon detection algorithm against an ingest created deta file. Currently all delta files used within this module must be a parquet file.<br>

???+ tip "Note"
    Ensure you have `__pycache__` directory in the location of the beacon.py file.

### **Import Module**

```python
import beacon
```

These are the available methods:

- [agglomerative_clustering()](#agglomerativeclustering)
- [cli_results()](#cliresults)
- [cluster_conns()](#clusterconn)
- [dbscan_clustering()](#dbscanclustering)
- [dbscan_by_variance()](#dbscanbyvariance)
- [get_dns()](#getdns)

???+ tip "Note"
    Any changes done to the beacon.py module within **JuypterLab** will require a reload of the beacon.py module.<br>
    
    Use the code below to reload the beacon.py module.

### **Reload Module**

```python
import importlib
imported_module = importlib.import_module("beacon")
importlib.reload(imported_module)
import beacon
```

## <a name="agglomerativeclustering"></a>**agglomerative_clustering(\*\*kwargs)**

Run an agglormerative clustering algorithm against a delta file to identify cluster points to be used to find a beacon.<br>

### **Request Syntax**

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

### **Parameters**

- **delta_file** <i>(string)</i> -- **[REQUIRED]**<br>
  Source delta file.<br>

- **delta_column** <i>(string)</i><br>
  Source delta column you want to search. Options below, ms = milliseconds and mins = minutes<br>
  **Options**
  _ delta_ms
  _ delta_mins

- **max_variance** <i>(float)</i> -- **[REQUIRED]**<br>
  Variance threshold for any potential beacons.<br>

- **min_records** <i>(int)</i> -- **[REQUIRED]**<br>
  Minimum number of delta records to search.<br>

- **cluster_factor** <i>(float)</i> -- **[REQUIRED]**<br>
  The likelihood percentage for a cluster.<br>

- **line_amounts** <i>(list)</i> -- **[REQUIRED]**<br>
  Line amounts to process at a time, in list format.<br>

- **min_delta_time** <i>(string)</i> -- **[REQUIRED]**<br>
  Minimum delta time to search by, in milliseconds.<br>

- **gold_loc** <i>(string)</i> <br>
  Results file location. Blank string ("") for no result file<br>
  **Default** = ""<br>

- **cli_return** <i>(boolean)</i> <br>
  Return Command Line Interface (CLI) results. Will display as a print statement and not a return variable.<br>
  **Default** = True<br>

- **overwrite** <i>(boolean)</i> <br>
  Overwrite existing files. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i> <br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

Gold file (string)

### **Example Run**

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

## <a name="cliresults"></a>**cli_results(\*\*kwargs)**

Return Command Line Interface (CLI) results from a gold file. Results will be printed to the screen.

### **Request Syntax**

```python
import beacon

request = beacon.cli_results(
    gold_file = "string",
    file_type = "string
)
```

### **Parameters**

- **gold_file** <i>(string)</i> --**[REQUIRED]**<br>
  Gold file location.<br>

- **file_type** <i>(string)</i> --**[REQUIRED]**<br>
  Gold file type (csv or parquet).<br>
  **Default** = "parquet"<br>

### **Returns**

None

### **Example Run**

```python
import beacon

beacon.cli_results(
    gold_file = "/tmp/gold/data/12345678.parquet"
)
```

## <a name="clusterconn"></a>**cluster_conns(\*\*kwargs)**

Return Command Line Interface (CLI) results from a gold file. Results will be printed to the screen.

### **Request Syntax**

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

### **Parameters**

- **delta_file** <i>(string)</i> -- **[REQUIRED]**<br>
  Source delta file.<br>

- **delta_column** <i>(string)</i> --**[REQUIRED]**<br>
  Source delta column you want to search.<br>

- **conn_cnt** <i>(int)</i><br>
  Total connection count for a group. Greater than equal (>=).<br>
  **Default** = 10<br>

- **conn_group** <i>(int)</i><br>
  Total number of connections groups. Greater than equal (>=).<br>
  **Default** = 5<br>

- **threshold** <i>(int)</i><br>
  The time threshold in minutes when determining connection groups.<br>
  **Default** = 60<br>

- **gold_loc** <i>(string)</i><br>
  Results file location. Blank string ("") for no result file<br>
  **Default** = ""<br>

- **cli_return** <i>(boolean)</i> <br>
  Return Command Line Interface (CLI) results. Will display as a print statement and not a return variable.<br>
  **Default** = True<br>

- **overwrite** <i>(boolean)</i><br>
  Overwrite existing files. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

Gold file (string)

### **Example Run**

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

## <a name="dbscanclustering"></a>**dbscan_clustering(\*\*kwargs)**

Run a DBSCAN cluster algorithm against a delta file to identify cluster points to be used to find a beacon.

### **Request Syntax**

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

### **Parameters**

- **delta_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source delta file.<br>

- **delta_column** <i>(string)</i> --**[REQUIRED]**<br>
  Source delta column you want to search.<br>

- **minimum_delta** <i>(int)</i> --**[REQUIRED]**<br>
  Minimum number of delta records to search using your delta column.<br>

- **spans** <i>(list)</i> <br>
  Spans you wish to search, in list format. Minimum number of delta records to search using your delta column.<br>
  <i>EXAMPLE: Will search two spans 0-5 and 5-10.<br>
  <t>[[0, 5], [5, 10]]</i><br>
  **Default** = []<br>

- **minimum_points_in_cluster** <i>(int)</i><br>
  Destination file type (csv or parquet).<br>
  **Default** = 4<br>

- **minimum_likelihood** <i>(float)</i> <br>
  Minimum likelihood value to identify a beacon.<br>
  **Default** = .70<br>

- **gold_loc** <i>(string)</i><br>
  Results file location. Blank string ("") for no result file<br>
  **Default** = ""<br>

- **cli_return** <i>(boolean)</i> <br>
  Return Command Line Interface (CLI) results. Will display as a print statement and not a return variable.<br>
  **Default** = True<br>

- **overwrite** <i>(boolean)</i><br>
  Overwrite existing files. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

Gold file (string)

### **Example Run**

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

## <a name="dbscanbyvariance"></a>**dbscan_by_variance(\*\*kwargs)**

Run a DBSCAN cluster by filtering out records by delta variance percentage and average delta time. Source delta file must be in parquet format.

### **Request Syntax**

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

### **Parameters**

- **delta_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source delta file.<br>

- **delta_column** <i>(string)</i> --**[REQUIRED]**<br>
  Source delta column you want to search.<br>

- **avg_delta** <i>(int)</i> --**[REQUIRED]**<br>
  Average delta time to include in the search using your delta column. Greater than equal (>=).<br>

- **conn_cnt** <i>(int)</i><br>
  Total connection count for filtering. Greater than equal (>=).<br>
  **Default** = 4<br>

- **span_avg** <i>(int)</i> <br>
  The percentage to increase and decrease from the connections total delta span.<br>
  <i>EXAMPLE: 15 will decrease 15% from the minimum and maximum delta span.<br>
  <t>min delta = 5<br>
  <t>max delta = 10<br>
  <t>span min = 4.25 (5 - (5 _ 15%))<br>
  <t>span max = 11.5 (10 + (10 _ 15%))</i><br>
  **Default** = 15<br>

- **variance_per** <i>(int)</i><br>
  Total variance perctage for filtering. Greater than equal (>=).<br>
  **Default** = 4<br>

- **gold_loc** <i>(string)</i><br>
  Results file location. Blank string ("") for no result file<br>
  **Default** = ""<br>

- **cli_return** <i>(boolean)</i> <br>
  Return Command Line Interface (CLI) results. Will display as a print statement and not a return variable.<br>
  **Default** = True<br>

- **overwrite** <i>(boolean)</i> <br>
  Overwrite existing files. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

Gold file (string)

### **Example Run**

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

## <a name="getdns"></a>**get_dns(\*\*kwargs)**

Lookup DNS record for an IP.

### **Request Syntax**

```python
import beacon

request = beacon.get_dns(
    ip = "string"
)
```

### **Parameters**

- **ip** <i>(list)</i> --**[REQUIRED]**<br>
  IP you want to lookup DNS entry.<br>
  **Default** = None<br>

### **Returns**

DNS Value (string)

### **Example Run**

```python
import beacon

dns = beacon.get_dns(
    ip = "127.0.0.1"
)

print(dns)
```

## <a name="packet"></a>**packet(\*\*kwargs)**

Run a Beacon search by packet size uniqueness.

### **Request Syntax**

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

### **Parameters**

- **delta_file** <i>(string)</i> -- **[REQUIRED]**<br>
  Source delta file.<br>

- **delta_column** <i>(string)</i> --**[REQUIRED]**<br>
  Source delta column you want to search.<br>

- **avg_delta** <i>(int)</i> --**[REQUIRED]**<br>
  Average delta time to include in the search using your delta column. Greater than equal (>=).<br>

- **conn_cnt** <i>(int)</i><br>
  Total connection count for a group. Greater than equal (>=).<br>
  **Default** = 5<br>

- **min_unique_percent** <i>(int)</i><br>
  Lowest packet uniqueness in percentage. For instance if you have 10 connections with 9 of them being the same packet size,\nyour unique package size is 10%.<br>
  **Default** = 5<br>

- **threshold** <i>(int)</i><br>
  The time threshold in minutes when determining connection groups.<br>
  **Default** = 60<br>

- **gold_loc** <i>(string)</i><br>
  Results file location. Blank string ("") for no result file<br>
  **Default** = ""<br>

- **cli_return** <i>(boolean)</i> <br>
  Return Command Line Interface (CLI) results. Will display as a print statement and not a return variable.<br>
  **Default** = True<br>

- **overwrite** <i>(boolean)</i><br>
  Overwrite existing files. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

Gold file (string)

### **Example Run**

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

## **ingest.py**

Below is how to load the ingest.py module. Ensure you have `__pycache__` directory in the location of the ingest.py file.

```python
import ingest
```

Any changes done to the ingest.py module within JuypterLab will require a reload of the ingest.py module. Use the code below to reload the ingest.py module.

```python
import importlib
imported_module = importlib.import_module("ingest")
importlib.reload(imported_module)
import ingest
```

These are the available methods:

- [add_dns()](#adddns)
- [build_bronze_layer()](#buildbronzelayer)
- [build_delta_files()](#builddeltafiles)
- [build_filter_files()](#buildfilterfiles)
- [build_null_files()](#buildnullfiles)
- [build_raw()](#buildraw)
- [convert_parquet_to_csv()](#convertparquettocsv)
- [download_s3_folder()](#downloads3folder)
- [filter_dataframe()](#filterdataframe)
- [get_latest_file()](#getlatestfile)
- [unzip()](#unzip)

## <a name="adddns"></a>**add_dns(\*\*kwargs)**

Add source and destination DNS entries to file/s based upon a whitlist parquet file, or Pandas DataFrame. Both the source and destination files need to be in parquet format.

### **Request Syntax**

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

### **Parameters**

- **src_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source folder or file location.<br>

- **dest_loc** <i>(string)</i> --**[REQUIRED]**<br>
  Destination folder or file location.<br>

- **file_type** <i>(string)</i> --**[REQUIRED]**<br>
  Destination file type (csv or parquet).<br>
  <i>Parquet format recommended!</i>

- **dns_file** <i>(string)</i> <br>
  Source DNS lookup file. A blank string is default. The lookup file must be in parquet format.<br>
  **Default** = ""<br>

- **dns_df** <i>(Pandas DataFrame)</i> <br>
  Source DNS Pandas DataFrame. A blank string is default.<br>
  **Default** = ""<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

None

### **Example Run**

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

## <a name="buildbronzelayer"></a>**build_bronze_layer(\*\*kwargs)**

Create a bronze data layer for a source folder location. Bronze data will tcp data only and will include source and destination DNS.

### **Request Syntax**

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

### **Parameters**

- **src_file** <i>(string)</i> --**[REQUIRED]**<br>
  Raw source folder location.<br>

- **bronze_loc** <i>(string)</i> --**[REQUIRED]**<br>
  Bronze layer folder location. The destination location for all bronze files<br>

- **dns_file** <i>(string)</i> <br>
  Source DNS lookup file. The lookup file must be in parquet format.<br>

- **overwrite** (boolean) <br>
  Overwrite existing files. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

None

### **Example Run**

```python
import ingest

ingest.build_bronze_layer(
    src_loc="/tmp/source/",
    bronze_loc="/tmp/bronze/zeek/raw/parquet/2022/04/22",
    dns_file = "/tmp/whitelist/whitelist_ip.parquet"
    )
```

## <a name="builddeltafiles"></a>**build_delta_files(\*\*kwargs)**

Create a delta file from a parquet folder location or file. Current unit of measuements are milliseconds and minutes. Source and destination files must be parquet. <br>

> **Note**<br>
> Destination file are named <i>delta_epochtime.parquet</i>.

### **Request Syntax**

```python
import ingest

request = ingest.build_delta_files(
    src_loc = "string",
    delta_file_loc = "string",
    delta_file_type = "string",
    overwrite = True|False,
    )
```

### **Parameters**

- **src_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source folder or file location.<br>

- **delta_file_loc** <i>(string)</i> --**[REQUIRED]**<br>
  Destination folder or file location for delta files.<br>

- **delta_file_type** <i>(string)</i><br>
  Destination file type (csv or parquet).<br>
  <i>Parquet format is recommended!</i><br>
  **Default** = parquet<br>

- **overwrite** <i>(boolean)</i> <br>
  Overwrite existing files. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

None

### **Example Run**

```python
import ingest

ingest.build_delta_files(
    src_loc = "/tmp/filtered/",
    delta_file_loc = "/tmp/delta"
    )
```

## <a name="buildfilterfiles"></a>**build_filter_files(\*\*kwargs)**

Create filtered files by searching for Ports, Source/Destination IPs or DNS entries. A default metadata.json will be created for historical filter identification purposes.

### **Request Syntax**

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

### **Parameters**

- **src_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source folder location.<br>

- **dest_file** <i>(string)</i><br>
  Destination file location for filters.<br>
  Use a unique folder name at the end to identify your filter, a data folder will appended automatically.<br>
  **Default** = ""<br>

- **port_filter** <i>(list)</i><br>
  Ports you want to filter by in a list format. **Inclusive results only**.<br>
  **Default** = None<br>

- **port_exclude** <i>(boolean)</i><br>
  Exclusive or inclusive search on port_filter values. **True or False (case-sensistive)**.<br>
  Exclusive = True (not in)<br>
  Inclusive = False (in)<br>
  **Default** = False<br>

- **src_filter** <i>(list)</i><br>
  Source IP you want to filter by, in a list format.<br>
  **Default search** with look for items ending with the item. **Equal to match**.<br>
  Use of a wildcard (\*) will perform a wildcard search.<br>
  **Default** = None<br>

- **src_exclude** <i>(boolean)</i><br>
  Exclusive or inclusive search on src_filter values. **True or False (case-sensistive)**.<br>
  Exclusive = True (not in)<br>
  Inclusive = False (in)<br>
  **Default** = True<br>

- **dest_filter** <i>(list)</i><br>
  Destination DNS you want to filter by, in a list format.<br>
  **Default search** with look for items ending with the item. **Equal to match**.<br>
  Use of a wildcard (\*) will perform a wildcard search.<br>
  **Default** = None<br>

- **dest_exclude** <i>(boolean)</i><br>
  Exclusive or inclusive search on dest_filter values. **True or False (case-sensistive)**.<br>
  Exclusive = True (not in)<br>
  Inclusive = False (in)<br>
  **Default** = True<br>

- **s_dns_filter** <i>(list)</i><br>
  Source DNS you want to filter by, in a list format.<br>
  **Default search** with look for items ending with the item. **Equal to match**.<br>
  Use of a wildcard (\*) will perform a wildcard search.<br>
  **Default** = None<br>

- **s_dns_exclude** <i>(boolean)</i><br>
  Exclusive or inclusive search on s_dns_filter values. **True or False (case-sensistive)**.<br>
  Exclusive = True (not in)<br>
  Inclusive = False (in)<br>
  **Default** = True<br>

- **d_dns_filter** <i>(list)</i><br>
  Destination DNS you want to filter by, in a list format.<br>
  **Default search** with look for items ending with the item. **Equal to match**.<br>
  Use of a wildcard (\*) will perform a wildcard search.<br>
  **Default** = None<br>

- **d_dns_exclude** <i>(boolean)</i><br>
  Exclusive or inclusive search on d_dns_filter values. **True or False (case-sensistive)**.<br>
  Exclusive = True (not in)<br>
  Inclusive = False (in)<br>
  **Default** = True<br>

- **match_filter** <i>(list)</i><br>
  Source and Destination DNS you want to filter by, in a list format.<br>
  **Default search** with look for items ending with the item. **Equal to match**.<br>
  Use of a wildcard (\*) will perform a wildcard search.<br>
  **In order for a match objects must be in both source and destination**.<br>
  **Default** = None<br>

- **match_exclude** <i>(boolean)</i><br>
  Exclusive or inclusive search on match_filter values. **True or False (case-sensistive)**.<br>
  Exclusive = True (not in)<br>
  Inclusive = False (in)<br>
  **Default** = True<br>

- **file_type** <i>(string)</i> <br>
  Destination file types. Parquet or CSV.<br>
  <i>Parquet format is recommended!</i><br>
  **Default** = parquet<br>

- **overwrite** <i>(boolean)</i> <br>
  Overwrite existing location. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

None

### **Example Run**

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

## <a name="buildnullfiles"></a>**build_null_files(\*\*kwargs)**

Create files with NULL DNS entries filter files.

### **Request Syntax**

```python
import ingest

request = ingest.build_null_files(
    src_loc = "string",
    dest_loc = "string",
    overwrite = True|False,
    file_type = "string"
    )
```

### **Parameters**

- **src_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source folder or file location.<br>

- **dest_loc** <i>(string)</i> --**[REQUIRED]**<br>
  Destination folder location.<br>

- **overwrite** <i>(boolean)</i> <br>
  Overwrite existing location. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **file_type** <i>(string)</i> <br>
  Destination file types. Parquet or CSV.<br>
  <i>Parquet format is recommended!</i><br>
  **Default** = parquet<br>

### **Returns**

None

### **Example Run**

```python
import ingest

ingest.build_null_files(
    src_loc = "/tmp/source",
    dest_loc = "/tmp/filtered/no_match")
```

## <a name="buildraw"></a>**build_raw(\*\*kwargs)**

Build inital parquet file from raw json zeek file. To be used only for single files. Use [build_bronze_layer()](#buildbronzelayer) for folder level processing.

### **Request Syntax**

```python
import ingest

ingest.build_raw(
    src_loc = "string",
    dest_loc = "string",
    overwrite = True|False,
    verbose = True|False
    )
```

### **Parameters**

- **src_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source file.<br>

- **dest_parquet_file** <i>(string)</i> --**[REQUIRED]**<br>
  Destination parquet file.<br>

- **overwrite** <i>(boolean)</i> <br>
  Overwrite existing files. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

None

### **Example Run**

```python
import ingest

ingest.build_raw(
    src_loc = "/tmp/source/test.json",
    dest_loc = "/tmp/raw/test.parquet"
    )
```

## <a name="convertparquettocsv"></a>**convert_parquet_to_csv(\*\*kwargs)**

Create a csv file from a parquet file.

### **Request Syntax**

```python
import ingest

request = ingest.convert_parquet_to_csv(
    par_file = "string",
    csv_file = "string"
    )
```

### **Parameters**

- **par_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source parquet file.<br>

- **csv_file** <i>(string)</i> --**[REQUIRED]**<br>
  Destination CSV file.<br>

### **Returns**

None

### **Example Run**

```python
import ingest

ingest.convert_parquet_to_csv(
    par_file = "/tmp/source/test.parquet",
    csv_file = "/tmp/dest/test.csv"
    )
```

## <a name="downloads3folder"></a>**download_s3_folder(\*\*kwargs)**

Download a AWS s3 folder to a local folder. <i>**Must have a AWS CLI Profile configured**</i>.<br>

### **Example Run**

```python
import ingest

request = ingest.download_s3_folder(
    s3_loc = "string",
    csv_file = "string",
    profile = "string"
    )
```

### **Parameters**

- **s3_loc** <i>(string)</i> --**[REQUIRED]**<br>
  s3 folder location.<br>

- **local_dest** <i>(string)</i> --**[REQUIRED]**<br>
  Local destination folder.<br>

- **profile** <i>(string)</i><br>
  AWS CLI Profile name.
  **Default** = default<br>

### **Returns**

None

### **Example Run**

```python
import ingest

ingest.download_s3_folder(
    s3_loc = "s3://bucket/foldername",
    csv_file = "/tmp/bucketname/foldername")
```

## <a name="filterdataframe"></a>**filter_dataframe(\*\*kwargs)**

Filter a Zeek Pandas dataframe for matching values. Returns a Pandas Dataframe.<br>

### **Request Syntax**

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

### **Parameters**

- **df** <i>(pandas dataframe)</i> --**[REQUIRED]**<br>
  Pandas Dataframe.<br>

- **filter_vals** <i>(list)</i> --**[REQUIRED]**<br>
  Values you want to filter by, in a list format.<br>
  **String values search types**<br>
  **Default search** with look for items ending with the item. **Equal to match**.<br>
  Use of a wildcard (\*) will perform a wildcard search.<br>

- **filter_column** <i>(string)</i> --**[REQUIRED]**<br>
  Pandas DataFrame column you want to search by. **Case sensistive**.<br>
  **Valid Options**<br>
  _ community_id <br>
  _ conn\*state <br>

  - duration <br>
    _ history <br>
    _ id.orig\*h <br>
  - id.orig\*p <br>
  - id.resp\*h <br>
  - id.resp\*p <br>
  - local\*orig <br>
  - local\*resp <br>
  - missed\*bytes <br>
  - orig\*bytes <br>
  - orig\*ip_bytes <br>
  - orig\*pkts <br>
  - proto <br>
    _ resp_bytes <br>
    _ resp\*ip_bytes <br>
  - resp\*pkts <br>
  - service <br>
    \_ ts <br> \* uid <br>
    <br>

- **filter_type** <i>(string)</i> --**[REQUIRED]**<br>
  The type of filter you are using.<br>
  **Valid Options**<br>
  _ int (integer)<br>
  _ string (string)<br> \* match (Matching Source and Destination DNS values)<br>

- **ret_org** <i>(boolean)</i><br>
  Return original dataframe if no results gathered. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

- **verbose** <i>(boolean)</i><br>
  Verbose logging. **True or False (case-sensistive)**.<br>
  **Default** = False<br>

### **Returns**

Pandas Dataframe

### **Example Run**

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

## <a name="getlatestfile"></a>**get_latest_file(\*\*kwargs)**

Get the most recent file from a folder location. Method is used to grab the latest delta or gold file. Returns a full path.<br>

### **Request Syntax**

```python
import ingest

request = ingest.get_latest_file(
    folder_loc = "string",
    file_type = "string"
    )

```

### **Parameters**

- **folder_loc** <i>(string)</i> --**[REQUIRED]**<br>
  Source folder location.<br>

- **file_type** <i>(string)</i> <br>
  Destination file type you want to search for. Parquet or CSV.<br>
  <i>Parquet format is recommended!</i><br>
  **Default** = parquet<br>

### **Example Run**

```python
import ingest

# PULL LATEST DELTA FILE
max_file = ingest.filter_dataframe(
    folder_loc = "/tmp/delta/"
    )

print(max_file)
```

## <a name="unzip"></a>**unzip(\*\*kwargs)**

Unzip a source raw file. Only tar files are available for unzipping.<br>

### **Request Syntax**

```python
import ingest

request = ingest.unzip(
    zip_file = "string",
    dest_loc = "string",
    file_type = "string"
    )

```

### **Parameters**

- **zip_file** <i>(string)</i> --**[REQUIRED]**<br>
  Source zip file.<br>

- **dest_loc** <i>(string)</i> --**[REQUIRED]**<br>
  Destination folder where the zip file will be extracted.<br>
  <i>Parquet format is recommended!</i><br>
  **Default** = parquet<br>

- **dest_loc** <i>(string)</i> <br>
  Zip file type.<br>
  <i>Currently the only valid option is tar</i><br>
  **Valid Options**<br> \* tar<br>
  **Default** = tar<br>

```python
import ingest

ingest.unzip(
    zip_file = "/tmp/aw_data_file.tar",
    dest_loc = "/tmp/raw/data"
    )
```
