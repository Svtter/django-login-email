from django.db import models

# Create your models here.


class EmailRecord(models.Model):
  """Record the token for login/register."""

  expired_time = models.DateTimeField(
    auto_now_add=True, verbose_name="Last register request time"
  )
  validated = models.BooleanField(default=False, verbose_name="Register Token validated")
  mail_type = models.CharField(max_length=100, verbose_name="Mail type")
  salt = models.CharField(max_length=100, verbose_name="Salt")
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


class IPBan(models.Model):
  """用于处理 IP 禁止发送的情况"""

  ip = models.GenericIPAddressField(verbose_name="IP Address", unique=True)
  reason = models.TextField(verbose_name="Reason")
  created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

  def __str__(self) -> str:
    return f"IP: {self.ip}"

  @classmethod
  def add_ip_ban(cls, ip: str, reason: str) -> "IPBan":
    """添加 IP 禁止发送的情况"""
    obj, _ = cls.objects.get_or_create(ip=ip)
    obj.reason = reason
    obj.save()
    return obj
