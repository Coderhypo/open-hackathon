# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""
import os
import yaml


class ConfigException(Exception):
    pass


WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = "{}/conf".format(WORK_DIR)
PROJECT_DIR = "{}/hackathon".format(WORK_DIR)
RESOURCE_DIR = "{}/resource".format(WORK_DIR)


class _DatabaseConfig:
    MONGODB_HOST = os.getenv("DB_SERVER", "localhost")
    MONGODB_PORT = int(os.getenv("DB_PORT", "27017"))
    MONGODB_DB = os.getenv("DB_DBNAME", "hackathon")

    def __init__(self, config_data):
        self.MONGODB_HOST = os.getenv("DB_SERVER") or config_data.get("server")
        self.MONGODB_PORT = int(os.getenv("DB_PORT") or str(config_data.get("port")))
        self.MONGODB_DB = os.getenv("DB_DBNAME") or config_data.get("dbname")


oauth_providers = ["DIRECT", "AUTHING"]


class _OAuthConfig:
    ENABLE_OAUTH = False
    PROVIDER = "AUTHING"

    # authing config
    AUTHING_CLIENT_ID = os.getenv("AUTHING_CLIENT_ID")
    AUTHING_STATE = os.getenv("AUTHING_STATE")

    # github oauth
    ENABLE_GITHUB_OAUTH = False
    GITHUB_CLIENT_ID = ""
    GITHUB_CLIENT_SECRET = ""

    # qq oauth
    ENABLE_QQ_OAUTH = False
    QQ_CLIENT_ID = ""
    QQ_CLIENT_SECRET = ""
    QQ_META_CONTENT = ""
    QQ_OAUTH_STATE = ""

    # wx oauth
    ENABLE_WECHAT_OAUTH = False
    WECHAT_APP_ID = ""
    WECHAT_SECRET = ""
    WECHAT_OAUTH_STATE = ""

    # wb oauth
    ENABLE_WEIBO_OAUTH = False
    WEIBO_CLIENT_ID = ""
    WEIBO_CLIENT_SECRET = ""
    WEIBO_META_CONTENT = ""

    # live oauth
    ENABLE_LIVE_OAUTH = False
    LIVE_CLIENT_ID = ""
    LIVE_CLIENT_SECRET = ""

    TOKEN_VALID_TIME_MINUTES = 60

    def __init__(self, config_data):
        self.ENABLE_OAUTH = config_data.get("enable", False)
        self.PROVIDER = config_data.get("provider")

        if self.PROVIDER not in oauth_providers:
            raise ConfigException("oauth provider {} not support yet".format(self.PROVIDER))

        if self.PROVIDER == "DIRECT":
            if config_data.get("enable_github", False):
                github_cfg = config_data["github"]
                self.ENABLE_GITHUB_OAUTH = True
                self.GITHUB_CLIENT_ID = github_cfg["client_id"]
                self.GITHUB_CLIENT_SECRET = github_cfg["client_secret"]

            if config_data.get("enable_qq", False):
                qq_cfg = config_data["qq"]
                self.ENABLE_QQ_OAUTH = True
                self.QQ_CLIENT_ID = qq_cfg["client_id"]
                self.QQ_CLIENT_SECRET = qq_cfg["client_secret"]
                self.QQ_META_CONTENT = qq_cfg["meta_content"]
                self.QQ_OAUTH_STATE = qq_cfg["state"]

            if config_data.get("enable_webchat", False):
                wx_cfg = config_data["wechat"]
                self.ENABLE_WECHAT_OAUTH = True
                self.WECHAT_APP_ID = wx_cfg["app_id"]
                self.WECHAT_SECRET = wx_cfg["secret"]
                self.WECHAT_OAUTH_STATE = wx_cfg["state"]

            if config_data.get("enable_webbo", False):
                wb_cfg = config_data["weibo"]
                self.ENABLE_WEIBO_OAUTH = True
                self.WEIBO_CLIENT_ID = wb_cfg["client_id"]
                self.WEIBO_CLIENT_SECRET = wb_cfg["client_secret"]
                self.WEIBO_META_CONTENT = wb_cfg["meta_content"]

            if config_data.get("enable_live", False):
                live_cfg = config_data["live"]
                self.ENABLE_LIVE_OAUTH = True
                self.LIVE_CLIENT_ID = live_cfg["client_id"]
                self.LIVE_CLIENT_SECRET = live_cfg["client_secret"]

        if self.PROVIDER == "AUTHING":
            authing_cfg = config_data["authing"]
            self.AUTHING_CLIENT_ID = authing_cfg["client_id"]
            self.AUTHING_STATE = authing_cfg["state"]

        # disable all direct oauth
        self.ENABLE_GITHUB_OAUTH = False
        self.ENABLE_QQ_OAUTH = False
        self.ENABLE_WECHAT_OAUTH = False
        self.ENABLE_WEIBO_OAUTH = False
        self.ENABLE_LIVE_OAUTH = False


