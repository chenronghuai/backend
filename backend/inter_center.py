import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, file_data, data, unpack
import utils
from utils import OrderType, DriverType, FoundRecordError, OrderStatus, CarType, FoundDriverError
from utils import TestMeta
import globalvar
import logging
import re
from sys import argv


logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_commit_order():
    case_str = ""
    for i in range(5):
        order_str = str("物流中心", "XMC", "361000", "XM", "361000")
        case_str += ',' + order_str
    temp = case_str.strip(',')
    return eval(temp)


@ddt
class TestInterCenter(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '监控管理', '城际调度中心', 'orderCenterNew.do')
        if argv[1] == 'HTTP1':
            cls.input_center_line("物流中心", "XMC", "361000", "XM", "361000")
        else:
            cls.input_center_line("漳州运营中心", "XMC", "361000", "XM", "361000")

    @classmethod
    def input_center_line(cls, center, origin, ori_value, destination, des_value):
        # WebDriver： 当WebDriver进行单击时，它会尽可能地尝试模拟真实用户使用浏览器时发生的情况。 假设您有一个元素A，它是一个表示“单击我”的按钮，一个元素B是一个div透明的元素，但具有其尺寸和zIndex设置，使其完全覆盖A。然后告诉WebDriver单击A。WebDriver将模拟点击，使B 首先 获得点击。为什么？因为B涵盖了A，并且如果用户尝试单击A，则B将首先获得该事件。A是否最终会获得click事件取决于B如何处理该事件。无论如何，在这种情况下，WebDriver的行为与真实用户尝试单击A时的行为相同。
        # JavaScript：现在，假设您使用JavaScript来做A.click()。 这种单击方法不能重现用户尝试单击A时实际发生的情况 。JavaScript将click事件直接发送给A，而B将不会获得任何事件。
        cls.driver.execute_script(
            "$('div.fs-dropdown.hidden>div.fs-options>div').each(function(ind,obj){if($(this).hasClass('selected')){$(this).click();}})")
        cls.driver.execute_script(
            "$('div.fs-dropdown.hidden>div.fs-options>div>div.fs-option-label').filter(function(index){return $(this).text()=='" + center + "';}).click()")
        utils.input_ori_des(cls.driver, origin, ori_value, destination, des_value)
        cls.driver.find_element_by_css_selector('div#ipt_line_query').click()

    def appoint_order(self, order_id, driver_id):
        self.driver.find_element_by_css_selector('#orderList').click()
        sleep(0.5)
        self.driver.find_element_by_css_selector('div.nav-right.td-opera > a[title="即时"]').click()
        sleep(0.5)
        self.driver.execute_script('$("#orderImmediately>table>tbody>tr").html("")')
        self.driver.find_element_by_css_selector('#order-nav-query').click()  #多订单指派，从2-->1时，需要重新查询确保以下的locator正确?
        order_css = utils.get_record_by_attr(self.driver, '#orderImmediately>table>tbody>tr', 'order-id', order_id)
        order_css += '>td.td-opera>a[name="order-list-appoint"]'
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, order_css))).click()
        WebDriverWait(self.driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/orderCtrl.do"]')))

        temp_css = utils.get_record_by_attr(self.driver, '#intercity-lists>tr>td:nth-child(1)>input', 'driver_id', driver_id)
        s1 = temp_css[:19]  # 由于司机ID信息存在于input,不同于常规的tr，需做特殊处理
        s2 = temp_css[41:]
        driver_css = s1 + s2 + '>td:nth-child(1)'
        self.driver.find_element_by_css_selector(driver_css).click()
        sleep(1)
        self.driver.find_element_by_css_selector('#todoSaveBtn').click()
        self.driver.switch_to.parent_frame()
        sleep(1)  # 切换到父iframe需强制sleep，否则接下来的上层iframe定位将会失败，不知原因
        try:
            WebDriverWait(self.driver, 1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn->a.layui-layer-btn0'))).click()
        except:
            pass
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))  # 确认指派后，等待指派成功弹框消失
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))  # 确认指派后，等待蒙层消失

    def select_driver(self, driver_id):
        try:
            utils.select_operation_by_attr(self.driver, 'div#intercityDriver>table',
                                           'div#intercityDriver>table>tbody#tdy_driver_queue>tr', 'driver-id',
                                           driver_id, '补单')
        except Exception:
            sleep(1)
            utils.select_operation_by_attr(self.driver, 'div#intercityDriver>table',
                                           'div#intercityDriver>table>tbody#tdy_driver_queue>tr', 'driver-id',
                                           driver_id, '补单')

    def add_inter_order(self, order_id):
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
        try:
            orders = self.driver.find_elements_by_css_selector('div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
        except Exception:
            sleep(1)
            orders = self.driver.find_elements_by_css_selector('div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
        id_lists = [x.get_attribute('order-id') for x in orders]
        for index, id_ in enumerate(id_lists):
            if id_ == order_id:
                expect_css = 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li:nth-child({})'.format(index + 1)
                self.driver.find_element_by_css_selector(expect_css).click()
                sleep(1)
                self.driver.find_element_by_css_selector('#orderAddBtn').click()
                self.driver.switch_to.parent_frame()
                sleep(1)
                try:
                    WebDriverWait(self.driver, 1).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn->a.layui-layer-btn0'))).click()
                except:
                    pass
                self.driver.switch_to.frame(
                    self.driver.find_element_by_css_selector('iframe[src^="/orderCtrl.do?method=getDriverAddOrdersPage"]'))
                self.driver.find_element_by_css_selector('#closeBtn').click()
                break
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.parent_frame()

    def filte_driver(self, order):
        if order.order_type == OrderType.CARPOOLING:
            for index, driver in enumerate(globalvar.driver_pool):
                if order.order_count <= driver.max_user-driver.appoint_user_count and driver.charter_count == 0:
                    driver.appoint_user_count += order.order_count
                    return driver.driver_id
                elif index == len(globalvar.driver_pool)-1:
                    raise FoundDriverError(order.order_type)

        elif order.order_type == OrderType.EXPRESS:
            for index, driver in enumerate(globalvar.driver_pool):
                if order.order_count <= driver.max_package-driver.appoint_package_count:
                    driver.appoint_package_count += order.order_count
                    return driver.driver_id
                elif index == len(globalvar.driver_pool)-1:
                    raise FoundDriverError(order.order_type)

        elif order.order_type in [OrderType.CHARACTER, OrderType.DAYSCHARACTER]:
            free_drivers = list(filter(lambda x: x.charter_count == 0 and x.appoint_user_count == 0, globalvar.driver_pool))
            for index, driver in enumerate(free_drivers):
                if CarType.PRIORITY_DIST[driver.car_type] >= CarType.PRIORITY_DIST[order.car_type]:
                    return driver.driver_id
                elif index == len(free_drivers) - 1:
                    raise FoundDriverError(order.order_type)

    test_case = ["物流中心", "XMC", "361000", "XM", "361000", 1],["物流中心", "XMC", "361000", "XM", "361000", 2],["物流中心", "XMC", "361000", "XM", "361000", 3],["物流中心", "XMC", "361000", "XM", "361000", 4],["物流中心", "XMC", "361000", "XM", "361000", 5]
    prod_case = ["漳州运营中心", "XMC", "361000", "XM", "361000", 1],["漳州运营中心", "XMC", "361000", "XM", "361000", 2],["漳州运营中心", "XMC", "361000", "XM", "361000", 3],["漳州运营中心", "XMC", "361000", "XM", "361000", 4],["漳州运营中心", "XMC", "361000", "XM", "361000", 5]
#    @unittest.skip("直接跳过")
    @data(*test_case if argv[1] == 'HTTP1' else prod_case)
    @unpack
#    @file_data('.\\testcase\\appoint_carpooling.json')
    def test_appoint(self, center, origin, ori_value, destination, des_value, index):
#        self.input_center_line(center, origin, ori_value, destination, des_value)
#        for order in globalvar.order_pool:
        inter_orders = []
        for order in globalvar.order_pool:
            if order.order_type in [OrderType.CARPOOLING, OrderType.EXPRESS, OrderType.CHARACTER, OrderType.DAYSCHARACTER]:
                inter_orders.append(order)
        order = inter_orders[index-1]
        driver_id = self.filte_driver(order)
        self.appoint_order(order.order_id, driver_id)
        self.driver.find_element_by_css_selector('div.nav-right.td-opera > a[title="已派"]').click()
        sleep(1)
        appointed_orders = self.driver.find_elements_by_css_selector(
                '#orderImmediately>table>tbody#tdy_driver_queue>tr')
        id_list = [x.get_attribute('order-id') for x in appointed_orders]
        status = True if order.order_id in id_list else False
        self.assertTrue(status)
        order.order_status = OrderStatus.APPOINTED if status else OrderStatus.WAITING

    @data({"driver_type": DriverType.CARPOOLING_DRIVER},{"driver_type": DriverType.CHARACTER_DRIVER},{"driver_type": DriverType.DAYSCHARACTER_DRIVER})
    @unpack
    @unittest.skip("直接跳过")
    def test_depart(self, driver_type):
#        self.input_center_line("物流中心", "XMC", "361000", "XM", "361000")
        self.driver.find_element_by_css_selector('#driverList').click()
        self.driver.find_element_by_css_selector('div.bbx-orderlist-nav>.nav-right.td-opera>a[title="专车排班"]').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody#tdy_driver_queue>tr')))
        depart_drivers = self.driver.find_elements_by_css_selector('tbody#tdy_driver_queue>tr')
        driver_id_list = [x.get_attribute('driver-id') for x in depart_drivers]
        for index, driver_id in enumerate(driver_id_list):
            if globalvar.get_value(driver_type) == driver_id:
                depart_css = 'tbody#tdy_driver_queue>tr:nth-child({})>td:nth-child(12)>a[name="driver-list-depart"]'.format(index+1)
                self.driver.find_element_by_css_selector(depart_css).click()
                self.driver.switch_to.default_content()
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))).click()
                self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, 'iframe[src="/orderCenterNew.do"]'))
                sleep(1)
                break
            elif globalvar.get_value(driver_type) != driver_id and index == len(driver_id_list) - 1:
                raise FoundRecordError(globalvar.get_value(driver_type), 'tbody#tdy_driver_queue>tr')
        self.driver.find_element_by_css_selector('div.nav-right.td-opera>a[title="已发车"]').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr')))
        departed_drivers = self.driver.find_elements_by_css_selector('div#intercityDriver>table>tbody#tdy_driver_queue>tr')
        id_list = [x.get_attribute('driver-id') for x in departed_drivers]
        status = True if globalvar.get_value(driver_type) in id_list else False
        self.assertTrue(status)

    @data({"driver_type": DriverType.CARPOOLING_DRIVER, "order_type": OrderType.CARPOOLING})
    @unpack
    @unittest.skip("直接跳过")
    def test_add_order(self, driver_type, order_type):
        self.input_center_line("物流中心", "XMC", "361000", "XM", "361000")
        self.driver.find_element_by_css_selector('#driverList').click()
        self.driver.find_element_by_css_selector('#order-car-query').click()
        self.select_driver(globalvar.get_value(driver_type))
        WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getDriverAddOrdersMergePage"]')))
        self.driver.find_element_by_xpath('//div[@class="order-ri-tit"]/ul/li[text()="补城际订单"]').click()
        WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getDriverAddOrdersPage"]')))
        self.add_inter_order(globalvar.get_value(order_type))
        self.driver.execute_script('$("div#intercityDriver>table>tbody#tdy_driver_queue>tr").html("")')
        sleep(1)
        self.driver.execute_script('$("#order-car-query").click()')
#        self.driver.find_element_by_css_selector('#order-car-query').click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr>td')))
        dispach_status_css = utils.get_record_by_attr(self.driver, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr', 'driver-id', globalvar.get_value(driver_type))
        text = self.driver.find_element_by_css_selector(dispach_status_css + '>td:nth-child(7)').text
        self.assertEqual(re.search(r'(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+', text).group(2), '2')
