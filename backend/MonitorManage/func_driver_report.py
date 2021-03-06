from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, strftime
import log
from selenium.common.exceptions import TimeoutException
import utils
import globalvar
import re
from common import Driver


class FuncDriverReport:

    is_phone = True

    def __init__(self):
        self.driver = globalvar.get_value('driver')
        utils.make_sure_driver(self.driver, '监控管理', '司机报班', '司机报班', 'driverReport.do')

    def report_action(self, ori_val, des_val):
        WebDriverWait(self.driver, 5).until(lambda x: x.find_element_by_id('driverUid').get_attribute('value') != '')
        self.driver.execute_script('$("#sel_origin").val("' + ori_val + '")')
        self.driver.execute_script('$("#sel_destination").val("' + des_val + '")')
        sleep(2)
        self.driver.find_element_by_css_selector('#report').click()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))

    def driver_report_by_phone(self, phone, ori_val, des_val):
        e_phone = self.driver.find_element_by_css_selector('#phone')
        e_phone.clear()
        self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        e_phone.send_keys(phone)
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))  # 等待蒙层消失
        self.driver.find_element(By.CSS_SELECTOR, '#query_driver').click()
        try:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody>tr')))
        except TimeoutException:  # except语句没有作用
            log.logger.error(f'列表找不到号码为{phone}的司机')
            raise ValueError
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'tbody>tr>td:nth-child(15)>a[name="btnReport"]')))
        self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(15)>a[name="btnReport"]').click()
        self.report_action(ori_val, des_val)

        # 添加司机进池
        driver_id = self.driver.find_element_by_css_selector('tbody>tr').get_attribute('data-uid')
        license_text = self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(11)').text
        max_user = int(re.search(r'(\d+)\D+(\d+)\D+', license_text).group(1))
        max_package = int(re.search(r'(\d+)\D+(\d+)\D+', license_text).group(2))
        car_type = self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(7)').text
        oc_center = self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(14)').text
        driver = Driver(driver_id, max_user, max_package, car_type, oc_center)
        globalvar.add_driver(driver)
        return self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(10)').text

    def driver_report_by_carnum(self, carnum, phone, ori_val, des_val):
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
            log.logger.error(f'找不到该车牌{carnum}关联的任何司机')
            return None
        records = self.driver.find_elements_by_css_selector('table#data_table>tbody>tr')
        for i in range(1, len(records)+1):
            css = '#data_table>tbody>tr:nth-child(%s)>td:nth-child(5)' % i
            if self.driver.find_element_by_css_selector(css).text == phone:
                self.b_driver = True
                css_report = '#data_table>tbody>tr:nth-child(%s)>td:nth-child(15)>a[name="btnReport"]' % i
                self.driver.find_element_by_css_selector(css_report).click()
                break
        if not self.b_driver:
            return '找不到该车牌和电话号码关联的司机'

        self.report_action(ori_val, des_val)

        # 添加司机进池
        css_record = 'tbody>tr:nth-child({})'.format(i)
        driver_id = self.driver.find_element_by_css_selector(css_record).get_attribute('data-uid')
        license_text = self.driver.find_element_by_css_selector(css_record+'>td:nth-child(11)').text
        max_user = int(re.search(r'(\d+)\D+(\d+)\D+', license_text).group(1))
        max_package = int(re.search(r'(\d+)\D+(\d+)\D+', license_text).group(2))
        car_type = self.driver.find_element_by_css_selector(css_record+'>td:nth-child(7)').text
        oc_center = self.driver.find_element_by_css_selector(css_record+'>td:nth-child(14)').text
        driver = Driver(driver_id, max_user, max_package, car_type, oc_center)
        globalvar.add_driver(driver)
        css_goal = css_record+'>td:nth-child(10)'
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
        driver_id = self.driver.find_element_by_css_selector('tbody>tr').get_attribute('data-uid')
        self.driver.switch_to.parent_frame()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn- > a.layui-layer-btn0'))).click()
        self.driver.switch_to.frame(self.driver.find_element_by_css_selector('iframe[src="/driverReport.do"]'))

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        cancel_driver = globalvar.get_driver(driver_id)
        globalvar.del_driver(cancel_driver)
        return self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(10)').text