from selenium import webdriver
import utils
import os
from time import sleep
from pytesseract import image_to_string
from PIL import Image, ImageEnhance
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login(url_section, user_section):
    """
    :param url: 目标url,读取config.ini的http section
    :param user: 用户信息,读取config.ini的user section
    :return: driver
    """
    driver = webdriver.Chrome()
    driver.get(utils.read_config_value(url_section, 'scheme') + utils.read_config_value(url_section, 'baseurl'))
    driver.maximize_window()
    driver.find_element_by_id('username').send_keys(utils.read_config_value(user_section, 'username'))
    driver.find_element_by_id('userpwd').send_keys(utils.read_config_value(user_section, 'password'))
    '''
    sleep(5)
    driver.find_element_by_id('loginBtn').click()
    '''
    sleep(1)
    # 以下为登录验证码自动识别
    while 1:
        driver.find_element_by_id('imgCode').clear()
        driver.save_screenshot(os.path.join(utils.get_path(), 'login.png'))
        code_ele = driver.find_element_by_xpath('//*[@id="changeImg"]')
        left = code_ele.location['x']
        top = code_ele.location['y']
        right = left + code_ele.size['width']
        down = top + code_ele.size['height']
        image = Image.open(os.path.join(utils.get_path(), 'login.png'))
        code_image = image.crop((left, top, right, down))
        imgry = code_image.convert("L")
        sharpness = ImageEnhance.Contrast(imgry)
        sharp_img = sharpness.enhance(2.0)
        str = image_to_string(sharp_img, lang='817')  # 调用名字为817.traineddata的训练数据识别验证码
        value = utils.cal_val(str)
        driver.find_element_by_id('imgCode').send_keys(value)
        driver.find_element_by_id('loginBtn').click()
        sleep(1)
        try:
            text_tip = driver.find_element_by_id('error-msg').text
            if text_tip is None:
                break

        except:
            break

    sleep(2)  # 出现安全预警弹窗没有关闭的情形，怀疑js没有加载完整，暂用此方法规避看看
    # 如果出现修改密码弹窗，关闭
    try:
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="layui-layer layui-layer-page yourclass layer-anim"]>span.layui-layer-setwin>a'))).click()
    except:
        pass
    # 如果出现乘客安全预警弹窗，关闭

    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="layui-layer layui-layer-page  layer-anim"]>span.layui-layer-setwin>a'))).click()
    except:
        pass

    return driver



