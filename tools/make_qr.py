import os
import sys
from pathlib import Path

import qrcode

# Read URL from command line argument or environment
url = None
if len(sys.argv) > 1:
    url = sys.argv[1].strip()

if not url:
    url = os.environ.get("QR_URL", "").strip()

if not url:
    print("ERROR: No QR URL provided. Pass URL as argument or set QR_URL environment variable.")
    sys.exit(1)

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
