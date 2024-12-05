# Welcome to Beacon Huntress

Beacon Huntress uses a combination of Python and Machine Learning to identify potential beacons.

## :material-rabbit: :material-turtle: <a name="fs_beacons"></a>**Fast/Slow Beacon**

Throughout this documentation you will see the terms <i>**Fast Beacon**</i> and <i>**Slow Beacon**</i>. These terms describe two different beaconing patterns according to the time interval that passes between connection events.

- A Fast Beacon is a beacon that has a short interval time. We consider anything <= 5 minutes a <i>**Fast Beacon**</i>.
- A Slow Beacon is a beacon that has a long interval time. We consider anything > 5 minutes a <i>**Slow Beacon**</i>.

???+ tip "Note"
    Beacon Huntress was tested using HTTP/HTTPS beacons. This version of Beacon Huntress has not yet been tested using DNS beacons -- although it should work.

## :material-lightbulb: **How to use**

Beacon Huntress can be used in two ways: via [Docker](#docker) or a [Jupyter Notebook](jupyter).

???+ warning "Warning"
    For the purposes of this documentation, Beacon Huntress is assumed to have been downloaded via Git.

To run Beacon Huntress, you will need to answer the following questions:

1. Where are my Zeek logs located?
2. Do I want to filter out any connections in my logs?
3. How many minutes do potential beacons wait before calling back? Are the beacons [Fast](#fs_beacons) or [Slow](#fs_beacons)?
4. How many connections does a potential beacon need to have in order to be reported?

With answers to these questions, you can begin to configure Beacon Huntress to run. Check the [Tutorial](tutorial) section for an example.

???+ tip "Beacon Huntress Default Settings"
    - Raw Bro/Zeek logs are copied to /tmp/raw/data. <br>
    - All connections using ports 80 and 443 are included. <br>
    - Local connections, i.e. connections with 127.0.0.1 as the source or destination, are excluded.
    - Various high-usage top sites are excluded. See [Default Filtered Hosts](defaultfilteredhosts) for the list of filtered sites.

## :material-docker: <a name="docker"></a>**Docker Setup**

The quickest way to set up this software is via docker-compose.

Before starting, ensure the following:

- Docker is installed and running (check with `docker --version` in the terminal).
- Docker-compose is installed (check with `docker-compose --version` or `docker compose --version` in the terminal).
- You have Zeek connection logs available.
- You have downloaded the Valkyrie Framework.

Good to go? OK, proceed with the following in the terminal:

1. `cd` to the Valkyrie Framework directory
2. Run `docker-compose up -d` or `docker compose up -d` depending on your docker version. This will create the database, and may take some time to complete.
3. Note that some docker volumes were created.
   - `_mysql` is your database, so that if the container stops, you do not lose previously saved data
4. Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser to access the Beacon Huntress Web UI.
5. Continue to the [Tutorial](tutorial) section for examples on how to start using Beacon Huntress.

For troubleshooting, check `docker logs -f beacon_huntress` to access Web UI logging.

???+ tip "Note"
    Beacon Huntress Docker containers will fail if you attempt to use any of the following ports:

      - 3000 (Grafana)
      - 3306 (MySQL)
      - 8000 (Django)

Once you have the list of IP's from the dashboard you should conduct further investigation and analysis of the Potential Beacons using tools such as nslookup, pcaps, etc. to assess their veracity. Depending on network traffic and Beacon Huntress configuration, some connections identified as Potential Beacons may not be malicious. You can filter these sites out of the results; for more details see the [User Interface](interface) documentation.

See the [Tutorial](tutorial) for running Beacon Huntress.

## :material-license: License

[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  
Copyright 2023 Carnegie Mellon University. See the [license file](https://github.com/cmu-sei/valkyrie_framework/blob/master/license.txt) for more details.
