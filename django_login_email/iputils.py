from django.core.cache import cache
from django.http import HttpRequest

from .models import IPBan


class Recorder(object):
  """用于记录发送情况"""

  times = 3
  minutes = 10

  def record(self, ip: str):
    """
    If ip in cache not exist, set `ip` in cache with 0 and 10 minutes expired.

    - same email account, 1 time in 10 minutes
    - different email account, 3 times in 10 minutes

    Else, incr `ip` in cache.
    """
    count = cache.get_or_set(ip, 0, self.minutes * 60)
    if count < self.times:
      cache.incr(ip)
      return True
    else:
      IPBan.add_ip_ban(
        ip, f"send email more than {self.times} times in {self.minutes} minutes"
      )
    return False


class IPBanUtils(object):
  """用于处理 IP 禁止发送的情况"""

  recorder = Recorder()

  def get_times(self):
    return self.recorder.times

  def get_client_ip(self, request: HttpRequest) -> str:
    """获取用户的真实IP地址

    Security Note:
        By default, this method only uses REMOTE_ADDR to prevent IP spoofing.
        Set USE_X_FORWARDED_FOR = True in Django settings only if your application
        is behind a trusted reverse proxy (nginx, apache, cloudflare, etc.) and
        the proxy is properly configured to set X-Forwarded-For.

    Args:
        request: Django HTTP请求对象

    Returns:
        str: 用户的IP地址
    """
    # Check if we should trust X-Forwarded-For header (only behind trusted proxy)
    from django.conf import settings

    use_x_forwarded_for = getattr(settings, "USE_X_FORWARDED_FOR", False)

    if use_x_forwarded_for:
      x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
      if x_forwarded_for:
        # Get the first IP in the chain (client IP)
        # Format: "client, proxy1, proxy2"
        ip = x_forwarded_for.split(",")[0].strip()
        return ip

    # Default: use REMOTE_ADDR (safe, cannot be spoofed)
    ip = request.META.get("REMOTE_ADDR", "")
    return ip

  def record_send(self, request: HttpRequest) -> bool:
    """记录发送情况

    Args:
        request: Django HTTP请求对象

    Returns:
        bool: 如果允许发送返回True，如果超过限制返回False
    """
    # 记录发送
    ip = self.get_client_ip(request)
    return self.recorder.record(ip)

  def is_ip_banned(self, ip: str) -> bool:
    """检查IP是否被禁止

    Args:
        ip: 需要检查的IP地址

    Returns:
        bool: 如果IP被禁止返回True，否则返回False
    """
    return IPBan.objects.filter(ip=ip).exists()
