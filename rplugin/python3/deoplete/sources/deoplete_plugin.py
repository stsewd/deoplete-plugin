import json
import re
from urllib import request
from urllib.error import HTTPError

from .base import Base


REPOS_PER_PAGE = 20


class Source(Base):

    def __init__(self, vim):
        Base.__init__(self, vim)

        self.name = 'plugin'
        self.mark = '[P]'
        self.filetypes = ['vim']
        self.input_pattern = r'(Plug)\s+\'(.+)/'
        self._current_page = 1

    def get_complete_position(self, context):
        m = re.search(self.input_pattern, context['input'])
        return m.end() if m else -1

    def _get_repo_endpoint(self, user, page):
        return (
            'https://api.github.com/users/{user}/repos'
            '?page={page}&per_page={per_page}'.format(
                user=user,
                page=page,
                per_page=REPOS_PER_PAGE
            )
        )

    def _get_repos(self, user, page):
        base_url = self._get_repo_endpoint(user, page)
        try:
            r = request.urlopen(base_url)
            raw_response = r.read().decode('utf-8')
            json_response = json.loads(raw_response)
            return [
                {
                    'word': repo['name'],
                    'menu': repo['description'],
                }
                for repo in json_response
            ]
        except HTTPError as e:
            if e.code == 403:
                self.print('API rate limit exceeded')
        except Exception as e:
            pass
        return []

    def _get_user(self, text):
        m = re.search(self.input_pattern, text)
        return m.group(2)

    def gather_candidates(self, context):
        input_text = context['input']
        user = self._get_user(input_text)
        repos = self._get_repos(user, self._current_page)
        self._current_page += 1
        context['is_async'] = bool(repos)
        return repos
