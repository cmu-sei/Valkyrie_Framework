![Beacon Huntress](../images/beacon_huntress.png)
#
## __Table of Contents__

> * [Home](../../../readme.md)
> * [Dashboard Overview](#overview)
>   * [Beacon](#beacon)
>       * [Total Records](#totalrecords)
>       * [Delta Connection](#deltaconnection)
>       * [Potential Beacons](#potentialbeacons)
#
## <a name="overview"></a>__Dashboard Overview__

Beacon Huntress provides a Grafana dashboard to assist with finding beacons. When using Docker, the dashboard is the best resource for visualizing and analyzing the details of potential beacons. Login to Grafana by visiting the link below in your web browser. Credentials can be found in the dashboard configuration file located at src/config/dashboard.conf.

Beacon Huntress Dashboard URL:  http://127.0.0.1:3000

#
## __Beacon__

The main dashboard is called Beacon. Clicking on the panels will provide additional information about the shown data. The Beacon dashboard includes the following panels: 

1) [Total Records](#totalrecords) <i>(clickable)</i>
2) [Delta Connections](#deltaconnections) <i>(clickable)</i>
3) [Potential Beacons](#potentialbeacons) <i>(clickable)</i>
4) Potential Beacons Connections Over Time
    * Timeline of the beacon connections present in the provided files.


![](../images/tutorial/ui_dash.png)



#
### <a name="totalrecords"></a>__Total Records__

The Total Records panel will show the total number of Bro/Zeek connections contained in your logs.  Clicking on the panel will take you to the File Details dashboard, which will display the source file location, the number of total connections in the file, and the number of connections that are potential beacons.

![](../images/dash/dash_filedetail.png)

#
### <a name="deltaconnections"></a>__Delta Connections__

The Delta Connections panel will display the total number of Delta Connections found in the logs. A Delta Connection is a unique grouping of repeated connections between a Source IP and a Destination IP; these may or may not be labeled Potential Beacons depending on the parameters used when configuring your cluster search algorithms; see the Beacon Algorithms section for more information on setting up your configuration file. Clicking on the panel will take you to the Delta Details dashboard, which provides additional information on each of the identified Delta Connections. 
Each connection listing will show the Source IP, Destination IP, Port, minimum and maximum times between connections, total connection count, average delta in milliseconds, and average delta in minutes.  Clicking on the Destination IP link will open a dashboard that displays the cluster groupings for the deltas.

![](../images/dash/dash_delta.png)

#
### <a name="potentialbeacons"></a>__Potential Beacons__

The Potential Beacon panel will display the total number of potential beacons that Beacon Huntress has identified based on your configuration file.  Click on the Destination IP link to go to the Beacon Details dashboard. This screen will display the cluster groupings and provide additional information from the Bro/Zeek logs such as Connection Duration, Source/Destination Bytes, and Connection State. In the example below, the deltas are closely clustered in several groups, and there is little variation in the delta times between each connection event. Low variance in deltas is typically a good indication of a potential beacon.

![](../images/dash/dash_beacon.png)


#
Valkyrie Framework<br>
Copyright 2023 Carnegie Mellon University.<br>
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.<br>
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.<br>
DM23-0210<br>