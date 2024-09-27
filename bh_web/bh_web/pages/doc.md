![Beacon Huntress](/static/images/beacon_huntress.png)

## __Table of Contents__

> * [Overview](#overview)
> * [Copy Zeek Logs](#zeek)
> * [Open Beacon Huntress](#webpage)
> * [Configure](#config)
> * [Example Run](#examplerun)
> * [Result Details](#resultdetails)
> * [Filter Beacons](#filterbeacons)
> * [Dashboard](#dashboard) 
> * [Logs](#logs)
> * [Run Configuration Details](#rcdetails)
> * [Algorithms]()
>   * [DBScan by Variance](#dbscanvar)
>   * [DBScan](#dbscan)
>   * [Agglomerative](#agg)
> * [Other Configurations]()
>   * [Filter Ips](#filterips)
> * [Light/Dark Mode](#lightdark)

#
## <a name="overview"></a>__Overview__

Beacon Huntress uses a combination of Python and Machine Learning to find potential beacons.

## <a name="zeek"></a>__Copy Zeek Logs__

Zeek connection logs are needed in order to run Beacon Huntress.  Below are the steps to copy Zeek Connection Logs.

1. Login to threat-hunt-05 as root.

2. Navigate to /tmp

    ```bash
    cd /tmp
    ```

3. In the example below we are storing Zeek conn.log in `/tmp/raw/data`.  SFTP zeek conn.log files from sonion2-fwd1 (10.0.11.218) to threat-hunt-05. Replace YYYY-MM-DD withthe date of the exercise. As the exercise continues ensure you copy the new hourly zeek log files.Repeat this step for the previous day's zeek conn.log's.

    ```bash
    # CREATE DIRECTORY \
    mkdir -p /tmp/raw/data/YYYY-MM-DD
    
    # START SFTP SHELL
    sftp root@10.0.11.218
    
    # SFTP COMMAND EXAMPLE
    get -R /nsm/zeek/logs/YYYY-MM-DD/conn.* /tmp/raw/data/Y
    ```

## <a name="webpage"></a>__Open Web Page__

To get started 

1. Open a browser window
2. Go to 127.0.0.1:8000
3. You will now see Beacon Huntress loaded.

![Alt text](/static/documentation/images/image.png)

## <a name="config"></a>__Configure__

How to configure Beacon Huntress to run a search.

1. Navigate to Settings and click on General.

![Alt text](/static/documentation/images/image-1.png)

2. You will have the following settings.  

    * __Raw Log Location__
        * Physical location of the raw Zeek logs
    * __Working File Type__
        * The type of files you want to use.  Parquet is the recommended setting
    * __Overwrite Existing Data__
        * Will overwrite all existing results
    * __Verbose Logging__
        * Verbose Logging True/False

![Alt text](/static/documentation/images/image-2.png)

## <a name="examplerun"></a>__Example Run__

This test run is using DB Scan by Variance with some test data.

1. To run a test use the test dataset located in /var/bh_test_data.  From the General Settings page change the Raw Log Location to /var/bh_test_data and click the save button.

![Alt text](/static/documentation/images/image-3.png)

2. Navigate to Execute and select DB Scan by Variance.

![Alt text](/static/documentation/images/image-4.png)

3. DB Scan by Variance expects the parameters below.  In this example do not change anything, just click the run button.   <b><i>PLEASE NOTE: Do not exit this page, you will be directed to the results page once it is completed.</b></i>

    * __Average Delta Time__
        * Average delta time to include in the search using your delta column. Greater than equal (<=).
    * __Connection Count__
        * Total connection count for filtering. Greater than equal (>=).
    * __Time Span Average__
        * The percentage to increase and decrease from the connections total delta span.<br>
		    EXAMPLE: 15 will decrease 15% from the minimum and maximum delta span.<br>
		    min delta = 5<br>
		    max delta = 10<br>
		    span min = 4.25 (5 - (5 * 15%))<br>
		    span max = 11.5 (10 + (10 * 15%))<br>
    * __Variance Percentage__
        * Total variance percentage for filtering. Greater than equal (>=).
    * __Minimum Likelihood Percentage__
        * Minimum likelihood value to identify a beacon.

4. From the results you will have the following columns.

    * __Group ID__
        * This is your beacon search identifier.  This will send you to a detail results screen..
    * __Date__
        * Date of beacon search.
    * __Beacon Count__
        * Number of potential beacons.
    * __Dashboard__
        * Link to a Grafana Dashboard.
    * __Log File__
        * The log file associated with this run.  Used for troubleshooting.
    * __Config__
        * The configuration used for the beacon search.
    * __Delete__
        * Permanently delete the beacon search.     

![Alt text](/static/documentation/images/image-5.png)

## <a name="resultdetails"></a>__Result Details__

From the Result Details page you can further investigate or filter potential beacons.  You will need to investigate these ips to determine if they are beacons.  In this example both IPs are in fact beacons.

1. Click on the Group ID

![Alt text](/static/documentation/images/image-6.png)

2. The result details page will display the following columns.

    * __ID__
        * Row identifier.
    * __Source IP__
        * Source IP Address.
    * __Destination IP__
        * Destination IP Address.
    * __Port__
        * Destination Port.
    * __Connection Count__
        * Number of connections for the source ip, destination ip and destination port.
    * __First Occurrence__
        * Date of first connection.
    * __Last Occurrence__
        * Date of latest connection.
    * __Filter__
        * Remove destination IP from future beacon results.

![Alt text](/static/documentation/images/image-7.png)

## <a name="filterbeacons"></a>__Filter Beacons__

You can filter out any falsely identified beacons from the Result Details page.

1. To filter a destination ip click on the filter button.  The destination ip will have be filtered from all beacon results.  The ip will be excluded in any future results.


![Alt text](/static/documentation/images/image-8.png)

2. To view or remove filtered beacons navigate to Settings, then Filtered Beacons.  Click on the trash can to remove an IP from filtered beacons.  Once remove the IP will show in beacon results.

    * __ID__
        * Row identifier.
    * __IP__	
        * IP that is filtered from beacon results.
    * __Description__
        * Description of why the beacon was filtered.  Please Note: This will be included in a future version.
    * __Filtered Date__
        * The date the IP was filtered.
    * __Option__
        * Delete the IP from the filtered beacons.

![Alt text](/static/documentation/images/image-9.png)

## <a name="dashboard"></a>__Dashboard__

You can access the Grafana Dashboard via the Dashboard button on the Result Details page.  

> ### __Note__
> For addtional details related to the Granfana Dashboard navigate to the github site.<br>
> https://github.com/cmu-sei/Valkyrie_Framework/blob/main/beacon_huntress/src/lib/documentation/dashboard.md

![Alt text](/static/documentation/images/image-10.png)

The dashboard will be embedding inside of Beacon Huntress or will be available via the Open Site in New Window button.

![Alt text](/static/documentation/images/image-11.png)

![Alt text](/static/documentation/images/image-12.png)

## <a name="logs"></a>__Logs__

You can access the Grafana Dashboard via the Dashboard button on the Result Details page.  The log files are used for troubleshooting a beacon search.

![Alt text](/static/documentation/images/image-14.png)

![Alt text](/static/documentation/images/image-15.png)

All logs files are available via the Logs button on the navigation pane.  You can open the log by clicking on the log file link.  To delete log files permanently click on the trash can.

![Alt text](/static/documentation/images/image-17.png)

## <a name="rcdetails"></a>__Run Configuration Details__

Beacon results configurations can be access via the Config link.

![Alt text](/static/documentation/images/image-18.png)

![Alt text](/static/documentation/images/image-19.png)

To find the algorithm used in the search, use the general.cluster type configuration

![Alt text](/static/documentation/images/image-20.png)

## <a name="dbscanvar"></a>__DBScan by Variance__

DBScan by variance uses the same principals as DBScan Clustering but will exclude the amount of records that is needed to be scanned by variance and spans are generated based upon the percentage given. If the variance is outside of the configured threshold it is excluded from the scan. This feature provides all the benefits of a DBScan without the performance overhead.

1. Navigate to Execute and select DB Scan by Variance.

![Alt text](/static/documentation/images/image-4.png)

2. DB Scan by Variance expects the parameters below.  In this example do not change anything, just click the run button.   <b><i>PLEASE NOTE: Do not exit this page, you will be directed to the results page once it is completed.</b></i>

    * __Average Delta Time__
        * Average delta time to include in the search using your delta column. Greater than equal (<=).
    * __Connection Count__	
        * Total connection count for filtering. Greater than equal (>=).
    * __Time Span Average__
        * The percentage to increase and decrease from the connections total delta span.<br>
		    EXAMPLE: 15 will decrease 15% from the minimum and maximum delta span.<br>
		    min delta = 5<br>
		    max delta = 10<br>
		    span min = 4.25 (5 - (5 * 15%))<br>
		    span max = 11.5 (10 + (10 * 15%))<br>
    * __Variance Percentage__
        * Total variance percentage for filtering. Greater than equal (>=).
    * __Minimum Likelihood Percentage__
        * Minimum likelihood value to identify a beacon.

## <a name="dbscan"></a>__DBScan Clustering__

DBScan stands for Density-Based Spatial Clustering of Applications with Noise.  DBScan discovers clusters of different sizes from a large amount of data that contains noise and outliers, see image below.  DBScan primarily uses two parameter Minimum Points and ESP (Epsilion).  Minimum points are the minimum number of points (a threshold) clustered together for a region to be considered dense.  EPS is the distance measure that will be used to locate the points for a cluster.        

1. Navigate to Execute and select DB Scan.

![Alt text](/static/documentation/images/image-22.png)

2. DBScan expects the parameters below.  <b><i>PLEASE NOTE: Do not exit this page, you will be directed to the results page once it is completed.</b></i>

    * __minimum_delta__
        * Minimum number of delta records to search using your delta column.

    * __spans__
        * Spans you wish to search, in list format. Minimum number of delta records to search using your delta column.<br>
        EXAMPLE: Will search two spans 0-5 and 5-10.<br>
        [[0, 5], [5, 10]]<br>

    * __minimum_points_in_cluster__
        * Destination file type (csv or parquet).

    * __minimum_likelihood__
        * Minimum likelihood value to identify a beacon.

## <a name="agg"></a>__Agglomerative Clustering__

Agglomerative cluster is a Hierarchical clustering used to group objects in clusters based upon similarity. Each item is treated as a singleton cluster, working from the bottom up. Clusters that are similar are merged into a larger cluster. This process continues until all the clusters are placed into a single large cluster, see image below.

1. Navigate to Execute and select Agglomerative.

![Alt text](/static/documentation/images/image-21.png)

2. Agglomerative clustering expects the parameters below.  <b><i>PLEASE NOTE: Do not exit this page, you will be directed to the results page once it is completed.</b></i>

    * __Maximum Variance Percentage__
        * Max Variance threshold for any potential beacons.
    * __Minimum Number of Values__
        * Minimum number of delta records to search.
    * __Cluster Factor Percentage__
        * The likelihood percentage for a cluster.
    * __Process Lines__
        * Line amounts to process at a time, in list format.
    * __Minimum Delta Time__
        * Minimum delta time to search by, in milliseconds.

## <a name="filterips"></a>__Filter IPs__

Configuration for additional filtering.  Filtering at this level will exclude/include prior to the beacon algorithm.  Filtered beacons are post beacon algorithm.

1. Navigate to Settings and click on Filters.

![Alt text](/static/documentation/images/image-23.png)

2. Filter expects the parameters below.  Change the parameter/s and click save.

    * __Filter__
        * Apply filters (True or False)
    * __Port Filter__<br>
        * Port filterg in comma delimited format.<br>
            New line per port.<br>
    * __Port Filter Exclusive__
        * Exclusive filter (True or False)<br>
            True = Exclusive<br>
            False = Inclusive<br>
    * __Source IP Filter__<br>
        * Source IP filtering in comma delimited format.<br>
            New line per port.<br
    * __Source IP Filter Exclusive__
        * Exclusive filter (True or False)<br>
            True = Exclusive<br>
            False = Inclusive<br>
    * __Destination IP Filter__<br>
        * Destination IP filtering in comma delimited format.<br>
            New line per port.<br
    * __Destination IP Filter Exclusive__
        * Exclusive filter (True or False)<br>
            True = Exclusive<br>
            False = Inclusive<br>

#
## <a name="lightdark"></a>__Light/Dark Mode__

Beacon Huntress has a light and dark mode.  To toggle between light and dark modes, click on the toggle switch.

### Light to Dark Mode

![Alt text](/static/documentation/images/image-25.png)

### Dark to Light Mode

![Alt text](/static/documentation/images/image-26.png)