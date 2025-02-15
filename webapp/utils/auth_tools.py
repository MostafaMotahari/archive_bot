import hmac
import hashlib
from os import getenv

def validate_init_data(init_data):
    encrypted_hash = init_data.get('hash', None)
    user_id = init_data.get('user', None)
    if not user_id or encrypted_hash: return False

    check_string = []
    for key in sorted(init_data.keys()):
        if key != 'hash':
            check_string.append(f"{key}={init_data[key][0]}")

    data_check_string = "\n".join(check_string)
    secret_key = hashlib.sha256(getenv('BOT_TOKEN').encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_hash, encrypted_hash)
