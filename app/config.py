import os
basedir = os.path.abspath(os.path.dirname(__file__))

# 数据库链接设置
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'microblog.db')

CSRF_ENABLED = True
# SECRET_KEY设置当CSRF启用时有效，这将生成一个加密的token供表单验证使用，你要确保这个KEY足够复杂不会被简单推测。
SECRET_KEY = 'you-will-never-guess'

# 文件上传目录
UPLOAD_FOLDER = os.path.join(basedir, 'static/resources')

# email server
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'youuserid'
MAIL_PASSWORD ='yourpassword'

# administrator list
ADMINS = ['1553291835@qq.com']


# log文件
LOG_FILE = os.path.join(basedir, 'tmp/microblog.log')

# 每页显示条数
POSTS_PER_PAGE = 3

# 全文检索
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 10

# 多语言配置
LANGUAGES = {
    'en' : 'English',
    'zh' : '中文'
}

BAIDU_APP_ID = 'your appid'
BAIDU_APP_KEY = 'your secret'


