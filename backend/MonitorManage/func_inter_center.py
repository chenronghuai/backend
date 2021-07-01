from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import utils
from utils import OrderType, DriverType, FoundRecordError, OrderStatus, CarType, FoundDriverError
import globalvar
from sys import argv


class FuncInterCenter:
    current_oc_center = []
    oc_flag = True

    def __init__(self):
        self.driver = globalvar.get_value('driver')
        utils.make_sure_driver(self.driver, '监控管理', '城际调度中心', '城际调度中心', 'orderCenterNew.do')
        if argv[1] == 'TEST':
            self.input_center_line("厦门运营中心", "XMC", "361000", "XM", "361000")
        else:
            self.input_center_line("漳州运营中心", "XMC", "361000", "XM", "361000")

    def setup_oc(self):
        self.driver = globalvar.get_value('driver')
        utils.switch_frame(self.driver, '监控管理', '城际调度中心', 'orderCenterNew.do')
        globalvar.opened_window_pool.append('orderCenterNew.do')
        self.input_center_line("物流中心", "XMC", "361000", "XM", "361000")

    def input_center_line(self, center, origin, ori_value, destination, des_value):
        # WebDriver： 当WebDriver进行单击时，它会尽可能地尝试模拟真实用户使用浏览器时发生的情况。 假设您有一个元素A，它是一个表示“单击我”的按钮，一个元素B是一个div透明的元素，但具有其尺寸和zIndex设置，使其完全覆盖A。然后告诉WebDriver单击A。WebDriver将模拟点击，使B 首先 获得点击。为什么？因为B涵盖了A，并且如果用户尝试单击A，则B将首先获得该事件。A是否最终会获得click事件取决于B如何处理该事件。无论如何，在这种情况下，WebDriver的行为与真实用户尝试单击A时的行为相同。
        # JavaScript：现在，假设您使用JavaScript来做A.click()。 这种单击方法不能重现用户尝试单击A时实际发生的情况 。JavaScript将click事件直接发送给A，而B将不会获得任何事件。
        self.driver.execute_script(
            "$('div.fs-dropdown.hidden>div.fs-options>div').each(function(ind,obj){if($(this).hasClass('selected')){$(this).click();}})")
        self.driver.execute_script(
            "$('div.fs-dropdown.hidden>div.fs-options>div>div.fs-option-label').filter(function(index){return $(this).text()=='" + center + "';}).click()")
        self.current_oc_center.clear()
        self.current_oc_center.append(center)
        utils.input_ori_des(self.driver, origin, ori_value, destination, des_value)
        sleep(1)  # 2021-5-21 灰度环境经常目的地方位被情况，怀疑与查询操作有冲突，加等待试试
        self.driver.find_element_by_css_selector('div#ipt_line_query').click()

    def appoint_order(self, order_id, driver_id):
        driver_css = ''
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
        records = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#intercity-lists>tr>td:nth-child(1)>input')))
        for i in range(1, len(records)+1):
            actual_value = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'#intercity-lists>tr:nth-child({i})>td:nth-child(1)>input'))).get_attribute(
                'driver_id')
            if driver_id == actual_value:
                driver_css = f'#intercity-lists>tr:nth-child({i})' + '>td:nth-child(1)'
                break

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
        try:
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
        except:
            self.driver.find_element_by_css_selector('#closeBtn').click()
            self.driver.switch_to.parent_frame()
            self.driver.switch_to.parent_frame()

    def add_fastline_order(self, order_id):
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
            try:
                orders = self.driver.find_elements_by_css_selector(
                    'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
            except Exception:
                sleep(1)
                orders = self.driver.find_elements_by_css_selector(
                    'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
            id_lists = [x.get_attribute('order-id') for x in orders]
            for index, id_ in enumerate(id_lists):
                if id_ == order_id:
                    expect_css = 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li:nth-child({})'.format(index + 1)
                    self.driver.find_element_by_css_selector(expect_css).click()
                    sleep(1)
                    self.driver.find_element_by_css_selector('#orderAddBtn').click()
                    sleep(1)
                    self.driver.find_element_by_css_selector('#closeBtn').click()
                    break
            self.driver.switch_to.parent_frame()
            self.driver.switch_to.parent_frame()
        except:
            self.driver.find_element_by_css_selector('#closeBtn').click()
            self.driver.switch_to.parent_frame()
            self.driver.switch_to.parent_frame()

    def filter_driver(self, order):
        net_drivers = list(filter(lambda _driver: _driver.driver_type == DriverType.NET_DRIVER and _driver.oc_center in self.current_oc_center, globalvar.driver_pool))
        if order.order_type in [OrderType.CARPOOLING, OrderType.FASTLINE]:
            for index, driver in enumerate(net_drivers):
                if order.order_count <= driver.max_user-driver.appoint_user_count and driver.charter_count == 0:
                    driver.appoint_user_count += order.order_count
                    return driver
                elif index == len(net_drivers)-1:
                    raise IndexError  # FoundDriverError(order.order_type)

        elif order.order_type == OrderType.EXPRESS:
            for index, driver in enumerate(net_drivers):
                if order.order_count <= driver.max_package-driver.appoint_package_count:
                    driver.appoint_package_count += order.order_count
                    return driver
                elif index == len(net_drivers)-1:
                    raise IndexError  # FoundDriverError(order.order_type)

        elif order.order_type in [OrderType.CHARACTER, OrderType.DAYSCHARACTER]:
            free_drivers = list(filter(lambda x: x.charter_count == 0 and x.appoint_user_count == 0, net_drivers))
            if len(free_drivers) == 0:
                raise IndexError
            else:
                for index, driver in enumerate(free_drivers):
                    if CarType.PRIORITY_DIST[driver.car_type] >= CarType.PRIORITY_DIST[order.car_type]:
                        driver.charter_count += 1
                        return driver
                    elif index == len(free_drivers) - 1:
                        raise IndexError  # FoundDriverError(order.order_type)