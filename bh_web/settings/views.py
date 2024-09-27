# Create your views here.  
from pathlib import Path
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from .forms import bh_settings_general, bh_filter_settings
from .models import conf_general, conf_filter
import os

BASE_DIR = Path(__file__).resolve().parent.parent


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
