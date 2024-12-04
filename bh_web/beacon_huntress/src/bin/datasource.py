import pandas as pd
import json
import sys
from elasticsearch import Elasticsearch


def safe_load(row):
    try:
        return json.loads(row)
    except json.JSONDecodeError:
        return None

def elastic_client(data):

    print(data)

    if data["auth"] == "api":
        # API KEY
        es = Elasticsearch(
            hosts="http://{}:{}".format(data["host"],data["port"]),
            api_key=data["api"],
            request_timeout=data["timeout"],
            verify_certs=False
            )

    return es

def elastic_index(client):

    df = pd.DataFrame(columns=["index_name", "cnt"])

    index = client.cat.indices(format="json")

    for x in index:
        df_2 = pd.DataFrame({"index_name": [x["index"]], "cnt": [x["docs.count"]]})
        df = pd.concat([df_2, df], ignore_index=True)

    df.sort_values("index_name",inplace=True, ignore_index=True)

    return df

def get_elastic_data(client, data, start_dte = "", end_dte = ""):
    

    query = {
            "query": {
                    "bool": {
                                "should": [
                                            {"match": {"container.id": "conn.log"}},
                                            #{"match": {"container.id": "dns.log"}},
                                ]
                            }
            }
    }

    # # START & END DATES
    # elif start_dte != "" and end_dte != "":
    #     query = {
    #         "query": {
    #             "bool": {
    #                 "must": [
    #                     {
    #                         "range": {
    #                             "ts": {
    #                                 "gte": start_dte,
    #                                 "lte": end_dte
    #                             }
    #                         }
    #                     }
    #                 ],
    #                 "should": [
    #                     {"match": {"container.id": "conn.log"}}
    #                     #{"match": {"container.id": "dns.log"}},
    #                 ]
    #             }
    #         }
    #     }        

    size = 10000
    total = 0
    time = "15m"

    print(data)

    if data["max_records"] == 0:
        max_rec = sys.maxsize
    else:
        max_rec = data["max_records"]

    response = client.search(index=data["index"], 
                        body=query,
                        size=size,
                        scroll=time) 

    scroll_id = response["_scroll_id"]
    vals = response["hits"]["hits"]
    conn_data = []

    for x in vals:
        # Check for Sec Onion or Elasic
        if data["data_type"] == "Elastic":
            conn_data.append({"data": x["_source"]["zeek"]})
        else:
            conn_data.append({"data": x["_source"]["message"]})

    total += size

    while len(vals) > 0:
        zeek = client.scroll(scroll_id=scroll_id, scroll=time)
        scroll_id = zeek["_scroll_id"]
        vals = zeek["hits"]["hits"]

        for x in vals:
            # Check for Sec Onion or Elasic
            # ELASTIC MAKE SURE ZEEK IS IN THE VALUE IF NOT SKIP
            if data["data_type"] == "Elastic":
                if "_source" in x and "zeek" in x["_source"]:
                    conn_data.append({"data": x["_source"]["zeek"]})
                else:
                    pass
            else:
                conn_data.append({"data": x["_source"]["message"]})

        total += size
        print(total)

        if total >= max_rec:
            print("Max Records...exiting scroll")
            break
            
    df = pd.json_normalize(conn_data)
    if df.empty:
        df_zeek = df
    else:
        if data["data_type"] == "Elastic":
            # remove data. columns
            df.columns = df.columns.str.replace('^data\.', '', regex=True)
            df_zeek = df
        else:
            df["data"] = df["data"].apply(safe_load)
            df = df.dropna(subset=["data"])
            df_zeek = pd.json_normalize(df["data"])

        # CHECK DATES 
        # TEMPORARY CHANGE TO ELASTIC QUERY IN THE FUTURE
        if start_dte != "" and end_dte != "":
            df_zeek = df_zeek.query("ts >= {} and ts <= {}".format(start_dte, end_dte))
        # ONLY START
        elif start_dte != "" and end_dte == "":
            df_zeek = df_zeek.query("ts >= {}".format(start_dte))
        # ONLY END
        elif start_dte == "" and end_dte != "":
            df_zeek = df_zeek.query("ts <= {}".format(end_dte))
        else:
            pass        

    return df_zeek

########################################################
## 
########################################################
