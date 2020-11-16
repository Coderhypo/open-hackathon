from hackathon.utils.httpclient import BaseClient

USER_INFO_URL = "https://api.weibo.com/2/users/show.json?access_token="
EMAIL_INFO_URL = "https://api.weibo.com/2/account/profile/email.json?access_token="

# https://api.weibo.com/oauth2/access_token?client_id=CLIENTID&client_secret=SECRET&grant_type=authorization_code&redirect_uri=URI&code=CODE"
ACCESS_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"


class HttpClient(BaseClient):
    pass
