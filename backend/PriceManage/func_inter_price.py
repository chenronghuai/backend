import utils
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from time import sleep
from sys import argv
import globalvar
import log
import sys
import traceback


class FuncInterPrice:

    def __init__(self):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '价格管理', '城际区域价格', 'price.do')

    def query_line(self, line_name):
        we_line_input = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((
            By.CSS_SELECTOR, '#baseLineName')))
        we_line_input.clear()
        we_line_input.send_keys(line_name)
        globalvar.GLOBAL_DRIVER.execute_script("$('#line_table>tbody').html('')")
        # 此句确保后续查询为最新结果，否则用例之间可能交叉导致出现StaleElementReferenceException异常
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                          '#btnQuery'))).click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5, ignored_exceptions=[StaleElementReferenceException]).until(lambda x:
            x.find_element_by_css_selector('#line_table>tbody>tr:nth-child(1)>td:nth-child(1)').text == line_name)

    def set_price(self, line_name, order_type, car_type, price):
        self.query_line(line_name)
        utils.select_operation_by_field(globalvar.GLOBAL_DRIVER, '#line_table', '线路名称', line_name, '编辑', '价格设定')
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it((
                By.CSS_SELECTOR, '[src^="/price-manager.do?method=getLinePricePage"]')))
            order_type_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#order_type')
            car_type_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#car_class_id')
            Select(order_type_sel).select_by_visible_text(order_type)
            Select(car_type_sel).select_by_visible_text(car_type)
            we_price = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#price')
            we_price.clear()
            we_price.send_keys(price)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#savePriceBtn').click()
            msg_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)

            return msg_text
        finally:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#delPriceBtn').click()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()

    def get_price(self, line_name, order_type, car_type):
        self.query_line(line_name)
        utils.select_operation_by_field(globalvar.GLOBAL_DRIVER, '#line_table', '线路名称', line_name, '编辑', '价格设定')
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/price-manager.do?method=getLinePricePage"]')))
            if order_type != '货':
                order_type += '车'
            else:
                order_type += '件'
            record_dict = {
                '订单类型': order_type,
                '车型': car_type
            }
            try:
                we_goal = utils.get_record_by_multi_field_value(globalvar.GLOBAL_DRIVER, '#price_table', record_dict)
            except:
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#pagebar_n_page').click()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                                  '#pagebar_p_page')))
                we_goal = utils.get_record_by_multi_field_value(globalvar.GLOBAL_DRIVER, '#price_table', record_dict)

            return globalvar.GLOBAL_DRIVER.find_element_by_css_selector(we_goal + '>td:nth-child(3)').text

        finally:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#delPriceBtn').click()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
