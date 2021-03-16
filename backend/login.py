from selenium import webdriver
import utils
import os
from time import sleep
from pytesseract import image_to_string
from PIL import ImageEnhance, ImageGrab
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import globalvar


def login(url_section, user_section):
    """
    :param url: 目标url,读取config.ini的http section
    :param user: 用户信息,读取config.ini的user section
    :return: driver
    """
    driver = webdriver.Chrome()
    globalvar.set_value('driver', driver)
    driver.get(utils.read_config_value(url_section, 'scheme') + utils.read_config_value(url_section, 'baseurl'))
    driver.maximize_window()
    driver.find_element_by_id('username').send_keys(utils.read_config_value(user_section, 'username'))
    driver.find_element_by_id('userpwd').send_keys(utils.read_config_value(user_section, 'password'))

    sleep(1)
    offset_height = driver.execute_script('return window.outerHeight-window.innerHeight')  # 识别码图片在窗口Y方向偏移量
    # 以下为登录验证码自动识别
    while True:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#imgCode'))).clear()
        code_ele = WebDriverWait(driver, 10).until((EC.visibility_of_element_located((By.CSS_SELECTOR, '#changeImg'))))
        left = code_ele.location['x']
        top = code_ele.location['y'] + offset_height
        right = left + code_ele.size['width']
        down = top + code_ele.size['height']
        code_image = ImageGrab.grab(bbox=(left, top, right, down))
        imgry = code_image.convert("L")
        sharpness = ImageEnhance.Contrast(imgry)
        sharp_img = sharpness.enhance(2.0)
        str = image_to_string(sharp_img, lang='817')  # 调用名字为817.traineddata的训练数据识别验证码
        value = utils.cal_val(str)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#imgCode'))).send_keys(value)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#loginBtn'))).click()
        sleep(0.5)
        try:
            text_tip = driver.find_element_by_id('error-msg').text
            if text_tip is None:
                break

        except:
            break

    sleep(2)  # 出现安全预警弹窗没有关闭的情形，怀疑js没有加载完整，暂用此方法规避
    # 如果出现修改密码弹窗，关闭
    try:
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="layui-layer layui-layer-page yourclass layer-anim"]>span.layui-layer-setwin>a'))).click()
    except:
        pass
    # 如果出现乘客安全预警弹窗，关闭

    try:
        WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="layui-layer layui-layer-page  layer-anim"]>span.layui-layer-setwin>a'))).click()
    except:
        pass
    return driver




