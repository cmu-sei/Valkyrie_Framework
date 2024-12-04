from django.contrib import admin
from .models import Agg, DBScan, DBScanVar, ByConnGroup, ByPConn, ByPacket

# Register your models here.
admin.site.register(Agg)
admin.site.register(DBScan)
admin.site.register(DBScanVar)
admin.site.register(ByConnGroup)
admin.site.register(ByPConn)
admin.site.register(ByPacket)