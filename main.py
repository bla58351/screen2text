"""
screen2text
使用方法：
    1.运行程序
    2.使用截图工具截取文字区域(
        windows10:"shift+windows+s"
        qq:"ctrl+alt+a"
        wechat:"alt+a"
        )
    3.等待(通常不会太久),在编辑区域使用快捷键(默认ctrl+shift+v)，就能转换成文字了。
    github:https://github.com/bla58351/screen2text
"""

from PIL import ImageGrab
from PIL import ImageChops
from PIL import Image
import io
import time
import base64
import requests
import keyboard

screen_height = 1080  # 屏幕纵向分辨率
hot_key = "ctrl+shift+v"  # 粘贴快捷键
bd_api_key = "a9nrUZgk0ZkiqZI5g2ijWuWs"  # api key
bd_secret_key = "8WR5BwijozHaMNLIzajs2vjotFp7zQcn"  # secret key
ocr_text = ""


def get_token(api_key, secret_key):
    """
    百度API请求token
    :param api_key: 百度API key
    :param secret_key: 百度secret key
    :return: 用于百度OCR api的access token
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    return requests.post("https://aip.baidubce.com/oauth/2.0/token", data=data).json()['access_token']


def ocr(img_base64):
    """
    百度ocr识别调用
    :param img_base64: 经base64编码的图片二进制流
    :return: 识别的文字/错误信息
    """
    url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={}'.format(
        get_token(bd_api_key, bd_secret_key))
    headers = {"Content-Type": "application/x-www-form-urlencoded"}  # 请求头
    data = {"image": img_base64}  # 构建post数据流
    try:
        results = requests.post(url, data=data, headers=headers, timeout=15).json()  # api请求
    except requests.exceptions.RequestException:  # 网络请求超时
        print("网络连接超时")
        return "网络连接超时"
    except:  # 其他错误
        print("发生未知错误")
        return "发生未知错误"
    if "error_code" in results:
        return results["error_msg"]
    else:
        words = []
        print(results)
        for i in results["words_result"]:
            words.append(str(i["words"]).replace(" ", ""))
        res_text = "\n".join(words)
        return res_text


def input_text():
    """
    粘贴文字
    :return: None
    """
    keyboard.write(ocr_text)


def get_text(img):
    """
    获取文字总函数
    :param img: 原始图片
    :return: 识别到的文字
    """
    img_bytes = io.BytesIO()
    img.save(img_bytes, 'png')
    img_base64 = base64.b64encode(img_bytes.getvalue())
    text = ocr(img_base64)
    print(text)
    return text


def main():
    keyboard.add_hotkey(hot_key, input_text)  # 绑定快捷键
    while True:  # 获取程序运行前剪切板内已经存在的图片
        if isinstance(ImageGrab.grabclipboard(), Image.Image):
            img_saved = ImageGrab.grabclipboard()
            if img_saved.height >= screen_height:  # 规避win10自带截屏使用screen快捷键工作时会截取整屏的特性
                continue
            global ocr_text
            ocr_text = get_text(img_saved)
            break
        else:
            time.sleep(1)
    while True:  # 获取程序运行时截图后剪切板内的图片
        time.sleep(1)
        if isinstance(ImageGrab.grabclipboard(), Image.Image):
            img = ImageGrab.grabclipboard()
            if img.height >= screen_height:
                continue
            diff = ImageChops.difference(img, img_saved)  # 比较图片是否一致
            if diff.getbbox() is None:
                continue
            else:
                img_saved = img
                ocr_text = get_text(img)


if __name__ == '__main__':
    main()
