import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
from utils import OrderType
from utils import TestMeta
import globalvar
import logging
from sys import argv


logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@ddt
class TestFlightOrderManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '班线管理', '班线订单管理', 'flightsOrderManager.do')

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data({"line": "高林SM专线"})
    @unpack
    def test_operate_flow(self, line):
        fastline_orders = list(filter(lambda x: x.order_type == OrderType.FASTLINE, globalvar.order_pool))
        self.driver.find_element_by_css_selector('#selLine').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname$="' + line + '"]'))).click()
        self.driver.execute_script("$('table#data_table>tbody>tr').html('')")
        self.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))
        temp_css = utils.get_record_by_attr(self.driver, 'table#data_table>tbody>tr', 'order-list-id',
                                            fastline_orders[0].order_id)
        check_css = temp_css + '>td.td-opera>a[title="检票"]'
        self.driver.find_element_by_css_selector(check_css).click()
        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))).click()
        '''
        WebDriverWait(self.driver, 5).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0')))
        sleep(2)
        '''
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        we_manage = self.driver.find_element_by_css_selector('iframe[src="/flightsOrderManager.do"]')
        self.driver.switch_to.frame(we_manage)
        sleep(2)
        complete_css = temp_css + '>td.td-opera>a[title="完单"]'
        self.driver.find_element_by_css_selector(complete_css).click()
        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))).click()
        '''
        WebDriverWait(self.driver, 5).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0')))
        sleep(2)
        '''
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        self.driver.switch_to.frame(we_manage)
        sleep(1)
        self.driver.execute_script("$('table#data_table>tbody>tr').html("")")
        self.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))
        status_css = temp_css + '>td:nth-child(11)'
        self.assertEqual(self.driver.find_element_by_css_selector(status_css).text, '已完成')
