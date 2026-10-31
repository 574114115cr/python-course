# ll_project/settings.py（末尾）
LOGIN_REDIRECT_URL = "learning_logs:index"   # 登录成功：去主页
LOGOUT_REDIRECT_URL = "learning_logs:index"  # 注销之后：回主页
LOGIN_URL = "accounts:login"                 # 被门禁拦下时：送到登录页
