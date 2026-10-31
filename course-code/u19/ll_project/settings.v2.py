# ll_project/settings.py（末尾）—— 登录/注销/门禁三件事
LOGIN_REDIRECT_URL = "learning_logs:index"   # 登录成功去主页
LOGOUT_REDIRECT_URL = "learning_logs:index"  # 注销后回主页
LOGIN_URL = "accounts:login"                 # 被门禁拦下时送到登录页
