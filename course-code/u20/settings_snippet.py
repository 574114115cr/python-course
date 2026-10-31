# settings_snippet.py —— INTENTIONALLY-BROKEN 演示用：改错题，数据库配置连不通
from platformshconfig import Config

config = Config()
if config.is_valid_platform():
    db_settings = config.credentials('database')
    # 有 bug：引擎写死 SQLite，读来的 PostgreSQL 连接信息一个都没用
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'db.sqlite3'}}
