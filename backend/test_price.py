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
import test_customer_call, test_inter_center, test_order_manage, login
from MonitorManage.func_customer_call import FuncCustomerCall
from sys import argv
import log


@ddt
class TestPrice(unittest.TestCase, metaclass=TestMeta):
    temp_order_pool = []

    @classmethod
    def setUpClass(cls):
#        cls.driver = globalvar.get_value('driver')
        cls.temp_order_pool = globalvar.order_pool
        globalvar.order_pool.clear()
        cls.__name__ = cls.__name__ + "（价格相关：修改价格）"

    @classmethod
    def tearDownClass(cls):
        globalvar.order_pool = cls.temp_order_pool

    @data('3.3',)
    def test_modify_price(self, price):
        try:
            utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
            cu = FuncCustomerCall()
            sleep(1)
            cu.getUserInfo("66666663")
            cu.selectOrderType('城际拼车')
            cu.input_customer_phone("66666663")
            cu.selectInterOrigin("XM", "厦门市|XMCJ", "软件园二期")
            cu.selectInterDestination("XM", "观日路24号")
            cu.selectDate('', '')
            cu.selectPCount(1)
            ori, des = cu.get_ori_des()
            cu.commit()
            i = cu.checkitem("拼车", ori, des, "66666663")
            cu.save_order(i, OrderType.CARPOOLING)
            utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
            utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#callOrderPage>table', '#callOrderPage>table>tbody>tr', 'order-id', globalvar.order_pool[0].order_id, '改价')
            utils.modify_price(globalvar.GLOBAL_DRIVER, price)
            we_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#phone')
            we_phone.clear()
            we_phone.send_keys('66666663')
            globalvar.GLOBAL_DRIVER.execute_script("$('#callOrderPage>table>tbody>tr').html('')")
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#query_all'))).click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#callOrderPage>table>tbody>tr')))
            order_css = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, '#callOrderPage>table>tbody>tr', 'order-id', globalvar.order_pool[0].order_id)
            index = re.search(r'.+child\((\d+)\)', order_css).group(1)
            self.assertIn(price, utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#callOrderPage>table', index, 8))
        finally:
            utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#callOrderPage>table', '#callOrderPage>table>tbody>tr',
                                           'order-id', globalvar.order_pool[0].order_id, '消单')
            utils.cancel_order(globalvar.GLOBAL_DRIVER, '联系不上司机', 'customerCall.do')
