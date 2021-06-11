import utils
from utils import OrderType, DriverType, FoundRecordError, FoundDriverError, CarType
import globalvar
import re
from sys import argv
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


def add_inter_order(driver, order_id):
    """
    补城际订单 - -补单页面操作
    :param  driver:
    :param  order_id: 订单ID
    :return:
    """
    try:
        WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getinterCityDriverAddOrdersPage"]')))
        sleep(1)
    #    utils.input_ori_des(driver, 'XMC', '361000', 'XM', '361000')   #  没有调用该函数，是由于在正式环境中，起点方位有默认值，导致无法输入起点
        we_ori = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName')))
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#startName-suggest>div')))
        we_ori.click()
        we_ori.send_keys(Keys.BACKSPACE)
        driver.execute_script("$('div#endsName-suggest').html('')")
        we_ori.send_keys('XMC')
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_origin'), '361000'))

        we_des = driver.find_element_by_css_selector('#endsName')
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
        sleep(1)
        we_des.send_keys(Keys.BACKSPACE)
        we_des.click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
        we_des.send_keys('XM')
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_destination'), '361000'))
        sleep(1)
        driver.find_element_by_css_selector('#btnQuery').click()

        WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
        try:
            orders = driver.find_elements_by_css_selector('div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
        except Exception:
            sleep(1)
            orders = driver.find_elements_by_css_selector('div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
        id_lists = [x.get_attribute('order-id') for x in orders]
        for index, id_ in enumerate(id_lists):
            if id_ == order_id:
                expect_css = 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li:nth-child({})'.format(index + 1)
                driver.find_element_by_css_selector(expect_css).click()
                sleep(1)
                driver.find_element_by_css_selector('#orderAddBtn').click()
                driver.switch_to.parent_frame()
                sleep(1)
                try:
                    WebDriverWait(driver, 1).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn->a.layui-layer-btn0'))).click()
                except:
                    pass
                driver.switch_to.frame(
                    driver.find_element_by_css_selector('iframe[src^="/orderCtrl.do?method=getinterCityDriverAddOrdersPage"]'))
                driver.find_element_by_css_selector('#closeBtn').click()
                break

    except TimeoutException:
        driver.find_element_by_css_selector('#closeBtn').click()
    finally:
        driver.switch_to.parent_frame()
        sleep(2)


def add_bus_order(driver, order_id):
    """
    补定制快线--补单页面操作
    :param driver:
    :param order_id:订单ID
    :return:
    """
    try:
        WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getKbDriverAddOrdersPage"]')))
        WebDriverWait(driver, 80).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
        driver.find_element_by_css_selector('.fs-label-wrap>.fs-label').click()
        if argv[1] == 'TEST':
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="高林SM专线"]'))).click()
        else:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="厦门测试班线"]'))).click()
        if argv[1] == 'STAGE':
            sleep(3)
        try:
            driver.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
        except:
            sleep(5)
            driver.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
        try:
            orders = driver.find_elements_by_css_selector('div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
        except Exception:
            sleep(1)
            orders = driver.find_elements_by_css_selector('div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
        id_lists = [x.get_attribute('order-id') for x in orders]
        for index, id_ in enumerate(id_lists):
            if id_ == order_id:
                expect_css = 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li:nth-child({})'.format(index + 1)
                driver.find_element_by_css_selector(expect_css).click()
                sleep(1)
                driver.find_element_by_css_selector('#orderAddBtn').click()
                break
        driver.find_element_by_css_selector('#closeBtn').click()
    except TimeoutException:
        driver.find_element_by_css_selector('#closeBtn').click()
    finally:
        sleep(1)
        driver.switch_to.parent_frame()


def filter_bus_driver(order):
    bus_drivers = list(filter(lambda _driver: _driver.driver_type == DriverType.BUS_DRIVER, globalvar.driver_pool))
    if len(bus_drivers) == 0:
        raise IndexError
        return '司机池找不到班线司机！'
    if order.order_type in [OrderType.CARPOOLING, OrderType.FASTLINE]:
        for index, driver in enumerate(bus_drivers):
            if order.order_count <= driver.max_user-driver.appoint_user_count and driver.charter_count == 0:
                driver.appoint_user_count += order.order_count
                return driver
            elif index == len(bus_drivers)-1:
                raise FoundDriverError(order.order_type)
                raise IndexError
                return '没有合适的司机'

    elif order.order_type in [OrderType.CHARACTER, OrderType.DAYSCHARACTER]:
        free_drivers = list(filter(lambda x: x.charter_count == 0 and x.appoint_user_count == 0, bus_drivers))
        if len(free_drivers) == 0:
            raise IndexError
            return '没有合适的司机'
        else:
            for index, driver in enumerate(free_drivers):
                if CarType.PRIORITY_DIST[driver.car_type] >= CarType.PRIORITY_DIST[order.car_type]:
                    driver.charter_count += 1
                    return driver
                elif index == len(free_drivers) - 1:
                    raise FoundDriverError(order.order_type)
                    raise IndexError
                    return '没有合适的司机'


def search_extract_driver(driver_, driver):

    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#driverList'))).click()
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#intercityDriver>table>#tdy_driver_queue>tr')))
    info_text = driver.find_element_by_css_selector('#intercityDriver>#pagebar>p').text
    page_num = int(re.search(r'.+/(.+)', info_text).group(1))
    for i in range(page_num):
        reported_driver_records = WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#intercityDriver>table>#tdy_driver_queue> tr')))
        for index, record in enumerate(reported_driver_records):
            flight_no_css = f'div#intercityDriver>table>tbody#tdy_driver_queue>tr:nth-child({index + 1})>td:nth-child(2)'
            flight_no = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, flight_no_css))).text
            record_driver_id = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'#intercityDriver>table>#tdy_driver_queue > tr:nth-child({index + 1}'))).get_attribute('driver_id')  # 确保不会碰到系统刷新导致瞬间DOM为空
            if record_driver_id == driver_.driver_id and flight_no == globalvar.get_value('FlightNo'):
                driver_css = f'div#intercityDriver>table>tbody#tdy_driver_queue>tr:nth-child({index + 1})'
                return driver_css
        driver.execute_script("$('#pagebar>a.next').click()")
        sleep(1)
