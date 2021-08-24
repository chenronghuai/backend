import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt
import utils
from utils import TestMeta
import globalvar
from selenium.webdriver.support.select import Select
from utils import FoundRecordError


class FuncUserManage:
    temp_order_pool = []

#    def __init__(self):
#        self.driver = globalvar.get_value('driver')

    def get_user_attr(self, user):
        """
        获取系统用户属性
        :param user: 用户账号名称（字符串）
        :return:
        """
        attr_dict = {}
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '系统管理', '用户管理', 'sysbbxuser.do')

        we_username = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userName')))
        we_username.clear()
        we_username.send_keys(user)
        globalvar.GLOBAL_DRIVER.execute_script("$('table#bbxuser_table>tbody>tr').html('')")
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
        try:
            we_tds = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
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
        """
        设置用户可用
        :param user: 用户账号名称（字符串）
        :return:
        """
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '系统管理', '用户管理', 'sysbbxuser.do')
        we_username = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userName')))
        we_username.clear()
        we_username.send_keys(user)
        globalvar.GLOBAL_DRIVER.execute_script('$("table#bbxuser_table>tbody").html("")')
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#bbxuser_table>tbody>tr')))
        utils.select_operation_by_field(globalvar.GLOBAL_DRIVER, 'table#bbxuser_table', '登录账号', user, '修改')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/sysbbxuser.do?method=infoBbxuser"]')))
        status_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#status')
        Select(status_sel).select_by_visible_text('可用')
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(2)
