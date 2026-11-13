import base64
import uuid

from io import BytesIO
from datetime import timedelta

import qrcode

from django.core.signing import Signer, BadSignature
from django.utils import timezone

from .models import QRSession

QR_TOKEN_VALIDITY_SECONDS = 45

qr_signer = Signer(salt="attendance.qr-session.v1")


def generate_qr_token(session):
    """
    Generate a signed token using the session ID and current nonce.
    The same session nonce produces the same token.
    """

    payload = {
        "session_id": session.id,
        "nonce": str(session.current_nonce),
    }

    return qr_signer.sign_object(payload)


def rotate_qr_token(session):
    """
    Generate a new nonce and invalidate all previously issued tokens.
    """

    now = timezone.now()

    if not session.is_currently_active:
        raise ValueError("This attendance session is not currently active.")

    session.current_nonce = uuid.uuid4()

    session.qr_expires_at = min(
        now + timedelta(seconds=QR_TOKEN_VALIDITY_SECONDS), session.ends_at
    )

    session.save(
        update_fields=[
            "current_nonce",
            "qr_expires_at",
            "updated_at",
        ]
    )

    return generate_qr_token(session)


def ensure_current_qr_token(session):
    """
    Return the existing QR token if valid.
    Otherwise generate a new one.
    """

    now = timezone.now()

    if not session.is_currently_active:
        raise ValueError("This attendance session is not currently active.")

    if session.qr_expires_at is None or session.qr_expires_at <= now:
        return rotate_qr_token(session)

    return generate_qr_token(session)


def generate_qr_image(token):
    """
    Generate a PNG QR image and return it as a Base64 data URI.
    """

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(token)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{encoded_image}"


def build_qr_response(session, token):
    return {
        "session_id": session.id,
        "title": session.title,
        "qr_payload": token,
        "qr_image": generate_qr_image(token),
        "expires_at": session.qr_expires_at,
        "validity_seconds": QR_TOKEN_VALIDITY_SECONDS,
    }


def validate_qr_token(token):
    """
    Validate signature, session, nonce, status and expiry.
    Returns the QRSession if valid, otherwise None.
    """

    try:
        payload = qr_signer.unsign_object(token)
    except (BadSignature, TypeError, ValueError):
        return None

    try:
        session = QRSession.objects.get(id=payload.get("session_id"))
    except (QRSession.DoesNotExist, ValueError, TypeError):
        return None

    now = timezone.now()

    if not session.is_currently_active:
        return None

    if session.qr_expires_at is None or session.qr_expires_at <= now:
        return None

    if str(session.current_nonce) != payload.get("nonce"):
        return None

    return session
