from fastapi import APIRouter
from pydantic import BaseModel
#from ..bh_web.beacon_huntress.src import beacon_huntress as bh

from pathlib import Path
import sys
import json

#print(str(Path(__file__).resolve().parents[2] / "bh_web"))
#exit(33)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "bh_web"))
from beacon_huntress.src import beacon_huntress as bh


router = APIRouter(prefix="/api/searches", tags=["Searches"])

# /ExeDBScanVar.html?DataSource=Zeek?RawLog=/tutorial/?Algo=DBScanVar?Avg=22?Conn=10?TSAvg=12?varPer=15?Likelihood=85

class QuickClusterSearchParams(BaseModel):
    Algo: str
    Log_type: str
    Log_dir: str
    Delta: str = None
    Call_back: int = 10
    Percent: int = 85
    Spans: str = None
    Span_avg: int = 12
    Variance: int = 15
    Start_dte: str = None
    End_dte: str = None
    Zip: bool = False
    Verbose: bool = False
    
@router.post("/quick_cluster")
def quick_cluster_search(quick_cluster_search_params: QuickClusterSearchParams):
    #read the config & update to new values 
    # todo : add build_conf to BH
    conf = bh.build_conf(quick_cluster_search_params.Algo,quick_cluster_search_params.Log_type,quick_cluster_search_params.Log_dir,
                  quick_cluster_search_params.Delta, quick_cluster_search_params.Call_back,quick_cluster_search_params.Percent,
                  quick_cluster_search_params.Spans,quick_cluster_search_params.Span_avg,quick_cluster_search_params.Variance,
                  quick_cluster_search_params.Start_dte,quick_cluster_search_params.End_dte,quick_cluster_search_params.Zip,
                  quick_cluster_search_params.Verbose)
    #pass the config
    return json.dumps(bh.main(conf))
    
class DetailedClusterSearchParams(BaseModel):
    MinimumDeltaTime: int
    TimeSpans: list[list[int]]
    MinimumClusterPoints: int
    LikelihoodPercentage: int

@router.post("/detailed_cluster")
def detailed_cluster_search(detailed_cluster_search_params: DetailedClusterSearchParams):
    return {"message": "Detailed cluster search endpoint"}


class HierarchicalSearchParams(BaseModel):
    MaximumVariancePercentage: int
    BeaconCallbackCount: int
    ClusteringFactorPercentage: int
    ProcessLines: int
    MinimumCallbackTimeInMilliseconds: int

@router.post("/hierarchical")
def hierarchical_search(hierarchical_search_params: HierarchicalSearchParams):
    return {"message": "Hierarchical search endpoint"}

