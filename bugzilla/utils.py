import base64
from ConfigParser import ConfigParser
import getpass
import os
import posixpath
import urllib


def urljoin(base, *args):
    """Remove any leading slashes so no subpaths look absolute."""
    return posixpath.join(base, *[str(s).lstrip('/') for s in args])


def qs(**kwargs):
    """Build a URL query string."""
    return '&'.join('%s=%s' % tuple(map(urllib.quote, map(str, pair)))
                    for pair in kwargs.items())


def get_credentials(username=None, api_key=None):

    # Try to get it from the environment first
    if not username:
        username = os.environ.get('BZ_USERNAME', None)
    password = os.environ.get('BZ_PASSWORD', None)
    if not api_key:
        api_key = os.environ.get('BZ_API_KEY', None)

    # Try to get it from the system keychain next 
    if not username and not password:
        try:
            import keyring
            if not username:
                # Grab the default username as we weren't passed in a specific one
                username = keyring.get_password('bugzilla', 'default_username')
            if username:
                # Get the password for the username
                password = keyring.get_password('bugzilla', username)
        except ImportError:
            # If they don't have the keyring lib, fall back to next method
            pass
    if not api_key:
        try:
            import keyring
            if not api_key:
                api_key = keyring.get_password('bugzilla', 'default_api_key')
        except ImportError:
            pass

    # Then try a config file in their home directory
    if not (username and password) and not api_key:
        rcfile = os.path.expanduser('~/.bztoolsrc')
        config = ConfigParser()
        config.add_section('bugzilla')
        if os.path.exists(rcfile):
            try:
                config.read(rcfile)
                api_key = config.get('bugzilla', 'api_key')
                username  = config.get('bugzilla', 'username')
                _password = config.get('bugzilla', 'password')
                if _password:
                    password = base64.b64decode(_password)
            except Exception:
                pass

    # Finally, prompt the user for the info if we didn't get it above
    if not (username and password) and not api_key:
        selection = '0'
        while True:
            selection = raw_input('1) Enter API Key\n2) Enter Username and Password\n> ')
            if selection == '1' or selection == '2':
                break
        # Enter API Key
        if selection == '1':
            api_key = raw_input('Bugzilla API Key: ')
            try:
                import keyring
                keyring.set_password('bugzilla', 'default_api_key', api_key)
            except ImportError:
                config.set('bugzilla', 'api_key', api_key)
                with open(rcfile, 'wb') as configfile:
                    config.write(configfile)
        # Enter Username and password
        elif selection == '2':
            username = raw_input('Bugzilla username: ')
            password = getpass.getpass('Bugzilla password: ')
            try:
                # Save the data to the keyring if possible
                import keyring
                keyring.set_password('bugzilla', 'default_username', username)
                keyring.set_password('bugzilla', username, password)
            except ImportError:
                # Otherwise save it to a config file
                config.set('bugzilla', 'username', username)
                config.set('bugzilla', 'password', base64.b64encode(password))
                with open(rcfile, 'wb') as configfile:
                    config.write(configfile)
    return username, password, api_key


def remove_credentials():
    try:
        import keyring
        username = keyring.get_password('bugzilla', 'default_username')
        if username:
            keyring.delete_password('bugzilla', username)
            keyring.delete_password('bugzilla', 'default_username')
        if keyring.get_password('bugzilla', 'default_api_key'):
            keyring.delete_password('bugzilla', 'default_api_key')
    except ImportError:
        rcfile = os.path.expanduser('~/.bztoolsrc')
        if os.path.isfile(rcfile):
            os.remove(rcfile)


FILE_TYPES = {
    'text':  'text/plain',
    'html':  'text/html',
    'xml':   'application/xml',
    'gif':   'image/gif',
    'jpg':   'image/jpeg',
    'png':   'image/png',
    'svg':   'image/svg+xml',
    'binary': 'application/octet-stream',
    'xul':    'application/vnd.mozilla.xul+xml',
}
