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
class TestDriverReport(unittest.TestCase, metaclass=utils.TestMeta):

    is_phone = True

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '监控管理', '司机报班', 'driverReport.do')

    @classmethod
    def tearDownClass(cls):
        pass

    def report_action(self):
        WebDriverWait(self.driver, 5).until(lambda x: x.find_element_by_id('driverUid').get_attribute('value') != '')
        self.driver.execute_script('$("#sel_origin").val("361000")')
        self.driver.execute_script('$("#sel_destination").val("361000")')
        sleep(2)
        self.driver.find_element_by_css_selector('#report').click()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        if self.is_phone:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#query_driver'))).click()
        else:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#query_carno'))).click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))

    def driver_report_by_phone(self, phone):
        e_phone = self.driver.find_element_by_css_selector('#phone')
        e_phone.clear()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        e_phone.send_keys(phone)
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))  # 等待蒙层消失
        self.driver.find_element(By.CSS_SELECTOR, '#query_driver').click()
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody>tr')))
        except:
            return '找不到司机'
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'tbody>tr>td:nth-child(15)>a[name="btnReport"]')))
        self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(15)>a[name="btnReport"]').click()
        self.report_action()
        return self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(10)').text

    def driver_report_by_carnum(self, carnum, phone):
        self.is_phone = False
        self.b_driver = False
        e_carnum = self.driver.find_element_by_css_selector('#selCar')
        e_carnum.clear()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        self.driver.execute_script('$("#selCar").val("' + carnum + '")')
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        self.driver.find_element_by_css_selector('#query_carno').click()  # 车牌查询
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr'))
            )
        except:
            return '找不到该车牌关联的任何司机'
        records = self.driver.find_elements_by_css_selector('table#data_table>tbody>tr')
        for i in range(len(records)):
            css = '#data_table>tbody>tr:nth-child(%s)>td:nth-child(5)' % (i + 1)
            if self.driver.find_element_by_css_selector(css).text == phone:
                self.b_driver = True
                css_report = '#data_table>tbody>tr:nth-child(%s)>td:nth-child(15)>a[name="btnReport"]' % (i + 1)
                self.driver.find_element_by_css_selector(css_report).click()
                break
        if not self.b_driver:
            return '找不到该车牌和电话号码关联的司机'

        self.report_action()
        css_goal = 'tbody>tr:nth-child(%s)>td:nth-child(10)' % (i + 1)
        return self.driver.find_element_by_css_selector(css_goal).text

    def driver_cancel_report(self, phone):
        e_phone = self.driver.find_element_by_css_selector('#phone')
        e_phone.clear()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        e_phone.send_keys(phone)
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        self.driver.find_element_by_css_selector('#query_driver').click()
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody>tr')))
        except:
            return '找不到司机'
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(15)>a:nth-child(2)').click()
        self.driver.switch_to.parent_frame()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn- > a.layui-layer-btn0'))).click()
        self.driver.switch_to.frame(self.driver.find_element_by_css_selector('iframe[src="/driverReport.do"]'))

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
#        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        '''
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#query_driver'))).click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr>td:nth-child(10)')))
        '''
        return self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(10)').text

#    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\driver_report_phone.json')
    def test_driver_report_by_phone(self, phone):
        report_status = self.driver_report_by_phone(phone)
        self.assertEqual(report_status, '报班')

#    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\driver_report_carnum.json')
    def test_driver_report_by_carnum(self, carnum, phone):
        report_status = self.driver_report_by_carnum(carnum, phone)
        self.assertEqual(report_status, '报班')

#    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\driver_report_phone.json')
    def test_driver_zcancel_report(self, phone):
        report_status = self.driver_cancel_report(phone)
        self.assertEqual(report_status, '未报班')

