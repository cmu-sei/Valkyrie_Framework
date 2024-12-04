## **Table of Contents**

> - [Home](../../../readme.md)
> - [Execute](#)
> - [Settings](#)
>   - [General](#general)
>   - [Filters](#)
>   - [Filtered Hosts](#)
>   - [Default Filtered Hosts](#dfh)
> - [Results](#)
>   - [Dashboard](#)
>   - [Filters](#)
>   - [Filtered Hosts](#)
> - [Logs](#)

# <a name="home"></a>**Overview**

This page outlines the usage and functionalities of the Beacon Huntress GUI.
<br></br>

# <a name="execute"></a>**Execute**

The Execute tab has three sections: Quick Cluster Search, Cluster Search, and Hierarchical Search. For more information on Beacon Huntress algorithm configurations, see [Beacon Huntress Algorithms](../documentation/beaconalgo.md).
<br></br>

# <a name="execute"></a>**Settings**

## <a name="general"></a>**General**

The General section contains the basic configuration for Beacon Huntress. These settings must be configured in order for Beacon Huntress to run.

1. Navigate to the Settings tab and click on General.

   ![](/assets/img/bh/gen_settings.png)

2. The following settings are available:

   - **Raw Log Location**
     - Physical location of the raw Zeek logs.
   - **Working File Type**
     - The type of files you want to use. Parquet is the recommended setting.
   - **Overwrite Existing Data**
     - Check this box to overwrite existing results after each execution.
   - **Verbose Logging**
     - Verbose Logging True/False.

## <a name="filter_ip"></a>**Filters**

This section allows for the configuration of additional IP and port filtering. Filtering at this level will exclude/include certain results before the beacon algorithm runs.

1. Navigate to Settings and click on Filters.

   ![](/assets/img/bh/filter_settings.png)

2. The following parameters can be changed:

   - **Filter**
     - Checkbox to turn filter settings on or off. <br>
       Checked = Apply filters<br>
       Unchecked = Do not apply filters
   - **Port Filter**
     - A list of ports, in comma delimited format.<br>
   - **Port Filter Exclusive**
     - Checkbox to determine whether the ports in the Port Filter list are included or excluded from results.<br>
       Checked = Excluded<br>
       Unchecked = Included
   - **Source IP Filter**
     - A list of Source IPs, in comma delimited format.<br>
   - **Source IP Filter Exclusive**
     - Checkbox to determine whether the IPs in the Source IP Filter list are included or excluded from results.<br>
       Checked = Excluded<br>
       Unchecked = Included
   - **Destination IP Filter**
     - A list of Destination IPs, in comma delimited format.<br>
   - **Destination IP Filter Exclusive**
     - Checkbox to determine whether the IPs in the Destination IP Filter list are included or excluded from results.<br>
       Checked = Excluded<br>
       Unchecked = Included

## <a name="filtered_hosts"></a>**Filtered Hosts**

The Filtered Hosts section will display any additional IP addresses that have been manually excluded from the beacon results. IPs that have been excluded from results using the Filters settings will not be displayed here. You can remove an IP address from this list by clicking on the "Trash Can" icon.
<br></br>
![](/bh_web/static/documentation/images/filtered_hosts.png)

## <a name="dfh"></a>**Default Filtered Hosts**

Default Filtered Hosts is a premade list of popular websites that are automatically filtered out from the results. These sites will not appear on the Filtered Hosts page. To see the complete list, go to the [Default Filtered Hosts](defaultfilteredhosts.md) page.

# <a name="results"></a>**Results**

You can navigate through results found by Beacon Huntress using the options on the Results page. Click on the "Group ID" to view potential beacons. Select "Dashboard" to display those results in a Grafana dashboard. Click on "Log File" to view the run logs. Choose "Config" to display the runtime configuration. Select "Delete" to <i><b>PERMANENTLY</b></i> remove the result set.

![ui_results](/assets/img/bh/results_quick_cluster.png)

# <a name="logs"></a>**Logs**

The Logs section holds the runtime logs for each Beacon Huntress execution. Logs can also be access via the [Results page](#results).

1. Navigate to Logs.

   ![](/assets/img/bh/log_highlighted.png)

2. Click on "File Name" to pull the details.

   ![](/assets/img/bh/log_details.png)
