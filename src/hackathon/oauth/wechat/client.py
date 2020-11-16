from hackathon.utils.httpclient import BaseClient

# https://api.weixin.qq.com/sns/oauth2/access_token?appid=APPID&secret=SECRET&code=CODE&grant_type=authorization_code
ACCESS_TOKEN_URL = "https://api.weixin.qq.com/sns/oauth2/access_token"
# https://api.weixin.qq.com/sns/userinfo?access_token=TOKEN&openid=OPENID"
USER_INFO_URL = "https://api.weixin.qq.com/sns/userinfo"


class HttpClient(BaseClient):
    pass
