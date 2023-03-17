![Beacon Huntress](src/lib/images/beacon_huntress.png)
#
## __Table of Contents__

> * [Overview](#overview)
> * [How to use](#howtouse)
> * [Command-line Example](#cli)
> * [Docker Example](#docker)
> * [Installation](src/lib/documentation/installation.md)
> * [Configuration](src/lib/documentation/configuration.md) 
> * [Run Options](src/lib/documentation/runoptions.md)
>   * [Command-line Interface (CLI)](src/lib/documentation/runoptions.md#a-idcliacommand-line-interface-cli)
>   * [Docker](src/lib/documentation/runoptions.md#a-iddockeradocker)
>   * [Jupyter Notebook](src/lib/documentation/runoptions.md#a-idjupyterajupyter-notebook)
> * [Search for Beacons](src/lib/documentation/beaconsearch.md)
> * [Dashboard](src/lib/documentation/dashboard.md)
> * [Modules](src/lib/documentation/modules.md)
#
## <a name="overview"></a>__Overview__

Beacon Huntress is designed to identify malicious network beacons. But first, what are network beacon? We define network beacons as events that occur (and re-occur) on a timed interval. Network beacons can be compared to a heartbeat signal over time. While there are legitimate uses for network beacons (e.g., WiFi, obtaining instructions from an API, beaming telemetry data home), network beaconing can also be a byproduct of malware connecting to a command and control (C2) server. Malware communicating with a C2 server can pass information or request new instructions.

Beacons can be difficult to spot with traditional security tools -- especially those that communicate infrequently. Beacon Huntress finds beacons within Zeek logs using machine learning algorithms that identify clustering.

Beacon Huntress uses a combination of Python and Machine Learning to find potential beacons.

### <a name="fs_beacons"></a>__Fast/Slow Beacon__
Throughout this documentation you will hear the term <i>__Fast Beacon__</i> and <i>__Slow Beacon__</i>.  These terms are related to searching for beacons at a time interval.
* Fast Beacon is a beacon that has a short interval time.  We consider anything <= 5 minutes a <i>__Fast Beacon__</i>.
* Slow Beacon is a beacon that has a long interval time.  We consider anything > 5 minutes a <i>__Slow Beacon__</i>.

> ### __Note__<br>
> 
> Beacon Huntress was tested using HTTP/HTTPS beacons. This version of Beacon Huntress has not yet been tested using DNS beacons -- although it should work.

#
## <a name="howtouse"></a>__How to use__

Once downloaded, Beacon Huntress can be used in multiple ways, including: [Docker](#docker), [Command-line Interface (CLI)](#cli) and [Jupyter Notebooks](src/lib/documentation/runoptions.md#a-idjupyterajupyter-notebook).<br>
To [configure](src/lib/documentation/configuration.md) Beacon Huntress, you will need to answer the following questions:<br>

> ### __Note__<br>
> 
> The assumption has been made that Beacon Huntress was downloaded via Git.


1. How do I want to run Beacon Huntress?
2. Where are my Zeek logs located?
3. Do I want to filter out any connections in my logs?
4. How many minutes do potential beacons wait before calling back?  Are the beacons [Fast](#fs_beacons) or [Slow](#fs_beacons)?
5. How many connections does a potential beacon need to have in order to be reported?
6. Do I want my results displayed to a dashboard or order to a command line?


With answers to these questions, you can begin to configure Beacon Huntress to run.  When using Docker or CLI you must setup the configuration files to check for beacons.<br>
Check the [Configuration Files](src/lib/documentation/configuration.md) section for more details.

#
## <a name="docker"></a>__Docker Example__

The quickest way to demo this software is via docker-compose. 
<br>This assumes:

1. Docker is installed and running (try `docker --version` in the terminal).
2. Docker-compose is installed (try `docker-compose --version` in the terminal).
3. You have Zeek logs available.

Good to go? OK, proceed with the following in the terminal:

1. `cd` to this directory
2. `docker-compose up -d` this may take some time on first run while the database is created
3. Note that some docker volumes were created, 
   - `_beacon_huntress` maps to where we will put Zeek logs for processing
   - `_mysql` is your database, so that if the container stops, you do not lose previously saved data
4. Place your Bro/Zeek logs in `_beacon_huntress` for processing.
5. Check `docker logs -f beacon_huntress` for access to logging.
6. Follow the instructions for the [dashboard](src/lib/documentation/dashboard.md).
7. Once you have the list of IP/s from the dashboard you should conduct further investigation and analysis of the Potential Beacons using tools such
as nslookup, pcaps, etc. to assess their veracity. Depending on network traffic and Beacon Huntress
configuration, some connections identified as Potential Beacons may not be malicious.  You can filter
these sites out of the results, for more details see [configuration](src/lib/documentation/configuration.md).

> ### __Note__<br>
> 
> Beacon Huntress default search option is [DBScan by Variance](#dbscanbyvariance) with [Slow Beacon Search](#fs_beacons) used in [dbscan_by_variance()](#dbscanbyvariance).<br>
> In order to change configuration, check the [Configuration Files](src/lib/documentation/configuration.md) section.


#
## <a name="cli"></a>__Command-line Example__

> ### __Note__<br>
> 
> For a manual install you must have Python 3.8 or greater, MySQL with a MySQL client and Granfana installed! It is recommended that you use that you use Docker for Beacon Huntress.

Here is a set of actions one would to take based on one example set of answers:

1. If I want to just use a [Command-line Interface (CLI)](src/lib/documentation/runoptions.md#a-idcliacommand-line-interface-cli), and complete a 1 time run, I would:
    * Change to the src directory:
      `cd src`
    * Setup the Python Virtual Environment:
      `sudo python3 -m venv bh`
    * Activate the Python Virtual Environment:
      `source bh/bin/activate`
    * Import the requirments file:
      `sudo pip3 install -r setup/requirements.txt`
    * Set my configuration in the  `src/config/config.conf` file.

2. My raw zeek logs are in /tmp/raw/data, so I set __raw_loc__ to that location within the Beacon Huntress YAML configuration file.  One needs to supply file locations for each step of the Beacon Huntress pipeline. 
<br>  We recommend that you create a new folder for each location.  The locations required for pipeline execution are __bronze_loc__, __silver_loc__ and __gold_loc__.

    ```yaml
      raw_loc: "/tmp/raw/data"
      bronze_loc: "/tmp/bronze/data"
      silver_loc: "/tmp/silver/data"
      gold_loc: "/tmp/gold/data"
    ```

3. Yes, I want to filter out some connections in my logs. I only want to include connection using ports 80 or 433.  I need to configure an __inclusive__ port filter.  Set the __port__ filter __exclude__ to false and __filter__ to a list of ports [80, 443].

    ```yaml
      port:
        exclude: false
        filter: [80, 443]
    ```

4. I want to look for beacons that take 20 minutes to call back.  So, I am looking for a slow beacon. DBScan by Variance is a good ML algorithm to use to look for slow beacons. I should set the __cluster_type__ = dbscan_var.

    ```yaml
      cluster_type: dbscan_var
    ```

5. I want to look for beacons that have at least 10 connections.  DBscan by variance has it's own configuration that I must now set.<br>
    * I want beacons that have at least 10 connections, so I need to set __conn_cnt__ to 10
    * I want beacons that call back in 20 minutes or less, so I need to set the __avg_delta__ to 20
    * There are more setting that I can set for this algorithm, so please see BACKHERE for more details
    ```yaml
      # DBSCAN BY VARIANCE CLUSTERING SETTINGS
      dbscan_var:
        avg_delta: 20
        conn_cnt: 10
    ```

6. I just want the results displayed as text on the screen.  I need to set the __dashboard__ to false.  All other __dashboard__ settings can remain the same.

    ```yaml
    # DASHBOARD SETTINGS
    # ENABLE DASHBOARD & SET CONFIG
    dashboard:
      dashboard: false
      conf: "config/dashboard.conf"
    ```

Now that you have configured Beacon Huntress, you can run a search.
Run `python3 beacon_huntress.py` to check for beacons.

```shell
(bh) python3 beacon_huntress.py
 ____                                     _   _                _
| __ )   ___   __ _   ___   ___   _ __   | | | | _   _  _ __  | |_  _ __   ___  ___  ___ 
|  _ \  / _ \ / _` | / __| / _ \ | '_ \  | |_| || | | || '_ \ | __|| '__| / _ \/ __|/ __|
| |_) ||  __/| (_| || (__ | (_) || | | | |  _  || |_| || | | || |_ | |   |  __/\__ \\__ \
|____/  \___| \__,_| \___| \___/ |_| |_| |_| |_| \__,_||_| |_| \__||_|    \___||___/|___/

Beacon Huntress starting the hunt!
        * Building Bronze Layer |################################| 5/5 file/s | 0:00:14
        * Filter Process |################################| 5/5 file/s | 0:00:03
        * Building Delta File |################################| 5/5 steps/s | 0:00:04
        * Searching for Beacons (DBScan by Variance) |################################| 1/1 connections | 0:00:00
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  POTENTIAL BEACONS (1) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
       source_ip       dest_ip  port  connection_count  avg_delta
0  127.0.0.1      127.0.0.1    80                15      20
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

7. Now you should conduct further investigation and analysis of the Potential Beacons using tools such
as nslookup, pcaps, etc. to assess their veracity. Depending on network traffic and Beacon Huntress
configuration, some connections identified as Potential Beacons may not be malicious.  You can filter
these sites out of the results, for more details see [configuration](src/lib/documentation/configuration.md).

#
Valkyrie Framework<br>
Copyright 2023 Carnegie Mellon University.<br>
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.<br>
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.<br>
DM23-0210<br>