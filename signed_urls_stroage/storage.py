import urllib.parse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.signing import Signer, BadSignature
from django.utils import timezone


class SignedAccessStorage(FileSystemStorage):
    def __init__(self, hours=1, location=None, base_url=None, *args, **kwargs):
        self.hours = hours
        super().__init__(
            location=location or settings.MEDIA_SIGNED_ROOT,
            base_url=base_url or settings.MEDIA_SIGNED_URL,
            *args, **kwargs)

    def url(self, name):
        return self.get_signed_url(name)

    def get_signed_url(self, name: str, hours: float = None) -> str:
        hours = hours or self.hours
        expires = int(timezone.now().timestamp() + hours * 3600)
        signer = Signer()
        full_value = '{}-{}'.format(name, expires)
        full_signature = signer.sign(full_value)
        signature = full_signature.split(signer.sep)[-1]  # just the signature part
        return '{}?{}'.format(super().url(name), urllib.parse.urlencode({
            'signature': signature,
            'expires': expires
        }))


signed_urls_storage = SignedAccessStorage()


