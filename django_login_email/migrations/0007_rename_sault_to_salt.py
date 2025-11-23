# Generated manually to rename field sault to salt

from django.db import migrations


class Migration(migrations.Migration):
  dependencies = [
    ("django_login_email", "0006_ipban"),
  ]

  operations = [
    migrations.RenameField(
      model_name="emailrecord",
      old_name="sault",
      new_name="salt",
    ),
  ]
