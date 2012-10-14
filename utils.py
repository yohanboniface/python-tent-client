import hmac
import time
import string
import pprint
import random
import hashlib
import requests

from base64 import b64encode

from colors import blue, yellow, red, cyan, magenta, green, white
from exception import ConnectionFailure

# Set this to True to get a ton of debugging info printed to the screen
debug = True
retries = 10


def debugAuth(s=''):
    if debug:
        print blue('%s' % s)


def debugMain(s=''):
    if debug:
        print yellow('%s' % s)


def debugError(s=''):
    if debug:
        print red('ERROR: %s' % s)


def debugDetail(s=''):
    if debug:
        print cyan('    %s' % s)


def debugJson(s=''):
    if debug:
        print magenta(pprint.pformat(s))


def debugRequest(s=''):
    if debug:
        print green(' >> %s' % s)


def debugRaw(s=''):
    if debug:
        print white('>       ' + s.replace('\n', '\n>       '))


def randomString():
    return ''.join([random.choice(string.letters + string.digits) for x in xrange(20)])


def removeUnicode(s):
    if type(s) == unicode:
        return s.encode('utf8')
    return s


def buildHmacSha256AuthHeader(mac_key_id, mac_key, method, resource, hostname, port):
    """Return an authentication header as per
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01
    """
    debugMain('HMAC SHA 256')
    debugDetail('mac key id: %s' % repr(mac_key_id))
    debugDetail('mac key: %s' % repr(mac_key))

    timestamp = int(time.time())
    nonce = randomString()

    msg = '\n'.join([
        str(timestamp),
        nonce,
        method,
        resource,
        hostname,
        str(port),
        '',
        ''
    ])
    debugDetail('input to hash: ' + repr(msg))
    debugRaw(msg)

    digest = hmac.new(removeUnicode(mac_key), removeUnicode(msg), hashlib.sha256).digest()
    mac = removeUnicode(b64encode(digest).decode())  # this produces unicode for some reason
    authHeader = 'MAC id="%s" ts="%s" nonce="%s" mac="%s"' % (removeUnicode(mac_key_id), timestamp, nonce, mac)
    debugDetail('auth header:')
    debugRaw(authHeader)
    return authHeader


def retry(method, *args, **kwargs):
    for ii in range(retries):
        try:
            return method(*args, **kwargs)
        except requests.exceptions.HTTPError:
            debugError('http error.  retrying... (that was attempt %s of %s)' % (ii, retries))
        except requests.exceptions.ConnectionError:
            debugError('connection error.  retrying... (that was attempt %s of %s)' % (ii, retries))
        time.sleep(1)
    print 'tried too many times'
    raise ConnectionFailure
