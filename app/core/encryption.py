from cryptography.fernet import Fernet

from app.core.config import settings

cipher = Fernet(
    settings.FERNET_KEY.encode()
)


def encrypt_data(data: str):
    return cipher.encrypt(
        data.encode()
    ).decode()


def decrypt_data(data: str):
    return cipher.decrypt(
        data.encode()
    ).decode()
