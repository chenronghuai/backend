import os
import re
import time
import unittest
from time import sleep, localtime
import configparser
import random
import globalvar
import log
from sys import argv
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from enum import Enum, unique
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, ElementClickInterceptedException


class OrderType(object):
    CARPOOLING = "拼车"
    CHARACTER = "包车"
    EXPRESS = "货件"
    INNER = "市内叫车"
    DAYSCHARACTER = "多日包车"
    FASTLINE = "快巴"
    HELPDRIVE = "代驾"


class OrderStatus(object):
    WAITING = "待处理"
    APPOINTED = "已指派"
    REWAITING = "重进队列"
    ONCAR = "已上车"
    OFFCAR = "已下车"
    COMPLETE = "已完成"
    CANCEL = "已取消"


class Node(object):
    ORDERED = '下单'
    APPOINTED = '指派'
    CANCELED = '取消'
    REAPPOINTED = '改派'


class CarType(object):
    TAXI = "出租车/5座"
    COM5 = "网约车/5座/舒适型"
    LUX5 = "网约车/5座/豪华型"
    COM7 = "商务七座/7座/舒适型"
    LUX7 = "商务七座/7座/豪华型"
    ANY = "所有车型"

    PRIORITY_DIST = {TAXI: 100, COM5: 200, LUX5: 300, COM7: 400, LUX7: 500}


@unique
class DriverType(Enum):
    '''
    CARPOOLING_DRIVER = 1
    CHARACTER_DRIVER = 2
    EXPRESS_DRIVER = 3
    INNER_DRIVER = 4
    DAYSCHARACTER_DRIVER = 5
    FASTLINE_DRIVER = 6
    HELPDRIVE_DRIVER = 7
    '''
    NET_DRIVER = 1
    BUS_DRIVER = 2


class FoundRecordError(Exception):
    def __init__(self, value, table):
        self.value = value
        self.table = table

    def __str__(self):
        return 'Could not found the {0} in {1}'.format(repr(self.value), repr(self.table))


class FoundDriverError(Exception):
    def __init__(self, id_):
        self.id_ = id_

    def __str__(self):
        return '找不到匹配的司机： {}'.format(repr(self.id_))


def cancel_order(driver, reason, from_src):
    """
    :param driver:
    :param reason: 取消原因，文本取后台取消原因文本
    :return: driver返回到进入时的iframe
    """
    WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getOrderCancelPage"]')))
    xpath_cancel = '//form/div/label[text()="' + reason + '"]'
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath_cancel))).click()
    driver.find_element_by_css_selector('#todoCancelBtn').click()
    try:
        driver.switch_to.parent_frame()
        return wait_for_laymsg(driver)

    except TimeoutException:  # 市内货代驾订单，可能由于超时系统自动取消订单，页面还有”消单“入口，机率极低
        driver.switch_to.default_content()
        sleep(2)  # 碰到超时，加等待试试，很难碰到
        WebDriverWait(driver, 2).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn-c>a.layui-layer-btn0'))).click()
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, 'iframe[src="/' + from_src + '"]'))
        return '乘客已经服务结束或者已经取消订单'


def reback_order(driver, reason):
    WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
        (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getOrderRebackPage"]')))
    xpath_cancel = '//form/div/label[text()="' + reason + '"]'
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, xpath_cancel))).click()
    driver.find_element_by_css_selector('#todoRebackBtn').click()
    msg_text = wait_for_laymsg(driver)
    driver.switch_to.parent_frame()
    return msg_text


def modify_price(driver, amount):
    """
    :param driver:
    :param amount: 改动后的金额，数字（可输入小数点后2位）
    :return: driver返回到进入时的iframe
    """
    WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/orderManage.do?method=getOrderManageModifyPrice"]')))
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#price')))
    driver.execute_script("$('#price').val('" + str(amount) + "')")
    driver.find_element_by_css_selector('#todoSureBtn').click()
    #强制停2妙，采用等待弹框消失，这种情形下driver貌似会进入到到最外层，与取消订单时的情形不同，后续跟踪！！！
    #sleep(2)
    wait_for_ajax(driver)
    driver.switch_to.parent_frame()


def read_config_value(section, name):
    """读取配置文件config.ini元素的值"""
#    path = os.path.split(os.path.realpath(__file__))[0]
    path = os.path.abspath(os.path.join(get_path(), os.path.pardir))
    config_path = os.path.join(path, 'config.ini')
    config = configparser.ConfigParser()
