from flask import Flask, render_template, request, jsonify
import base64
import os
from datetime import datetime, timezone

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
    "app": """Orange Power Plant Backup Service
Status: degraded
Last operator: Shorton
Incident note: unexplained remote activity detected from internal Redis segment.
""",
    "classified": """CLASSIFIED ORANGE POWER PLANT DOCUMENT

Backup server containment failed.
The attacker moved from the internal Redis calculator environment into this backup host.

SOC note:
Do not trust exposed internal tooling.
Do not expose backup interfaces.
Do not ignore orange alarms.
""",
    "requirements.txt": """flask==3.0.3
orange-reactor-utils==8.0
redis-diagnostics==1.4
backup-recovery-agent==0.0.0-broken
""",
    "flag": "XMON{Tor_Over_VPN???}\n"
}


def fake_encrypt(content: str) -> str:
    encoded = base64.b64encode(content.encode()).decode()
    chunks = [encoded[i:i + 48] for i in range(0, len(encoded), 48)]
    return "\n".join(chunks)


ENCRYPTED_FILES = {
    f"{name}.cl0p": fake_encrypt(content)
    for name, content in PLAINTEXT_FILES.items()
}


@app.route("/")
def index():
    encrypted_files = [
        {
            "name": "app.cl0p",
            "type": "encrypted application folder",
            "size": "4.1 KB",
        },
        {
            "name": "classified.cl0p",
            "type": "encrypted document",
            "size": "8.8 KB",
        },
        {
            "name": "requirements.txt.cl0p",
            "type": "encrypted dependency list",
            "size": "1.7 KB",
        },
        {
            "name": "flag.cl0p",
            "type": "encrypted flag file",
            "size": "512 B",
        },
    ]

    system_files = [
        {
            "name": "decryptor",
            "type": "recovery utility",
            "size": "31 KB",
        },
        {
            "name": "AAA_READ_AAA.txt",
            "type": "ransom note",
            "size": "3.4 KB",
        },
    ]

    return render_template(
        "index.html",
        encrypted_files=encrypted_files,
        system_files=system_files,
        ransom_note=RANSOM_NOTE,
    )


@app.route("/api/file/<path:filename>")
def get_file(filename):
    if filename == "AAA_READ_AAA.txt":
        return jsonify({
            "ok": True,
            "filename": filename,
            "content": RANSOM_NOTE,
            "encrypted": False
        })

    if filename == "decryptor":
        return jsonify({
            "ok": True,
            "filename": filename,
            "content": "Orange Backup Recovery Utility\nKey required.\nStatus: locked.\n",
            "encrypted": False
        })

    if filename in ENCRYPTED_FILES:
        return jsonify({
            "ok": True,
            "filename": filename,
            "content": ENCRYPTED_FILES[filename],
            "encrypted": True
        })

    return jsonify({
        "ok": False,
        "error": "File not found"
    }), 404


@app.route("/api/decrypt", methods=["POST"])
def decrypt():
    data = request.get_json(silent=True) or {}
    key = data.get("key", "").strip()

    if key != DECRYPTION_KEY:
        return jsonify({
            "ok": False,
            "message": "Invalid recovery key. Decryption failed. Remaining files stay locked."
        }), 403

    decrypted_files = {
        "app": PLAINTEXT_FILES["app"],
        "classified": PLAINTEXT_FILES["classified"],
        "requirements.txt": PLAINTEXT_FILES["requirements.txt"],
        "flag": PLAINTEXT_FILES["flag"],
    }

    return jsonify({
        "ok": True,
        "message": "Recovery key accepted. Files decrypted successfully.",
        "decrypted_at": datetime.now(timezone.utc).isoformat(),
        "files": decrypted_files
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "orange-backup-ransomware-ctf"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
