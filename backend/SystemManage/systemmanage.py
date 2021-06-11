import globalvar
import utils
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from SystemManage.test_user_manage import TestUserManage
from selenium.webdriver.support.select import Select
from utils import FoundRecordError
from time import sleep


def get_user_attr(driver, user):
    """"
    获取系统用户属性
    """

    attr_dict = {}
    if "sysbbxuser.do" in globalvar.opened_window_pool:
        utils.switch_exist_frame(driver, "sysbbxuser.do", "用户管理")
    else:
        TestUserManage.setUpClass()

    we_username = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userName')))
    we_username.clear()
    we_username.send_keys(user)
    driver.find_element_by_css_selector('#btnQuery').click()
    try:
        we_tds = WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'table#bbxuser_table>tbody>tr>td')))
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


def set_user_available(driver, user):
    if "sysbbxuser.do" in globalvar.opened_window_pool:
        utils.switch_exist_frame(driver, "sysbbxuser.do", "用户管理")
    else:
        TestUserManage.setUpClass()

    we_username = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#userName')))
    we_username.clear()
    we_username.send_keys(user)
    driver.find_element_by_css_selector('#btnQuery').click()
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#bbxuser_table>tbody>tr')))
#    driver.find_element_by_css_selector('a.modify').click()
    utils.select_operation_by_field(driver, 'table#bbxuser_table', '登录账号', user, '修改')
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/sysbbxuser.do?method=infoBbxuser"]')))
    status_sel = driver.find_element_by_css_selector('#status')
    Select(status_sel).select_by_visible_text('可用')
    driver.find_element_by_css_selector('#btnSave').click()
    driver.switch_to.parent_frame()
    sleep(2)


