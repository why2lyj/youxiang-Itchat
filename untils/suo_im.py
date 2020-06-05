# coding=utf-8
"""

"""
import json
import urllib
import urllib.parse
import urllib.request
import datetime

class Suo_mi(object):
    '''
    需要注册 http://suo.im/ ， 而后获得 key
    '''

    def __init__(self, app_key):
        self.app_key = app_key
        # 我们默认短址一年后过期
        self.expireDate = (datetime.date.today() + datetime.timedelta(days=365)).strftime('%Y-%m-%d')

    def get_short_url(self, url: str)  -> str:
        '''
        :param url: 长址
        :return: 返回suo.im的短址
        '''
        # 取值地址，接口地址
        api_url = f'''http://suo.im/api.htm?format=json&url={urllib.parse.quote(url)}&key={self.app_key}&expireDate={self.expireDate}'''
        request = urllib.request.Request(url=api_url)
        response = urllib.request.urlopen(request)
        data = response.read()
        short_url = json.loads(data)['url']
        return short_url

if __name__ == '__main__':

    # example
    url = 'https://union-click.jd.com/jdc?e=&p=AyIGZRtcFAsRAlEfWxQyEg9QGlIQBxAPUhNrUV1KWQorAlBHU0VeBUVOWk1RAk8ECllHGAdFBwtaV1MJBAJQXk8JF0EfGQIaAlQSXhAAGgBdDBsZdmtdPGwoFUJlbilLL0xLRXA8azxhW0dEIkMnRWETb1NsOXJxZnM2WS9KVHV%2BJhscYQBmYSFSMFVhe3MNbBJARWZuMXssTHFFYB18JHV2YkUCTTBecVtOEGwDbVJyZCZbLE12dGQMb15ja0RULH8oVXVNVQVsP2kFcW4maDthcVd%2FLG8%2FYUttWyFiK3d1cGdBGS4le3V5LHsaHUFwbCMdMHF6blwrQyNRch4LZR5aFAMSDlYfWBIyEgZUGFIQBxEGUCtrFQMiRjscXREKEQJlGmsVBhoHVRxYHAMaD1wTaxUKFjcNRgVSVktTBVwPSjIiN1YrayUCETdWKwV7A0EHXRwORgF8XQVTEh0GUQY7GF4RChMCXB1rFwMTBVc%3D'
    print(urllib.parse.quote(url))
    app_key = ''
    c = Suo_mi(app_key).get_short_url(url)
    print(c)

