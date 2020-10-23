import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, strftime
import datetime
from selenium import webdriver
from ddt import ddt, data, file_data, unpack
import utils
import globalvar


@ddt
class TestCustomerCall(unittest.TestCase):
    '''
    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '监控管理', '客户来电', 'customerCall.do')
     '''
    def __init__(self):
        self.driver = globalvar.get_value('driver')
        utils.switch_frame(self.driver, '监控管理', '客户来电', 'customerCall.do')

    def getUserInfo(self, phone):
        self.driver.execute_script("$('#userTypeDiv').html('')")
        we_number = self.driver.find_element_by_css_selector("#phone")
        we_number.clear()
        we_number.send_keys(phone)
        self.driver.find_element_by_css_selector("#query_all").click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#userTypeDiv')))
        return True

    def test_driver_report_by_carnum(self):
        report_status = self.getUserInfo(13328775856)
        self.assertEqual(report_status, True)


