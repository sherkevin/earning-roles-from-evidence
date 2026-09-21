from __future__ import annotations
import argparse
import io
import zipfile
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PASSWORD = "WEquKLy##9M@qu"
SALT = b"Nvx#rYcYQ2%btf"

def decrypt(data: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
        backend=default_backend(),
    )
    key = kdf.derive(PASSWORD.encode())
    iv, ciphertext = data[:16], data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    dec = cipher.decryptor()
    return dec.update(ciphertext) + dec.finalize()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    data = Path(args.bundle).read_bytes()
    raw = decrypt(data)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(raw), "r") as zf:
        names = zf.namelist()
        zf.extractall(out)
    print("files", len(names))
    for name in names[:30]:
        print(name)

if __name__ == "__main__":
    main()
