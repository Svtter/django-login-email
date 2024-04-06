# Handle email token
import os
import base64
import json
import urllib.parse
import typing as t

from Crypto.Cipher import AES
from django.conf import settings
import datetime

Token = str
EmailAndSalt = str
Email = str

TokenDict = t.TypedDict("TokenDict", {"email": Email, "expire_time": int, "salt": str})


class TokenGenerator(object):
    def __init__(self, minutes: int) -> None:
        self.minutes = minutes

    def get_expire_time(self) -> int:
        return int((datetime.datetime.now() + datetime.timedelta(minutes=self.minutes)).timestamp())

    def gen_salt(self, email) -> str:
        return email + os.urandom(16)

    def gen(self, email, save_token: t.Callable[[TokenDict], None]) -> str:
        """call save_token to save token in database or somewhere"""
        token: TokenDict = {
            "email": email,
            "expire_time": self.get_expire_time(),
            "salt": self.gen_salt(email),
        }
        save_token(token)
        token_str = json.dumps(token)
        return token_str


class TokenManager(object):
    key: bytes
    generator: TokenGenerator

    def __init__(self, minutes: int) -> None:
        self.key = settings.SECRET_KEY[:32].encode("utf-8")
        self.generator: TokenGenerator = TokenGenerator(minutes)

    def check_token(self, token_uncrypt: str, get_salt: t.Callable[[str], str]) -> t.Optional[TokenDict]:
        """check salt and expire-time"""
        token_dict: TokenDict = json.loads(token_uncrypt)
        if token_dict["salt"] == get_salt(token_dict["email"]) and token_dict["expire_time"] > int(
            datetime.datetime.now().timestamp()
        ):
            return token_dict
        return None

    def get_mail(self, token_uncrypt: TokenDict) -> Email:
        return token_uncrypt["email"]

    def encrypt(self, plaintext, key):
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return nonce + ciphertext + tag

    def decrypt(self, ciphertext, key):
        nonce = ciphertext[:16]
        tag = ciphertext[-16:]
        ciphertext = ciphertext[16:-16]
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext

    def encrypt_mail(self, email: Email, save_token: t.Callable[[TokenDict], None]) -> str:
        """email -> token -> base64 -> utf-8 -> urlquote"""
        # add salt.
        content = self.generator.gen(email, save_token)
        content = content.encode("utf-8")
        return urllib.parse.quote(base64.b64encode(self.encrypt(content, self.key)).decode("utf-8"))

    def decrypt_token(self, token: Token) -> str:
        t = urllib.parse.unquote(token).encode("utf-8")
        print(t)
        t = base64.b64decode(t)
        return self.decrypt(t, self.key).decode("utf-8")
