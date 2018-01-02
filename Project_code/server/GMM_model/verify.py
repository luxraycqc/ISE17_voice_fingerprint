from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import pickle
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

keys = {}

def register_keyfile(username):
    """
    Register the private key for the given user for use in signing/decrypting.
    """
    f = "keys/{}-key.pem".format(username)    
    with open(f, "rb") as key_file:
        k=key_file.read()
        keys[username] = serialization.load_pem_private_key(
            k,
            password=None,
            backend=default_backend()
        )

def generate_key(username):
    """
    Ensure that a private/public keypair exists in username-key.pem for the
    given user. If it does not, create one, and store the private key on disk.
    Finally, return the user's PEM-encoded public key.
    """

    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend

    f = "keys/{}-key.pem".format(username)

    import os.path
    if not os.path.isfile(f):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )     

        pem = private_key.private_bytes(
           encoding=serialization.Encoding.PEM,
           format=serialization.PrivateFormat.TraditionalOpenSSL,
           encryption_algorithm=serialization.NoEncryption()
        )

        with open(f, "wb") as key_file:
            key_file.write(pem)

        public_key = private_key.public_key()
    else:
        with open(f, "rb") as key_file:
            public_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            ).public_key()

def rsa_decrypt(private_key, data):
    """
    Decrypt data with RSA
    """
    a = private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )
    return a

def rsa_encrypt(public_key, data):
    """
    Encrypt data with RSA
    """
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None
        )
    )

def generate_symmetric_key(encrypt_key):
    """
    Generates a symmetric key and the encrypted version using a user's or
    group's public key
    """
    key = Fernet.generate_key()
    encrypted_key = rsa_encrypt(encrypt_key, key)
    return key, encrypted_key


def decrypt_sym(key, data):
    """
    Decrypt the given data with the given key.
    """
    f = Fernet(key)
    blah = f.encrypt(b'a')
    return f.decrypt(data)

def encrypt_sym(key, data):
    """
    Encrypt the given data with the given key.
    """
    f = Fernet(key)
    return f.encrypt(data)

def get_public_key(username):
    f = "keys/{}-key.pem".format(username)
    with open(f, "rb") as key_file:
        public_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        ).public_key()
        return public_key

def get_private_key(username):
    return keys[username]

def hash(signal):
    return hashes.SHA256(signal)

def sign_wav(signal, username):
    register_keyfile(username)
    private_key = get_private_key(username)
    signer = private_key.signer(
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signer.update(signal)
    signature = signer.finalize()
    return signature

def verify_wav(signal, username, signature):
    public_key = get_public_key(username)
    verifier = public_key.verifier(
        signature,
        padding.PSS(
            mgf = padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    verifier.update(signal)
    return verifier.verify()