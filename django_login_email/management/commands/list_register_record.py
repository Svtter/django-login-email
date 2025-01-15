from django.core.management.base import BaseCommand

from django_login_email import models


class Command(BaseCommand):
  def handle(self, *args, **kwargs):
    print(models.EmailRecord.objects.all())
