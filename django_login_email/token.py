# Handle email token
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
    minutes: int = 10

    def get_expire_time(self) -> int:
        return int((datetime.datetime.now() + datetime.timedelta(minutes=self.minutes)).timestamp())

    def gen(self, email, salt):
        return json.dumps(
            {
                "email": email,
                "expire_time": self.get_expire_time(),
                "salt": salt,
            }
        )


class TokenManager(object):
    salt: str = "randomsalt"
    key: bytes
    generator: TokenGenerator = TokenGenerator()

    def __init__(self) -> None:
        self.key = settings.SECRET_KEY[:32].encode("utf-8")

    def check_token(self, token_uncrypt: str) -> t.Optional[TokenDict]:
        """check salt and expire-time"""
        token_dict: TokenDict = json.loads(token_uncrypt)
        if token_dict["salt"] == self.salt and token_dict["expire_time"] > int(datetime.datetime.now().timestamp()):
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

    def encrypt_mail(self, email: Email) -> str:
        """email -> token -> base64 -> utf-8 -> urlquote"""
        # add salt.
        content = self.generator.gen(email, self.salt)
        content = content.encode("utf-8")
        return urllib.parse.quote(base64.b64encode(self.encrypt(content, self.key)).decode("utf-8"))

    def decrypt_token(self, token: Token) -> str:
        t = urllib.parse.unquote(token).encode("utf-8")
        print(t)
        t = base64.b64decode(t)
        return self.decrypt(t, self.key).decode("utf-8")