class _GuacamoleConfig:
    HOST = "guacamole"
    PORT = 8080

    def __init__(self, config_data):
        self.HOST = config_data["host"]
        self.PORT = config_data["port"]


storage_types = ["s3", "minio", "local"]


class _StorageConfig:
    TYPE = "local"
    SIZE_LIMIT_KILO_BYTES = 5 * 1024

    def __init__(self, config_data):
        self.TYPE = config_data["type"]
        if self.TYPE not in storage_types:
            raise ConfigException("storage type {} not support yet".format(self.TYPE))
        self.SIZE_LIMIT_KILO_BYTES = config_data["size_limit_kilo_bytes"]


voice_verify_providers = ["rong_lian"]
sms_providers = ["china_telecom"]


class _NotifyConfig:
    # smtp config
    ENABLE_SMTP = False
    SMTP_HOST = ""
    SMTP_PORT = 587
    SMTP_DEFAULT_SENDER = ""
    SMTP_RECEIVERS_FORCED = []
    SMTP_USERNAME = ""
    SMTP_PASSWORD = ""

    # voice config
    ENABLE_VOICE_VERIFY = False
    VOICE_VERIFY_PROVIDER = "rong_lian"

    # https://www.yuntongxun.com/
    RONG_LIAN_ACCOUNT_SID = ""
    RONG_LIAN_AUTH_TOKEN = ""
    RONG_LIAN_APP_ID = ""
    RONG_LIAN_SERVER_IP = "https://app.cloopen.com"
    RONG_LIAN_SERVER_PORT = "8883"
    RONG_LIAN_SOFT_VERSION = "2013-12-26"
    RONG_LIAN_PLAY_TIMES = 3
    RONG_LIAN_DISPLAY_NUMBER = ""
    RONG_LIAN_RESPONSE_URL = ""
    RONG_LIAN_LANGUAGE = "zh"

    # sms config
    ENABLE_SMS = False,
    SMS_PROVIDER = "china_telecom"

    # http://www.189.cn/
    CHINA_TELECOM_URL = "http://api.189.cn/v2/emp/templateSms/sendSms"
    CHINA_TELECOM_APP_ID = ""
    CHINA_TELECOM_APP_SECRET = ""
    CHINA_TELECOM_URL_ACCESS_TOKEN = "https://oauth.api.189.cn/emp/oauth2/v3/access_token"

    def __init__(self, config_data):
        if config_data.get("enable_smtp", False):
            smtp_cfg = config_data["smtp"]
            self.ENABLE_SMTP = True
            self.SMTP_HOST = smtp_cfg["host"]
            self.SMTP_PORT = smtp_cfg["port"]
            self.SMTP_DEFAULT_SENDER = smtp_cfg["default_sender"]
            self.SMTP_RECEIVERS_FORCED = smtp_cfg["receivers_forced"]
            self.SMTP_USERNAME = smtp_cfg["username"]
            self.SMTP_PASSWORD = smtp_cfg["password"]

        if config_data.get("enable_voice_verify", False):
            self.ENABLE_VOICE_VERIFY = True
            self.VOICE_VERIFY_PROVIDER = config_data["voice_verify_privider"]
            if self.VOICE_VERIFY_PROVIDER not in voice_verify_providers:
                raise ConfigException("voice verify provider {} not support yet".format(self.VOICE_VERIFY_PROVIDER))

            voice_cfg = config_data[self.VOICE_VERIFY_PROVIDER]
            if self.VOICE_VERIFY_PROVIDER == "rong_lian":
                self.RONG_LIAN_ACCOUNT_SID = voice_cfg["account_sid"]
                self.RONG_LIAN_AUTH_TOKEN = voice_cfg["auth_token"]
                self.RONG_LIAN_APP_ID = voice_cfg["app_id"]
                self.RONG_LIAN_SERVER_IP = voice_cfg["server_url"]
                self.RONG_LIAN_SERVER_PORT = voice_cfg["server_port"]
                self.RONG_LIAN_SOFT_VERSION = voice_cfg["soft_version"]
                self.RONG_LIAN_PLAY_TIMES = voice_cfg["play_time"]
                self.RONG_LIAN_DISPLAY_NUMBER = voice_cfg["display_number"]
                self.RONG_LIAN_RESPONSE_URL = voice_cfg["response_url"]
                self.RONG_LIAN_LANGUAGE = voice_cfg["language"]

        if config_data.get("enable_sms", False):
            self.ENABLE_SMS = True
            self.SMS_PROVIDER = config_data["sms_privider"]
            if self.SMS_PROVIDER not in sms_providers:
                raise ConfigException("sms provider {} not support yet".format(self.SMS_PROVIDER))

            sms_cfg = config_data[self.SMS_PROVIDER]
            if self.SMS_PROVIDER == "china_telecom":
                self.CHINA_TELECOM_URL = sms_cfg["server_url"]
                self.CHINA_TELECOM_APP_ID = sms_cfg["app_id"]
                self.CHINA_TELECOM_APP_SECRET = sms_cfg["app_secret"]
                self.CHINA_TELECOM_URL_ACCESS_TOKEN = sms_cfg["access_token"]


