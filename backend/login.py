from selenium import webdriver
import utils
import log
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.common.exceptions import WebDriverException
from time import sleep
from sys import argv
import sys
from pytesseract import image_to_string
from PIL import ImageEnhance
if sys.platform.startswith('lin'):
    import pyscreenshot as ImageGrab
else:
    from PIL import ImageGrab
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import globalvar
from selenium.webdriver.chrome.options import Options



def login(url_section, user_section, main_flag=True):
    """
    :param url: 目标url,读取config.ini的http section
    :param user: 用户信息,读取config.ini的user section
    :param main_flag: 是否主线程标志
    :return: driver
    """
    driver = None
    options = Options()
    if sys.platform.startswith('lin'):
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
    else:  # 关闭浏览器受到自动化测试软件控制的提示
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
    try:
        driver = webdriver.Chrome(options=options)
        globalvar.set_value('driver', driver)
        globalvar.GLOBAL_DRIVER = driver
        driver.get(utils.read_config_value(url_section, 'scheme') + utils.read_config_value(url_section, 'baseurl'))
    except WebDriverException:
        log.logger.critical(f"服务器{utils.read_config_value(url_section, 'scheme') + utils.read_config_value(url_section, 'baseurl')}没有反应！请确认浏览器与驱动是否匹配！")
        exit(1)
    driver.maximize_window()
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#loginform')))
    except TimeoutException:
        log.logger.critical(f"服务器{utils.read_config_value(url_section, 'scheme') + utils.read_config_value(url_section, 'baseurl')}----404")
        exit(1)
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
        str_ = image_to_string(sharp_img, lang='817')  # 调用名字为817.traineddata的训练数据识别验证码
        value = utils.cal_val(str_)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#imgCode'))).send_keys(value)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#loginBtn'))).click()
        sleep(0.5)
        try:
            text_tip = driver.find_element_by_id('error-msg').text

            if text_tip == '':
                break
            elif text_tip == '图形答案不正确':
                sleep(1)
            elif text_tip == '用户名或密码错误':
                raise ValueError('用户名或密码错误！')
        # 灰度环境出现如下异常
        except StaleElementReferenceException:
            break

        except ValueError:
            log.logger.critical('用户名或密码错误')
            if main_flag:
                exit(2)
            break

        except NoSuchElementException:
            break

    sleep(2)  # 出现安全预警弹窗没有关闭的情形，怀疑js没有加载完整，暂用此方法规避
    # 如果出现修改密码弹窗，关闭
    try:
        '''
        WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="layui-layer layui-layer-page yourclass layer-anim"]>span.layui-layer-setwin>a'))).click()
        '''
        new_psw = utils.generate_password()
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userpwd'))).send_keys(new_psw)
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userpwdSure'))).send_keys(
            new_psw)
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnSure'))).click()
        utils.modify_config_value(argv[2], 'password', new_psw)
        driver.quit()
        login(url_section, user_section)
    except:
        pass
    # 如果出现乘客安全预警弹窗，关闭

    try:
        WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[class="layui-layer layui-layer-page  layer-anim"]>span.layui-layer-setwin>a'))).click()
    except:
        pass
    return driver




