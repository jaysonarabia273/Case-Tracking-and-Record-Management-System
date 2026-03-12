import os
import socket
from pathlib import Path

import qrcode


def build_default_url() -> str:
    host = os.environ.get("COMPUTERNAME") or socket.gethostname() or "localhost"
    port = os.environ.get("QR_PORT", "8000")
    return f"http://{host}:{port}"


url = os.environ.get("QR_URL", "").strip() or build_default_url()
out = Path(__file__).resolve().parents[1] / "Capstone" / "static" / "app" / "qr-student-access.png"
out.parent.mkdir(parents=True, exist_ok=True)

img = qrcode.QRCode(
    version=4,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=14,
    border=3,
)
img.add_data(url)
img.make(fit=True)
qr = img.make_image(fill_color="black", back_color="white")
qr.save(out)

print(f"QR URL: {url}")
print(f"QR file: {out}")
