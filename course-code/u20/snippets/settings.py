# settings.py（片段）—— 三处改动
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # ① 紧跟 SecurityMiddleware，在其他中间件之前
    # ... 其余中间件
]

STATIC_ROOT = BASE_DIR / "staticfiles"              # ② collectstatic 汇总到这里

STORAGES = {                                        # ③ Django 4.2+ 的写法
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
