from flask import Flask, render_template, request, jsonify
import hashlib
import hmac
import base64
import time

app = Flask(__name__)

DECRYPTION_KEY = "8f3b9a7c2d1e4f6a90b73c5d8e21f4a6"

RANSOM_NOTE = """Attention!

We are the ones who hacked you and DOWNLOAD yor data!

We have extensive experience and a strong reputation in this field.
Take what is written below seriously!!!!
We DOWNLOADED - 1,65 Tb

We DOWNLOADED - Your financial documentation, HR Documents, Accounting, your mails,
Databases, private correspondence about transactions, employee documents, company documents,
Internal manuals, production data, and much more.

If necessary, we are ready to provide all the evidence.

Contact us within 48 hours in our chat:
https://chatgpt.com/g/g-6a16b4de7a008191a9ba093eac918cc1-ransomdata

due to blocking of telecom operators
if you write from proton.me please write here un-l0ck@l3aks.com

About us:
OUR BLOG - "link": http://abc.onion/
"""

PLAINTEXT_FILES = {
    "app": """Orange Power Plant backup application snapshot

Status:
- Redis pivot observed
- Backup host accessed
- Recovery process interrupted
- Local classified material encrypted

This file was restored by the decryptor.
""",
    "classified": """CLASSIFIED ORANGE POWER PLANT RECOVERY DOCUMENT

Incident:
Kimsuky gained access to the backup server after the Redis incident.

Recovered flag:
XMON{Tor_Over_VPN???}
""",
    "requirements.txt": """flask==3.0.3
cryptography==42.0.8
requests==2.32.3
""",
    "backup_notes": """OPP-BACKUP-2024

Fish_ note:
The attacker did not store the key on this server.
Negotiation channel must be used to recover encrypted material.

Do not trust files ending in .cl0p.
"""
}

GIBBERISH_NAMES = {
    "app": "x8qz91f2.cl0p",
    "classified": "mzz0_19xk.cl0p",
    "requirements.txt": "r4nd0m_pkg.cl0p",
    "backup_notes": "9fksl2qp.cl0p"
}


def derive_stream(key: str, length: int) -> bytes:
    stream = b""
    counter = 0

    while len(stream) < length:
        block = hmac.new(
            key.encode(),
            f"orange-power-plant-{counter}".encode(),
            hashlib.sha256
        ).digest()
        stream += block
        counter += 1

    return stream[:length]


def encrypt_text(value: str, key: str) -> str:
    data = value.encode()
    stream = derive_stream(key, len(data))
    encrypted = bytes([a ^ b for a, b in zip(data, stream)])
    return base64.b64encode(encrypted).decode()


def decrypt_text(value: str, key: str) -> str:
    encrypted = base64.b64decode(value.encode())
    stream = derive_stream(key, len(encrypted))
    decrypted = bytes([a ^ b for a, b in zip(encrypted, stream)])
    return decrypted.decode(errors="replace")


ENCRYPTED_FILES = {
    original_name: encrypt_text(content, DECRYPTION_KEY)
    for original_name, content in PLAINTEXT_FILES.items()
}


@app.route("/")
def index():
    encrypted_listing = []

    for original_name, gibberish_name in GIBBERISH_NAMES.items():
        encrypted_listing.append({
            "real_name": original_name,
            "display_name": gibberish_name,
            "size": len(ENCRYPTED_FILES[original_name]),
            "status": "ENCRYPTED"
        })

    return render_template(
        "index.html",
        encrypted_files=encrypted_listing,
        ransom_note=RANSOM_NOTE
    )


@app.route("/api/decrypt", methods=["POST"])
def decrypt():
    body = request.get_json(silent=True) or {}
    supplied_key = body.get("key", "").strip()

    time.sleep(1.2)

    if supplied_key != DECRYPTION_KEY:
        return jsonify({
            "ok": False,
            "message": "Invalid recovery key. Decryption failed. Files remain locked."
        }), 403

    restored_files = []

    for original_name, encrypted_value in ENCRYPTED_FILES.items():
        restored_files.append({
            "name": original_name,
            "content": decrypt_text(encrypted_value, supplied_key),
            "size": len(decrypt_text(encrypted_value, supplied_key)),
            "status": "RESTORED"
        })

    return jsonify({
        "ok": True,
        "message": "Recovery key accepted. Encrypted files restored.",
        "files": restored_files
    })


@app.route("/health")
def health():
    return {"status": "locked"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
