![Beacon Huntress](../images/beacon_huntress.png)
#
## __Table of Contents__

> * [Home](../../../readme.md)
> * [Execute](#)
> * [Settings](#)
>      * [Data Sources](#ds)
>      * [Filters](#)
>      * [Filtered Hosts](#)
>      * [Default Filtered Hosts](#dfh)
> * [Results](#)
>      * [Dashboard](#)
>      * [Filters](#)
>      * [Filtered Hosts](#)
> * [Logs](#)


#
# <a name="home"></a>__Overview__
This page outlines the usage and functionalities of the Beacon Huntress UI.
<br></br>

# <a name="execute"></a>__Execute__

The Execute tab has three sections: Quick Cluster Search, Cluster Search, and Hierarchical Search. For more information on Beacon Huntress algorithm configurations, see [Beacon Huntress Algorithms](../documentation/beaconalgo.md).
<br></br>
# <a name="execute"></a>__Settings__

## <a name="ds"></a>__Data Sources__

The Data Sources section contains the data sources for Beacon Huntress. Reusable data sources are now available in Beacon Huntress. Current Data Source types are Zeek Connection Logs, Security Onion and Elastic. 

> ### __Note__<br>
> 
> Beacon Huntress uses Zeek Connection Logs to find beacons. Elastic data sources must use Zeek Connection indices.


1. Navigate to the Settings tab and click on Data Sources. 

    ![](/bh_web/static/documentation/images/datasources.png)

2. Zeek Connection Logs is the default data source, and the source file location is entered at run time. To add a new data source, click the New button.

    ![](/bh_web/static/documentation/images/datasources_new.png)

3. Select a Data Source Type from the drop-down list. Input fields will be dynamically generated based upon the chosen type.

    ![](/bh_web/static/documentation/images/datasources_dsdrop.png)

### <a name="zeek_ds"></a>__Zeek Connection Logs__

Zeek Connection Logs are raw Zeek connection logs.

![](/bh_web/static/documentation/images/ds_zeek.png)

* The following inputs are required for Zeek Connection Logs:

    * __Data Source Name__
        * Unique name for your data source.<br>
    * __Raw Log Location__
        * Raw Zeek file location.<br>

### <a name="seconion_ds"></a>__Security Onion__

Security Onion data source will use Zeek connection logs contained inside of the application. The indices will be automatically selected. Click [API Key](/bh_web/beacon_huntress/src/lib/documentation/interface.md#api) for more details.

![](/bh_web/static/documentation/images/ds_seconion.png)

* The following inputs are required for Security Onion:

    * __Data Source Name__
        * Unique name for your data source.<br>
    * __Host__
        * Security Onion Elastic Host Name.<br>
    * __Port__
        * Security Onion Elastic Port Name.<br>
    * __API Key__
        * Security Onion Elastic API Name.<br>        
        * API Key can be viewed by clicking the eye button.

### <a name="elastic_ds"></a>__Elastic__

Elastic data source will use Zeek connection logs contained inside of the application. The indices will be automatically selected. Click [API Key](/bh_web/beacon_huntress/src/lib/documentation/interface.md#api) for more details.

![](/bh_web/static/documentation/images/ds_elastic.png)

* The following inputs are required for Elastic:

    * __Data Source Name__
        * Unique name for your data source.<br>
    * __Host__
        * Elastic Host Name.<br>
    * __Port__
        * Elastic Port Name.<br>
    * __API Key__
        * Elastic API Name.<br>
        API Key can be viewed by clicking the eye button.
    * __Index__
        * Elastic Index Name (Multi-Select).<br>
        Click the button to load the indices. You must have the correct Host, Port and API Key in order to load the indices.            

#
## <a name="filter_ip"></a>__Filters__

This section allows for the configuration of additional IP and port filtering. Filtering at this level will include/exclude certain results before the beacon algorithm runs.

1. Navigate to Settings and click on Filters.

    ![](/bh_web/static/documentation/images/filter_settings.png)

2. The following parameters can be changed:

    * __Filter__
        * Checkbox to turn filter settings on or off. <br>
        Checked = Apply filters<br>
        Unchecked = Do not apply filters
    * __Port Filter__
        * A list of ports, in comma delimited format.<br>
    * __Port Filter Exclusive__
        * Checkbox to determine whether the ports in the Port Filter list are included or excluded from results.<br>
        Checked = Excluded<br>
        Unchecked = Included
    * __Source IP Filter__
        * A list of Source IPs, in comma delimited format.<br>
    * __Source IP Filter Exclusive__
        * Checkbox to determine whether the IPs in the Source IP Filter list are included or excluded from results.<br>
        Checked = Excluded<br>
        Unchecked = Included
    * __Destination IP Filter__
        * A list of Destination IPs, in comma delimited format.<br>
    * __Destination IP Filter Exclusive__
        * Checkbox to determine whether the IPs in the Destination IP Filter list are included or excluded from results.<br>
        Checked = Excluded<br>
        Unchecked = Included


#
## <a name="filtered_hosts"></a>__Filtered Hosts__

The Filtered Hosts section will display any additional IP addresses that have been manually excluded from the beacon results. IPs that have been excluded from results using the Filters settings will not be displayed here. You can remove an IP address from this list by clicking on the "Trash Can" icon.
<br></br>
    ![](/bh_web/static/documentation/images/filtered_hosts.png)

#
## <a name="dfh"></a>__Default Filtered Hosts__

Default Filtered Hosts is a premade list of popular websites that are automatically filtered out from the results. These sites will not appear on the Filtered Hosts page. To see the complete list, go to the [Default Filtered Hosts](defaultfilteredhosts.md) page. 


#
# <a name="results"></a>__Results__

You can navigate through results found by Beacon Huntress using the options on the Results page. Click on "Group ID" to view potential beacons. Select "Dashboard" to display those results in a Grafana dashboard. Click on "Log File" to view the run logs. Choose "Config" to display the runtime configuration. Select "Delete" to <i><b>PERMANENTLY</b></i> remove the result set.

![ui_results](/bh_web/static/documentation/images/results_quick_cluster.png)

#
# <a name="logs"></a>__Logs__

The Logs section holds the runtime logs for each Beacon Huntress execution. Logs can also be accessed via the [Results page](#results).

1. Navigate to Logs.

    ![](/bh_web/static/documentation/images/log_highlighted.png)

2. Click on "File Name" to pull the details.

    ![](/bh_web/static/documentation/images/log_details.png)

#
Valkyrie Framework<br>
Copyright 2023 Carnegie Mellon University.<br>
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.<br>
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.<br>
DM23-0210<br>