#    config.read(config_path, encoding='utf-8')
    config.read(config_path, encoding='utf-8')
    value = config.get(section, name)
    return value


def modify_config_value(section, name, value):
    """修改配置文件config.ini元素的值"""
    path = os.path.abspath(os.path.join(get_path(), os.path.pardir))
    config_path = os.path.join(path, 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    config.set(section, name, value)
    config.write(open(config_path, 'w', encoding='utf-8'))


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
        index_oper = -1
        for i in oper:
            index_oper = sub_str.find(i)
            if index_oper != -1:
                break
        if index_oper != -1:
            oper_liter = sub_str[index_oper]
            first_num = extract_digit(sub_str[0:index_oper])
            second_num = extract_digit(sub_str[index_oper + 1:len(sub_str)])
            sub_str = first_num + oper_liter + second_num
            value = eval(sub_str)
        else:
            value = 0

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
                          "')>=0;}).click()")
    sleep(1)
    we_childmenu = driver.find_element_by_css_selector('[tit=' + child_menu + ']')
    we_childmenu.location_once_scrolled_into_view
    we_childmenu.click()

    sleep(0.5)
    driver.switch_to.default_content()
    title = driver.execute_script("return $('.tab-tit>li').last().attr('tit')")
    globalvar.set_value(frame_name, title)

    WebDriverWait(driver, 5).until(
        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src="/' + frame_name + '"]')))
    sleep(2)  # 预留时间加载js


def switch_exist_frame(driver, to_src, title):
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, 'iframe[src="/' + to_src + '"]'))
    driver.execute_script(
        "$(window.parent.$('.tab-tit>li').filter(function(index){return $(this).text().indexOf('" + title + "')>=0;})).click()")


def get_first_order(order_type):
    for index, order in enumerate(globalvar.order_pool):
        if order.order_type == order_type and order.order_status == OrderStatus.WAITING:
            return order
        elif index == len(globalvar.order_pool)-1:
            log.logger.warning(f'订单池里没有{order_type}类型的订单')
            raise IndexError


def get_cell_content(driver, table_selector, row, column):
    """
    获取表格单元格数据
    :param driver:
    :param table_selector:表格的CSS定位
    :param row: 单元格的行
    :param column: 单元格的列
    :return: 返回单元格数据
    """
    cell_selector = 'tbody > tr:nth-child({0}) > td:nth-child({1})'.format(row, column)  # 经验证，不管是1条还是多条记录，该定位语句都没有问题
    fetch_text = ''
    try:
        fetch_text = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, table_selector + '>' + cell_selector))).text
    except TimeoutException:
        log.logger.warning(f'获取单元格内容超时：位置={table_selector}>{cell_selector}')
    finally:
        return fetch_text


def get_record_by_attr(driver, locator, attr_name, value):
    """
    通过记录属性值查询记录在表中的位置
    :param driver:
    :param locator: 元素的CSS locator
    :param attr_name: 字符串，属性的名称
    :param value: 字符串，属性的值
    :return: 记录所在的行locator: *>table>tbody>tr:nth-child(n)
    """
    # 灰度环境可能需要很久的等待时间
    records = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, locator)))
    if len(records) > 0:
        for i in range(len(records)):
            # 下面try模块的目的，为了规避DOM为空的情形
            try:
                actual_value = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator + f':nth-child({i+1})'))).get_attribute(attr_name)
            except StaleElementReferenceException:
                actual_value = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, locator + f':nth-child({i + 1})'))).get_attribute(
                    attr_name)
            if actual_value == value:
                return locator + ':nth-child({})'.format(i + 1)
            elif actual_value != value and i == len(records) - 1:
                log.logger.info(f'找不到记录：目标值={value},最后一条记录值={actual_value}')
                raise FoundRecordError(value, locator)
    else:
        log.logger.warning(f'该定位下({locator})没有找到任何记录')
        raise FoundDriverError('该定位下没有找到任何记录', locator)


