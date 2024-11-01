from django.contrib import admin
from api.models import *

# Register your models here.
admin.site.register(Software)
admin.site.register(Comment)
admin.site.register(Department)
admin.site.register(Vendor)
admin.site.register(ContactPerson)
admin.site.register(Division)
admin.site.register(GlAccount)
admin.site.register(SoftwareToOperate)
admin.site.register(HardwareToOperate)
