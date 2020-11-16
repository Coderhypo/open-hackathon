from hackathon.utils.httpclient import BaseClient

# https://graph.qq.com/oauth2.0/token?state=openhackathon&grant_type=authorization_code&client_id=CLIENTID&client_secret=SECRET&redirect_uri=%%s&code=%%s'
ACCESS_TOKEN_URL = "https://graph.qq.com/oauth2.0/token"
OPENID_URL = "https://graph.qq.com/oauth2.0/me?access_token="
# https://graph.qq.com/user/get_user_info?access_token=TOKEN&oauth_consumer_key=KEY&openid=OPENID
USER_INFO_URL = "https://graph.qq.com/user/get_user_info"


class HttpClient(BaseClient):
    pass
