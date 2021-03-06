import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
import log
from utils import OrderType, DriverType, OrderStatus, FoundDriverError
from utils import TestMeta
import globalvar
import test_customer_call, test_inter_center, test_order_manage, login
from sys import argv
from SystemManage.func_user_manage import FuncUserManage
from SystemManage.func_oc_manage import FuncOcManage
from MonitorManage.func_customer_call import FuncCustomerCall
from MonitorManage.func_inter_center import FuncInterCenter


@ddt
class TestPermission(unittest.TestCase, metaclass=TestMeta):

    temp_order_pool = []

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        cls.temp_order_pool = globalvar.order_pool
        globalvar.order_pool.clear()
        cls.__name__ = cls.__name__ + "（权限管理：运营中心订单共享权限，订单管理中账号线路权限、订单完成车队权限）"

    @classmethod
    def tearDownClass(cls):
        utils.switch_exist_frame(cls.driver, 'customerCall.do', '客户')
        we_phone = cls.driver.find_element_by_css_selector('#phone')
        we_phone.clear()
        we_phone.send_keys('66666663')
        WebDriverWait(cls.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#query_all'))).click()
        WebDriverWait(cls.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#callOrderPage>table>tbody>tr')))
        for order in globalvar.order_pool:
            utils.select_operation_by_attr(cls.driver, '#callOrderPage>table', '#callOrderPage>table>tbody>tr',
                                           'order-id', order.order_id, '消单')
            utils.cancel_order(cls.driver, '联系不上司机')

        globalvar.order_pool = cls.temp_order_pool

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data(['厦门运营中心', '物流中心', True], ['厦门运营中心', '物流中心', False])
    @unpack
    def test_oc_share(self, share_src, share_to, share_flag):
        om = getattr(self, 'om', FuncOcManage())

        try:
            om.share_setup(share_src, share_to, share_flag)
            utils.make_sure_driver(self.driver, '监控管理', '客户来电', '客户', 'customerCall.do')
            '''
            if 'customerCall.do' in globalvar.opened_window_pool:
                utils.switch_exist_frame(om.driver,  'customerCall.do', '客户')
            else:
                test_customer_call.TestCustomerCall.setUpClass()
            '''
            cu = FuncCustomerCall()
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

            ic = FuncInterCenter()
            if 'orderCenterNew.do' in globalvar.opened_window_pool:
                utils.switch_exist_frame(om.driver, 'orderCenterNew.do', '城际调度')
                # 切换到“物流中心”
                ic.input_center_line("物流中心", "XMC", "361000", "XM", "361000")
            else:
                ic.setup_oc()
            
            WebDriverWait(om.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#orderList'))).click()
            om.driver.find_element_by_css_selector('#order-nav-query').click()
            sleep(0.5)
            om.driver.find_element_by_css_selector('div.nav-right.td-opera > a[title="即时"]').click()
            try:
                records = WebDriverWait(om.driver, 5).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#orderImmediately>table>tbody>tr')))
            except:
                records = []
            id_list = []
            for record in records:
                id_list.append(record.get_attribute('order-id'))
            if share_flag:
                self.assertTrue(globalvar.order_pool[-1].order_id in id_list)
            else:
                self.assertTrue(globalvar.order_pool[-1].order_id not in id_list)
        finally:
            utils.switch_exist_frame(om.driver, 'operations-center.do', '运营中心管理')
            om.restore(share_src, share_to)
            sleep(2)

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data(['USER3', True], ['USER4', True], ['USER3', False], ['USER4', False])
    @unpack
    def test_order_filter(self, user, flag):
        # 确认用户账号是否可用，不可用时置为可用
        sm = getattr(self, 'sm', FuncUserManage())
        om = getattr(self, 'om', FuncOcManage())
        user_attr_dict = sm.get_user_attr(utils.read_config_value(user, 'username'))
        if user_attr_dict['status'] in ['锁定', '不可用']:
            sm.set_user_available(utils.read_config_value(user, 'username'))
        # 切回运营中心页面
        utils.switch_exist_frame(globalvar.get_value('driver'), 'operations-center.do', '运营中心管理')
        temp_driver = globalvar.get_value('driver')
        new_driver = login.login('TEST', user)
        try:
            om.share_setup('厦门运营中心', '物流中心', flag)
            utils.switch_frame(new_driver, '监控管理', '订单管理', 'orderManage.do')
            WebDriverWait(new_driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnQuery'))).click()
            records = WebDriverWait(new_driver, 5).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'table>tbody>tr')))
            id_list = [x.get_attribute('order-list-id') for x in records]
            line_list = str(utils.read_config_value(user, 'line_own')).split(',')
            if flag:
                if '厦门市到厦门市' in line_list:
                    self.assertTrue(globalvar.order_pool[-1].order_id in id_list)
                else:
                    self.assertTrue(globalvar.order_pool[-1].order_id not in id_list)
            else:
                self.assertTrue(globalvar.order_pool[-1].order_id not in id_list)
        finally:
            new_driver.quit()
            globalvar.set_value('driver', temp_driver)
            om.restore('厦门运营中心', '物流中心')





