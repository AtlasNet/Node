import os
import tempfile


def get_output(fx):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.close()
    fx(f.name)
    content = open(f.name).read()
    os.unlink(f.name)
    return content

def provide_input(fx, data):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(data)
    f.close()
    result = fx(f.name)
    os.unlink(f.name)
    return result

def sanitize_key(pem):
    return pem.strip().replace('\r', '')
