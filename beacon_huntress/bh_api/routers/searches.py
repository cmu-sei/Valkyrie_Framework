from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/searches", tags=["Searches"])

# /ExeDBScanVar.html?DataSource=Zeek?RawLog=/tutorial/?Algo=DBScanVar?Avg=22?Conn=10?TSAvg=12?varPer=15?Likelihood=85

class QuickClusterSearchParams(BaseModel):
    DataSource: str
    RawLog: str
    Algo: str
    Avg: int
    Conn: int
    TSAvg: int
    varPer: int
    Likelihood: int

@router.post("/quick_cluster")
def quick_cluster_search(quick_cluster_search_params: QuickClusterSearchParams):
    return {"message": "Quick cluster search endpoint"}


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

