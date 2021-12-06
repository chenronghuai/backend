import utils
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By
from time import sleep
from sys import argv
import globalvar
import log
import sys
import traceback


class FuncCustomerQuery:

    def __init__(self):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '客户管理', '客户查询', 'user_manage.do')

    def query(self, **kwargs):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnQuery')))
        we_user_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#phone')
        we_user_phone.clear()
        we_user_name = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#userName')
        we_user_name.clear()

        for k, v in kwargs.items():
            if k == 'phone':
                we_user_phone.send_keys(v)
            elif k == 'name':
                we_user_name.send_keys(v)
            else:
                log.logger.debug(f'{v}--不支持的查询参数')
                raise IndexError
        globalvar.GLOBAL_DRIVER.execute_script('$("#user_table>tbody").html("")')
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                          '#user_table>tbody>tr')))

    def set_black(self, *args):
        self.query(phone=args[0])
        flag = globalvar.GLOBAL_DRIVER.execute_script("return $('#user_table>tbody>tr').attr('is_black')")
        if "0" == flag:
            utils.select_operation_by_field(globalvar.GLOBAL_DRIVER, '#user_table', '手机号码', args[0], '拉黑', '操作')
            try:
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, '[src^="/user_manage.do?method=toDefriendPage"]')))
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                                  '#defriendRadio_1'))).click()
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#todoDefriendBtn').click()
                result_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
                return result_text
            finally:
                globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        else:
            log.logger.debug(f'{args[0]}--该号码已经是拉黑状态！')
            raise IndexError

    def set_white(self, *args):
        self.query(phone=args[0])
        flag = globalvar.GLOBAL_DRIVER.execute_script("return $('#user_table>tbody>tr').attr('is_black')")
        if "0" != flag:
            utils.select_operation_by_field(globalvar.GLOBAL_DRIVER, '#user_table', '手机号码', args[0], '漂白', '操作')
            globalvar.GLOBAL_DRIVER.switch_to.default_content()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
                                                                                              'a.layui-layer-btn0'))).click()
            globalvar.GLOBAL_DRIVER.switch_to.frame(
                globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, 'iframe[src="/user_manage.do"]'))
            result_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
            return result_text
        else:
            log.logger.debug(f'{args[0]}--该号码已经是漂白状态！')
            raise IndexError