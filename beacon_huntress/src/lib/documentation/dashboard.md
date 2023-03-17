![Beacon Huntress](../images/beacon_huntress.png)
#
## __Table of Contents__

> * [Home](../../../readme.md)
> * [Overview](#overview)
>   * [Beacon](#beacon)
>       * [Total Records](#totalrecords)
>       * [Delta Connection](#deltaconnection)
>       * [Potential Beacons](#potentialbeacons)
#
## <a name="overview"></a>__Overview__

Beacon Huntress provides a Grafana dashboard to assist with finding beacons.  You can use the dashboard you can drill into each level to provide more details on the data.<br>
When using Docker this is preferred method to showing any potential beacons.  You can login to Grafana by clicking the link below.  The credentials can be found the the dashboard configuration located in src/config/dashboard.conf.

[127.0.0.1:3000](http://127.0.0.4:3000)

#
## __Beacon__

Beacon is the main dashboard, and most panels are clickable for details.  Below are the sections to the beacon dashboard.

1) [Total Records](#totalrecords) <i>(clickable)</i>
2) [Delta Connections](#deltaconnection) <i>(clickable)</i>
3) Potential Beacons Over Time
    * Timeline of beacons across your files.
4) Potential Beacons Count
    * Count of potential beacons.
5) [Potential Beacons]() <i>(clickable)</i>

![](../images/beacon_dash.png)



#
### <a name="totalrecords"></a>__Total Records__

Total Records will display the total number of Bro/Zeek connections contained in your files.  When clicking on the panel you will go to the File Details dashboard.<br>
File Details dashboard will display the source file location, number of connections in the file and the number of connections that are potential beacons.

![](../images/dash_filedetail.png)

#
### <a name="deltaconnection"></a>__Delta Connection__

Delta Connection will display the total number of Delta Connections.  Delta Connections are a unique group by Source IP Address, Destination IP Address and Port.<br>
When clicking on the panel you will go to the Delta Details dashboard.  This screen will pull the groupings, minimum connection time, maximum connection time, total connection count, average delta in milliseconds, and average delta in minutes. You can also use this as dashboard to find potential beacons.  When `clicking on the Destination IP link`, another dashboard will display cluster groupings for the deltas.  Below are examples of a Beacon Cluster and a Non-Beacon Cluster.  

![](../images/dash_delta.png)

__Beacon Cluster Example__

This is an example of a beacon's cluster points.  Notice how the deltas are in clustered in several groups.  This would be a good indication that this is a potential beacon, for there isn't much varing of deltas.

![](../images/dash_deltadetail_b.png)

__Non-Beacon Cluster Example__

This is an example of a non-beacon's cluster points.  Notice how the deltas are in a straight line and there is not much spacing or groups.  Too much varing of deltas would be a good indication that this is actual traffic and not a potential beacon.

![](../images/dash_deltadetail_nb.png)

#
### <a name="potentialbeacons"></a>__Potential Beacons__

Potential Beacon will display the total number of potential beacon based upon your configuration file.  When `clicking on the Destination IP link` you will go to the Beacon Details dashboard.  This screen will display the cluster groupings as well as providing details from the Bro/Zeek logs such as Connection Duration, Source/Destination Bytes, and Connection State.  This example is a beacon.  Notice how the deltas are in clustered in several groups.  This would be a good indication that this is a potential beacon, for there isn't much varing of deltas.

![](../images/dash_beacon.png)


#
Valkyrie Framework<br>
Copyright 2023 Carnegie Mellon University.<br>
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.<br>
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.<br>
DM23-0210<br>