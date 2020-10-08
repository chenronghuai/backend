import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, strftime
import datetime
from selenium import webdriver
from ddt import ddt, data, file_data, unpack
import utils
import login

@ddt
class TestDriverReport(unittest.TestCase):

    is_phone = True
    @classmethod
    def setUpClass(cls):
        cls.driver = login.login('HTTP', 'USER')
        utils.switch_frame(cls.driver, '监控管理', '司机报班', 'driverReport.do')

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def report_action(self):
        ori = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName')))
        '''
        等DOM树加载了suggest条目，再点击起始方位
        '''
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#startName-suggest>div')))
        ori.click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest')))
        ori.send_keys('XM')
        WebDriverWait(self.driver, 5).until(EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_origin'), "361000"))
        des = self.driver.find_element_by_css_selector('#endsName')
        '''
        等DOM树加载了suggest条目，再点击终点方位
        '''
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
        des.click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#endsName-suggest')))
        des.send_keys('XM')
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_destination'), "361000"))
        self.driver.find_element_by_css_selector('#report').click()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')
        #        self.driver.execute_script('layer.load(3, {shade: [0.5,"#fff"]})')
#        WebDriverWait(self.driver, 30).until(lambda s: s.execute_script("return jQuery.active == 0"))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        if self.is_phone:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#query_driver'))).click()
        else:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#query_carno'))).click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))
#        sleep(5)  # 等待蒙层消失

    def driver_report_by_phone(self, phone):
        e_phone = self.driver.find_element_by_css_selector('#phone')
        e_phone.clear()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        e_phone.send_keys(phone)
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#query_driver'))).click()
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
        e_carnum = self.driver.find_element_by_css_selector('#selCar')
        e_carnum.clear()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
#        self.driver.execute_script("$('#selCar-suggest').html('')")
        e_carnum.send_keys(carnum)
#        sleep(1)
#        e_carnum.click()
#        WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[text="' + carnum + '"]'))).click()
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        self.driver.find_element_by_css_selector('#query_carno').click()  # 车牌查询
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr'))
            )
        except:
            return '找不到该车牌关联的任何司机'
#        sleep(1)  # 等待遮挡层消失，否则”报班“按钮接收不到点击事件？暂无更好办法
        records = self.driver.find_elements_by_css_selector('table#data_table>tbody>tr')
        for i in range(len(records)):
            css = '#data_table>tbody>tr:nth-child(%s)>td:nth-child(5)' % (i + 1)
            if self.driver.find_element_by_css_selector(css).text == phone:
                css_report = '#data_table>tbody>tr:nth-child(%s)>td:nth-child(15)>a[name="btnReport"]' % (i + 1)
                self.driver.find_element_by_css_selector(css_report).click()
                break
        self.report_action()
        css_goal = 'tbody>tr:nth-child(%s)>td:nth-child(10)' % (i + 1)
        return self.driver.find_element_by_css_selector(css_goal).text

    def driver_cancel_report(self, phone):
        e_phone = self.driver.find_element_by_css_selector('#phone')
        e_phone.clear()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        e_phone.send_keys(phone)
        self.driver.find_element_by_css_selector('#query_driver').click()
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody>tr')))
        except:
            return '找不到司机'
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(15)>a:nth-child(2)').click()
        sleep(1)
        self.driver.switch_to.parent_frame()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn- > a.layui-layer-btn0'))).click()
        sleep(2)  # 等待蒙层消失
        self.driver.switch_to.frame(self.driver.find_element_by_css_selector('iframe[src="/driverReport.do"]'))
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')
#        self.driver.find_element_by_css_selector('#query_driver').click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#query_driver'))).click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))
        return self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(10)').text

#    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\driver_report_phone.json')
    def test_driver_report_by_phone(self, phone):
        report_status = self.driver_report_by_phone(phone)
        self.assertEqual(report_status, '报班')

    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\driver_report_carnum.json')
    def test_driver_report_by_carnum(self, carnum, phone):
        report_status = self.driver_report_by_carnum(carnum, phone)
        self.assertEqual(report_status, '报班')

#    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\driver_report_phone.json')
    def test_driver_zcancel_report(self, phone):
        report_status = self.driver_cancel_report(phone)
        self.assertEqual(report_status, '未报班')

