from fastapi import APIRouter
from pydantic import BaseModel, Field
from pathlib import Path
import sys
import json
from fastapi.responses import JSONResponse


# Import Beacon Huntress
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bh_web"))
from beacon_huntress.src import beacon_huntress as bh


router = APIRouter(tags=["Searches"])

# /ExeDBScanVar.html?DataSource=Zeek?RawLog=/tutorial/?Algo=DBScanVar?Avg=22?Conn=10?TSAvg=12?varPer=15?Likelihood=85

class QuickClusterSearchParams(BaseModel):
    log_type: str = Field(default = "conn", description="Log Type parameter")
    log_dir: str = Field(default = "", description="Log file locations")
    delta: int = Field(default = 20, description="Average callback time in minutes")
    call_back: int = Field(default = 10, description="The minimum number of connection callbacks")
    percent: int = Field(default = 85, description="The minimum percentage of cluster points")
    span_avg: int = Field(default = 12, description="The percentage for the span of EPS")
    variance: int = Field(default = 15, description="The maximum percentage of jitter that is allowed")
    start_dte: str = ""
    end_dte: str = ""
    zip: bool = False
    verbose: bool = False

@router.post("/quick_cluster")
def quick_cluster_search(quick_cluster_search_params: QuickClusterSearchParams):
    """
    # Quick Cluster Search

    ## Input Values
    - **log_type**
        - Log Type parameter (Zeek Connection = conn, )\n
    - **log_dir**
        - Log directory location\n
    - **delta**
        - Average callback time in minutes\n
    - **call_back**
        - The minimum number of connection callbacks\n
    - **percent**
        - The minimum percentage of cluster points\n
    - **span_avg**
        - The percentage for the span of EPS\n
    - **variance**
        - The maximum percentage of jitter that is allowed\n
    - **start_dte**
        - The start date time\n
    - **end_dte**
        - The end date time\n
    - **zip**
        - Is the file a zip file (True or False)\n
    - **verbose**
        - Verbose logging (True of False)\n
    ## Return Values
    - **beacon_group**
        - Beacon Huntress run results group\n
    - **cnt**
        - Number of potential beacons\n
    - **log_file**
        - Beacon Huntress run results log file\n
    """

    # Run Beacon Huntress
    conf = bh.build_conf(
        algo = "quick",
        log_type = quick_cluster_search_params.log_type,
        log_dir = quick_cluster_search_params.log_dir,
        delta = quick_cluster_search_params.delta,
        call_back = quick_cluster_search_params.call_back,
        percent = quick_cluster_search_params.percent,
        spans = None,
        span_avg = quick_cluster_search_params.span_avg,
        line_amounts= None,
        variance = quick_cluster_search_params.variance,
        start_dte = quick_cluster_search_params.start_dte,
        end_dte = quick_cluster_search_params.end_dte,
        zip = quick_cluster_search_params.zip,
        verbose = quick_cluster_search_params.verbose
        )
    ret_val = bh.main(conf)
    return JSONResponse(content=ret_val)

class DetailedClusterSearchParams(BaseModel):
    log_type: str = Field(default = "conn", description="Log Type parameter")
    log_dir: str = Field(default = "", description="Log file locations")
    delta: int = Field(default = 20, description="Average callback time in minutes")
    time_spans: list[list[int]] = Field(default = [[0, 5], [2, 15], [15, 35], [30, 60]], description="Clustered time spans")
    call_back: int = Field(default = 10, description="The minimum number of connection callbacks")
    percent: int = Field(default = 85, description="The minimum percentage of cluster points")
    start_dte: str = ""
    end_dte: str = ""
    zip: bool = False
    verbose: bool = False

