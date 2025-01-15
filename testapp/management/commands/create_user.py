from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
  def handle(self, *args, **kwargs):
    User.objects.create_superuser(
      username="test@test.com",
      email="test@test.com",
      password="test",
    )
    self.stdout.write("Create superuser test@test.com, with password test.")
