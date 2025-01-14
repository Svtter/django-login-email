import datetime

from .. import email, models, token
from . import utils


class MailRecordModelMixin(email.EmailInfoMixin):
  """Here is an example for MailRecord, using django model. You could implement yourself."""

  def reset_mail(self, mail: str):
    """reset mail token expired time."""
    # models.EmailLogin.objects.filter(email=mail).delete()
    e = models.EmailLogin.objects.get(email=mail)
    e.expired_time = e.expired_time - datetime.timedelta(minutes=self.tl.minutes)
    e.validated = False
    e.save()

  def get_mail_record(self, mail: str) -> email.MailRecord:
    """get mail record to validate the sault, and validated status."""
    # for easy to change. use a function.
    try:
      e = models.EmailLogin.objects.get(email=mail)
      return email.MailRecord(
        email=e.email, expired_time=e.expired_time, validated=e.validated, sault=e.sault
      )
    except models.EmailLogin.DoesNotExist:
      return email.MailRecord(email=mail, expired_time=None, validated=False, sault="")

  def transform_timestamp(self, ts: int) -> datetime.datetime:
    return utils.transform_timestamp(ts)

  def save_token(self, token: token.TokenDict):
    """When generate new token, should call this method."""
    try:
      models.EmailLogin.objects.filter(email=token["email"]).update(
        sault=token["salt"],
        expired_time=self.transform_timestamp(token["expired_time"]),
      )
    except models.EmailLogin.DoesNotExist:
      models.EmailLogin.objects.create(
        email=token["email"],
        sault=token["salt"],
        expired_time=self.transform_timestamp(token["expired_time"]),
      )

  def disable_token(self, token: token.TokenDict):
    models.EmailLogin.objects.filter(sault=token["salt"]).update(validated=True)
