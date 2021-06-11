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
from selenium.webdriver.support.select import Select
from utils import FoundRecordError


@ddt
class TestUserManage(unittest.TestCase, metaclass=TestMeta):
    temp_order_pool = []

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '系统管理', '用户管理', 'sysbbxuser.do')
        globalvar.opened_window_pool.append('sysbbxuser.do')

    @classmethod
    def tearDownClass(cls):
        pass

    def get_user_attr(self, user):
        """"
        获取系统用户属性
        """

        attr_dict = {}
        if "sysbbxuser.do" in globalvar.opened_window_pool:
            utils.switch_exist_frame(self.driver, "sysbbxuser.do", "用户管理")
        else:
            TestUserManage.setUpClass()

        we_username = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userName')))
        we_username.clear()
        we_username.send_keys(user)
        self.driver.find_element_by_css_selector('#btnQuery').click()
        try:
            we_tds = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'table#bbxuser_table>tbody>tr>td')))
            fields_value = []
            for i in we_tds:
                fields_value.append(i.text)
            attr_dict['role'] = fields_value[5]
            attr_dict['status'] = fields_value[6]
            attr_dict['mobilelogin'] = fields_value[7]
            attr_dict['superservice'] = fields_value[8]
            attr_dict['customerphone'] = fields_value[9]
            attr_dict['driverphone'] = fields_value[10]
        except:
            raise FoundRecordError
        return attr_dict

    def set_user_available(self, user):
        if "sysbbxuser.do" in globalvar.opened_window_pool:
            utils.switch_exist_frame(self.driver, "sysbbxuser.do", "用户管理")
        else:
            TestUserManage.setUpClass()

        we_username = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userName')))
        we_username.clear()
        we_username.send_keys(user)
        self.driver.execute_script('$("table#bbxuser_table>tbody").html("")')
        self.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#bbxuser_table>tbody>tr')))
        utils.select_operation_by_field(self.driver, 'table#bbxuser_table', '登录账号', user, '修改')
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/sysbbxuser.do?method=infoBbxuser"]')))
        status_sel = self.driver.find_element_by_css_selector('#status')
        Select(status_sel).select_by_visible_text('可用')
        self.driver.find_element_by_css_selector('#btnSave').click()
        self.driver.switch_to.parent_frame()
        sleep(2)
