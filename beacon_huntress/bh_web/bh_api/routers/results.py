from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from pathlib import Path
import sys
import json

# Import
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bh_web"))
from beacon_huntress.src.bin.api_mod import get_results, result_grid_group, log_detail_view, del_result, del_log_file, filter_host, del_fil_host, get_fil_host, get_top_talkers

router = APIRouter(tags=["Results"])

@router.get("/beacon_groups")
def results():
    """
    # Get Beacon Groups

    ## Return values
    - **beacon_group**
        - Results group_id to be used for `/beacon_groups`
    - **date**
        - Date of search\n
    - **beacon_count**
        - Number of potential beacons\n
    - **log_file**
        - Results log_file name to used for `get_log_file`\n
    """
    return result_grid_group()

@router.get("/beacon_results")
def results(beacon_group: str = Query(None)):
    """
    # Get Beacon Results

    ## Input parameter
    - **beacon_group_id**
        - Beacon Group UUID

    ## Return values
    - **ID**
        - Unique row identifier
    - **Source IP**
        - Source IP address
    - **Destination IP**
        - Destination IP address
    - **Port**
        - Destination Port ID
    - **Score**
        - Clustered score
    - **DNS**
        - DNS name
    - **Connection Count**
        - Number of connection for each unique Source IP, Destination IP and Port.
    - **First Occurrence**
        - Minimum date for each unique Source IP, Destination IP and Port.
    - **Last Occurrence**
        - Maximum date for each unique Source IP, Destination IP and Port.
    """
    return get_results(beacon_group)

@router.delete("/beacon_results")
def results(beacon_group: str = Query(None)):
    """
    # Delete Beacon Results

    ## Input parameter
    - **beacon_group_id**
        - Beacon Group UUID

    ## Return values
    - **Data**
        - **Deleted**
            - Beacon data has been deleted (True/False)
        - **Message**
            - Message details
    - **Log**
        - **Deleted**
            - Log file has been deleted (True/False)
        - **Message**
            - Message details
    """
    return del_result(beacon_group)

@router.get("/top_talkers")
def results(beacon_group: str = Query(None)):
    """
    # Get Beacon Results

    ## Input parameter
    - **beacon_group_id**
        - Beacon Group UUID

    ## Return values
    - **ID**
        - Unique row identifier
    - **Source IP**
        - Source IP address
    - **Destination IP**
        - Destination IP address
    - **Port**
        - Destination Port ID
    - **Total Number of Connections**
        - The total number of connections for each unique Source IP, Destination IP and Port.
    """
    return get_top_talkers(beacon_group)

@router.get("/log_file")
def results(log_file: str = Query(None)):
    """
    # Get log file details

    ## Input parameter
    - **log_file**
        - Log file name

    ## Return values
    - **file_content**
            - Log file details
    """

    return log_detail_view(log_file)

@router.delete("/log_file")
def results(log_file: str = Query(None)):
    """
    # Delete log file

    ## Input parameter
    - **log_file**
        - Log file name

    ## Return values
    - **Deleted**
        - Log file has been deleted (True/False)
    - **Message**
        - Message details
    """

    return del_log_file(log_file)

@router.post("/filter_host")
def results(ip: str = Query(None)):
    """
    # Filter Host (beacon ip)

    ## Input parameter
    - **ip**
        - Destination IP address

    ## Return values
    - **Filtered**
        - IP is filtered (True/False)
    - **Message**
        - Message details
    """

    return filter_host(ip)

@router.delete("/filter_host")
def results(ip: str = Query(None)):
    """
    # Removed filter host (beacon ip)

    ## Input parameter
    - **ip**
        - Destination IP address

    ## Return values
    - **Filtered**
        - IP is removed from filtered list (True/False)
    - **Message**
        - Message details
    """

    return del_fil_host(ip)

@router.get("/filter_host")
def results():
    """
    # Get all filter beacon ip

    ## Input parameter
    - **ip**
        - Destination IP address

    ## Return values
    - **Filtered**
        - IP is removed from filtered list (True/False)
    - **Message**
        - Message details
    """

    return get_fil_host()