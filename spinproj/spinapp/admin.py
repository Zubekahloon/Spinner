from django.contrib import admin
from spinapp.models import User, AssignedHouse, House

# Register your models here.
admin.site.register(User)
admin.site.register(AssignedHouse)
admin.site.register(House)
