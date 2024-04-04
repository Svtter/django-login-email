# Handle email token

from Crypto.Cipher import AES
from django.conf import settings

Token = str
EmailAndSalt = str
Email = str


class TokenManager(object):
    salt: str = "randomsalt"
    key: str

    def __init__(self) -> None:
        self.key = settings.SECRET_KEY

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

    def encrypt_mail(self, email: Email) -> Token:
        # add salt.
        content = email + self.salt
        return self.encrypt(content, self.key)

    def decrypt_token(self, token: Token) -> EmailAndSalt:
        return self.decrypt(token, self.key)
