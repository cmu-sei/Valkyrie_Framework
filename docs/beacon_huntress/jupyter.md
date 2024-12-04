# <a name="jupyter"></a>**Jupyter Notebook**

Complete the steps below to setup Beacon Huntress on Jupyter.

???+ tip "Note"
    Beacon Huntress has python dependancies that are required for operation. **Do not skip steps 5 & 6 from the setup!**

### <a name="setup"></a>**Juptyer Notebook Setup**

1. Create a folder in Jupyter called `beacon_huntress`.<br>
2. Copy the `/src/lib/jupyter/beacon_huntress.ipynb` file from this repository into the beacon_huntress folder in Jupyter.<br>
3. Copy the `/src/bin/beacon/beacon.py` folder from this repository into Jupyter.<br>
4. Copy the `/src/bin/ingest.py` folder from this repository into Jupyter.<br>
5. Copy the `/src/lib/jupyter/requirements.txt` file into the beacon_huntress folder in Jupyter.<br>
6. Open a Jupyter terminal session and execute the code below to install the requirements.txt into a Jupyter kernel called beacon_huntress.<br>

```shell
# CREATE VIRTUAL ENV
python3 -m venv beacon_huntress

# ACTIVATE VIRTUAL ENV
source $HOME/beacon_huntress/bin/activate

# INSTALL REQUIREMENTS FILE
pip3 install -r beacon_huntress/requirements.txt

# LOAD KERNEL TO JUPYTER
sudo ipython kernel install --name "beacon_huntress"
```

After everything is installed you should see this structure:

![jupyter1](../images/jupyter_1.png)

### <a name="jupyter_run"></a>**Run Jupyter Notebook**

Open beacon_huntress.ipynb inside a Jupyter notebook. Run the steps below.

1. Run the `BUILD BRONZE DATA LAYER` shell.

   - **src_loc** <i>(string) </i><br>
     Raw Bro/Zeek logs folder.
   - **bronze_loc** <i>(string)</i><br>
     Bronze folder location. Folder where data will compressed and converted to parquet format.

   ```python
   import ingest

   # BUILD BRONZE DATA LAYER
   ingest.build_bronze_layer(
       src_loc="data/raw/data",
       bronze_loc="data/bronze/zeek/raw/parquet/mc3"
       )
   ```

2. Run the `CREATE FILTERED FILES` shell to filter files.

   - **src_loc** <i>(string)</i><br>
     Raw Bro/Zeek logs folder.
   - **dest_exclude_file** <i>(string)</i><br>
     Destination folder location for non-matching filters. **Matches are excluded from the results.**.<br>
     Use a unique folder name at the end to identify your filter, a data folder will appended automatically.<br>
     Pass a blank double quote ("") to skip the creation of an exclude file.<br>
   - **port_filter** <i>(list)</i><br>
     Ports you want to include, in list format.

   ```python
   # CREATE FILTERED FILES
   # SEE README.MD FOR ADDITIONAL OPTIONS
   ingest.build_filter_files(
   src_loc = "data/bronze/zeek/raw/parquet/mc3",
   dest_exclude_file = "data/bronze/zeek/filtered/parquet",
   port_filter = [80, 443]
   )
   ```

3. Run the `BUILD DELTA FILES` shell to build the delta files.

   - **src_file** <i>(string)</i><br>
     Source folder or file location.<br>
   - **delta_file_loc** <i>(string)</i><br>
     Destination folder or file location for delta files.<br>

   ```python
   # BUILD DELTA FILES
   ingest.build_delta_files(src_loc = "data/bronze/zeek/filtered/parquet",
                        delta_file_loc = "data/silver/delta")
   ```

4. Choose the algorithm you want to run and configure the settings. Some examples are included below, but see the [Beacon Algorithms](../documentation/beaconalgo.md) page for more details.

   - Agglomerative Clustering

     ```python
     import beacon

     # AGGLOMERATIVE CLUSTERING
     # SLOW BEACON
     beacon.agglomerative_clustering(
        delta_file = "data/silver/delta/delta_1655318432.parquet",
        delta_column = "delta_mins",
        max_variance = .12,
        min_records = 10,
        cluster_factor = .70,
        line_amounts = [1],
        min_delta_time = 1200000
     )
     ```

   - DBScan Clustering

     ```python
     import beacon

     # DBSCAN
     # SLOW BEACON
     beacon.dbscan_clustering(
         delta_file = "data/silver/delta/delta_1655318432.parquet",,
         delta_column = "delta_mins",
         spans = [[0, 5], [2, 15], [15, 35], [30, 60]],
         minimum_delta = 20,
         minimum_points_in_cluster = 10,
         minimum_likelihood = 0.70
     )
     ```

   - DBScan by Variance

     ```python
     import beacon

     # DBSCAN by VARIANCE
     # SLOW BEACON
     beacon.dbscan_by_variance(
         delta_file = "data/silver/delta/delta_1655318432.parquet",
         delta_column = "delta_mins",
         avg_delta = 20,
         conn_cnt = 10,
         span_avg = 15,
         variance_per = 15,
         minimum_likelihood = 70
     )
     ```
