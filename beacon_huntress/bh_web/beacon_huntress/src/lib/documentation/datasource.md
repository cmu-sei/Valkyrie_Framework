![Beacon Huntress](../../../src/lib/images/beacon_huntress.png)
#
## __Table of Contents__

> * [Home](../../../readme.md)
> * [Data Sources](#datasource)
>   * [Elastic](#elastic)
>   * [Security Onion](#seconion)
>   * [Zeek Connection Logs](#zeek)
> * [Create Elastic API](#api)

## <a name="datasource"></a>__Data Sources__

Beacon Huntress now has the ability to store data sources to allow repeatable usage. Current data types are Zeek Connection Logs, Elastic Indices, and Security Onion Indices. Beacon Huntress defaults to the Zeek Connection Logs data source, which allows the user to select their raw Zeek connection logs. For details on setting up an [API Key](#api), please click the link.

## <a name="elastic"></a>__Elastic__

The Elastic data source will use Zeek connection logs contained inside of the application. The indices will be manually selected. Click the link for details on setting up an [API](#api).

To create an Elastic data source, follow the steps below.

1. Under "Settings" click "Data Sources".
2. Click the "New" button.

    ![](/bh_web/static/documentation/images/ds_page.png)

3. Select "Elastic" in the "Data Source Type" drop-down list.

    * The following inputs are required for Elastic:

        * __Data Source Name__
            * Unique name for your data source.<br>
        * __Host__
            * Elastic Host Name.<br>
        * __Port__
            * Elastic Port Name.<br>
        * __API Key__
            * Elastic API Name.<br>        
            * API Key can be viewed by clicking the eye button.
        * __Index__
            * Elastic Index Name (Multi-Select).<br>        
            * Click the button to load the indices. <b><i>You must have the correct Host, Port and API Key in order to load the indices.</b></i>

    ![](/bh_web/static/documentation/images/ds_elastic.png)

4. Click the "Add" button to create the new data source.

    ![](/bh_web/static/documentation/images/new_es_ds.png)

5. The new data source will now be available for any "Search For Beacon" data source.

    ![](/bh_web/static/documentation/images/es_search.png)


## <a name="seconion"></a>__Security Onion__

The Security Onion data source will use Zeek connection logs contained inside of the application. The indices will be automatically selected. Click the link for details on setting up an [API](#api).

1. Under "Settings" click "Data Sources".
2. Click the "New" button.

    ![](/bh_web/static/documentation/images/ds_page.png)

3. Select "Elastic" in the "Data Source Type" drop-down list.

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

    ![](/bh_web/static/documentation/images/ds_seconion.png)

4. Click "Add" button to create the new data source.

    ![](/bh_web/static/documentation/images/new_so_ds.png)

5. The new data source will now be available for any "Search For Beacon" data source.

    ![](/bh_web/static/documentation/images/so_search.png)



## <a name="zeek"></a>__Zeek Logs__

Zeek Connection Logs must be provided for Beacon Huntress to analyze. Follow the steps below to copy your Zeek logs from their initial location to a local directory that can be accessed by Beacon Huntress. It's recommended to organize the logs into separate directories, with each directory corresponding to a single day.

1. In this example, we will copy Zeek connection logs to the ```/zeek``` directory. The ```/zeek``` directory is mounted to the Docker container beacon_huntress.

    ```bash
    # CREATE DIRECTORY (REPLACE YYYY-MM-DD WITH DATE)
    mkdir -p /zeek/raw/data/YYYY-MM-DD

    # START SFTP SHELL
    sftp root@YOUR_FTP_SERVER

    # SFTP COMMAND EXAMPLE (REPLACE YYYY-MM-DD WITH DATE)
    get -R zeek/logs/YYYY-MM-DD/conn.* /zeek/raw/data/YYYY-MM-DD
    ```

2. Under "Settings" click "Data Sources".
3. Click the "New" button.

    ![](/bh_web/static/documentation/images/ds_zeek.png)

* The following inputs are required for Zeek Connection Logs:

    * __Data Source Name__
        * Unique name for your data source.<br>
    * __Raw Log Location__
        * Raw Zeek file location.<br>    

4. Click "Add" button to create the new data source.

    ![](/bh_web/static/documentation/images/new_zeek_ds.png)

5. The new data source will now be available for any "Search For Beacon" data source.

    ![](/bh_web/static/documentation/images/zeek_search.png)

## <a name="api"></a>__Create Elastic API__

Elastic and Security Onion data sources can be accessed by using the Elastic API. In order to use these data sources you must set up an Elastic API Key.

> ### __Note__<br>
> 
> Elastic Indices must be Zeek Connection Logs. Beacon Huntress only works with Zeek Connection Logs.

1. From the Elastic Management Console, navigate to "Security" then "API Keys".

    ![](/bh_web/static/documentation/images/e_api.png)

2. Click on the "Create API Key" button.

    ![](/bh_web/static/documentation/images/e_api_create.png)

3. Give the API key the name "bh_api" and restrict permissions according to your organization's security policies. Finally, click the "Create API Key" button.

    ![](/bh_web/static/documentation/images/e_api_name.png)

4. Copy the API key for Beacon Huntress usage.

    > ### __Note__<br>
    > 
    > Once you leave the screen, the API key will not be retrievable. Best practice is to store the API key in a password safe. 

    ![](/bh_web/static/documentation/images/e_api_key.png)

#
Valkyrie Framework<br>
Copyright 2023 Carnegie Mellon University.<br>
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.<br>
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.<br>
DM23-0210<br>