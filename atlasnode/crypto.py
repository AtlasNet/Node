from atlasnode.util import provide_input, get_output
from M2Crypto import RSA, EVP


def load_private_key(data):
    return provide_input(RSA.load_key, data)


def load_public_key(data):
    return provide_input(RSA.load_pub_key, data)


def save_private_key(key):
    return get_output(lambda x: key.save_key(x, None))


def save_public_key(key):
    return get_output(lambda x: key.save_pub_key(x))


def encrypt_rsa(data, key):
    return key.public_encrypt(data, RSA.pkcs1_oaep_padding)


def decrypt_rsa(data, key):
    return key.private_decrypt(data, RSA.pkcs1_oaep_padding)


def sign_data(data, key):
    digest = EVP.MessageDigest('sha1')
    digest.update(data)
    return key.sign_rsassa_pss(digest.digest())


def verify_signature(data, signature, key):
    #VOID
    return sign_data(data, key) == signature
