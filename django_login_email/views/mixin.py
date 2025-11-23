import datetime

from .. import email, models, token
from . import utils


class MailRecordModelMixin(email.EmailFunc):
  """Here is an example for MailRecord, using django model. You could implement yourself."""

  def reset_mail(self, mail: str):
    """reset mail token expired time."""
    # models.EmailLogin.objects.filter(email=mail).delete()
    e = models.EmailRecord.objects.get(email=mail)
    e.expired_time = e.expired_time - datetime.timedelta(minutes=self.tl.minutes)
    e.validated = False
    e.save()

  def get_mail_record(self, mail: str) -> email.MailRecord:
    """get mail record to validate the salt, and validated status."""
    # for easy to change. use a function.
    try:
      e = models.EmailRecord.objects.get(email=mail)
      return email.MailRecord(
        email=e.email, expired_time=e.expired_time, validated=e.validated, salt=e.salt
      )
    except models.EmailRecord.DoesNotExist:
      return email.MailRecord(email=mail, expired_time=None, validated=False, salt="")

  def transform_timestamp(self, ts: int) -> datetime.datetime:
    return utils.transform_timestamp(ts)

  def save_token(self, token: token.TokenDict):
    """When generate new token, should call this method."""
    try:
      mail = models.EmailRecord.objects.get(email=token["email"])
      mail.salt = token["salt"]
      mail.expired_time = self.transform_timestamp(token["expired_time"])
      mail.mail_type = token["mail_type"]
      mail.validated = False
      mail.save()

    except models.EmailRecord.DoesNotExist:
      models.EmailRecord.objects.create(
        email=token["email"],
        salt=token["salt"],
        expired_time=self.transform_timestamp(token["expired_time"]),
        mail_type=token["mail_type"],
        validated=False,
      )

  def disable_token(self, token: token.TokenDict):
    models.EmailRecord.objects.filter(salt=token["salt"]).update(validated=True)
