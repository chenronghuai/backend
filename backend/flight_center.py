import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
import fast_line
from utils import OrderType, DriverType, OrderStatus, FoundDriverError
from utils import TestMeta
import globalvar
import logging
from common import Driver
from sys import argv


logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@ddt
class TestFlightCenter(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver,  '班线管理', '班次调度中心', 'flightsOrderCenter.do')

    def input_center_line(self, center, line):
        self.driver.execute_script("$('#selCenter').click()")
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
        self.driver.find_element_by_css_selector('.fs-label-wrap>.fs-label').click()
        self.driver.execute_script("""
            $('.fs-options>div').each(function(inx, obj){if($(this).hasClass('selected')){$(this).removeClass('selected');}});
           """)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="' + line + '"]'))).click()
        self.driver.find_element_by_css_selector('#ipt_line_query').click()

    def new_flight_driver(self, center, line, driver_team, driver_phone):
        try:
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
                (By.CSS_SELECTOR, 'div#selFlights-suggest>div[dataname="' + globalvar.get_value('FlightNo') + '"]'))).click()
            self.driver.find_element_by_css_selector('#chooseDriver').click()
            WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=toChooseFlightsDriver"]')))
            self.driver.find_element_by_css_selector('#selMotorcade').click()
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selMotorcade-suggest>div[dataname$="' + driver_team + '"]'))).click()
            self.driver.find_element_by_css_selector('#phone1').send_keys(driver_phone)
            self.driver.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#driver_table>tbody>tr')))
            td_count = self.driver.find_elements_by_css_selector('table#driver_table>tbody>tr>td')
            if len(td_count) == 1:
                self.driver.find_element_by_css_selector('#btnEsc').click()
                self.driver.switch_to.parent_frame()
                self.driver.find_element_by_css_selector('#btnEsc').click()
                raise FoundDriverError(f'{driver_phone}-找不到司机或司机已报班')
            css = utils.get_record_by_field_value(self.driver, 'table#driver_table', '司机手机', driver_phone)
            self.driver.find_element_by_css_selector(css).click()
            self.driver.find_element_by_css_selector('#btnSave').click()
            self.driver.switch_to.parent_frame()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#driver-lists>tr')))
            # 添加司机进池
            driver_id = self.driver.find_element_by_css_selector('tbody#driver-lists>tr').get_attribute('driver_id')
            max_user = int(self.driver.find_element_by_css_selector('tbody#driver-lists>tr').get_attribute('max_passenger'))
            max_package = 0
            car_type = self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(5)').text
            oc_center = '漳州运营中心'
            driver = Driver(driver_id, max_user, max_package, car_type, oc_center, driver_type=DriverType.BUS_DRIVER)
            globalvar.add_driver(driver)

            self.driver.find_element_by_css_selector('#btnSave').click()
            #如下的等待弹框消失语句，执行后将导致后续的定位出现问题，似乎默认把driver切到最外层？
    #        WebDriverWait(self.driver, 5).until(
    #            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
    #        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
            self.driver.switch_to.parent_frame()
        finally:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(
                self.driver.find_element(By.CSS_SELECTOR, 'iframe[src="/flightsOrderCenter.do"]'))

        sleep(3)

    def appoint_flight_driver(self, driver_phone):
        WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=toAssignOrChangeOrder"]')))
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#driverPhone'))).send_keys(
            driver_phone)
        self.driver.find_element_by_css_selector('#searchBtn').click()
        sleep(1)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#service-vue>div>div>table#driver-schedule>tbody#driver-schedule-list>tr:nth-child(1)'))).click()
        self.driver.switch_to.parent_frame()  # 指派与输入电话不在同一iframe，怪异的设计

        tip_text = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.dispatch-tip-info'))).text
        if tip_text == '新增司机排班':
            # 添加司机进池
            self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, 'iframe[src^="/flightsOrderCenter.do?method=toAssignOrChangeOrder"]'))
            driver_id = self.driver.find_element_by_css_selector('tbody#driver-schedule-list>tr').get_attribute('driver-id')
            # 以下信息简单处理，没跟实际车辆相关
            max_user = 4
            max_package = 0
            car_type = '网约车/5座/舒适型'
            oc_center = '漳州运营中心'
            driver = Driver(driver_id, max_user, max_package, car_type, oc_center, driver_type=DriverType.BUS_DRIVER)
            globalvar.add_driver(driver)
            self.driver.switch_to.parent_frame()
        self.driver.find_element_by_css_selector('div>a.layui-layer-btn0').click()
        sleep(3)

    test_case_report = ["漳州运营中心", "高林SM专线", "老王测试专用车队", "13345678972"],
    prod_case_report = ["漳州运营中心", "厦门测试专线", "帮邦行厦门公司", "17700000001"],

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_case_report if argv[1] == 'HTTP1' else prod_case_report)
    @unpack
    def test_flight_driver_report(self, center, line, driver_team, driver_phone):
        self.input_center_line(center, line)
        self.driver.find_element_by_css_selector('#driverList').click()
        sleep(0.5)
        self.driver.execute_script("$('#addDriverSchedule').click()")
        WebDriverWait(self.driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=editFlightsDriver"]')))
        self.new_flight_driver(center, line, driver_team, driver_phone)
        reported_drivers = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr')))
        driver_phone_list = []
        for i in range(1, len(reported_drivers) + 1):
            driver_phone_list.append(utils.get_cell_content(self.driver, 'div#intercityDriver>table', i, 5))
        status = True if driver_phone in driver_phone_list else False
        self.assertTrue(status)

    test_case_appoint = ["漳州运营中心", "高林SM专线", "13345678966"],
    prod_case_appoint = ["漳州运营中心", "厦门测试班线", "17700000001"],

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_case_appoint if argv[1] == 'HTTP1' else prod_case_appoint)
    @unpack
    def test_appoint(self, center, line, driver_phone):
        self.input_center_line(center, line)
        self.driver.find_element_by_css_selector('#orderList').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        fastline_orders = list(filter(lambda x: x.order_type == OrderType.FASTLINE and x.order_status == OrderStatus.WAITING, globalvar.order_pool))
        order_css = utils.get_record_by_attr(self.driver, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr', 'order-id', fastline_orders[0].order_id)
        order_css += '>td.td-opera>a.modify'
#        self.driver.find_element_by_css_selector(order_css).click()  # 偶发element is not attached to the page document，与系统自动刷新有关？
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, order_css))).click()

        self.appoint_flight_driver(driver_phone)
        self.driver.execute_script("$('div#orderImmediately>table>tbody#tdy_driver_queue>tr').html('')")
        self.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        status_css = utils.get_record_by_attr(self.driver, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr',
                                             'order-id', fastline_orders[0].order_id)
        status_css += '>td:nth-child(12)'
        status_text = self.driver.find_element_by_css_selector(status_css).text
        status = True if status_text == '已指派' else False
        if status:
            fastline_orders[0].order_status = OrderStatus.APPOINTED
        self.assertTrue(status)

    @data(OrderType.CARPOOLING, OrderType.FASTLINE)
    def test_add_order(self, order_type):
        order_ = utils.get_first_order(order_type)
        driver_ = fast_line.filter_bus_driver(order_)
        if argv[1] == 'HTTP1':
            self.input_center_line('漳州运营中心', '高林SM专线')
        else:
            self.input_center_line('漳州运营中心', '厦门测试班线')
        driver_css = fast_line.search_extract_driver(driver_, self.driver)  # 不可直接使用filter_bus_driver得到的司机，因为同一个司机不同班次并存于列表
        pre_add_count = int(self.driver.find_element_by_css_selector(driver_css + '>td:nth-child(9)').text)
        if order_type in [OrderType.FASTLINE]:
            self.driver.find_element_by_css_selector(
                driver_css + '>td:nth-child(11)>a[name="btnRepairOrderKb"]').click()
            fast_line.add_bus_order(self.driver, order_.order_id)
        else:
            self.driver.find_element_by_css_selector(driver_css + '>td:nth-child(11)>a[name="btnRepairOrderInterc"]').click()
            fast_line.add_inter_order(self.driver, order_.order_id)
        after_add_count = int(WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, driver_css + '>td:nth-child(9)'))).text)
        status = True if after_add_count == pre_add_count + order_.order_count else False
        if status:
            order_.order_status = OrderStatus.APPOINTED
        self.assertTrue(status)

