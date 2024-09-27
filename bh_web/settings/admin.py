from django.contrib import admin
from .models import conf_general, conf_filter


admin.site.register(conf_general)
admin.site.register(conf_filter)
