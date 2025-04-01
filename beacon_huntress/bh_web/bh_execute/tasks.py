'''
Valkyrie Framework
Copyright 2023 Carnegie Mellon University.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
DM23-0210
'''

from __future__ import absolute_import, unicode_literals

from celery import shared_task

from beacon_huntress.src.bin.web import exe_bh
from beacon_huntress.src.bin.datasource import elastic_client, load_elastic_data
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time

@shared_task
def example_task(x,y):
    return x * y
    
@shared_task
def run_algo(request,algo):

    try:
        print("Running algorithm {}".format(algo))
        ret_val = exe_bh(dict(request),algo)

    except Exception as e:
        ret_val = {"cnt": -1}
        message = str(e)

    if ret_val["cnt"] == 0:
        message = "No potential beacons! See log file <a href=/LogDetails.html?filename={0}>{0}</a> for more details!".format(ret_val["log_file"])
    elif ret_val["cnt"] > 0:
        message = "Potential beacons! <a href=/ResultDetails.html?uid={0}>{0}</a>".format(str(ret_val["beacon_group"]))
    else:
        message = "ERROR: {}".format(message)
        print(message)

    time.sleep(1)
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "notifications",
        {"type": "notify", "message": message, "cnt": ret_val["cnt"]}
    )

    return ret_val

@shared_task
def load_ds_data(request):

    data = {"host": "".join(request["es_host"]), 
        "port": "".join(request["es_port"]), 
        "api": "".join(request["api_key"]), 
        "data_type": request["data_type"],
        "index": request["es_index"], 
        "ds_name": request["ds_name"], 
        "auth": "api", 
        "max_records": 0}

    print("Loading data for {}".format(data["ds_name"]))

    try:
        # LOAD CLIENT
        es = elastic_client(data)

        ret_val = load_elastic_data(
            client=es,
            data = data,
            chunk_size = 25000
        )
        cnt = len(ret_val)

    except Exception as err:
        ret_val = ""
        message = str(err)
        cnt = -1

    if cnt == 0:
        message = "No data to load! Please try another index!"
    elif cnt > 0:
        message = "Data for Data Source {} is loaded!".format(request["ds_name"])
    else:
        message = "ERROR: {}".format(message)
        print(message)

    # SLEEP FOR 1 SEC TO ALLOW MESSAGE TO BE RETURNED 
    # IF THE PROCESS IS FASTER THAN THE TIME IT TAKES TO LOAD THE PAGE
    time.sleep(1)
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {"type": "notify", "message": message, "cnt": cnt}
    )
    
    return ret_val