@router.post("/detailed_cluster")
def detailed_cluster_search(detailed_cluster_search_params: DetailedClusterSearchParams):
    """
    # Detailed Cluster Search

    ## Input Values
    - **log_type**
        - Log Type parameter (Zeek Connection = conn, )\n
    - **log_dir**
        - Log directory location\n
    - **delta**
        - Average callback time in minutes\n
    - **call_back**
        - The minimum number of connection callbacks\n
    - **percent**
        - The minimum percentage of cluster points\n
    - **spans**
        - The time spans to search in list form\n
        - [[0, 5], [2, 15], [15, 35], [30, 60]]\n
    - **variance**
        - The maximum percentage of jitter that is allowed\n
    - **start_dte**
        - The start date time\n
    - **end_dte**
        - The end date time\n
    - **zip**
        - Is the file a zip file (True or False)\n
    - **verbose**
        - Verbose logging (True of False)\n
    ## Return Values
    - **beacon_group**
        - Beacon Huntress run results group\n
    - **cnt**
        - Number of potential beacons\n
    - **log_file**
        - Beacon Huntress run results log file\n
    """

    # Run Beacon Huntress
    conf = bh.build_conf(
        algo = "cluster",
        log_type = detailed_cluster_search_params.log_type,
        log_dir = detailed_cluster_search_params.log_dir,
        delta = detailed_cluster_search_params.delta,
        call_back = detailed_cluster_search_params.call_back,
        percent = detailed_cluster_search_params.percent,
        spans = detailed_cluster_search_params.time_spans,
        span_avg = None,
        variance = None,
        line_amounts= None,
        start_dte = detailed_cluster_search_params.start_dte,
        end_dte = detailed_cluster_search_params.end_dte,
        zip = detailed_cluster_search_params.zip,
        verbose = detailed_cluster_search_params.verbose
        )

    ret_val = bh.main(conf)
    return JSONResponse(content=ret_val)

class HierarchicalSearchParams(BaseModel):
    log_type: str = Field(default = "conn", description="Log Type parameter")
    log_dir: str = Field(default = "", description="Log file locations")
    delta: int = Field(default = 20, description="Average callback time in minutes")
    line_amounts: list[int] = Field(default = [1], description="Line amounts to process at a time, in list format.")
    call_back: int = Field(default = 10, description="The minimum number of connection callbacks")
    variance: int = Field(default = 15, description="The maximum percentage of jitter that is allowed")
    percent: int = Field(default = 85, description="The minimum percentage of cluster points")
    start_dte: str = ""
    end_dte: str = ""
    zip: bool = False
    verbose: bool = False

@router.post("/hierarchical")
def hierarchical_search(hierarchical_search_params: HierarchicalSearchParams):
    """
    # Hierarchical Search

    ## Input Values
    - **log_type**
        - Log Type parameter (Zeek Connection = conn, )\n
    - **log_dir**
        - Log directory location\n
    - **delta**
        - Average callback time in minutes\n
    - **call_back**
        - The minimum number of connection callbacks\n
    - **percent**
        - The minimum percentage of cluster points\n
    - **spans**
        - The time spans to search in list form\n
        - [[0, 5], [2, 15], [15, 35], [30, 60]]\n
    - **variance**
        - The maximum percentage of jitter that is allowed\n
    - **start_dte**
        - The start date time\n
    - **end_dte**
        - The end date time\n
    - **zip**
        - Is the file a zip file (True or False)\n
    - **verbose**
        - Verbose logging (True of False)\n
    ## Return Values
    - **beacon_group**
        - Beacon Huntress run results group\n
    - **cnt**
        - Number of potential beacons\n
    - **log_file**
        - Beacon Huntress run results log file\n
    """

{
  "log_type": "conn",
  "log_dir": "/tutorial",
  "delta": 20,
  "line_amounts": [
    1
  ],
  "call_back": 10,
  "variance": 15,
  "percent": 85,
  "start_dte": "",
  "end_dte": "",
  "zip": false,
  "verbose": false
}


    # Run Beacon Huntress
    conf = bh.build_conf(
        algo = "hierarchical",
        log_type = hierarchical_search_params.log_type,
        log_dir = hierarchical_search_params.log_dir,
        delta = hierarchical_search_params.delta,
        call_back = hierarchical_search_params.call_back,
        percent = hierarchical_search_params.percent,
        spans = None,
        span_avg = None,
        variance = hierarchical_search_params.variance,
        line_amounts= hierarchical_search_params.line_amounts,
        start_dte = hierarchical_search_params.start_dte,
        end_dte = hierarchical_search_params.end_dte,
        zip = hierarchical_search_params.zip,
        verbose = hierarchical_search_params.verbose
        )

    ret_val = bh.main(conf)
    return JSONResponse(content=ret_val)