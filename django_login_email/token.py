# Handle email token
import base64
import datetime
import hashlib
import json
import logging
import os
import typing as t
import urllib.parse

from Crypto.Cipher import AES
from django.conf import settings

Token = str
EmailAndSalt = str
Email = str

TokenDict = t.TypedDict(
  "TokenDict", {"email": Email, "expired_time": int, "salt": str, "mail_type": str}
)

logger = logging.getLogger(__name__)


class TokenGenerator(object):
  """generate token by minutes"""

  def __init__(self, minutes: int) -> None:
    self.minutes = minutes

  def get_expired_time(self) -> int:
    return int(
      (datetime.datetime.now() + datetime.timedelta(minutes=self.minutes)).timestamp()
    )

  def gen_salt(self, email) -> str:
    return email + str(base64.b64encode(os.urandom(16)))

  def gen(self, email, mail_type: str, save_token: t.Callable[[TokenDict], None]) -> str:
    """call save_token to save token in database or somewhere"""
    token: TokenDict = {
      "email": email,
      "expired_time": self.get_expired_time(),
      "salt": self.gen_salt(email),
      "mail_type": mail_type,
    }
    save_token(token)
    token_str = json.dumps(token)
    return token_str


class TokenManager(object):
  """manage the email generate token"""

  key: bytes
  generator: TokenGenerator

  def __init__(self, minutes: int) -> None:
    # Use SHA-256 to derive a fixed 32-byte key from SECRET_KEY
    self.key = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    self.generator: TokenGenerator = TokenGenerator(minutes)

  def transform_token(self, token_uncrypt: Token) -> TokenDict:
    token_dict: TokenDict = json.loads(token_uncrypt)
    return token_dict

  def check_token(
    self, token_dict: TokenDict, get_salt: t.Callable[[], str]
  ) -> t.Optional[TokenDict]:
    """check salt and expire-time"""
    logger.info(f"token_dict: {token_dict}")
    if not token_dict["salt"] == get_salt():
      logger.info(f"salt is error, {token_dict['salt']}, {get_salt()}")
      return None
    if token_dict["expired_time"] > int(datetime.datetime.now().timestamp()):
      logger.info("expired_time is ok")
      return token_dict
    logger.info("expired_time is error")
    return None

  def get_mail(self, token_uncrypt: TokenDict) -> Email:
    """Read the email from token"""
    return token_uncrypt["email"]

  def _encrypt(self, plaintext, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + ciphertext + tag

  def _decrypt(self, ciphertext, key):
    nonce = ciphertext[:16]
    tag = ciphertext[-16:]
    ciphertext = ciphertext[16:-16]
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext

  def encrypt_mail(
    self, email: Email, mail_type: str, save_token: t.Callable[[TokenDict], None]
  ) -> str:
    """email -> token -> base64 -> utf-8 -> urlquote"""
    # add salt.
    content = self.generator.gen(email, mail_type, save_token)
    content = content.encode("utf-8")
    return urllib.parse.quote(
      base64.b64encode(self._encrypt(content, self.key)).decode("utf-8")
    )

  def decrypt_token(self, token: Token) -> str:
    t = urllib.parse.unquote(token).encode("utf-8")
    t = base64.b64decode(t)
    return self._decrypt(t, self.key).decode("utf-8")
