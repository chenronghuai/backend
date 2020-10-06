import os
from time import sleep
import configparser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def read_config_value(section, name):
    """读取配置文件config.ini元素的值"""
#    path = os.path.split(os.path.realpath(__file__))[0]
    path = os.path.abspath(os.path.join(get_path(), os.path.pardir))
    config_path = os.path.join(path, 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    value = config.get(section, name)
    return value


def get_path():
    """获取项目所在路径"""
    path = os.path.split(os.path.realpath(__file__))[0]
    return path


def extract_digit(s_source):
    """对识别到的操作数进行截取，过滤掉易混淆的0或者空格"""
    s_temp, s_result = '', s_source
    if len(s_source) > 1:
        for i in s_source:
            if i != '0' and i != ' ':
                s_temp += i
        if len(s_temp) == 0:
            s_temp = '0'
        s_result = s_temp[0]

    return s_result


def cal_val(s_img):
    """计算识别出的表达式的值"""
    try:
        index_equ = s_img.find('=')
        sub_str = s_img[0:index_equ]
        oper = ('+', '-', '*')
        for i in oper:
            index_oper = sub_str.find(i)
            if index_oper != -1:
                break
        oper_liter = sub_str[index_oper]
        first_num = extract_digit(sub_str[0:index_oper])
        second_num = extract_digit(sub_str[index_oper + 1:len(sub_str)])

        sub_str = first_num + oper_liter + second_num
        value = eval(sub_str)
    except:
        value = 0
    return value


def switch_frame(driver, mother_menu, child_menu, frame_name):
    """
    切换frame(窗口)
    :param driver:
    :param mother_menu:字符串，侧边栏主菜单的名称
    :param child_menu:字符串，侧边栏子菜单的名称
    :return:
    """
    driver.switch_to.default_content()
    # 有展开侧边栏时，收起
    driver.execute_script("""var openTitle; 
    $('.side-tit').each(function(inx, obj){if($(this).hasClass('on')){openTitle = $(this);}});
    $(openTitle).removeClass('on').siblings('.sub-list').slideUp('on');
    $(openTitle).siblings("i").removeClass("open");""")
    sleep(1)
    driver.execute_script("$('.side-tit').filter(function(index){return $(this).text().indexOf('" + mother_menu +
                          "')>0;}).click()")
    sleep(1)
    driver.find_element_by_css_selector('[tit=' + child_menu + ']').click()
    WebDriverWait(driver, 5).until(
        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src="/' + frame_name + '"]')))
    sleep(2)  # 预留时间加载js


