from bugzilla.models import *
from bugzilla.utils import *
import requests


class InvalidAPI_ROOT(Exception):
    def __str__(self):
        return "Invalid API url specified. " + \
               "Please set BZ_API_ROOT in your environment " + \
               "or pass it to the agent constructor"


class BugzillaAgent(object):
    def __init__(self, api_root=None, username=None, password=None, api_key=None):
        
        if not api_root:
            api_root = os.environ.get('BZ_API_ROOT')
            if not api_root:
                raise InvalidAPI_ROOT
        self.API_ROOT = api_root
        self.api_key = None
        self.token = None
        if api_key:
            self.api_key = api_key
        elif username and password:
            self.token = self.login(username, password).token

    def login(self, username, password):
        url = urljoin(self.API_ROOT, 'login?login={}&password={}'.format(username, password))
        return Login.get(url)

    def logout(self, token):
        url = urljoin(self.API_ROOT, 'logout?token={}'.format(token))
        Logout.get(url).deliver()

    def create_bug(self, params={}):
        """
        Ref: https://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#create-bug
        :return: {'id': int} or {'code': int, 'message': str, 'documentation': str, 'error', bool}
        """
        url = urljoin(self.API_ROOT, 'bug')
        res_json = self.post(url, params)
        return res_json

    def update_bug(self, bug_id, params={}):
        """
        Ref: https://bugzilla.readthedocs.io/en/latest/api/core/v1/bug.html#update-bug
        :return: {'bugs': [{'id': int, 'changes': obj, 'last_change_time': str, ...}, ...]} or {'code': int, 'message': str, 'documentation': str, 'error', bool}
        """
        url = urljoin(self.API_ROOT, 'bug/{}'.format(bug_id))
        res_json = self.put(url, params)
        return res_json

    def post(self, url, params):
        # ref: http://bugzilla.readthedocs.io/en/latest/api/core/v1/general.html#authentication
        if self.api_key:
            params['api_key'] = self.api_key
        elif self.token:
            params['token'] = self.token
        return requests.post(url, data=params).json()

    def put(self, url, params):
        # ref: http://bugzilla.readthedocs.io/en/latest/api/core/v1/general.html#authentication
        if self.api_key:
            params['api_key'] = self.api_key
        elif self.token:
            params['token'] = self.token
        return requests.put(url, data=params).json()

    def get_bug(self, bug, include_fields='_default,token,cc,keywords,whiteboard', exclude_fields=None, params={}):
        params['include_fields'] = include_fields
        params['exclude_fields'] = exclude_fields

        url = urljoin(self.API_ROOT, 'bug/%s?%s' % (bug, self.qs(**params)))
        print(url)
        return BugSearch.get(url).bugs

    def get_bug_list(self, params={}):
        url = urljoin(self.API_ROOT, 'bug?%s' % (self.qs(**params)))
        return BugSearch.get(url).bugs

    def qs(self, **params):
        # ref: http://bugzilla.readthedocs.io/en/latest/api/core/v1/general.html#authentication
        if self.api_key:
            params['api_key'] = self.api_key
        elif self.token:
            params['token'] = self.token
        return qs(**params)

    def __del__(self):
        if self.token:
            self.logout(self.token)


class BMOAgent(BugzillaAgent):
    def __init__(self, username=None, password=None):
        super(BMOAgent, self).__init__('https://api-dev.bugzilla.mozilla.org/latest/', username, password)
