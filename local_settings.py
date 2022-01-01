from config import APP_CODE

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": APP_CODE,
        "USER": "root", #数据库用户名
        "PASSWORD": "root", #数据库密码
        "HOST": "localhost",
        "PORT": "3306",
    },
}