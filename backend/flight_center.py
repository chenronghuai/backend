import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
from utils import OrderType
from utils import TestMeta
import globalvar
import logging
from sys import argv


logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@ddt
class TestFlightCenter(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver,  '班线管理', '班次调度中心', 'flightsOrderCenter.do')

    def input_center_line(self, center, line):
        self.driver.find_element_by_css_selector('#selCenter').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
        self.driver.find_element_by_css_selector('.fs-label-wrap>.fs-label').click()
        self.driver.execute_script("""
            $('.fs-options>div').each(function(inx, obj){if($(this).hasClass('selected')){$(this).removeClass('selected');}});
           """)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="' + line + '"]'))).click()

    def new_flight_driver(self, center, line, flight_no, driver_team, driver_phone):
        self.driver.find_element_by_css_selector('#selCenter').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
        self.driver.find_element_by_css_selector('#selLine').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname$="' + line + '"]'))).click()

        self.driver.find_element_by_css_selector('#flightsDate').click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.laydate-btns-confirm'))).click()
        self.driver.find_element_by_css_selector('#selFlights').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selFlights-suggest>div[dataname="' + flight_no + '"]'))).click()
        self.driver.find_element_by_css_selector('#chooseDriver').click()
        WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=toChooseFlightsDriver"]')))
        self.driver.find_element_by_css_selector('#selMotorcade').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selMotorcade-suggest>div[dataname$="' + driver_team + '"]'))).click()
        self.driver.find_element_by_css_selector('#phone1').send_keys(driver_phone)
        self.driver.find_element_by_css_selector('#btnQuery').click()
        css = utils.get_record_by_field_value(self.driver, 'table#driver_table', '司机手机', driver_phone)
        self.driver.find_element_by_css_selector(css).click()
        self.driver.find_element_by_css_selector('#btnSave').click()
        self.driver.switch_to.parent_frame()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#driver-lists>tr')))
        self.driver.find_element_by_css_selector('#btnSave').click()
        #如下的等待弹框消失语句，执行后将导致后续的定位出现问题，似乎默认把driver切到最外层？
#        WebDriverWait(self.driver, 5).until(
#            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
#        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        self.driver.switch_to.parent_frame()
        sleep(3)

    def appoint_flight_driver(self, driver_phone):
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#driverPhone'))).send_keys(
            driver_phone)
        self.driver.find_element_by_css_selector('#searchBtn')
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#driver-schedule-list>tr'))).click()
        self.driver.switch_to.parent_frame()
        self.driver.find_element_by_css_selector('div>a.layui-layer-btn0').click()
        sleep(3)

    @unittest.skipIf(argv[3] == 'flow', '流程不跑')
    @data({"center":"漳州运营中心", "line":"高林SM专线", "flight_no":"CS009", "driver_team":"老王测试专用车队", "driver_phone":"13345678966"})
    @unpack
    def test_flight_driver_report(self, center, line, flight_no, driver_team, driver_phone):
        self.input_center_line(center, line)
        self.driver.find_element_by_css_selector('#driverList').click()
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#addDriverSchedule'))).click()
        WebDriverWait(self.driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=editFlightsDriver"]')))
        self.new_flight_driver(center, line, flight_no, driver_team, driver_phone)
        reported_drivers = self.driver.find_elements_by_css_selector('div#intercityDriver>table>tbody#tdy_driver_queue>tr')
        driver_phone_list = []
        for i in range(1, len(reported_drivers)+1):
            driver_phone_list.append(utils.get_cell_content(self.driver, 'div#intercityDriver>table', i, 5))
        status = True if driver_phone in driver_phone_list else False
        self.assertTrue(status)

    test_case = ["漳州运营中心", "高林SM专线", "13345678966"],
    prod_case = ["漳州运营中心", "厦门测试班线", "17700000001"],

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_case if argv[1] == 'HTTP1' else prod_case)
    @unpack
    def test_appoint(self, center, line, driver_phone):
        self.input_center_line(center, line)
        self.driver.find_element_by_css_selector('#orderList').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        fastline_orders = list(filter(lambda x: x.order_type == OrderType.FASTLINE, globalvar.order_pool))
        order_css = utils.get_record_by_attr(self.driver, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr', 'order-id', fastline_orders[0].order_id)
        order_css += '>td.td-opera>a.modify'
        self.driver.find_element_by_css_selector(order_css).click()
        WebDriverWait(self.driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=toAssignOrChangeOrder"]')))
        self.appoint_flight_driver(driver_phone)
        self.driver.execute_script("$('div#orderImmediately>table>tbody#tdy_driver_queue>tr').html("")")
        self.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        status_css = utils.get_record_by_attr(self.driver, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr',
                                             'order-id', fastline_orders[0].order_id)
        status_css += '>td:nth-child(12)'
        self.assertEqual(self.driver.find_element_by_css_selector(status_css).text, '已指派')
