from django.contrib import admin

from django_login_email import models

# Register your models here.


@admin.register(models.EmailRecord)
class EmailRecordAdmin(admin.ModelAdmin):
  list_display = ("email", "expired_time", "validated", "mail_type")
