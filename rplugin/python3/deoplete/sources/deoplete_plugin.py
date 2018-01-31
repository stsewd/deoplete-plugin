import json
import re
from urllib import request

from .base import Base


def get_repos(user):
    base_url = 'https://api.github.com/users/{user}/repos'.format(
        user=user
    )
    with request.urlopen(base_url) as r:
        raw_response = r.read().decode('utf-8')
        json_response = json.loads(raw_response)
        return [
            repo['name']
            for repo in json_response
        ]
    return []


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'plugin'
        self.mark = '[P]'
        self.filetypes = ['vim']
        self.input_pattern = r'(Plug)\s+\'(.+)/'

    def get_complete_position(self, context):
        m = re.search(self.input_pattern, context['input'])
        return m.end() if m else -1

    def gather_candidates(self, context):
        input_text = context['input']
        m = re.search(self.input_pattern, input_text)
        user = m.group(2)
        return get_repos(user)