def get_record_by_field_value(driver, locator, td_val, value):
    """

    :param driver:
    :param locator: 表的locator: *>table
    :param td_val: 字符串，待查表头的列名
    :param value: 字符串，待查列的值
    :return: 记录所在的行locator: *>table>tbody>tr:nth-child(*)
    """
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, locator)))
    text_list = [x.text for x in WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, locator + '>thead>tr>th')))]
    for index, val in enumerate(text_list, 1):
        if td_val == val:
            records = driver.find_elements_by_css_selector(locator + '>tbody>tr')
            for i in range(len(records)):
                css_td = 'td:nth-child({})'.format(index)
                if (WebDriverWait(driver, 5, ignored_exceptions=[StaleElementReferenceException]).until(EC.visibility_of(records[
                    i].find_element_by_css_selector(css_td)))).text == value:
                    return locator + '>tbody>tr:nth-child({})'.format(i+1)
                elif records[i].find_element_by_css_selector(css_td).text != value and i == len(records) - 1:
                    raise FoundRecordError(value, locator)
        elif td_val == val != td_val and index == len(text_list)-1:
            raise FoundRecordError(td_val, locator)


def get_record_by_multi_field_value(driver, locator, sour_dict):
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator + '>tbody>tr')))
    tds = driver.find_elements_by_css_selector(locator + '>thead>tr>th')
    records = driver.find_elements_by_css_selector(locator + '>tbody>tr')
    value_dict = {}
    for field, value in sour_dict.items():
        for index, val in enumerate(tds, 1):
            if val.text == field:
                value_dict[index] = value
                break
            elif val.text != field and index == len(tds):
                log.logger.error(f'该表没有"{field}"字段')
                raise IndexError
    for i in range(len(records)):
        k = 0
        for index_, value_ in value_dict.items():
            css_td = 'td:nth-child({})'.format(index_)
            if records[i].find_element_by_css_selector(css_td).text == value_:
                k += 1
                if k == len(value_dict):
                    return locator + '>tbody>tr:nth-child({})'.format(i + 1)
                continue
            else:
                break
        if i == len(records)-1:
            raise IndexError


def select_operation_by_field(driver, table_locator, field_name, value, opera_text, opera_field_name):
    """
    通过表格字段值确定记录，再根据操作菜单的字段名称及菜单名称进行点击操作
    :param driver:
    :param table_locator: 表的css locator
    :param attr_name: 属性名称
    :param value: 属性的值
    :param opera_text: 操作文案
    :param opera_field_name: 待操作菜单的字段名称，一般为“操作”
    :return:
    """
    record_locator = get_record_by_field_value(driver, table_locator, field_name, value)
    try:
        text_list = [x.text for x in WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_locator + '>thead>tr>th')))]
    except:
        sleep(1)
        text_list = [x.text for x in WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_locator + '>thead>tr>th')))]
    for index, text in enumerate(text_list):
        if opera_field_name in text:
            a_css = record_locator + '>td:nth-child({})'.format(index+1)
            try:
                WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, a_css))).find_element_by_link_text(opera_text).click()
            except:
                sleep(1)
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, a_css))).find_element_by_link_text(
                    opera_text).click()
        elif opera_field_name not in text and index == len(text_list)-1:
            raise IndexError  # FoundRecordError("操作", table_locator)


def get_opera_text(driver, opera_locator):
    """
    获取操作栏操作菜单的文本列表
    :param driver:
    :param opera_locator: 操作菜单的CSS定位，到达td>a层
    :return: 操作菜单文本列表
    """
    opera_text = []
    all_opera_elements = driver.find_elements_by_css_selector(opera_locator)
    for element in all_opera_elements:
        opera_text.append(element.get_attribute('title'))
    return opera_text


def select_operation_by_attr(driver, table_locator, attr_locator, attr_name, value, opera_text):
    """
    从列表“操作”栏点击具体的操作文本
    :param driver:
    :param table_locator: 表的css locator
    :param attr_locator: 属性的css locator
    :param attr_name: 属性名称
    :param value: 属性的值
    :param opera_text: 操作文案
    :return:
    """
    record_locator = get_record_by_attr(driver, attr_locator, attr_name, value)
    try:
        text_list = [x.text for x in WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_locator + '>thead>tr>th')))]
    except:
        sleep(1)
        text_list = [x.text for x in WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_locator + '>thead>tr>th')))]
    for index, text in enumerate(text_list):
        if "操作" in text:
            a_css = record_locator + '>td:nth-child({})'.format(index+1)
            try:
                WebDriverWait(driver, 5, ignored_exceptions=[ElementClickInterceptedException]).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                  a_css))).find_element_by_link_text(opera_text).click()
            except:
                sleep(1)
                WebDriverWait(driver, 5, ignored_exceptions=[ElementClickInterceptedException]).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, a_css))).find_element_by_link_text(
                    opera_text).click()
        elif "操作" not in text and index == len(text_list)-1:
            log.logger.error(f'{table_locator}表格没有"操作"字段')
            raise IndexError  # FoundRecordError("操作", table_locator)


