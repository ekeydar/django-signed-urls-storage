from django.core.signing import Signer, BadSignature
from django.utils import timezone


def check_signature(name: str, signature: str, expires: int) -> str:
    """
    check signature and expiration timestamp
    """
    signer = Signer()
    full_value = '{}-{}'.format(name, expires)
    try:
        signer.unsign('{}{}{}'.format(full_value, signer.sep, signature))
    except BadSignature:
        return False
    if expires < timezone.now().timestamp():
        return False
    return True


