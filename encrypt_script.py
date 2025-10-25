#!/usr/bin/env python3
"""
encrypt_script.py
Usage:
  python3 encrypt_script.py -i myscript.py -o myscript.py.enc
Will prompt for password.
"""
import argparse, os, sys
from getpass import getpass
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

MAGIC = b"PYENCv1!"   # 8 bytes header
SALT_LEN = 16
NONCE_LEN = 12        # GCM nonce
TAG_LEN = 16
PBKDF2_ITERS = 200_000

def derive_key(password: str, salt: bytes) -> bytes:
    return PBKDF2(password.encode('utf-8'), salt, dkLen=32, count=PBKDF2_ITERS, hmac_hash_module=SHA256)

def encrypt_file(inpath, outpath, password):
    with open(inpath, 'rb') as f:
        plaintext = f.read()
    salt = get_random_bytes(SALT_LEN)
    key = derive_key(password, salt)
    nonce = get_random_bytes(NONCE_LEN)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    with open(outpath, 'wb') as fo:
        fo.write(MAGIC)
        fo.write(salt)
        fo.write(nonce)
        fo.write(ciphertext)
        fo.write(tag)
    print(f"Encrypted {inpath} -> {outpath}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-i','--input', required=True)
    p.add_argument('-o','--output', required=True)
    args = p.parse_args()

    if not os.path.isfile(args.input):
        print("Input file not found.", file=sys.stderr); sys.exit(2)
    pw = getpass("Password: ")
    if not pw:
        print("Empty password not allowed.", file=sys.stderr); sys.exit(2)
    encrypt_file(args.input, args.output, pw)

if __name__ == "__main__":
    main()