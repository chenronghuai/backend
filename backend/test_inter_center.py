import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from time import sleep
from ddt import ddt, file_data, data, unpack
import utils
from utils import OrderType, DriverType, FoundRecordError, OrderStatus, CarType, FoundDriverError
from utils import TestMeta
import globalvar
import re
import log
from sys import argv
from MonitorManage.func_inter_center import FuncInterCenter


@ddt
class TestInterCenter(unittest.TestCase, metaclass=TestMeta):
    current_oc_center = []
    oc_flag = True
    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        cls.ic = FuncInterCenter()
        cls.__name__ = cls.__name__ + "（城际调度中心：指派拼车、包车、货件，补单拼车、货件、快线，发车功能，运营中心订单可视权限）"

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data('泉州运营中心', '厦门运营中心')
    def test_driver_permission(self, oc_center):
        except_iter = []
        unexcept_iter = []
        self.ic.input_center_line(oc_center, "XMC", "361000", "XM", "361000")
        goal_drivers = list(
            filter(lambda driver_: driver_.oc_center in self.ic.current_oc_center, globalvar.driver_pool))
        goal_not_drivers = list(
            filter(lambda driver_: driver_.oc_center not in self.ic.current_oc_center, globalvar.driver_pool))

        try:
            driver_id_list = []
            we_actual_drivers = WebDriverWait(self.ic.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody#tdy_driver_queue>tr')))
            for i in we_actual_drivers:
                driver_id_list.append(i.get_attribute('driver-id'))
        except StaleElementReferenceException:
            driver_id_list = []
            we_actual_drivers = WebDriverWait(self.ic.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody#tdy_driver_queue>tr')))
            for i in we_actual_drivers:
                driver_id_list.append(i.get_attribute('driver-id'))
        for driver in goal_drivers:
            except_iter.append(driver.driver_id in driver_id_list)
        for driver in goal_not_drivers:
            unexcept_iter.append(driver.driver_id in driver_id_list)
        return all(except_iter) and not any(unexcept_iter)

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(OrderType.CARPOOLING, OrderType.EXPRESS, OrderType.CHARACTER)
#    @unpack
    def test_appoint(self, order_type):
        if self.ic.oc_flag and argv[1] == 'TEST':
            self.ic.input_center_line("厦门运营中心", "XMC", "361000", "XM", "361000")
            self.ic.oc_flag = False
        order = utils.get_first_order(order_type)
        driver = self.ic.filter_driver(order)
        if driver == '没有合适的司机':
            return 'N/A'
        self.ic.appoint_order(order.order_id, driver.driver_id)
        self.ic.driver.find_element_by_css_selector('div.nav-right.td-opera > a[title="已派"]').click()
#        sleep(1)
#        appointed_orders = self.driver.find_elements_by_css_selector(
#                '#orderImmediately>table>tbody#tdy_driver_queue>tr')
        appointed_orders = WebDriverWait(self.ic.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#orderImmediately>table>tbody#tdy_driver_queue>tr')))
        try:
            id_list = [x.get_attribute('order-id') for x in appointed_orders]
        except StaleElementReferenceException:
            WebDriverWait(self.ic.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#orderImmediately>table>tbody#tdy_driver_queue>tr')))
            id_list = [x.get_attribute('order-id') for x in appointed_orders]
        log.logger.debug(f'已指派订单ID：{id_list}')
        status = True if order.order_id in id_list else False
        self.assertTrue(status)
        order.order_status = OrderStatus.APPOINTED if status else OrderStatus.WAITING

    @data(OrderType.CARPOOLING, OrderType.EXPRESS, OrderType.FASTLINE)
#    @unittest.skip("直接跳过")
    def test_add_order(self, order_type):
        order = utils.get_first_order(order_type)
        driver = self.ic.filter_driver(order)
        appointed_user_count = driver.appoint_user_count
        appointed_package_count = driver.appoint_package_count
        self.ic.driver.find_element_by_css_selector('#driverList').click()
        self.ic.driver.find_element_by_css_selector('#order-car-query').click()
        self.ic.select_driver(driver.driver_id)
        WebDriverWait(self.ic.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getDriverAddOrdersMergePage"]')))
        if order_type in [OrderType.CARPOOLING, OrderType.CHARACTER, OrderType.EXPRESS, OrderType.DAYSCHARACTER]:
            self.ic.driver.find_element_by_xpath('//div[@class="order-ri-tit"]/ul/li[text()="补城际订单"]').click()
            WebDriverWait(self.ic.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getDriverAddOrdersPage"]')))
            self.ic.add_inter_order(order.order_id)

        elif order_type in [OrderType.FASTLINE]:
            self.ic.driver.find_element_by_xpath('//div[@class="order-ri-tit"]/ul/li[text()="补快线订单"]').click()
            WebDriverWait(self.ic.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getDriverAddBusOrdersPage"]')))
            self.ic.driver.find_element_by_css_selector('div.fs-label-wrap>div.fs-label').click()
            WebDriverWait(self.ic.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.fs-options>div>div.fs-option-label')))
            if argv[1] == 'TEST':
                self.ic.driver.execute_script(
                    "$('div.fs-dropdown>div.fs-options>div>div.fs-option-label').filter(function(index){return $(this).text()=='高林SM专线';}).click()")
            else:
                self.ic.driver.execute_script(
                    "$('div.fs-dropdown>div.fs-options>div>div.fs-option-label').filter(function(index){return $(this).text()=='厦门测试班线';}).click()")
            self.ic.driver.find_element_by_css_selector('#btnQuery').click()
            self.ic.add_fastline_order(order.order_id)

        self.driver.execute_script('$("div#intercityDriver>table>tbody#tdy_driver_queue").html("")')
        sleep(1)
        self.driver.execute_script('$("#order-car-query").click()')
        WebDriverWait(self.ic.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr>td:nth-child(1)')))
        dispach_status_css = utils.get_record_by_attr(self.ic.driver, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr',
                                                      'driver-id', driver.driver_id)
        text = self.ic.driver.find_element_by_css_selector(dispach_status_css + '>td:nth-child(7)').text
        if order_type in [OrderType.CARPOOLING, OrderType.FASTLINE]:
            result_appointed_count = int(re.search(r'(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+', text).group(2))
            status = True if result_appointed_count == appointed_user_count else False
        elif order_type in [OrderType.EXPRESS]:
            result_package_count = int(re.search(r'(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+', text).group(3))
            status = True if result_package_count == appointed_package_count else False
        self.assertTrue(status)
        order.order_status = OrderStatus.APPOINTED if status else OrderStatus.WAITING

    @data(1, 2)
#    @unittest.skip("直接跳过")
    def test_depart(self, index):
        depart_drivers = list(filter(lambda x: x.driver_type == DriverType.NET_DRIVER and x.oc_center in self.ic.current_oc_center, globalvar.driver_pool))
        self.ic.driver.find_element_by_css_selector('#driverList').click()
#        self.driver.execute_script('$("tbody#tdy_driver_queue").html("")')
        self.ic.driver.find_element_by_css_selector('div.bbx-orderlist-nav>.nav-right.td-opera>a[title="专车排班"]').click()
        WebDriverWait(self.ic.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody#tdy_driver_queue>tr')))
        utils.select_operation_by_attr(self.ic.driver, '#intercityDriver>table', '#intercityDriver>table>tbody>tr', 'driver-id', depart_drivers[index-1].driver_id, '发车')
        self.ic.driver.switch_to.default_content()
        WebDriverWait(self.ic.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0')))
        self.ic.driver.execute_script("""$('div[type="dialog"]>div>a.layui-layer-btn0').click()""")
        self.ic.driver.switch_to.frame(self.ic.driver.find_element(By.CSS_SELECTOR, 'iframe[src="/orderCenterNew.do"]'))
        sleep(1)
        self.ic.driver.find_element_by_css_selector('div.nav-right.td-opera>a[title="已发车"]').click()
        departed_drivers = WebDriverWait(self.ic.driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr')))
        # try模块为了规避系统刷新时DOM为空导致的异常
        try:
            id_list = [x.get_attribute('driver-id') for x in departed_drivers]
        except:
            sleep(1)
            id_list = [x.get_attribute('driver-id') for x in departed_drivers]
        status = True if depart_drivers[index-1].driver_id in id_list else False
        self.assertTrue(status)
        sleep(1)



