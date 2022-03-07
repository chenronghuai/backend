import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from time import sleep
from ddt import ddt, data, unpack
import utils
import log
from utils import OrderType, OrderStatus
from utils import TestMeta
import globalvar
from sys import argv
from FlightManage.func_flight_center import FuncFlightCenter
from PaVManage.func_line import FuncLine


@ddt
class TestFlightCenter(unittest.TestCase, metaclass=TestMeta):

    TEST_LINE_ID = "350200_to_350200048"
    PROD_LINE_ID = "350400_to_350400001"
    LINE_ID = TEST_LINE_ID if argv[1] == 'TEST' else PROD_LINE_ID

    @classmethod
    def setUpClass(cls):
        cls.__name__ = cls.__name__ + "（班次调度中心：快线司机排班，指派未排班司机即排班，指派快线订单给排班司机，快线司机补网约单、快线单，快线订单自动指派）"
        cls.fc = FuncFlightCenter()
        cls.lm = FuncLine()
        cls.resume_flag = True
        cls.lm.queryLine(line_num=cls.LINE_ID)
        route_status_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#line_table>tbody>tr>td:nth-child(11)'))).text
        if route_status_text == '开启':  # 确保线路路由处于关闭状态
            cls.fc.toggle_auto_appoint(cls.LINE_ID, False)
            cls.resume_flag = False
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '班线管理', '班次调度中心', 'flightsOrderCenter.do')

    @classmethod
    def tearDownClass(cls):
        if cls.resume_flag:  # 恢复线路到初始路由状态
            cls.fc.toggle_auto_appoint(cls.LINE_ID, False)

    test_case_report = ["漳州运营中心", "高林SM专线", "老王测试专用车队", "13345678972"],
    prod_case_report = ["漳州运营中心", "厦门测试班线", "测试，禁用", "14100010008"],

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_case_report if argv[1] == 'TEST' else prod_case_report)
    @unpack
    def test_flight_driver_report(self, center, line, driver_team, driver_phone):

        self.fc.input_center_line(center, line)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#driverList').click()
        sleep(0.5)
        globalvar.GLOBAL_DRIVER.execute_script("$('#addDriverSchedule').click()")
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=editFlightsDriver"]')))
        self.fc.new_flight_driver(center, line, driver_team, driver_phone)
        reported_drivers = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr')))
        driver_phone_list = []
        for i in range(1, len(reported_drivers) + 1):
            driver_phone_list.append(utils.get_cell_content(globalvar.GLOBAL_DRIVER, 'div#intercityDriver>table', i, 5))
        status = True if driver_phone in driver_phone_list else False
        self.assertTrue(status)

    test_case_appoint = ["漳州运营中心", "高林SM专线", "13345678966"],
    prod_case_appoint = ["漳州运营中心", "厦门测试班线", "17700000001"],

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_case_appoint if argv[1] == 'TEST' else prod_case_appoint)
    @unpack
    def test_appoint(self, center, line, driver_phone):
        self.fc.input_center_line(center, line)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#orderList').click()
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        except TimeoutException:
            log.logger.error(f'订单列表里没有快线订单!')
            raise IndexError
        fastline_orders = list(filter(lambda x: x.order_type == OrderType.FASTLINE and x.order_status == OrderStatus.WAITING, globalvar.order_pool))
        assert len(fastline_orders) > 0, '没有待指派快线订单'

        order_css = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr', 'order-id', fastline_orders[0].order_id)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
        order_status_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, order_css + '>td:nth-child(12)'))).text
        if order_status_text == '已指派':  # 处理当开启自动指派时，订单已处于已指派状态
            for order in fastline_orders:
                order.order_status = OrderStatus.APPOINTED
            assert True
        else:
            order_operate_css = order_css + '>td.td-opera>a[title="指派"]'
    #        globalvar.GLOBAL_DRIVER.find_element_by_css_selector(order_css).click()  # 偶发element is not attached to the page document，与系统自动刷新有关？
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, order_operate_css))).click()
            self.fc.appoint_flight_driver(driver_phone)
            globalvar.GLOBAL_DRIVER.execute_script("$('div#orderImmediately>table>tbody#tdy_driver_queue>tr').html('')")
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
            status_css = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr',
                                                 'order-id', fastline_orders[0].order_id)
            status_css += '>td:nth-child(12)'
            status_text = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(status_css).text
            status = True if status_text == '已指派' else False
            if status:
                fastline_orders[0].order_status = OrderStatus.APPOINTED
            self.assertTrue(status)

    @data(OrderType.CARPOOLING, OrderType.FASTLINE)
    def test_add_order(self, order_type):
        order_ = utils.get_first_order(order_type)
        driver_ = self.fc.filter_bus_driver(order_)
        if argv[1] == 'TEST':
            self.fc.input_center_line('漳州运营中心', '高林SM专线')
        else:
            self.fc.input_center_line('漳州运营中心', '厦门测试班线')
        driver_css = self.fc.search_extract_driver(driver_)  # 不可直接使用filter_bus_driver得到的司机，因为同一个司机不同班次并存于列表
        try:
            assert isinstance(driver_css, str)
        except:
            log.logger.error(f'the type of dviver_css is {type(driver_css)}')
        pre_add_count = int(WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, driver_css + '>td:nth-child(9)'))).text)
        if order_type in [OrderType.FASTLINE]:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector(
                driver_css + '>td:nth-child(11)>a[name="btnRepairOrderKb"]').click()
            try:
                self.fc.add_bus_order(order_.order_id)
            except:
                assert False
            else:
                order_.order_status = OrderStatus.APPOINTED
                order_.appoint_driver = driver_
        else:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector(driver_css + '>td:nth-child(11)>a[name="btnRepairOrderInterc"]').click()
            try:
                self.fc.add_inter_order(order_.order_id)
                if '补单操作成功!' not in getattr(self.fc, 'add_result_text', '未获取到补单结果信息'):
                    log.logger.error(f'补城际订单失败，msg={getattr(self.fc, "add_result_text", "未获取到补单结果信息")}')
                    assert False
            except:
                assert False
            else:
                order_.order_status = OrderStatus.APPOINTED
                order_.appoint_driver = driver_
        '''
        if argv[1] != 'TEST':
            sleep(4)
#        globalvar.GLOBAL_DRIVER.execute_script("""$('#tdy_driver_queue>tr[page_type="driver_queue"]').html('')""")
#        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flights_driver_query').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#tdy_driver_queue>tr[page_type="driver_queue"]')))
        after_add_count = int(WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, driver_css + '>td:nth-child(9)'))).text)
        status = True if after_add_count == pre_add_count + order_.order_count else False
        if status:
            order_.order_status = OrderStatus.APPOINTED
        else:
            log.logger.error(f'指派前人数{pre_add_count}，订单人数{order_.order_count}，指派后人数{after_add_count}')
        self.assertTrue(status)
        '''
    test_case_line = ("350200_to_350200048",)
    prod_case_line = ("350400_to_350400001",)

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_case_line if argv[1] == 'TEST' else prod_case_line)
    def test_auto_appoint(self, line_id):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '人员车辆管理', '线路管理', 'line.do')
        expect_iter = []
        self.fc.toggle_auto_appoint(line_id)  # 开启线路自动指派
        if argv[1] == 'TEST':
            sleep(20)
        else:
            sleep(40)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#orderList').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10, ignored_exceptions=(StaleElementReferenceException,)).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        fast_line_orders = list(filter(lambda order: order.order_type == OrderType.FASTLINE, globalvar.order_pool))
        order_id_list = [order.order_id for order in fast_line_orders]
        for id_ in order_id_list:
            tr_locator = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, 'div#orderImmediately>table>tbody#tdy_driver_queue>tr', 'order-id', id_)
            status_text = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(tr_locator+'>td:nth-child(12)').text
            if status_text == '已指派':
                expect_iter.append(True)
            else:
                expect_iter.append(False)
                break
        self.assertTrue(all(expect_iter))
