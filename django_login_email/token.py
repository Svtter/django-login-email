# Handle email token
import base64
import urllib.parse

from Crypto.Cipher import AES
from django.conf import settings

Token = str
EmailAndSalt = str
Email = str


class TokenManager(object):
    salt: str = "randomsalt"
    key: bytes

    def __init__(self) -> None:
        self.key = settings.SECRET_KEY[:32].encode("utf-8")

    def check_salt(self, token_uncrypt: str):
        if token_uncrypt.endswith(self.salt):
            return True
        return False

    def get_mail(self, token_uncrypt: str):
        return token_uncrypt[: -len(self.salt)]

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
        content = email + self.salt
        content = content.encode("utf-8")
        return urllib.parse.quote(base64.b64encode(self.encrypt(content, self.key)).decode("utf-8"))

    def decrypt_token(self, token: Token) -> str:
        t = urllib.parse.unquote(token).encode("utf-8")
        print(t)
        t = base64.b64decode(t)
        return self.decrypt(t, self.key).decode("utf-8")
