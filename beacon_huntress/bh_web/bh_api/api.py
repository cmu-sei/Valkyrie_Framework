from fastapi import FastAPI
from bh_api.routers.application import router as api_app
from bh_api.routers.searches import router as api_search
from bh_api.routers.results import router as api_results

bh_desc = """
# Beacon Huntress API

This API will run Beacon Huntress searches.

## Application

Application information

- **Version**
    - Beacon Huntress Version Information
- **Configuration**
    - Beacon Huntress Default Configuration

## Searches

Run Beacon Huntress searches

- **Quick Cluster**
    - Beacon Huntress Quick Cluster Search
- **Detailed Cluster**
    - Beacon Huntress Detailed Cluster Search
- **Hierarchical**
    - Beacon Huntress Hierarchical Search

## Results

Receive Beacon Huntress searches results for
- **Beacon Groups**
    - Get Beacon Huntress results beacon groups
- **Beacon Results**
    - Display the Beacon Huntress results
    - Delete Beacon Huntress results
- **Top Talkers**
    - Get Top Talkers results
- **Log File**
    - Display the run results log file
    - Delete the run results log file
- **Filter Hosts**
    - Filter benign traffic from Beacon Huntress results
    - Remove filtered benign traffic
    - Get filtered hosts
"""

app = FastAPI(description=bh_desc)

app.include_router(api_app, prefix="/application")
app.include_router(api_search, prefix="/searches")
app.include_router(api_results, prefix="/results")