def get_operation_field_text(driver, table_locator, record_locator):
    """
    获取操作栏菜单文本
    :param driver: webdriver对象
    :param table_locator: 表的CSS locator
    :param record_locator: 目标记录的CSS locator
    :return: 操作菜单的文本列表
    """
    operation_text_list = []
    we_fields = WebDriverWait(driver, 5, ignored_exceptions=(StaleElementReferenceException,)).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_locator + '>thead>tr>th')))

    a_text_css = record_locator + f'>td:nth-child({len(we_fields)})>a'

    operation_texts = [x.text for x in WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((
        By.CSS_SELECTOR, a_text_css)))]
    '''
    try:
        operation_texts = [x.text for x in WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((
            By.CSS_SELECTOR, a_text_css)))]
    except TimeoutException:
        log.logger.error('记录显示超时或者没有满足条件的记录！')
        raise IndexError
    '''  # 该try块会导致超时，不解
    for i in operation_texts:
        if i.find('\n') != -1:  # 特殊处理类似'分享\n6'的文本
            i = i[:i.find('\n')]
        operation_text_list.append(i)
    return operation_text_list


def get_time(date, t_time):
    if date == "今天" or date == "":
        secs = time.time()
    elif date == "明天":
        secs = time.time()+24*60*60  # 加一天的秒数

    month = localtime(secs).tm_mon
    month_str = str(month) if month >= 10 else '0' + str(month)
    day = localtime(secs).tm_mday
    day_str = str(day) if day >= 10 else '0' + str(day)
    if t_time == "":
        hour = localtime(secs).tm_hour
        hour_str = str(hour) if hour >= 10 else '0' + str(hour)
        minute = localtime(secs).tm_min
        minute_str = str(minute) if minute >= 10 else '0' + str(minute)
    else:
        hour_str = str(t_time)[0:2]
        minute_str = str(t_time)[2:4]
        if date == "今天" or date == "":  # 跨凌晨12点会有问题
            hour = localtime(secs).tm_hour
            hour_num = hour*60
            minute = localtime(secs).tm_min
            minute_num = minute
            if (int(hour_str)*60+int(minute_str))-(hour_num+minute_num) < 40:  # 40分钟内算即时单
                hour_str = str(hour) if hour >= 10 else '0' + str(hour)
                minute_str = str(minute) if minute >= 10 else '0' + str(minute)

    t_date = (month_str, day_str)
    date = '-'.join(t_date)
    t_time = (hour_str, minute_str)
    ti = ':'.join(t_time)
    t_result = (date, ti)
    return ' '.join(t_result)


def convert_to_minute(t):
    t_t = str(t).split(':')
    return int(t_t[0])*60 + int(t_t[1])


def convert_to_stamp(time_str):
    """
    把'03-16 15:29'格式的时间转化为时间戳
    :param time_str:待转化的时间，字符串，格式要求为'03-16 15:29'
    :return:时间戳，秒数
    """
    result = time_str.split(' ')
    date_list = result[0].split('-')
    time_list = result[1].split(':')
    year = time.localtime()[0]

    return time.mktime((year, int(date_list[0]), int(date_list[1]), int(time_list[0]), int(time_list[1]), 30, 0, 0, 0))


def normal_to_datetime(src):
    """
    把'2020-07-06 08:53:55'格式的时间转化为datetime对象，用于时间先后对比
    :param src:字符串，格式为'2020-07-06 08:53:55'
    :return:datetime对象
    """
    assert isinstance(src, str)
    dt_list = src.split(' ')
    date_list = dt_list[0].split('-')
    time_list = dt_list[1].split(':')
    return datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]), int(time_list[0]), int(time_list[1]), int(time_list[2]))


def input_ori_des(driver,  origin, ori_value, destination, des_value):
    try:
        we_ori = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName')))
        we_ori.clear()
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#startName-suggest>div')))
        driver.execute_script("$('div#endsName-suggest').html('')")  # 清除目的方位，用于判断起始方位确定后，目的地建议方位返回时机
        we_ori.click()
        WebDriverWait(driver, 15).until(
            lambda x: x.execute_script("return $('#startName-suggest').css('display')") == 'block')
        we_ori.send_keys(origin)
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_origin'), ori_value))
    except:
        return '输入起点方位错误'

    try:
        if argv[1] != 'TEST':
            sleep(5)  # 非测试环境增加等待时间
        we_des = driver.find_element_by_css_selector('#endsName')
        we_des.clear()
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
#        driver.execute_script("$('div#endsName-suggest').html('')")
        we_des.click()
        WebDriverWait(driver, 15).until(
            lambda x: x.execute_script("return $('#endsName-suggest').css('display')") == 'block')
        we_des.send_keys(destination)
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_destination'), des_value))
    except:
        return '输入终点方位错误'


