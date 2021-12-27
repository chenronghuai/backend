from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import traceback
import log
import sys
import utils
import globalvar
from selenium.webdriver.support.select import Select
from utils import FoundRecordError


class FuncUserManage:
    temp_order_pool = []

    def __init__(self):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '系统管理', '用户管理', 'sysbbxuser.do')

    def query(self, **kwargs):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnQuery')))

        we_role_name = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#roleName')
        we_role_name.clear()
        we_user_account = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#userName')
        we_user_account.clear()
        we_user_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#userPhone')
        we_user_phone.clear()
        we_user_name = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#userNik')
        we_user_name.clear()

        for k, v in kwargs.items():
            if k == 'role_name':
                we_role_name.send_keys(v)
            elif k == 'account':
                we_user_account.send_keys(v)
            elif k == 'phone':
                we_user_phone.send_keys(v)
            elif k == 'name':
                we_user_name.send_keys(v)
            else:
                log.logger.debug(f'{v}--不支持的查询参数')
                raise IndexError
        globalvar.GLOBAL_DRIVER.execute_script('$("#bbxuser_table>tbody").html("")')
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(lambda x: len(x.find_elements_by_css_selector(
            '#bbxuser_table>tbody>tr>td')) > 1)
        sleep(1)

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
        utils.select_operation_by_field(globalvar.GLOBAL_DRIVER, 'table#bbxuser_table', '登录账号', user, '修改', '操作')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/sysbbxuser.do?method=infoBbxuser"]')))
        status_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#status')
        Select(status_sel).select_by_visible_text('可用')
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(2)

    def set_user_attr(self, *args, **kwargs):
        self.query(account=args[0])
        utils.select_operation_by_field(globalvar.GLOBAL_DRIVER, '#bbxuser_table', '登录账号', args[0], '修改', '操作')
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/sysbbxuser.do?method=infoBbxuser"]')))
            for k, v in kwargs.items():
                if k == 'available':
                    available_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#status')
                    Select(available_sel).select_by_visible_text(v)
                elif k == 'customer_phone':
                    c_phone_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#showPhone')
                    Select(c_phone_sel).select_by_visible_text(v)
                elif k == 'driver_phone':
                    d_phone_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#showDriverPhone')
                    Select(d_phone_sel).select_by_visible_text(v)
                else:
                    log.logger.debug(f'{v}--不支持的修改参数')
                    raise IndexError
        except:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnEsc').click()
        else:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
            return utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
        finally:
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()

    def add_user(self, name, phone, center, role):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                          '#addBtn'))).click()
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/sysbbxuser.do?method=infoBbxuser&pagetype=add"]')))
            we_user_name = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#userNik')
            we_user_name.clear()
            we_user_name.send_keys(name)

            we_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#phone')
            we_phone.clear()
            we_phone.send_keys(phone)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#userName').click()
            try:  # 处理电话号码已经存在的情形
                WebDriverWait(globalvar.GLOBAL_DRIVER, 2).until(EC.visibility_of_element_located((
                    By.CSS_SELECTOR, 'div.layui-layer-content')))
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnEsc').click()
                globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
                return '该电话号码已存在！'
            except:
                pass

            try:
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnChoose').click()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, '[src^="/sysbbxuser.do?method=toUserInfoRolePage&pagetype=add"]')))
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selCenter').click()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname="' + center + '"]'))).click()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                            '#btnChoose'))).click()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                                  'table>tbody#role-list>tr')))
                record_locator = utils.get_record_by_field_value(globalvar.GLOBAL_DRIVER, 'div.table.hTable>table',
                                                              '角色名称', role)
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector(record_locator + '>td:nth-child(1)').click()
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()

            finally:
                globalvar.GLOBAL_DRIVER.switch_to.parent_frame()

            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
            globalvar.GLOBAL_DRIVER.switch_to.default_content()
            try:
                result_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((
                    By.CSS_SELECTOR, '.layui-layer-content.layui-layer-padding'))).text
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('a.layui-layer-btn0').click()
                return result_text
            finally:
                globalvar.GLOBAL_DRIVER.switch_to.frame(globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, 'iframe[src="/sysbbxuser.do"]'))
        except:
            traceback.print_tb(sys.exc_info()[2])

    def del_user(self, name):
        self.query(name=name)
        try:
            record_locator = utils.get_record_by_field_value(globalvar.GLOBAL_DRIVER, '#bbxuser_table', '用户姓名', name)
        except NoSuchElementException:
            log.logger.debug(f'{name}--该账号查无记录！')
            raise IndexError
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector(record_locator).click()
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#deleteBtn').click()
        globalvar.GLOBAL_DRIVER.switch_to.default_content()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                          'a.layui-layer-btn0'))).click()
        globalvar.GLOBAL_DRIVER.switch_to.frame(globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, 'iframe[src="/sysbbxuser.do"]'))
        result_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
        return result_text