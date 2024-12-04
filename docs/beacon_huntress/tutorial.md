## **Table of Contents**

> - [Home](../../../readme.md)
> - [How to use](#howtouse)
>   - [Tutorial](#bh_tutorial)
>   - [Zeek Logs](#zeek)

## <a name="bh_tutorial"></a>**Tutorial**

This tutorial will provide an example for running Beacon Huntress using a generic dataset.

> ### **Note**
>
> You must complete the [Docker Setup](#docker) prior to running this tutorial.

1. Visit http://127.0.0.1:8000 in your web browser to access the main page of the Beacon Huntress Web UI.

   ![bh_ui](/assets/img/bh/home_page.png)

2. Go to the "Settings" tab and select "General".

   ![ui_set_gen](/assets/img/bh/gen_settings.png)

3. Change the "Raw Log Location" to `/tutorial` and click "Save".

   ![ui_raw_loc](/assets/img/bh/set_tutorial.png)

4. Go to the "Execute" tab and select "Quick Cluster Search". Keeping the default settings, click "Run". The execution will take a moment.

   ![ui_set](/assets/img/bh/search_quick_cluster.png)

5. After the execution is finished, you'll be redirected to the results page. For this dataset, the "Beacon Count" column shows that two potential beacons have been identified. Several options are now available. Click on the "Group ID" to view the potential beacons. Click the "Dashboard" icon to display results in a Grafana dashboard. Click on the "Log File" icon to view the run logs. Click the "Config" icon to display runtime configuration. Click the "Delete" icon to <i><b>PERMANENTLY</b></i> remove this result set.

   ![ui_results](/assets/img/bh/results_quick_cluster.png)

6. For now, click the "Group ID" to view potential beacons. In this example, Beacon Huntress has identified two potential beacons: 7.7.7.1 and 2.17.188.84, or "fandango.com". The 7.7.7.1 connection is our target test beacon, but the connections to "fandango.com" are benign traffic. Since the identification of "fandango.com" is incorrect, we will exclude this result from the current and future runs by clicking the "Filter" icon.

   ![ui_result_detail](/assets/img/bh/results_details_highlight.png)

7. Now, the results from "fandango.com" are filtered out.

   ![ui_results_filter](/assets/img/bh/results_details_filtered.png)

8. To view all your filtered hosts, go to the "Settings" tab and select "Filtered Hosts". Filtered hosts can be removed from this list by clicking the "Trash Can" icon in the "Option" column, which will cause them to once again appear in the results.

   ![ui_fil_host](/assets/img/bh/filtered_hosts.png)

9. Go back to the "Results" tab and click on the "Dashboard" icon.

   ![ui_results_click](/assets/img/bh/result_dash_highlighted.png)

10. A Grafana dashboard will open in a new browser tab. See [Dashboard]() for more details on dashboard usage and functionalities.

    ![ui_dash](/assets/img/bh/dash_main.png)

### Congratulations! You have completed your first Beacon Huntress test run!

<br>

## <a name="zeek"></a>**Zeek Logs**

Zeek Connection Logs must be provided for Beacon Huntress to analyze. Follow the steps below to copy your Zeek logs from their initial location to a local directory that can be accessed by Beacon Huntress. It's recommended to organize the logs into separate directories, with each directory corresponding to a single day.

1. In this example, we will copy Zeek conn logs to the `/tmp` directory. The `/tmp` directory is mounted to the Docker container beacon_huntress.

   ```bash
   # CREATE DIRECTORY (REPLACE YYYY-MM-DD WITH DATE)
   mkdir -p /tmp/raw/data/YYYY-MM-DD

   # START SFTP SHELL
   sftp root@YOUR_FTP_SERVER

   # SFTP COMMAND EXAMPLE (REPLACE YYYY-MM-DD WITH DATE)
   get -R zeek/logs/YYYY-MM-DD/conn.* /tmp/raw/data/YYYY-MM-DD
   ```

2. In the Beacon Huntress Web UI, go to "Settings" and select "General". Change the "Raw Log Location" to `/tmp/raw/data` and click "Save".

   ![ui_set_gen](/assets/img/bh/gen_settings.png)

3. Now when you execute Beacon Huntress, it will return results for potential beacons found in any log files located in `/tmp/raw/data`. See [tutorial](#tutorial) for more details on understanding Beacon Huntress results.