def generate_password():
    s = ''
    cha_l = 'abcdefghijklmnopqrstuvwxyz'
    cha_u = 'ABCDEFGHIJKLMNOPQRESTUVWXYZ'
    for i in range(2):
        t = random.choice(cha_l)
        s += t
    for i in range(2):
        t = random.randrange(0, 9, 1)
        s += str(t)
    s += '_'
    for i in range(5):
        t = random.choice(cha_u)
        s += t
    return s


def get_subscribe_order():
    """
    获取网约预约单
    :return:预约单的id列表
    """
    id_list = []
    net_orders = filter(lambda order_: order_.order_type != OrderType.FASTLINE, globalvar.order_pool)
    for order in net_orders:
        if convert_to_stamp(order.appoint_time)-time.time() > 2400:  # 过滤出用车时间离现在超过40分钟的订单
            id_list.append(order.order_id)
    return id_list


def wait_for_laymsg(driver):
    """
    等待layer msg弹框出现和消失
    :param driver:webdriver对象
    :return: 弹框的文本内容，供后续流程判断
    """
    def func(driver_):
        try:
            text = driver_.find_element_by_css_selector('.layui-layer-content.layui-layer-padding').text
            return text
        except StaleElementReferenceException:
            return False

    result_text = WebDriverWait(driver, 15, 0.1).until(func)
    try:
        WebDriverWait(driver, 15).until_not(lambda x: x.find_element_by_css_selector('.layui-layer-content.layui-layer-padding'))
        WebDriverWait(driver, 10).until_not(lambda x: x.find_element_by_css_selector('.layui-layer.layui-layer-loading.layui-anim'))
    except:
        pass
    return result_text


def wait_for_load(driver):
    """
    等待载入旋转图标消失
    :param driver:
    :return:
    """
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.layui-layer-content.layui-layer-loading3')))
    WebDriverWait(driver, 15).until_not(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.layui-layer-content.layui-layer-loading3')))


def wait_for_ajax(driver_):
    wait = WebDriverWait(driver_, 15)
    try:
        wait.until(lambda x: x.execute_script('return jQuery.active') == 0)
        wait.until(lambda x: x.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        pass


def make_sure_driver(driver, mother_menu, child_menu, src_link):
    """
    确保当前的iframe有效
    :param driver: webdriver
    :param mother_menu: 母菜单（字符串）
    :param child_menu: 子菜单（字符串）
    :param title: 窗口标题（字符串）
    :param src_link: iframe属性src的字串（字符串）
    :return:
    """
    if src_link in globalvar.opened_window_pool:
        switch_exist_frame(driver, src_link, globalvar.get_value(src_link))
    else:
        switch_frame(driver, mother_menu, child_menu, src_link)
        globalvar.opened_window_pool.append(src_link)


class TestMeta(type):
    """
    创建TestCase的元类，改变测试方法的名称，使得测试方法的执行顺序按照其在测试类的出现的先后位置
    """
    def __new__(cls, name, bases, attrs):
        i = 10
        new_attrs = attrs.copy()
        for k, v in attrs.items():
            if k.startswith('test') and callable(v):
                suf = k[4:]
                new_key = 'test_{}'.format(i) + suf
                i += 1
                new_attrs.pop(k)
                new_attrs[new_key] = v
        return super().__new__(cls, name, bases, new_attrs)


class SequentialTestLoader(unittest.TestLoader):
    """
    按照用例的书写顺序执行，配合TestMeta类使用
    定义时：class Testxxx(unittest,  metaclass=TestMeta)
    加载时：SequentialTestLoader().loadTestsFromTestCase(Testxxx)
    """
    def getTestCaseNames(self, testCaseClass):
        test_names = super().getTestCaseNames(testCaseClass)
        testcase_methods = list(testCaseClass.__dict__.keys())
        test_names.sort(key=testcase_methods.index)

        def get_index(x):
            return int(re.match(r'test_(\d+)_.+', x).group(1))

        try:
            test_names.sort(key=get_index)
        except:
            pass
        return test_names
