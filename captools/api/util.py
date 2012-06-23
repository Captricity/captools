import os
from urllib import urlencode
from hashlib import sha256

def generate_request_access_signature(parameters, secret_key):
    """
    Generate the parameter signature used during third party access requests
    """
    # pull out the parameter keys
    keys = parameters.keys()

    # alphanumerically sort the keys in place
    keys.sort()

    # create an array of url encoded key:value pairs
    encoded_pairs = [urlencode({key:parameters[key]}) for key in keys] 

    # create the serialized parameters in a single, URL style string
    serialized_parameters = '&'.join(encoded_pairs)

    # create the string with the secret key and the parameters which will be hashed
    string_to_hash = '%s:%s' % (secret_key, serialized_parameters)

    # return the hex digest of the hashed string
    return sha256(string_to_hash).hexdigest()

_example_form_image_paths = ['page1.png', 'page2.png']
_example_form_image_paths = map(
        lambda x: os.path.join(os.path.dirname(__file__), 'img', x),
        _example_form_image_paths)
example_form_image_paths = map(lambda x: os.path.abspath(x), _example_form_image_paths)
