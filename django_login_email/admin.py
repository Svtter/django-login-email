from django.contrib import admin

from django_login_email import models

# Register your models here.


@admin.register(models.EmailRecord)
class EmailRecordAdmin(admin.ModelAdmin):
  list_display = ("email", "expired_time", "validated", "mail_type")


@admin.register(models.IPBan)
class IPBanAdmin(admin.ModelAdmin):
  """Users could cancel limitation by delete the IPBan object; or add new IPBan object."""

  list_display = ("ip", "reason", "created_at")
