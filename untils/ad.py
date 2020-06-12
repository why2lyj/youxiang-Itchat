# coding=utf-8
"""
广告监测
"""
import pyzbar.pyzbar as pyzbar
from PIL import Image

def QRcode_detection(image: str) -> bool:
    '''
    判断图片是否存在二维码
    :param image: images的实际路径
    :return: True or False， True 说明发送图片有二维码信息
    '''

    # image = "test.jpg"
    img = Image.open(image)
    barcodes = pyzbar.decode(img)
    for barcode in barcodes:
        return True
        # barcodeData = barcode.data.decode("utf-8")
    return False
