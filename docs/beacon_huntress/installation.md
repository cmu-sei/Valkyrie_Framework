## **Table of Contents**

> - [Home](../../../readme.md)
> - [Overview](#overview)
>   - [Requirements](#requirements)
>   - [Manual Install](#manual)
>     - [Pre-Requirement](#pre-requirements)
>     - [Linux](#linux)
>     - [Jupyter](#jupyter)
>     - [Windows](#windows)

#

## **Overview**

Beacon Huntress can be installed Manually or via Docker. Instruction to install Beacon Huntress are below.<br>

#

## **Requirments**

Below are the minimum requirements to run Beacon Huntress with or without the dashboard.

- Python 3.8 or greater
- 2 GB of memory
- 2 vCPU

#

## <a name="manual"></a>**Manual Install**

Below are the steps to install Beacon Huntress manually.

> ### **Note**<br>
>
> Beacon Huntress has python dependancies that are required for operation.<br>
> All required python dependanices can be found in either respective requirements.txt file.

- [Linux](#linux)
- [Jupyter](#jupyter)
- [Windows](#windows)

#

## **Pre-Requirments**

For a manual install you must have Python 3.8 or greater, MySQL with a MySQL client and Granfana installed! It is recommended that you use that you use Docker for Beacon Huntress.

#

## **Linux**

Complete the steps below setup Beacon Huntress manually. Beacon Huntress has python dependancies that are required for operation.<br>
Dashboard is currently only available using Docker.

> ### **Note**<br>
>
> When running Beacon Huntress instance outside of Docker it is <i>**recommended**</i> that a </i>**Python Virtual Environment**</i> is setup to prevent any issues with the current environment.<br>

1. Copy all the files in the beacon_huntress to /var. <i>Your folder may not be in $HOME</i>
   ```shell
   sudo cp -R $HOME/beacon_huntress /var
   ```
2. Check Python version.
   ```shell
   sudo python3 --version
   ```
3. If Python is missing or lower than version 3.8 install using the steps below.

   ```shell
   # INSTALL PYTHON
   sudo apt-get install python3.10

   # INSTALL PIP3
   sudo apt-get install python3-pip

   # IF PYTHON3.8 IS INSTALLED RUN THE COMMAND BELOW
   sudo apt-get install python3.8-venv
   ```

4. Complete a Virtual Environment Setup by running the steps below.

   ```shell
   # CD TO BEACON_HUNTRESS HOME TO ENSURE VIRTUAL ENVIRONMENT IS IN BEACON HUNTRESS
   cd /var/beacon_huntress

   # CREATE VIRTUAL ENV
   sudo python3 -m venv bh

   # ACTIVATE VIRTUAL ENV
   source bh/bin/activate

   # INSTALL REQUIREMENTS FILE
   sudo pip3 install -r setup/requirements.txt

   # RUN COMMAND BELOW TO DEACTIVATE ENVIRONMENT
   deactivate bh
   ```

#

## **Jupyter**

Complete the steps below setup Beacon Huntress manually. Beacon Huntress has python dependancies that are required for operation.<br>

> ### **Note**<br>
>
> For a manual setup it is <i>**recommended**</i> that you setup a </i>**Python Virtual Environment**</i> to prevent any issue.
> You can either install directly to your machine or kernel as below or install a Virtual Environment (<i>**Instructions Not Included**</i>).

1.  Create a folder in Jupyter called `beacon_huntress`.
2.  Copy the `/lib/jupyter/beacon_huntress.ipynb` file from this repository into the beacon_huntress folder in Jupyter.
3.  Copy the `beacon/beacon.py` folder from this repository into Jupyter.
4.  Copy the `ingest/ingest.py` folder from this repository into Jupyter.
5.  Copy the `lib/jupyter/requirements.txt` file into the beacon_huntress folder in Jupyter.
6.  Execute the code below to install the requirements.txt into a Jupyter kernel called beacon_huntress.
    <br>

    ````shell # CREATE VIRTUAL ENV
    python3 -m venv bh

        # ACTIVATE VIRTUAL ENV (LINUX)
        source $HOME/bh/bin/activate

        # ACTIVATE VIRTUAL ENV (LINUX)
        . .\bh\activate

        # INSTALL REQUIREMENTS FILE
        pip3 install -r setup/requirements.txt

        # LOAD KERNEL TO JUPYTER
        sudo ipython kernel install --name "beacon_huntress"
        ```
    ````

#

## **Windows**

Complete the steps below setup Beacon Huntress manually. Beacon Huntress has python dependancies that are required for operation.<br>
Dashboard is currently only available using Docker.

> ### **Note**<br>
>
> When running Beacon Huntress instance outside of Docker it is <i>**recommended**</i> that a </i>**Python Virtual Environment**</i> is setup to prevent any issues with the current environment.<br>
> See [Virtual Environment Setup]() for more details.

1. After downloading, cd to the beacon_huntress directory. <span style="color:yellow"><i>Your folder may not be in $HOME</i></span>
   ```shell
   cd $HOME\beacon_huntress
   ```
2. Check Python version.
   ```shell
   py --version
   ```
3. If Python is missing or lower than version 3.8 install. Download and install from the location below.

   https://www.python.org/downloads/release/python-3100/

4. Complete a Virtual Environment Setup by running the steps below.

   ```shell
   # CD TO BEACON_HUNTRESS HOME TO ENSURE VIRTUAL ENVIRONMENT IS IN BEACON HUNTRESS
   cd beacon_huntress

   # CREATE VIRTUAL ENV
   py -m venv bh

   # ACTIVATE VIRTUAL ENV
   .\bh\scripts\activate

   # INSTALL REQUIREMENTS FILE
   pip3 install -r setup/requirements.txt

   # RUN COMMAND BELOW TO DEACTIVATE ENVIRONMENT
   .\bh\scripts\deactivate.bat
   ```
