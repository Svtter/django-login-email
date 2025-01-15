from django.db import models

# Create your models here.


class EmailRecord(models.Model):
  """Record the token for login/register."""

  expired_time = models.DateTimeField(
    auto_now_add=True, verbose_name="Last register request time"
  )
  validated = models.BooleanField(default=False, verbose_name="Register Token validated")
  mail_type = models.CharField(max_length=100, verbose_name="Mail type")
  sault = models.CharField(max_length=100, verbose_name="Sault")
  email = models.EmailField(verbose_name="Email", unique=True, null=False)

  @classmethod
  def set_email_expired_time(cls, email, datetime) -> "EmailRecord":
    obj, _ = cls.objects.get_or_create(email=email)
    obj.set_expired_time(datetime)
    return obj

  def set_expired_time(self, datetime):
    self.expired_time = datetime
    self.validated = False
    self.save()

  def __str__(self) -> str:
    return f"Email: {self.email}, mail_type: {self.mail_type}"
