#!/usr/bin/env python3
# decrypt_restore.py
# Usage: python3 decrypt_restore.py -i corrupted_file -o restored.py
from getpass import getpass
import argparse, sys, os
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

def decrypt_file(inpath, outpath, password):
    size = os.path.getsize(inpath)
    with open(inpath, 'rb') as f:
        magic = f.read(len(MAGIC))
        if magic != MAGIC:
            raise SystemExit("File header mismatch — not a supported encrypted file.")
        salt = f.read(SALT_LEN)
        nonce = f.read(NONCE_LEN)
        rest = f.read()
    if len(rest) < TAG_LEN:
        raise SystemExit("File too small / truncated.")
    ciphertext = rest[:-TAG_LEN]
    tag = rest[-TAG_LEN:]
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        raise SystemExit("Decryption failed: wrong password or corrupted file.")
    with open(outpath, 'wb') as fo:
        fo.write(plaintext)
    print("Restored ->", outpath)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('-i','--input', required=True)
    p.add_argument('-o','--output', required=True)
    args = p.parse_args()
    if not os.path.isfile(args.input):
        raise SystemExit("Input not found.")
    pw = getpass("Password: ")
    decrypt_file(args.input, args.output, pw)

if __name__ == "__main__":
    main()