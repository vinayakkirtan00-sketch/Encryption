
    <h1>Python Script Encryption & Recovery (Termux / Linux)</h1><div class="section">
    <h2>1. Check which file got corrupted</h2>
    <p>Run these commands to check if the file is text or binary:</p>
    <pre><code class="cmd">file encrypt_script.py

file run_encrypted.py</code></pre> <p>Peek first bytes as hex:</p> <pre><code class="cmd">head -c 64 encrypt_script.py | xxd head -c 64 run_encrypted.py | xxd</code></pre> <p>Or view the first few lines as text:</p> <pre><code class="cmd">head -n 5 encrypt_script.py head -n 5 run_encrypted.py</code></pre> <p>If output shows ASCII text → fine. If you see weird binary symbols → file is encrypted.</p> </div>

<div class="section">
    <h2>2. If you overwrote the original script</h2>
    <p>If you used the same file for input and output (example: <code>-i run_encrypted.py -o run_encrypted.py</code>), your original file got encrypted.</p>
    <p>To recover, you’ll need the same password used during encryption. Without it, recovery is not possible.</p>
</div>

<div class="section">
    <h2>3. Decrypt with <code>decrypt_restore.py</code></h2>
    <p>Create a new file <code>decrypt_restore.py</code> and paste this code:</p>
    <pre><code>#!/usr/bin/env python3

from getpass import getpass import argparse, sys, os from Crypto.Cipher import AES from Crypto.Protocol.KDF import PBKDF2 from Crypto.Hash import SHA256

MAGIC = b"PYENCv1!" SALT_LEN = 16 NONCE_LEN = 12 TAG_LEN = 16 PBKDF2_ITERS = 200_000

def derive_key(password: str, salt: bytes) -> bytes: return PBKDF2(password.encode('utf-8'), salt, dkLen=32, count=PBKDF2_ITERS, hmac_hash_module=SHA256)

def decrypt_file(inpath, outpath, password): with open(inpath, 'rb') as f: magic = f.read(len(MAGIC)) if magic != MAGIC: raise SystemExit("Invalid encrypted file header.") salt = f.read(SALT_LEN) nonce = f.read(NONCE_LEN) rest = f.read() ciphertext = rest[:-TAG_LEN] tag = rest[-TAG_LEN:] key = derive_key(password, salt) cipher = AES.new(key, AES.MODE_GCM, nonce=nonce) plaintext = cipher.decrypt_and_verify(ciphertext, tag) with open(outpath, 'wb') as fo: fo.write(plaintext) print(f"Restored -> {outpath}")

def main(): p = argparse.ArgumentParser() p.add_argument('-i','--input', required=True) p.add_argument('-o','--output', required=True) args = p.parse_args() pw = getpass("Password: ") decrypt_file(args.input, args.output, pw)

if name == "main": main()</code></pre> <p>Then run:</p> <pre><code class="cmd">python3 decrypt_restore.py -i run_encrypted.py -o run_encrypted_restored.py</code></pre> <p>If you enter the correct password, you’ll get your restored Python file.</p> </div>

<div class="section">
    <h2>4. Encryptor Script: <code>encrypt_script.py</code></h2>
    <pre><code>#!/usr/bin/env python3

"""Encrypt Python file""" import argparse, os, sys from getpass import getpass from Crypto.Cipher import AES from Crypto.Protocol.KDF import PBKDF2 from Crypto.Hash import SHA256 from Crypto.Random import get_random_bytes

MAGIC = b"PYENCv1!" SALT_LEN = 16 NONCE_LEN = 12 TAG_LEN = 16 PBKDF2_ITERS = 200_000

def derive_key(password: str, salt: bytes) -> bytes: return PBKDF2(password.encode('utf-8'), salt, dkLen=32, count=PBKDF2_ITERS, hmac_hash_module=SHA256)

def encrypt_file(inpath, outpath, password): with open(inpath, 'rb') as f: plaintext = f.read() salt = get_random_bytes(SALT_LEN) key = derive_key(password, salt) nonce = get_random_bytes(NONCE_LEN) cipher = AES.new(key, AES.MODE_GCM, nonce=nonce) ciphertext, tag = cipher.encrypt_and_digest(plaintext) with open(outpath, 'wb') as fo: fo.write(MAGIC + salt + nonce + ciphertext + tag) print(f"Encrypted {inpath} -> {outpath}")

def main(): p = argparse.ArgumentParser() p.add_argument('-i','--input', required=True) p.add_argument('-o','--output', required=True) args = p.parse_args() if os.path.abspath(args.input) == os.path.abspath(args.output): sys.exit("Error: input and output must differ.") pw = getpass("Password: ") encrypt_file(args.input, args.output, pw)

if name == "main": main()</code></pre> </div>

<div class="section">
    <h2>5. Runner Script: <code>run_encrypted.py</code></h2>
    <pre><code>#!/usr/bin/env python3

import argparse, os, sys from getpass import getpass from Crypto.Cipher import AES from Crypto.Protocol.KDF import PBKDF2 from Crypto.Hash import SHA256

MAGIC = b"PYENCv1!" SALT_LEN = 16 NONCE_LEN = 12 TAG_LEN = 16 PBKDF2_ITERS = 200_000

def derive_key(password: str, salt: bytes) -> bytes: return PBKDF2(password.encode('utf-8'), salt, dkLen=32, count=PBKDF2_ITERS, hmac_hash_module=SHA256)

def run_encrypted(path, password): with open(path, 'rb') as f: magic = f.read(len(MAGIC)) if magic != MAGIC: raise ValueError("Invalid encrypted file.") salt = f.read(SALT_LEN) nonce = f.read(NONCE_LEN) rest = f.read() ciphertext = rest[:-TAG_LEN] tag = rest[-TAG_LEN:] key = derive_key(password, salt) cipher = AES.new(key, AES.MODE_GCM, nonce=nonce) plaintext = cipher.decrypt_and_verify(ciphertext, tag) exec(compile(plaintext.decode('utf-8'), '<decrypted>', 'exec'), {'name': 'main'})

def main(): p = argparse.ArgumentParser() p.add_argument('-i','--input', required=True) args = p.parse_args() pw = getpass("Password: ") run_encrypted(args.input, pw)

if name == "main": main()</code></pre> </div>

<div class="section">
    <h2>6. Safety Tips</h2>
    <ul>
        <li>Never use same file for input & output.</li>
        <li>Always keep backups.</li>
        <li>Test encryption on a copy first.</li>
        <li>If sharing, provide <code>run_encrypted.py</code> separately.</li>
    </ul>
</div>

</body>
</html>