class _FeatureConfig:
    # oauth feature switch
    ENABLE_GITHUB_OAUTH = False
    ENABLE_QQ_OAUTH = False
    ENABLE_WECHAT_OAUTH = False
    ENABLE_WEIBO_OAUTH = False
    ENABLE_LIVE_OAUTH = False


class BaseConfig:
    DEBUG = False
    SERVER_ENDPOINT = "http://localhost:15000"

    FEATURE = _FeatureConfig()

    def __init__(self,
                 db_cfg: _DatabaseConfig,
                 oauth_cfg: _OAuthConfig,
                 storage_cfg: _StorageConfig,
                 notify_cfg: _NotifyConfig,
                 guacamole_cfg: _GuacamoleConfig):
        self.DATABASE = db_cfg
        self.OAUTH = oauth_cfg
        self.STORAGE = storage_cfg
        self.NOTIFY = notify_cfg
        self.GUACAMOLE = guacamole_cfg


class DevConfig(BaseConfig):
    env_name = "develop"
    DEBUG = True
    SECRET_KEY = "secret_key"


class StageConfig(BaseConfig):
    env_name = "stage"
    DEBUG = True
    SECRET_KEY = "secret_key"


class ProdConfig(BaseConfig):
    env_name = "prod"
    SECRET_KEY = os.getenv("SECRET_KEY")


configs = {
    DevConfig.env_name: DevConfig,
    StageConfig.env_name: StageConfig,
    ProdConfig.env_name: ProdConfig,
}


def load_config():
    config_file = "{}/config.yaml".format(CONFIG_DIR)
    env_name = os.getenv("ENVNAME")
    try:
        file = open(config_file, "r")
        config_data = yaml.safe_load(file)
    except Exception as e:
        raise ConfigException("read config file {} failed: {}", format(config_file, str(e)))

    current = configs.get(env_name, ProdConfig.env_name)
    if not current:
        raise ConfigException("env config not found: {}".format(env_name))

    try:
        db_cfg = _DatabaseConfig(config_data.get("db"))
        oauth_cfg = _OAuthConfig(config_data.get("oauth"))
        storage_cfg = _StorageConfig(config_data.get("storage"))
        notify_cfg = _NotifyConfig(config_data.get("notify"))
        guacamole_cfg = _GuacamoleConfig(config_data.get("guacamole"))
        cfg = current(
            db_cfg=db_cfg,
            oauth_cfg=oauth_cfg,
            storage_cfg=storage_cfg,
            notify_cfg=notify_cfg,
            guacamole_cfg=guacamole_cfg)
        cfg.SERVER_ENDPOINT = config_data["server_endpoint"]
        cfg.DEBUG = cfg.DEBUG or config_data.get("DEBUG", False)
    except KeyError as e:
        raise ConfigException("config file key not found: {}".format(e))

    return cfg


# init when startup
Config = load_config()


def reload_config():
    global Config
    Config = load_config()
