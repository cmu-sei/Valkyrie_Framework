![Beacon Huntress](src/lib/images/beacon_huntress.png)
#
## __Table of Contents__

> * [Home](../readme.md)
> * [Overview](#overview)
> * [How to use](#howtouse)
>   * [Arguments](#args)
>   * [CLI](#cli)
>   * [Module/Jupyter Notebook](#bhmod)
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

## <a name="howtouse"></a>__How to use__

This lightweight version of Beacon Huntress can be used in two ways: via [CLI](#cli) or loading the Beacon Huntress module [Module Run](#bhmod).<br>

> ### __Note__<br>
>
> For the purposes of this documentation, Beacon Huntress is assumed to have been downloaded via Git.

To run Beacon Huntress, you will need to answer the following questions:<br>

1. Where are my Zeek logs located?
2. Do I want to filter out any connections in my logs?
3. How many minutes do potential beacons wait before calling back?  Are the beacons [Fast](#fs_beacons) or [Slow](#fs_beacons)?
4. How many connections does a potential beacon need to have in order to be reported?

## <a name="xx"></a>**XX**

### Parameters

**algo**: *str*
- Beacon Algorithm
   - Quick Cluster Search = q or quick
   - Cluster Search = c or cluster
   - Agglomerative Clustering = a or agg

**log_type**: *str*
- Log File Type
   - Zeek Connection = conn or c
   - Http = http or h
   - Delta File = delta or d

**log_dir**: *str*
- Raw Log Directory
   - Example: '/tutorial'

**delta**: *int*
- Average Delta time in minutes
- Example: 25

**call_back**: *int*
- Number of Beacon Callbacks
   - Example: 10

**percent**: *int*
- Likelihood Percentage Filter *ONLY CLUSTERING ALGOS*
   - Example: 85

**spans**: *list*
- Spans you wish to search in list format. Minimum number of delta records to search using your delta column. *ONLY CLUSTER SEARCH (c/cluster)*
   - Example: [[0, 5], [2, 15], [15, 35], [30, 60], [60, 120], [480, 1440]]
   - Default: [[0, 5], [2, 15], [15, 35], [30, 60], [60, 120], [480, 1440]]

**span_avg**: *int*
- The percentage to increase and decrease from the connections total delta span *ONLY QUICK CLUSTER SEARCH ONLY (q/quick).
   - Example: 15
      - 15 will decrease 15% from the minimum and maximum delta span.
   - Default: 15

**variance**: *int*
- The amount of allowed variance or jitter in percentage *ONLY QUICK CLUSTER SEARCH (q/quick)*
   - Default: 15"

**start_dte**:
- Start Date for filters. Date or datetime in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' or blank('') for no filter.
   - Default: ''

**end_dte**:
- End Date for filters. Date or datetime in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM' or blank('') for no filter.
   - Default: ''

**write_file**: *bool*
- Write results to files (True/False)
   - Default: False

**write_file_type**: *str*
- Write results files as either CSV or Parquet
   - Default: CSV

**zip**: *bool*
- Log/s are zip files (True/False)
   - Default: False"

**verbose**: *bool*
- Enable Verbose logging (True/False)
   - Default: False

**show_results**: *bool*
- Show results (True/False)
   - Default: True

## <a name="cli"></a>**CLI**

The CLI is one way to run the software.

Before starting, ensure the following:

- You have downloaded the Valkyrie Framework.

1. `cd` to the `bh_web/beacon_huntress/src` directory
2. Activate the Python virtual environment.

   **Linux**
   ```bash
   source BH/bin/activate
   ```

   **Windows**
   ```cmd
   BH\scripts\activate
   ```
3. Run a test using the tutorial dataset via the options below. The aggregated results will appear on the screen.

   **Linux**
   ```bash
   python3 beacon_huntress.py --algo "quick" --log_dir "../../datasets\tutorial" --log_type "conn" --delta 20 --call_back 10 --percent 85
   ```

   **Windows**
   ```cmd
   python3 beacon_huntress.py --algo "quick" --log_dir "..\..\datasets\tutorial" --log_type "conn" --delta 20 --call_back 10 --percent 85
   ```
4. All data will be writen to the cli_results directory located in the src directory. The exact location of the results will be printed on the screen, see example below.
   ```cmd
   08-26 15:06:54 INFO:    All export files are located in cli_results/8587e322-1d32-48fb-849d-0575e3021857
   ```
5. Available arguments can be listed by using the help menu `--help` or `-h`
   ```cmd
   python3 beacon_huntress.py --help
   ```

## <a name="bhmod"></a>**Beacon Huntress Module**

You can also run Beacon Huntress via Python or a Jupyter Notebook. Below is an example to get the results for both Beacon Huntress and Top Talkers into a pandas DataFrame.

> ### __Note__<br>
>
> You must activate the Python Virtual Environment before using the code below.

```python
# LOAD MODULES
import pandas as pd
from beacon_huntress import BeaconHuntress

# RUN BEACON HUNTRESS
bh = BeaconHuntress()
val = bh.run(algo="quick",
             log_type = "conn",
             log_dir = "C:\\bh_cli\\beacon_huntress\\bh_web\\datasets\\tutorial\\",
             delta = 20,
             call_back = 10,
             percent = 85,
             show_results = False)

# BEACON RESULTS
df = pd.DataFrame.from_dict(val["results"],orient='columns')

# TOP TALKERS
df = pd.DataFrame.from_dict(val["top_talkers"],orient='columns')
```

#
Valkyrie Framework<br>
Copyright 2023 Carnegie Mellon University.<br>
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.<br>
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.<br>
DM23-0210<br>