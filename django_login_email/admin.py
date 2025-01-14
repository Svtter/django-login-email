from django.contrib import admin

from django_login_email import models

# Register your models here.


@admin.register(models.EmailRegister)
class EmailRegisterAdmin(admin.ModelAdmin):
  list_display = ("email", "expired_time", "validated")


@admin.register(models.EmailLogin)
class EmailLoginAdmin(admin.ModelAdmin):
  list_display = ("email", "expired_time", "validated")
