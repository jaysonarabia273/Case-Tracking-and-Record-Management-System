from django.contrib import admin
from .models import Profile, Case, Comment, Appointment

# Register your models here.
admin.site.register(Profile)
admin.site.register(Case)
admin.site.register(Comment)
admin.site.register(Appointment)