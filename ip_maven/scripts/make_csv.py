from lxml import etree
import pandas as pd

# XML
file_name = 'C:\\arin\\datasets\\arin_db.xml'

# ETREE ITERATOR TO PARSE LOOKING FOR <NET>
# UNCOMMENT FOR POC
#context = etree.iterparse(file_name, events=("end",), tag=('{http://www.arin.net/bulkwhois/core/v1}net', '{http://www.arin.net/bulkwhois/core/v1}poc', '{http://www.arin.net/bulkwhois/core/v1}org'))
context = etree.iterparse(file_name, events=("end",), tag=('{http://www.arin.net/bulkwhois/core/v1}net', '{http://www.arin.net/bulkwhois/core/v1}org'))

ns = {"ns": "{http://www.arin.net/bulkwhois/core/v1}"}

# Variables
tag = ""
total_poc = {}
total_net = {}
total_org = {}
cnt = 0 
pro_cnt = 0
overall = 0

# LOOP THROUGH TAGS
for event, net in context:
    cnt +=1
    overall +=1

    # PROGRESS
    if (cnt == 5000):
        pro_cnt += cnt
        print(f"Processed {pro_cnt}")
        cnt = 0

    # SET THE TAGS
    if str(net.tag).replace(ns["ns"],"") == "poc":
        tag = "poc"
    elif str(net.tag).replace(ns["ns"],"") == "net":
        tag = "net"
    else:
        tag = "org"

    # ITERATE OVER CHILD ELEMENTS OF <NET> & <POC>
    value = {}
    for child in net:
        
        if tag == "net":
            # SEARCH FOR SPECIFIC TAGS & ADD TO DICTIONARY VARIABLE
            if child.tag.split('}')[1] in ["startAddress", "endAddress", "handle", "name", "orgHandle", "parentHandle"]:
                value[child.tag.split('}')[1]] = child.text.strip()
        elif tag == "poc":
            # SEARCH FOR SPECIFIC TAGS & ADD TO DICTIONARY VARIABLE
            #if child.tag.split('}')[1] in ["companyName", "registrationDate", "updateDate", "handle"]:
            value[child.tag.split('}')[1]] = child.text.strip()
        elif tag == "org":
            # SEARCH FOR SPECIFIC TAGS & ADD TO DICTIONARY VARIABLE
            if child.tag.split('}')[1] in ["iso3166-1", "streetAddress"]:
                for x in child:
                    value[x.tag.split('}')[1]] = x.text
            else:
                value[child.tag.split('}')[1]] = child.text

    # CLEAR MEMORY
    net.clear()

    if tag == "net":
        # ADD TO DICTIONARY
        total_net[overall] = value
    elif tag == "poc":
        total_poc[overall] = value
    elif tag == "org":
        total_org[overall] = value

# CREATE DATAFRAMES
df_poc = pd.DataFrame.from_dict(total_poc,orient='index')
df_net = pd.DataFrame.from_dict(total_net,orient='index')
df_org = pd.DataFrame.from_dict(total_org,orient='index')

# FINAL DATAFRAME
df_final = df_net.merge(df_org,how="left",left_on="orgHandle",right_on="handle").\
    rename(columns={"handle_x":"handle", "name_x":"name","name_y":"customerName","iso3166-2":"state","line":"streetAddress"}).drop(columns=["handle_y","pocLinks"])

# FINAL EXPORT
df_final.to_csv("..\\datasets\whois_db.csv")