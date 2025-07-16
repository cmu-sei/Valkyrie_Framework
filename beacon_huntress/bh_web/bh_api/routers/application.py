from fastapi import APIRouter
from pydantic import BaseModel
import sys
import os
import json
from pathlib import Path

# Beacon Huntress Main
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "bh_web"))
from beacon_huntress.src import beacon_huntress as bh

router = APIRouter(tags=["Application"])

@router.get("/version")
def server_info():
    return {"title": "Beacon Huntress", "version": "2.2", "description": "Beacon Huntress provides an automated approach for detecting and analyzing software beacons (software often communicates with remote servers at regular intervals to receive instructions or send data) in network traffic. By leveraging machine learning techniques and structured analysis, it helps security teams identify potentially malicious communications.\
    The tool enhances situational awareness and response capabilities in cyber defense operations."}

# === configuration ===

@router.get("/configuration")
def get_configuration():

    # GET CONFIG FILE
    cur_folder = Path(__file__).parent
    conf_file = os.path.join(cur_folder.parent.parent, "beacon_huntress", "src", "config", "config.conf")

    conf = bh._load_config(conf_file)
    return json.dumps(conf)
