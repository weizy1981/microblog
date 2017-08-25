import urllib
import hashlib
import random
import http
from app import app

def translate(text, destLang='zh'):
    appid = app.config['BAIDU_APP_ID']
    secretKey = app.config['BAIDU_APP_KEY']
    res_value = ''
    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = text
    fromLang = 'auto'
    toLang = destLang
    salt = random.randint(32768, 65536)

    sign = appid + q + str(salt) + secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode('utf-8'))
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        results = response.read().decode('utf-8').split(':')[5]
        result = results.split('}')[0]
        res_value = result.encode('latin-1').decode('unicode_escape')

    except Exception as e:
        print(e)

    finally:
        if httpClient:
            httpClient.close()

        return res_value
