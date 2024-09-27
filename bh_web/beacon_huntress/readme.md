![Beacon Huntress](src/lib/images/beacon_huntress.png)
#
## __Table of Contents__

> * [Home](../readme.md)
> * [Overview](#overview)
> * [How to use](#howtouse)
>   * [Docker Setup](#docker)
>   * [Tutorial](src/lib/documentation/tutorial.md)
>   * [User Interface](src/lib/documentation/interface.md)
>   * [Beacon Huntress Dashboard](src/lib/documentation/dashboard.md)
>   * [Jupyter Notebook](src/lib/documentation/jupyter.md)
> * [Beacons Algorithms](src/lib/documentation/beaconalgo.md)


#
## <a name="overview"></a>__Overview__

Beacon Huntress uses a combination of Python and Machine Learning to identify potential beacons.

### <a name="fs_beacons"></a>__Fast/Slow Beacon__
Throughout this documentation you will see the terms <i>__Fast Beacon__</i> and <i>__Slow Beacon__</i>. These terms describe two different beaconing patterns according to the time interval that passes between connection events. 
* A Fast Beacon is a beacon that has a short interval time.  We consider anything <= 5 minutes a <i>__Fast Beacon__</i>.
* A Slow Beacon is a beacon that has a long interval time.  We consider anything > 5 minutes a <i>__Slow Beacon__</i>.

> ### __Note__<br>
> 
> Beacon Huntress was tested using HTTP/HTTPS beacons. This version of Beacon Huntress has not yet been tested using DNS beacons -- although it should work.

<br>


## <a name="howtouse"></a>__How to use__

Beacon Huntress can be used in two ways: via [Docker](#docker) or a [Jupyter Notebook](src/lib/documentation/runoptions.md#a-idjupyterajupyter-notebook).<br>

> ### __Note__<br>
> 
> For the purposes of this documentation, Beacon Huntress is assumed to have been downloaded via Git.


To run Beacon Huntress, you will need to answer the following questions:<br>

1. Where are my Zeek logs located?
2. Do I want to filter out any connections in my logs?
3. How many minutes do potential beacons wait before calling back?  Are the beacons [Fast](#fs_beacons) or [Slow](#fs_beacons)?
4. How many connections does a potential beacon need to have in order to be reported?



With answers to these questions, you can begin to configure Beacon Huntress to run. Check the [Tutorial](src/lib/documentation/tutorial.md) section for an example.

> ### __Beacon Huntress Default Settings__<br>
> * Raw Bro/Zeek logs are copied to /tmp/raw/data. <br>
> * All connections using ports 80 and 443 are included. <br>
> * Local connections, i.e. connections with 127.0.0.1 as the source or destination, are excluded.
> * Various high-usage top sites are excluded. See [Default Filtered Hosts](src/lib/documentation/defaultfilteredhosts.md) for the list of filtered sites.


<br>

## <a name="docker"></a>__Docker Setup__

The quickest way to set up this software is via docker-compose. 

Before starting, ensure the following:

* Docker is installed and running (check with `docker --version` in the terminal).
* Docker-compose is installed (check with `docker-compose --version` or `docker compose --version` in the terminal).
* You have Zeek connection logs available.
* You have downloaded the Valkyrie Framework.


Good to go? OK, proceed with the following in the terminal:

1. `cd` to the Valkyrie Framework directory
2. Run `docker-compose up -d` or `docker compose up -d` depending on your docker version. This will create the database, and may take some time to complete.
3. Note that some docker volumes were created.
   - `_mysql` is your database, so that if the container stops, you do not lose previously saved data
4. Visit http://127.0.0.1:8000 in your web browser to access the Beacon Huntress Web UI. 
5. Continue to the [Tutorial](src/lib/documentation/tutorial.md) section for examples on how to start using Beacon Huntress.

For troubleshooting, check `docker logs -f beacon_huntress` to access Web UI logging.

> ### __Note__<br>
> 
> Beacon Huntress Docker containers will fail if you attempt to use any of the following ports:
> * 3000 (Grafana)
> * 3306 (MySQL)
> * 8000 (Django)

Once you have the list of IP's from the dashboard you should conduct further investigation and analysis of the Potential Beacons using tools such as nslookup, pcaps, etc. to assess their veracity. Depending on network traffic and Beacon Huntress configuration, some connections identified as Potential Beacons may not be malicious.  You can filter these sites out of the results; for more details see the [User Interface](src/lib/documentation/interface.md) documentation.



### See [Tutorial](src/lib/documentation/tutorial.md) for running Beacon Huntress.

#
Valkyrie Framework<br>
Copyright 2023 Carnegie Mellon University.<br>
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.<br>
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.<br>
DM23-0210<br>