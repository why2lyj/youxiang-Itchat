# coding=utf-8
"""
首先要感谢下这篇文章：
https://www.jianshu.com/p/f9b5e3020789

值得看的一篇文章：
http://g.alicdn.com/tmapp/tida-doc/docs/top/00API%E8%B0%83%E7%94%A8%E8%AF%B4%E6%98%8E.html

"""
import hashlib
import json
import random
import time
import urllib
import urllib.parse
import urllib.request

TB_API_ROOT = 'http://gw.api.taobao.com/router/rest?'

class TbApiClient(object):

    def __init__(self, app_key, secret_key, adzone_id):
        self.app_key = app_key
        self.secret_key = secret_key
        self.adzone_id = adzone_id

    #排序
    def ksort(self, d):
        return [(k, d[k]) for k in sorted(d.keys())]

    #MD5加密
    def md5(self, s, raw_output=False):
        """Calculates the md5 hash of a given string"""
        res = hashlib.md5(s.encode())
        if raw_output:
            return res.digest()
        return res.hexdigest()

    #计算sign
    def createSign(self, paramArr):
        sign = self.secret_key
        paramArr = self.ksort(paramArr)
        paramArr = dict(paramArr)
        for k, v in paramArr.items():
            if k != '' and v != '':
                sign += k + v
        sign += self.secret_key
        sign = self.md5(sign).upper()
        return sign

    #参数排序
    def createStrParam(self, paramArr):
        strParam = ''
        for k, v in paramArr.items():
            if k != '' and v != '':
                strParam += k + '=' + urllib.parse.quote_plus(v) + '&'
        return strParam

    #高效API调用示例
    def taobao_tbk_dg_optimus_material(self, material_id: str):
        '''
        通用物料推荐，传入官方公布的物料id，可获取指定物料
        淘宝接口文档：
        http://bigdata.taobao.com/api.htm?spm=a219a.7386797.0.0.4ad5669aWaaQFi&source=search&docId=33947&docType=2

        :param material_id:  详见https://market.m.taobao.com/app/qn/toutiao-new/index-pc.html#/detail/10628875?_k=gpov9a
        :param adzone_id:  广告位
        :return:
        '''
        # 请求参数，根据API文档修改
        # TODO
        # 把分页现在这里随机有一定考虑
        # 原因是：1. 不同 material_id 得到的数据不一，且刷新周期不一
        #                    2. 微信发送不可太频繁，我仅是怕被封，决定取很小一部分数据
        page_no = str(random.choices(['1','2','3','4', '5', '6', '7', '8', '9'])[0])
        page_size = str(random.randint(8, 10))

        postparm = {
                    'page_no': page_no,
                    'page_size': page_size,
                    'adzone_id': self.adzone_id,
                    'material_id': material_id,
                    'method': 'taobao.tbk.dg.optimus.material'
                    }
        # 公共参数，一般不需要修改
        paramArr = {'app_key': self.app_key,
                    'v': '2.0',
                    'sign_method': 'md5',
                    'format': 'json',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }

        paramArr = {**paramArr, **postparm}
        sign = self.createSign(paramArr)
        strParam = self.createStrParam(paramArr)
        strParam += 'sign=' + sign
        url = TB_API_ROOT + strParam
        print(url)
        res = urllib.request.urlopen(url).read()
        return res

    def taobao_tbk_tpwd_create(self, text: str, url: str):
        '''
        提供淘客生成淘口令接口，淘客提交口令内容、logo、url等参数，生成淘口令关键key如：￥SADadW￥，后续进行文案包装组装用于传播
        淘宝接口文档：
        http://bigdata.taobao.com/api.htm?spm=a219a.7386797.0.0.494b669atcwg9a&source=search&docId=31127&docType=2

        :param text: 口令弹框内容
        :param url: 口令跳转目标页
        :return: 返回淘口令，如<￥SADadW￥>
        '''

        postparm = {
                    'text': text,
                    'url': url,
                    'method': 'taobao.tbk.tpwd.create'
                    }
        # 公共参数，一般不需要修改
        paramArr = {'app_key': self.app_key,
                    'v': '2.0',
                    'sign_method': 'md5',
                    'format': 'json',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }

        paramArr = {**paramArr, **postparm}
        sign = self.createSign(paramArr)
        strParam = self.createStrParam(paramArr)
        strParam += 'sign=' + sign
        url = TB_API_ROOT + strParam
        res = urllib.request.urlopen(url).read()
        tao_command = json.loads(res)['tbk_tpwd_create_response']['data']['model']
        return tao_command

    def tkl_parser(self, tkl):
        '''
        :param tkl: str 淘口令，例如 ￥ABCDEFG￥
        :return: str  返回自己的淘口令
        '''
        # 取值地址，接口地址
        url = f'''http://www.taofake.com/index/tools/gettkljm.html?tkl={urllib.parse.quote(tkl)}'''
        # 伪装定义浏览器header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

        request = urllib.request.Request(url=url, headers=headers)
        response = urllib.request.urlopen(request)
        data = response.read()
        return self.taobao_tbk_tpwd_create(json.loads(data)['data']['content'], json.loads(data)['data']['url'])
