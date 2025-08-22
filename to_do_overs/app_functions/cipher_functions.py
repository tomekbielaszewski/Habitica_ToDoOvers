#!/usr/bin/env python
"""
Cipher functions for the Habitica To Do Over tool.
"""
from __future__ import print_function
from __future__ import absolute_import

__author__ = "Katie Patterson kirska.com"
__license__ = "MIT"

import os
import sys

# import argparse
from cryptography.fernet import Fernet

from .local_defines import CIPHER_FILE


def generate_cipher_key():
    """Generates a cipher key.

    Generates a cipher key to be used for storing
    sensitive data in the database.
    This will make all existing data GARBAGE so use with caution.
    """
    key = Fernet.generate_key()
    with open(CIPHER_FILE, "wb") as cipher_file:
        cipher_file.write(key)


def encrypt_text(text):
    """Encrypt some text using the cipher key.

    Read the cipher key from file and use it to encrypt some text.

    Args:
        text: the text to be encrypted.

    Returns:
        The encrypted text.
    """
    with open(CIPHER_FILE, "rb") as cipher_file:
        key = cipher_file.read()
        cipher_suite = Fernet(key)
        cipher_text = cipher_suite.encrypt(bytes(text, "utf-8"))
        return cipher_text


def decrypt_text(cipher_text, cipher_file_path=CIPHER_FILE):
    """Decrypt some text back into the plain text.

    Read the cipher key from file and use it to decrypt some text.

    Args:
        cipher_text: the encrypted text we want to decrypt.
        cipher_file_path: optional specification of path to file.

    Returns:
        The decrypted text.
    """
    with open(cipher_file_path, "rb") as cipher_file:
        key = cipher_file.read()
        cipher_suite = Fernet(key)
        if isinstance(cipher_text, str):
            cipher_text = cipher_text[2:-1]
            cipher_text = bytes(cipher_text, "utf-8")
        plain_text = cipher_suite.decrypt(cipher_text)
        return plain_text


def test_cipher(test_text):
    """Test the cipher functions.

    Encrypt and then decrypt some text using the cipher stored
    in the cipher file.

    Args:
        test_text: some plain text we want to test encrypting and decrypting.
    """
    cipher_text = encrypt_text(test_text)
    print(cipher_text)
    plain_text = decrypt_text(cipher_text)
    print(plain_text)


def ensure_cipher_file(path):
    """Ensure cipher.bin exists."""
    path = os.path.abspath(path)

    if not os.path.isfile(path):
        sys.stderr.write(
            "⚠️ Required cipher file not found: " + path + "\n"
        )
        generate_cipher_key()
        print("✅ New cipher file generated!\n")

    print("✅ Cipher file found in bind-mounted directory: " + path + "\n")

ensure_cipher_file(CIPHER_FILE)
