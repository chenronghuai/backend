import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
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
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '班线管理', '班线订单管理', 'flightsOrderManager.do')
        globalvar.opened_window_pool.append('flightsOrderManager.do')

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(1, 2, 3)
    def test_operate_flow(self, index):
        global init_flag
        if init_flag:
            self.driver.find_element_by_css_selector('#selLine').click()
            if argv[1] == 'TEST':
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname$="高林SM专线"]'))).click()
            else:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname$="厦门测试班线"]'))).click()
            self.driver.execute_script("$('table#data_table>tbody>tr').html('')")
            self.driver.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))
            init_flag = False

        order = self.fastline_orders[index-1]
        sleep(1)
        if order.order_status == OrderStatus.APPOINTED:
            temp_css = utils.get_record_by_attr(self.driver, 'table#data_table>tbody>tr', 'order-list-id',
                                                order.order_id)
            check_css = temp_css + '>td.td-opera>a[title="检票"]'
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, check_css))).click()
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))) # 直接点击偶发无效，加下面js试试
            self.driver.execute_script("""$('div[type="dialog"]>div>a.layui-layer-btn0').click()""")
            WebDriverWait(self.driver, 15).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0')))
            we_manage = self.driver.find_element_by_css_selector('iframe[src="/flightsOrderManager.do"]')
            self.driver.switch_to.frame(we_manage)
            complete_css = temp_css + '>td.td-opera>a[title="完单"]'
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, complete_css))).click()
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))) # 直接点击偶发无效，加下面js试试
            self.driver.execute_script("""$('div[type="dialog"]>div>a.layui-layer-btn0').click()""")
            WebDriverWait(self.driver, 15).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0')))
            self.driver.switch_to.frame(we_manage)
            self.driver.execute_script("$('table#data_table>tbody>tr').html('')")
            status_css = temp_css + '>td:nth-child(11)'
            actual_text = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, status_css))).text
            self.assertEqual(actual_text, '已完成')

        elif order.order_status == OrderStatus.WAITING:
            temp_css = utils.get_record_by_attr(self.driver, 'table#data_table>tbody>tr', 'order-list-id',
                                                order.order_id)
            cancel_css = temp_css + '>td.td-opera>a[title="消单"]'
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, cancel_css))).click()
            utils.cancel_order(self.driver, '车辆故障')
            sleep(1)
#            self.driver.execute_script("$('table#data_table>tbody>tr').html('')")
            status_css = temp_css + '>td:nth-child(11)'
            actual_text = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, status_css))).text
            self.assertEqual(actual_text, '客服取消')
