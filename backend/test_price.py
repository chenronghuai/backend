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
from PaVManage.func_line import FuncLine
import test_customer_call, test_inter_center, test_order_manage, login
from MonitorManage.func_customer_call import FuncCustomerCall
from sys import argv
import log


@ddt
class TestPrice(unittest.TestCase, metaclass=TestMeta):
    temp_order_pool = []

    @classmethod
    def setUpClass(cls):
        cls.temp_order_pool = globalvar.order_pool
        globalvar.order_pool.clear()
        cls.__name__ = cls.__name__ + "（杂项：修改价格、身份认证）"

    @classmethod
    def tearDownClass(cls):
        globalvar.order_pool = cls.temp_order_pool

    @data('3.3',)
    def test_modify_price(self, price):
        try:
            utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
            cu = FuncCustomerCall()
            sleep(1)
            cu.get_user_info(globalvar.CLASSIC_PHONE_NUMBER)
            cu.select_order_type('城际拼车')
            cu.input_customer_phone(globalvar.CLASSIC_PHONE_NUMBER)
            cu.selectInterOrigin("XM", "厦门市|XMCJ", "软件园二期")
            cu.selectInterDestination("XM", "观日路24号")
            cu.selectDate('', '')
            cu.selectPCount(1)
            if globalvar.get_value('INTER_AUTH_FLAG') == '是':
                cu.add_passenger_auth()
            ori, des = cu.get_ori_des()
            cu.commit()
            i = cu.checkitem("拼车", ori, des, globalvar.CLASSIC_PHONE_NUMBER)
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

    @data(globalvar.INTERLINE_ID,)
    def test_line_auth(self, line_id):
        try:
            setattr(self, 'MODIFY_FLAG', False)
            lm = FuncLine()
            lm.queryLine(line_num=line_id)
            utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr',
                                           'data-line-id', line_id, '修改')
            # 以下确保线路开启身份认证
            if '否' == lm.get_inter_line_attr()['auth']:
                lm.queryLine(line_num=line_id)
                utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr',
                                               'data-line-id', line_id, '修改')
                lm.modifyInterLine(identity_auth='是')
                setattr(self, 'MODIFY_FLAG', True)

            cu = FuncCustomerCall()
            sleep(1)
            cu.get_user_info(globalvar.CLASSIC_PHONE_NUMBER)
            cu.select_order_type('城际拼车')
            cu.input_customer_phone(globalvar.CLASSIC_PHONE_NUMBER)
            cu.selectInterOrigin("XM", "厦门市|XMCJ", "软件园二期")
            cu.selectInterDestination("XM", "望海路59号")
            cu.selectDate('', '')
            cu.selectPCount(1)
            cu.add_passenger_auth()
            ori, des = cu.get_ori_des()
            msg_text = cu.commit()
            i = cu.checkitem("拼车", ori, des, globalvar.CLASSIC_PHONE_NUMBER)
            cu.save_order(i, OrderType.CARPOOLING)
            utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#data_table',
                                           '#data_table>tbody>tr',
                                           'order-list-id', globalvar.order_pool[1].order_id, '消单')
            utils.cancel_order(globalvar.GLOBAL_DRIVER, '联系不上司机', 'customerCall.do')
            self.assertEqual('提交订单成功!', msg_text)
        except:
            assert False
        finally:
            if getattr(self, 'MODIFY_FLAG', False):
                utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '人员车辆管理', '线路管理', 'line.do')
                lm.queryLine(line_num=line_id)
                utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr',
                                               'data-line-id', line_id, '修改')
                lm.modifyInterLine(identity_auth='否')


