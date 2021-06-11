import unittest
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
from utils import OrderType, DriverType, OrderStatus, FoundDriverError
from utils import TestMeta
import globalvar
import oc_manage, customer_call, inter_center, order_manage, login
from sys import argv


@ddt
class TestPrice(unittest.TestCase, metaclass=TestMeta):
    temp_order_pool = []

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        cls.temp_order_pool = globalvar.order_pool
        globalvar.order_pool.clear()
        cls.__name__ = cls.__name__ + "（价格相关：修改价格）"

    @classmethod
    def tearDownClass(cls):
        globalvar.order_pool = cls.temp_order_pool

    @data('3.3',)
    def test_modify_price(self, price):
        try:
            if 'customerCall.do' in globalvar.opened_window_pool:
                utils.switch_exist_frame(self.driver,  'customerCall.do', '客户')
            else:
                customer_call.TestCustomerCall.setUpClass()
            cu = customer_call.TestCustomerCall()
            sleep(1)
            cu.getUserInfo("66666663")
            cu.selectOrderType('城际拼车')
            cu.input_customer_phone("66666663")
            cu.selectInterOrigin("XM", "厦门市|XMCJ", "软件园二期")
            cu.selectInterDestination("XM", "观日路24号")
            cu.selectDate('', '')
            cu.selectPCount(1)
            cu.commit()

            i = cu.checkitem("拼车")
            cu.save_order(i, OrderType.CARPOOLING)
            utils.select_operation_by_attr(self.driver, '#callOrderPage>table', '#callOrderPage>table>tbody>tr', 'order-id', globalvar.order_pool[0].order_id, '改价')
            utils.modify_price(self.driver, price)
            we_phone = self.driver.find_element_by_css_selector('#phone')
            we_phone.clear()
            we_phone.send_keys('66666663')
            self.driver.execute_script("$('#callOrderPage>table>tbody>tr').html('')")
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#query_all'))).click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#callOrderPage>table>tbody>tr')))
            order_css = utils.get_record_by_attr(self.driver, '#callOrderPage>table>tbody>tr', 'order-id', globalvar.order_pool[0].order_id)
            index = re.search(r'.+child\((\d+)\)', order_css).group(1)
            self.assertIn(price, utils.get_cell_content(self.driver, '#callOrderPage>table', index, 8))
        finally:
            utils.select_operation_by_attr(self.driver, '#callOrderPage>table', '#callOrderPage>table>tbody>tr',
                                           'order-id', globalvar.order_pool[0].order_id, '消单')
            utils.cancel_order(self.driver, '联系不上司机')