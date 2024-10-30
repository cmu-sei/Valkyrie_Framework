# Create your views here.  
from pathlib import Path
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib import messages
from .forms import bh_settings_general, bh_filter_settings, bh_datasources
from .models import conf_general, conf_filter
from beacon_huntress.src.bin.data import get_data, data_to_json, add_ds, del_data, upd_ds
from beacon_huntress.src.bin.datasource import elastic_client, elastic_index
import os, json, numpy as np

# BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

def _get_context(df):
    df_html = df.to_html(escape=False, 
                         index=False, 
                         #justify="left",
                         classes="table table-striped", 
                         table_id="grid"
                         )

    # replace dataframe class
    df_html = df_html.replace('class="dataframe ', 'class="')
    df_html = df_html.replace('<tr>','<tr class="text-end">')
    context = {"files": df_html}

    return context

def _eds_json(df):

    # RETURN VALUE
    ret_dict = []

    # FIX THE DATA COLUMN AND MAKE IT JSON
    df["data"] = df["data"].apply(lambda x: json.loads(x.replace("'", '"')))

    # GENERIC FIELDS
    ret_dict.append({"id": "ds_type", "label": "Data Source Type", "value": df["ds_type"][0], "type": "text", "desc": ""})
    ret_dict.append({"id": "ds_name", "label": "Data Source Name", "value": df["ds_name"][0], "type": "text", "desc": "Give a unique name to your data source"})

    # DATA FIELDS
    for key, value in dict(df["data"][0]).items():
        if key == "host":
            label = "Host"
            desc = "Elastic Host Name."
        elif key == "port":
            label = "Port"
            desc = "Elastic Port Number."
        else:
            label = key
            desc = ""

        ret_dict.append({"id": key, "label": label, "value": value, "type": "text", "desc": desc})          

    return ret_dict

def _upd_api_key(val):

    data = json.loads(val.replace("'", '"'))

    if "api_key" in data:
        data["api_key"] = "******"
        
        return json.dumps(data)
    else:
        return val
            
def _mask_api(df):

    if len(df.loc[df["data"].str.contains('api_key', na=False)]) > 0:
        print("HERE")
        
        # CREATE MASK JSON COLUMN
        df["is_mask"] = df["data"].apply(lambda x: "api_key" in x if isinstance(x,str) else False)
        df.loc[df["is_mask"] == True, "data"] = df.loc[df["is_mask"] == True, "data"].apply(_upd_api_key)

    else:
        pass
    
    return df

def setting_view(request):

    submitted = False

    # SAVE FORM
    if request.method == "POST":
        form = bh_settings_general(request.POST)

        if form.is_valid():
            form.save()

            messages.info(request, "Changes saved!")
            return HttpResponseRedirect('/GenSettings.html?submitted=True')
    else:
        set_data = conf_general.objects.latest("row_id")
        form = bh_settings_general(instance=set_data)

        if submitted in request.GET:
            submitted = True

    return render(request, os.path.join(BASE_DIR, "settings", "pages", "GenSettings.html"), {'form': form})

def filter_view(request):

    submitted = False

    # SAVE FORM
    if request.method == "POST":
        form = bh_filter_settings(request.POST)

        if form.is_valid():
            form.save()

            messages.info(request, "Changes saved!")
            return HttpResponseRedirect('/FilterSettings.html?submitted=True')
    else:
        set_data = conf_filter.objects.latest("row_id")
        form = bh_filter_settings(instance=set_data)

        if submitted in request.GET:
            submitted = True

    return render(request, os.path.join(BASE_DIR, "settings", "pages", "FilterSettings.html"), {'form': form})

def ds_view(request):
    if request.method == 'POST':
        form = bh_datasources(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            # Do something with the data
            return render(request, 'success.html')
    else:
        form = bh_datasources()
    return render(request, 'Datasources.html', {'form': form})

def get_datasources(request, mask = True):

    # GET DATASOURCES
    df = get_data("data_sources")

    # SET DELETE LINK FOR ALL BUT THE DEFAULT
    df["Delete"] = np.where(df["ds_name"] == "Zeek Connection Logs", "",df["rowid"].apply(lambda x: '<a href="/DelDS?rowid={}"><i class="fa-regular fa-trash-can"></i></a>'.format(x)))
    df["Edit"] = np.where(df["ds_name"] == "Zeek Connection Logs", "",df["rowid"].apply(lambda x: '<a href="/EditDS?rowid={}"><i class="fa-solid fa-pen-to-square"></i></a>'.format(x)))

    # MASK API KEY FROM DATA SOURCES PAGES
    if mask == True:
        df = _mask_api(df)

    df.rename(columns={"ds_name": "Name", "ds_type": "Type", "data": "Data", "create_date": "Created Date"},inplace=True)
    df = df.reset_index(drop=True)
    df["ID"] = (df.index) + 1

    df = df[["ID", "Name", "Type", "Data", "Created Date", "Edit", "Delete"]]

    context = _get_context(df)

    return render(request, os.path.join(BASE_DIR, "settings", "pages", "DataSources.html"), context)  

def new_ds(request):

    if request.method == "POST":

        try:
            add_ds(request.POST)

            messages.info(request, "Added Data Source {}".format(request.POST.get("ds_name")))
        except BaseException as err:
            messages.error(request, "ERROR: {}".format(err))

        return HttpResponseRedirect("/DataSources.html")
    else:
        df = get_data("data_type")

        # GATHER DROP LIST ITEMS & CONVERT TO JSON
        df = get_data("data_type")
        options = data_to_json(df)

        return render(request, os.path.join(BASE_DIR, "settings", "pages", "NewDataSource.html"), context={"options": options})
    
def del_ds(request):

    try:
        rowid = request.GET.get("rowid")

        del_data("data_source",rowid)
    except BaseException as err:
        messages.error(request, "ERROR: {}".format(err))        
    
    # RELOAD RESULTS VIEW
    return HttpResponseRedirect("/DataSources.html")

def edit_ds(request):

    if request.method == "POST":
        try:
            for key, value in request.POST.items():
                print(f'{key}: {value}')

            print("rowid: {}".format(request.GET.get("rowid")))
            upd_ds(request)
            #messages.info(request, "Updated Data Source {}".format(request.POST.get("ds_name")))

        except BaseException as err:
            messages.error(request, "ERROR: {}".format(err))

        # RELOAD RESULTS VIEW
        return HttpResponseRedirect("/DataSources.html")

    else:
        try:
            rowid = request.GET.get("rowid")
            df = get_data("data_sources", rowid)
            options = _eds_json(df)

        except BaseException as err:
            messages.error(request, "ERROR: {}".format(err))

        return render(request, os.path.join(BASE_DIR, "settings", "pages", "EditDS.html"), context={"options": options})

def get_elasticindex(request):

    if request.method == 'GET':

        data = {"host": request.GET.get("host"),
                "port": request.GET.get("port"),
                "auth": "api",
                "api": request.GET.get("api"),
                "timeout": 10}
        try:
            es = elastic_client(data)
            df = elastic_index(es)
            df = data_to_json(df)

            return JsonResponse(df,safe=False)
        except BaseException as err:

            # UNCOMMENT TO THE RANGE
            #df = [{"index_name": "beacon_huntress_error", "cnt": 0}]
            df = [{"index_name": "Test Index", "cnt": 0}]

            messages.error(request, "ERROR: {}".format(err))
            return JsonResponse(df,safe=False)

    
