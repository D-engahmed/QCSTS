import hashlib
import hmac
import os


# Paymob's transaction callback HMAC uses the documented transaction fields
# concatenated in the provider-defined order and SHA-512 with the merchant HMAC
# secret. Never trust the callback payload before this check.
TRANSACTION_HMAC_FIELDS = (
    "amount_cents",
    "created_at",
    "currency",
    "error_occured",
    "has_parent_transaction",
    "id",
    "integration_id",
    "is_3d_secure",
    "is_auth",
    "is_capture",
    "is_refunded",
    "is_standalone_payment",
    "is_voided",
    "order_id",
    "owner",
    "pending",
    "source_data_pan",
    "source_data_sub_type",
    "source_data_type",
    "success",
)


def _transaction_values(obj: dict) -> list[str]:
    order = obj.get("order")
    order = order if isinstance(order, dict) else {}
    source = obj.get("source_data")
    source = source if isinstance(source, dict) else {}
    values = {
        "amount_cents": obj.get("amount_cents"),
        "created_at": obj.get("created_at"),
        "currency": obj.get("currency"),
        "error_occured": obj.get("error_occured"),
        "has_parent_transaction": obj.get("has_parent_transaction"),
        "id": obj.get("id"),
        "integration_id": obj.get("integration_id"),
        "is_3d_secure": obj.get("is_3d_secure"),
        "is_auth": obj.get("is_auth"),
        "is_capture": obj.get("is_capture"),
        "is_refunded": obj.get("is_refunded"),
        "is_standalone_payment": obj.get("is_standalone_payment"),
        "is_voided": obj.get("is_voided"),
        "order_id": order.get("id"),
        "owner": obj.get("owner"),
        "pending": obj.get("pending"),
        "source_data_pan": source.get("pan"),
        "source_data_sub_type": source.get("sub_type"),
        "source_data_type": source.get("type"),
        "success": obj.get("success"),
    }
    return [str(values[key]) for key in TRANSACTION_HMAC_FIELDS]


def calculate_transaction_hmac(obj: dict, secret: str) -> str:
    message = "".join(_transaction_values(obj)).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha512).hexdigest()


def verify_transaction_hmac(obj: dict, supplied_hmac: str | None, secret: str | None = None) -> bool:
    secret = secret or os.environ.get("PAYMOB_HMAC_SECRET", "")
    if not secret or not supplied_hmac:
        return False
    expected = calculate_transaction_hmac(obj, secret)
    return hmac.compare_digest(expected, supplied_hmac)
