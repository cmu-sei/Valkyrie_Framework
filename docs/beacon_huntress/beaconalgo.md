# Beacon Huntress Algorithms

Beacon Huntress can be configured to search for beacons using the algorithms below. Each Machine Learning (ML) algorithm has its own unique parameters and is used to search for slow or fast beacons based on time intervals.

## <a name="searchforbeacons"></a>**Advanced Search for Beacons**

Below are the current algorithms that can be used when searching for beacons.

- [Detailed Cluster Search](#clustersearch)
  - Use with Fast or Slow Beacons
- [Hierarchical Search](#hierarchicalsearch)
  - Use with Fast Beacons
- [Quick Cluster Search](#quickcluster)
  - Use with Fast or Slow Beacons

???+ tip "Note"
    Algorithms can be set by using the `cluster_type` option in [config.conf](../configuration). The default algorithm is Quick Cluster Search with Slow Beacon parameters used for [dbscan_by_variance()](#dbscanbyvariance).<br>

## <a name="beaconssearch"></a>**Beacon Searches**

### <a name="clustersearch"></a>**Detailed Cluster Search**

Cluster Search is also known as DBScan, which stands for Density-Based Spatial Clustering of Applications with Noise. DBScan can identify clusters of different sizes within large data samples that contain noise and outliers. DBScan primarily uses two parameters: Minimum Points and EPS (Epsilion). The Minimum Points parameter represents the minimum number of data points (the threshold) that must be clustered together for a region to be considered dense. EPS is the maximum distance between two data points for them to be considered part of the same cluster.

- DBScan cluster is a good choice for searching either [Fast Beacons](../#fs_beacons) or [Slow Beacons](../#fs_beacons). However, this is the slowest running algorithim.

![](../assets/img/bh/dbscan.png)
<br>image source: https://www.kdnuggets.com/2020/04/dbscan-clustering-algorithm-machine-learning.html

### **Parameters**

- **Minimum Delta Time** <i>(int)</i><br>
  The minimum time interval in minutes for your search.<br>

- **Time Spans** <i>(list)</i> <br>
  Spans of time that you wish to search, in list format. <br>
  <i>EXAMPLE: To search within two time spans, 0-5 mins and 5-10 mins:<br>
  <t>[[0, 5], [5, 10]]</i><br>

- **Minimum Cluster Points** <i>(int)</i><br>
  The minimum number of cluster points/connections needed to identify a potential beacon.<br>

- **Likelihood Percentage** <i>(int)</i> <br>
  The minimum likelihood percentage from the Machine Learning algorithm needed to flag a potential beacon.<br>

Below are two examples for finding fast and slow beacons using DBScan clustering.

#### **Fast Beacon Search**

Searching for beacons with 70% likelihood, time spans (0-5 mins, 2-15 mins, 15-35 mins, 30-60 mins), at least 10 connections, and min delta time of 1 minute.

```
Minimum Delta Time = 1
Time Spans = [[0, 5], [2, 15], [15, 35], [30, 60]]
Minimum Cluster Points = 10
Likelihood Percentage = 70
```

![](../assets/img/bh/cluster_fast.png)

#### **Slow Beacon Search**

Searching for beacons with 70% likelihood, time spans (0-5 mins, 2-15 mins, 15-35 mins, 30-60 mins), at least 10 connections, and min delta time of 20 minutes.

```
Minimum Delta Time = 20
Time Spans = [[0, 5], [2, 15], [15, 35], [30, 60]]
Minimum Cluster Points = 10
Likelihood Percentage = 70
```

![](../assets/img/bh/cluster_slow.png)

### <a name="hierarchicalsearch"></a>**Hierarchical Search**

Hierarchical Search uses agglomerative clustering, which is a hierarchical clustering technique used to group objects based on similarity. Each item is treated as a singleton cluster, and clusters that are sufficiently similar are merged together into a larger cluster, working from the bottom up. This process continues until all the clusters are placed into a single large cluster, see image below.

- Agglomerative clustering works well when searching for [Fast Beacons](../#fs_beacons).

![](../assets/img/bh/agg_cluster.png)
<br>image source: https://www.geeksforgeeks.org/hierarchical-clustering-in-data-mining/

### **Parameters**

- **Maximum Variance Percentage** <i>(int)</i><br>
  Variance threshold for any potential beacons.<br>

- **Beacon Callback Count** <i>(int)</i><br>
  Minimum number of delta records to search.<br>

- **Clustering Factor Percentage** <i>(int)</i><br>
  The likelihood percentage for a cluster.<br>

- **Process Lines** <i>(list)</i><br>
  Line amounts to process at a time, in list format.<br>

- **Minimum Callback Time (ms)** <i>(int)</i><br>
  Minimum delta time to search by, in milliseconds.<br>

Below are two examples for finding fast and slow beacons using Agglomerative clustering.

???+ warning "Wrning"
    Hierarchical Search is **NOT** a recommended algorithm for searching for Slow Beacons.<br>

#### **Fast Beacon Search**

Searching for beacons with 70% likelihood, 12% max variance, at least 10 connections, and delta time of 60 seconds.

```
Maximum Variance Percentage = 12
Beacon Callback Count =  10
Clustering Factor Percentage = 70
Process Lines = 1
Minimum Callback Time (ms) = 60000
```

![](../assets/img/bh/agg_fast.png)

#### **Slow Beacon Search**

Searching for beacons with 70% likelihood, 12% max variance, at least 10 connections, and delta time of 15 minutes.

```
Maximum Variance Percentage = 12
Beacon Callback Count =  10
Clustering Factor Percentage = 70
Process Lines = 1
Minimum Callback Time (ms) = 900000
```

![](../assets/img/bh/agg_slow.png)

### <a name="quickclustersearch"></a>**Quick Cluster Search**

Quick Cluster Search uses the same principals as [Detailed Cluster Search](#clustersearch) but some records will be filtered out before the scan if they surpass the user-set variance percentage. If the variance is above the configured threshold, it is excluded from the scan. This feature provides all the benefits of a DBScan without the performance overhead.

- DBScan by Variance cluster is a good choice for searching either [Fast Beacons](../#fs_beacons) or [Slow Beacons](../#fs_beacons).
  - This provides a perfomance increase over Cluster Search, because some connections will be pre-filtered by the variance setting.

### **Parameters**

- **Average Delta Time** <i>(int)</i><br>
  Average delta time to include in the search using your delta column. Less than equal (<>=).<br>

- **Connection Count** <i>(int)</i><br>
  Total connection count for filtering. Greater than equal (>=).<br>

- **Time Span Average** <i>(int)</i> <br>
  The percentage to increase and decrease from the connections total delta span.<br>
  <i>EXAMPLE: 15 will decrease 15% from the minimum and maximum delta span.<br>
  <t>min delta = 5<br>
  <t>max delta = 10<br>
  <t>span min = 4.25 (5 - (5 _ 15%))<br>
  <t>span max = 11.5 (10 + (10 _ 15%))</i><br>

- **Variance Percentage** <i>(int)</i><br>
  Total variance perctage for filtering. Greater than equal (>=).<br>
  **Default** = 4<br>

- **Minimum Likelihood Percentage** <i>(int)</i> <br>
  Minimum likelihood value to identify a beacon.<br>

Below are two examples for finding fast and slow beacons using DBScan by variance clustering.

#### **Fast Beacon Search**

Searching for beacons with 70% likelihood, at least 10 connections, 15% span average, min variance 15% and min delta time of 5 minutes.

```
Average Delta Time = 5
Connection Count = 10
Time Span Average = 15
Variance Percentage = 15
Minimum Likelihood Percentage = 70
```

![](../assets/img/bh/quickcluster_fast.png)

#### **Slow Beacon Search**

Searching for beacons with 70% likelihood, at least 10 connections, 15% span average, min variance 15% and min delta time of 20 minutes.<br>
Note this will also search for fast beacons as avg_delta <=

```
Average Delta Time = 20
Connection Count = 10
Time Span Average = 15
Variance Percentage = 15
Minimum Likelihood Percentage = 70
```

![](../assets/img/bh/quickcluster_slow.png)
