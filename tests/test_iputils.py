from django.core.cache import cache

from django_login_email import iputils


class IPBanUtils(iputils.IPBanUtils):
  def get_client_ip(self, request):
    return "127.0.0.1"


def test_iputils(db):
  cache.clear()  # Clear cache before test to prevent pollution
  ip_utils = IPBanUtils()
  ip_utils.record_send({"REMOTE_ADDR": "127.0.0.1"})
  assert not ip_utils.is_ip_banned("127.0.0.1")


def test_iputils_3_times(db):
  cache.clear()  # Clear cache before test to prevent pollution
  ip_utils = IPBanUtils()
  for _ in range(ip_utils.get_times()):
    ip_utils.record_send({"REMOTE_ADDR": "127.0.0.1"})
  assert not ip_utils.is_ip_banned("127.0.0.1")

  ip_utils.record_send({"REMOTE_ADDR": "127.0.0.1"})
  assert ip_utils.is_ip_banned("127.0.0.1")
