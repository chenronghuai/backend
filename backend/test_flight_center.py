import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
import log
from utils import OrderType, OrderStatus
from utils import TestMeta
import globalvar
from sys import argv
from FlightManage.func_flight_center import FuncFlightCenter


@ddt
class TestFlightCenter(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        cls.__name__ = cls.__name__ + "（班次调度中心：快线司机排班，指派未排班司机即排班，指派快线订单给排班司机，快线司机补网约单、快线单）"
        cls.fc = FuncFlightCenter()

    test_case_report = ["漳州运营中心", "高林SM专线", "老王测试专用车队", "13345678972"],
    prod_case_report = ["漳州运营中心", "厦门测试班线", "测试，禁用", "16666666666"],

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_case_report if argv[1] == 'TEST' else prod_case_report)
    @unpack
    def test_flight_driver_report(self, center, line, driver_team, driver_phone):

        self.fc.input_center_line(center, line)
        self.fc.driver.find_element_by_css_selector('#driverList').click()
        sleep(0.5)
        self.fc.driver.execute_script("$('#addDriverSchedule').click()")
        WebDriverWait(self.fc.driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=editFlightsDriver"]')))
        self.fc.new_flight_driver(center, line, driver_team, driver_phone)
        reported_drivers = WebDriverWait(self.fc.driver, 5).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr')))
        driver_phone_list = []
        for i in range(1, len(reported_drivers) + 1):
            driver_phone_list.append(utils.get_cell_content(self.fc.driver, 'div#intercityDriver>table', i, 5))
        status = True if driver_phone in driver_phone_list else False
        self.assertTrue(status)

    test_case_appoint = ["漳州运营中心", "高林SM专线", "13345678966"],
    prod_case_appoint = ["漳州运营中心", "厦门测试班线", "17700000001"],

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_case_appoint if argv[1] == 'TEST' else prod_case_appoint)
    @unpack
    def test_appoint(self, center, line, driver_phone):
        self.fc.input_center_line(center, line)
        self.fc.driver.find_element_by_css_selector('#orderList').click()
        WebDriverWait(self.fc.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        fastline_orders = list(filter(lambda x: x.order_type == OrderType.FASTLINE and x.order_status == OrderStatus.WAITING, globalvar.order_pool))
        order_css = utils.get_record_by_attr(self.fc.driver, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr', 'order-id', fastline_orders[0].order_id)
        order_css += '>td.td-opera>a.modify'
#        self.driver.find_element_by_css_selector(order_css).click()  # 偶发element is not attached to the page document，与系统自动刷新有关？
        WebDriverWait(self.fc.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, order_css))).click()

        self.fc.appoint_flight_driver(driver_phone)
        self.fc.driver.execute_script("$('div#orderImmediately>table>tbody#tdy_driver_queue>tr').html('')")
        self.fc.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.fc.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        status_css = utils.get_record_by_attr(self.fc.driver, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr',
                                             'order-id', fastline_orders[0].order_id)
        status_css += '>td:nth-child(12)'
        status_text = self.fc.driver.find_element_by_css_selector(status_css).text
        status = True if status_text == '已指派' else False
        if status:
            fastline_orders[0].order_status = OrderStatus.APPOINTED
        self.assertTrue(status)
        log.logger.debug(f'第一个可指派快线订单{fastline_orders[0].order_id}指派后状态为：{fastline_orders[0].order_status}')

    @data(OrderType.CARPOOLING, OrderType.FASTLINE)
    def test_add_order(self, order_type):
        order_ = utils.get_first_order(order_type)
        driver_ = self.fc.filter_bus_driver(order_)
        if argv[1] == 'TEST':
            self.fc.input_center_line('漳州运营中心', '高林SM专线')
        else:
            self.fc.input_center_line('漳州运营中心', '厦门测试班线')
        driver_css = self.fc.search_extract_driver(driver_)  # 不可直接使用filter_bus_driver得到的司机，因为同一个司机不同班次并存于列表
        assert isinstance(driver_css, str)
        pre_add_count = int(WebDriverWait(self.fc.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, driver_css + '>td:nth-child(9)'))).text)
        if order_type in [OrderType.FASTLINE]:
            self.fc.driver.find_element_by_css_selector(
                driver_css + '>td:nth-child(11)>a[name="btnRepairOrderKb"]').click()
            self.fc.add_bus_order(order_.order_id)
        else:
            self.fc.driver.find_element_by_css_selector(driver_css + '>td:nth-child(11)>a[name="btnRepairOrderInterc"]').click()
            self.fc.add_inter_order(order_.order_id)
        if argv[1] != 'TEST':
            sleep(2)
        after_add_count = int(WebDriverWait(self.fc.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, driver_css + '>td:nth-child(9)'))).text)
        status = True if after_add_count == pre_add_count + order_.order_count else False
        if status:
            order_.order_status = OrderStatus.APPOINTED
        self.assertTrue(status)
        log.logger.debug((f'补单后订单{order_.order_id}状态为：{order_.order_status}'))

