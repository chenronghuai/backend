import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
import log
from utils import OrderType, OrderStatus
from utils import TestMeta
import globalvar
from sys import argv


init_flag = True


@ddt
class TestFlightOrderManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.fastline_orders = list(filter(lambda x: x.order_type == OrderType.FASTLINE, globalvar.order_pool))
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '班线管理', '班线订单管理', 'flightsOrderManager.do')
        cls.__name__ = cls.__name__ + "（快线订单管理：快线订单检票、完单等操作）"

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(1, 2, 3, 4)
    def test_operate_flow(self, index):
        global init_flag
        if init_flag:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selLine').click()
            if argv[1] == 'TEST':
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname$="高林SM专线"]'))).click()
            else:
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname$="厦门测试班线"]'))).click()
            globalvar.GLOBAL_DRIVER.execute_script("$('table#data_table>tbody>tr').html('')")
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))
            init_flag = False

        order = self.fastline_orders[index-1]
        sleep(1)
        if order.order_status == OrderStatus.APPOINTED:
            temp_css = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, 'table#data_table>tbody>tr', 'order-list-id',
                                                order.order_id)
            check_css = temp_css + '>td.td-opera>a[title="检票"]'
            WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, check_css))).click()
            globalvar.GLOBAL_DRIVER.switch_to.default_content()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))) # 直接点击偶发无效，加下面js试试
            globalvar.GLOBAL_DRIVER.execute_script("""$('div[type="dialog"]>div>a.layui-layer-btn0').click()""")
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src="/flightsOrderManager.do"]')))
            msg_check_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
            if '检票通过' not in msg_check_text:
                log.logger.error(f'检票失败，msg={msg_check_text}')
                assert False

            complete_css = temp_css + '>td.td-opera>a[title="完单"]'
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, complete_css))).click()
            globalvar.GLOBAL_DRIVER.switch_to.default_content()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))) # 直接点击偶发无效，加下面js试试
            globalvar.GLOBAL_DRIVER.execute_script("""$('div[type="dialog"]>div>a.layui-layer-btn0').click()""")
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src="/flightsOrderManager.do"]')))
            msg_complete_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
            if '完单成功！' not in msg_complete_text:
                log.logger.error(f'完单失败，msg={msg_complete_text}')
                assert False

            globalvar.GLOBAL_DRIVER.execute_script("$('table#data_table>tbody>tr').html('')")
            status_css = temp_css + '>td:nth-child(11)'
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
            actual_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, status_css))).text
            self.assertEqual(actual_text, '已完成')

        elif order.order_status == OrderStatus.WAITING:
            temp_css = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, 'table#data_table>tbody>tr', 'order-list-id',
                                                order.order_id)
            cancel_css = temp_css + '>td.td-opera>a[title="消单"]'
            WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cancel_css))).click()
            msg_text = utils.cancel_order(globalvar.GLOBAL_DRIVER, '车辆故障', 'flightsOrderManager.do')
            if '已成功取消订单!' in msg_text:
                globalvar.GLOBAL_DRIVER.execute_script("$('table#data_table>tbody>tr').html('')")
                status_css = temp_css + '>td:nth-child(11)'
#                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnQuery'))).click()
                actual_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, status_css))).text
                self.assertEqual(actual_text, '客服取消')
            else:
                log.logger.error(f'取消班线订单失败，msg={msg_text}')
                raise IndexError
