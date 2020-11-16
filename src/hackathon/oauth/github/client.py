from hackathon.utils.httpclient import BaseClient

ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
USER_INFO_URL = 'https://api.github.com/user'
EMAILS_INFO_URL = 'https://api.github.com/user/emails'


class HttpClient(BaseClient):
    pass
