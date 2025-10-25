#!/usr/bin/env python3
"""
run_encrypted.py
Usage:
  python3 run_encrypted.py -i myscript.py.enc
Will prompt for password, decrypt in-memory and exec() the script.
"""
import argparse, os, sys
from getpass import getpass
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

MAGIC = b"PYENCv1!"
SALT_LEN = 16
NONCE_LEN = 12
TAG_LEN = 16
PBKDF2_ITERS = 200_000

def derive_key(password: str, salt: bytes) -> bytes:
    return PBKDF2(password.encode('utf-8'), salt, dkLen=32, count=PBKDF2_ITERS, hmac_hash_module=SHA256)

def run_encrypted(path, password):
    with open(path, 'rb') as f:
        magic = f.read(len(MAGIC))
        if magic != MAGIC:
            raise ValueError("Not a supported encrypted Python file.")
        salt = f.read(SALT_LEN)
        nonce = f.read(NONCE_LEN)
        data = f.read()  # remaining == ciphertext + tag
    if len(data) < TAG_LEN:
        raise ValueError("File truncated or invalid.")
    ciphertext = data[:-TAG_LEN]
    tag = data[-TAG_LEN:]
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        raise ValueError("Decryption/authentication failed - wrong password or corrupted file.")
    # Execute code in its own globals context
    code_str = plaintext.decode('utf-8')
    globs = {"__name__":"__main__","__file__": "<encrypted>"}
    exec(compile(code_str, "<decrypted>", 'exec'), globs)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-i','--input', required=True)
    args = p.parse_args()
    if not os.path.isfile(args.input):
        print("Input file not found.", file=sys.stderr); sys.exit(2)
    pw = getpass("Password: ")
    if not pw:
        print("Empty password not allowed.", file=sys.stderr); sys.exit(2)
    try:
        run_encrypted(args.input, pw)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()