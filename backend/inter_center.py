import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, strftime
import time
from selenium.webdriver.support.select import Select
from ddt import ddt, data, file_data, unpack
import utils
from utils import TestMeta
import globalvar


@ddt
class TestInterCenter(unittest.TestCase, metaclass=utils.TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '监控管理', '城际调度中心', 'orderCenterNew.do')

    def input_center_line(self, center, origin, ori_value, destination, des_value):
        self.driver.execute_script(
            "$('div.fs-dropdown.hidden>div.fs-options>div').each(function(ind,obj){if($(this).hasClass('selected')){$(this).click();}})")
        self.driver.execute_script(
            "$('div.fs-dropdown.hidden>div.fs-options>div>div.fs-option-label').filter(function(index){return $(this).text()=='" + center + "';}).click()")
        we_ori = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName')))
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#startName-suggest>div')))
        we_ori.click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest')))
        we_ori.send_keys(origin)
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_origin'), ori_value))
        we_des = self.driver.find_element_by_css_selector('#endsName')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
        we_des.click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'endsName-suggest')))
        we_des.send_keys(destination)
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_destination'), des_value))
        self.driver.find_element_by_css_selector('div#ipt_line_query').click()

    def appoint_order(self, order_id, driver_id):
        self.driver.find_element_by_css_selector('#orderList').click()
        self.driver.execute_script('$("#tdy_driver_queue>tr").html("")')
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#order-nav-query>span'))
        ).click()  # 点击查询
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#orderImmediately>table>tbody>tr')))
        records = self.driver.find_elements_by_css_selector('#orderImmediately>table>tbody>tr')

        for i in range(1, len(records) + 1):
            if records[i - 1].get_attribute('order-id') == order_id:
                css = '#tdy_driver_queue>tr:nth-child({})>td.td-opera>a[name="order-list-appoint"]'.format(i)
                self.driver.find_element_by_css_selector(css).click()
                WebDriverWait(self.driver, 5).until(
                    EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/orderCtrl.do"]')))
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '#intercity-lists>tr')))
                drivers = self.driver.find_elements_by_css_selector('#intercity-lists>tr>td:nth-child(1)>input')

                for j in range(len(drivers)):
                    if drivers[j].get_attribute('driver_id') == driver_id:
                        if len(drivers) > 1:
                            focus_driver_css = '#intercity-lists>tr:nth-child({})>td:nth-child(1)'.format(j + 1)
                        elif len(drivers) == 1:
                            focus_driver_css = '#intercity-lists>tr>td:nth-child(1)'
                        self.driver.find_element_by_css_selector(focus_driver_css).click()
                        sleep(1)
                        self.driver.find_element_by_css_selector('#todoSaveBtn').click()
                        '''加下面代码块将导致无法切换到91行“已派”页，不知原因
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
                        WebDriverWait(self.driver, 5).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
                        '''
                        break

                    elif j == len(drivers) - 1:
                        self.driver.find_element_by_css_selector('#todoExitBtn').click()
                self.driver.switch_to.parent_frame()
                break

    @file_data('.\\testcase\\appoint_carpooling.json')
    def test_carpooling(self, center, origin, ori_value, destination, des_value):
        self.input_center_line(center, origin, ori_value, destination, des_value)
        self.appoint_order(globalvar.get_value('carpooling_order_id'), globalvar.get_value('carpooling_driver_id'))
        sleep(2)
        self.driver.find_element_by_css_selector('div.nav-right.td-opera > a[title="已派"]').click()
        sleep(1)
        appointed_orders = self.driver.find_elements_by_css_selector('#orderImmediately>table>tbody#tdy_driver_queue>tr')
        id_list = [x.get_attribute('order-id') for x in appointed_orders]
        return True if globalvar.get_value('carpooling_order_id') in id_list else False

