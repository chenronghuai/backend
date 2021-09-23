from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, strftime
import utils
import log
from utils import OrderType, DriverType, FoundRecordError, OrderStatus, CarType, FoundDriverError
import globalvar
from sys import argv


class FuncInterCenter:
    current_oc_center = []
    oc_flag = True
    driver_node_css_dict = {
        '专车排班': '#intercityDriver>table>tbody>tr[page_type="driver_queue"]',
        '已发车': '#intercityDriver>table>tbody>tr[page_type="driver_dispatch"]'
    }
    order_node_css_dict = {
        '即时': '#orderImmediately>table>tbody.immediate-order',
        '已派': '#orderImmediately>table>tbody.dispatched-order'
    }

    def __init__(self):
#        self.driver = globalvar.get_value('driver')
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '城际调度中心', 'orderCenterNew.do')
        if argv[1] == 'TEST':
            self.input_center_line("厦门运营中心", "XMC", "361000", "XM", "361000")
        else:
            self.input_center_line("漳州运营中心", "XMC", "361000", "XM", "361000")

    def setup_oc(self):
        globalvar.GLOBAL_DRIVER = globalvar.get_value('driver')
        utils.switch_frame(globalvar.GLOBAL_DRIVER, '监控管理', '城际调度中心', 'orderCenterNew.do')
        globalvar.opened_window_pool.append('orderCenterNew.do')
        self.input_center_line("物流中心", "XMC", "361000", "XM", "361000")

    def input_center_line(self, center, origin, ori_value, destination, des_value):
        # WebDriver： 当WebDriver进行单击时，它会尽可能地尝试模拟真实用户使用浏览器时发生的情况。 假设您有一个元素A，它是一个表示“单击我”的按钮，一个元素B是一个div透明的元素，但具有其尺寸和zIndex设置，使其完全覆盖A。然后告诉WebDriver单击A。WebDriver将模拟点击，使B 首先 获得点击。为什么？因为B涵盖了A，并且如果用户尝试单击A，则B将首先获得该事件。A是否最终会获得click事件取决于B如何处理该事件。无论如何，在这种情况下，WebDriver的行为与真实用户尝试单击A时的行为相同。
        # JavaScript：现在，假设您使用JavaScript来做A.click()。 这种单击方法不能重现用户尝试单击A时实际发生的情况 。JavaScript将click事件直接发送给A，而B将不会获得任何事件。
        globalvar.GLOBAL_DRIVER.execute_script(
            "$('div.fs-dropdown.hidden>div.fs-options>div').each(function(ind,obj){if($(this).hasClass('selected')){$(this).click();}})")
        globalvar.GLOBAL_DRIVER.execute_script(
            "$('div.fs-dropdown.hidden>div.fs-options>div>div.fs-option-label').filter(function(index){return $(this).text()=='" + center + "';}).click()")
        self.current_oc_center.clear()
        self.current_oc_center.append(center)
        utils.input_ori_des(globalvar.GLOBAL_DRIVER, origin, ori_value, destination, des_value)
        sleep(1)  # 2021-5-21 灰度环境经常目的地方位被清空，怀疑与查询操作有冲突，加等待试试
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div#ipt_line_query').click()

    def appoint_order(self, order_id, driver_id):
        driver_css = ''
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#orderList').click()
        sleep(0.5)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.nav-right.td-opera > a[title="即时"]').click()
        sleep(0.5)
        globalvar.GLOBAL_DRIVER.execute_script('$("#orderImmediately>table>tbody>tr").html("")')
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#order-nav-query').click()  # 多订单指派，从2-->1时，需要重新查询确保以下的locator正确?
        order_css = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, '#orderImmediately>table>tbody>tr', 'order-id', order_id)
        order_css += '>td.td-opera>a[name="order-list-appoint"]'
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, order_css))).click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getOrderDriverAppointPage"]')))
        try:
            records = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#intercity-lists>tr>td:nth-child(1)>input')))
            for i in range(1, len(records) + 1):
                actual_value = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, f'#intercity-lists>tr:nth-child({i})>td:nth-child(1)>input'))).get_attribute(
                    'driver_id')
                if driver_id == actual_value:
                    driver_css = f'#intercity-lists>tr:nth-child({i})' + '>td:nth-child(1)'
                    break

            globalvar.GLOBAL_DRIVER.find_element_by_css_selector(driver_css).click()
            sleep(1)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#todoSaveBtn').click()
        except:
            log.logger.error(f'订单（{order_id}）匹配司机（{driver_id}）出现异常！')
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#todoExitBtn').click()

        try:
            msg_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.layui-layer-content.layui-layer-padding'))).text
            setattr(self, 'appoint_result_text', msg_text)
        except:
            pass

        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(1)  # 切换到父iframe需强制sleep，否则接下来的上层iframe定位将会失败，不知原因
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 1).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn->a.layui-layer-btn0'))).click()
            msg_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.layui-layer-content.layui-layer-padding'))).text
            setattr(self, 'appoint_result_text', msg_text)
        except:
            pass



    def select_driver(self, driver_id):
        try:
            utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, 'div#intercityDriver>table',
                                           'div#intercityDriver>table>tbody#tdy_driver_queue>tr', 'driver-id',
                                           driver_id, '补单')
        except Exception:
            sleep(1)
            utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, 'div#intercityDriver>table',
                                           'div#intercityDriver>table>tbody#tdy_driver_queue>tr', 'driver-id',
                                           driver_id, '补单')

    def add_inter_order(self, order_id):
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
            try:
                orders = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
            except Exception:
                sleep(1)
                orders = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
            id_lists = [x.get_attribute('order-id') for x in orders]
            for index, id_ in enumerate(id_lists):
                if id_ == order_id:
                    expect_css = 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li:nth-child({})'.format(index + 1)
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector(expect_css).click()
                    sleep(1)
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#orderAddBtn').click()
                    try:
                        msg_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, '.layui-layer-content.layui-layer-padding'))).text
                        setattr(self, 'add_result_text', msg_text)
                    except:
                        pass
                    globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
                    sleep(1)
                    try:
                        WebDriverWait(globalvar.GLOBAL_DRIVER, 1).until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn->a.layui-layer-btn0'))).click()
                        try:
                            msg_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, '.layui-layer-content.layui-layer-padding'))).text
                            setattr(self, 'add_result_text', msg_text)
                        except:
                            pass
                    except:
                        pass
                    globalvar.GLOBAL_DRIVER.switch_to.frame(
                        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('iframe[src^="/orderCtrl.do?method=getDriverAddOrdersPage"]'))
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#closeBtn').click()
                    break
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        except:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#closeBtn').click()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()

    def add_fastline_order(self, order_id):
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
            try:
                orders = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector(
                    'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
            except Exception:
                sleep(1)
                orders = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector(
                    'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')
            id_lists = [x.get_attribute('order-id') for x in orders]
            for index, id_ in enumerate(id_lists):
                if id_ == order_id:
                    expect_css = 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li:nth-child({})'.format(index + 1)
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector(expect_css).click()
                    sleep(1)
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#orderAddBtn').click()
                    msg_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
                    setattr(self, 'add_result_text', msg_text)
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#closeBtn').click()
                    break
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        except:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#closeBtn').click()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()

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
                log.logger.error(f'没有匹配的包车司机！')
                raise IndexError
            else:
                for index, driver in enumerate(free_drivers):
                    if CarType.PRIORITY_DIST[driver.car_type] >= CarType.PRIORITY_DIST[order.car_type]:
                        driver.charter_count += 1
                        return driver
                    elif index == len(free_drivers) - 1:
                        log.logger.error(f'没有匹配的包车车型！')
                        raise IndexError  # FoundDriverError(order.order_type)

    def get_operate_text(self, category):
        text_list = []
        info_dict = {}
        if category in ['专车排班', '系统排班', '专车核单', '已发车', '返程发车', 'U+在线']:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#driverList'))).click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.nav-right.td-opera > a[title="' + category + '"]'))).click()
            try:
#                WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'{self.driver_node_css_dict[category]}>td')))  # 偶发超时，不解？注释掉不影响流程
                text_list = utils.get_operation_field_text(globalvar.GLOBAL_DRIVER, '#intercityDriver>table', f'{self.driver_node_css_dict[category]}:nth-child(1)')
            except StaleElementReferenceException:
                sleep(2)
                text_list = utils.get_operation_field_text(globalvar.GLOBAL_DRIVER, '#intercityDriver>table', f'{self.driver_node_css_dict[category]}:nth-child(1)')
            except TimeoutException:
                log.logger.error(f'超时或没有{category}司机的记录！')
                raise IndexError

        elif category in ['即时', '预约', '异常', '已派', '分享']:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#orderList'))).click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.nav-right.td-opera > a[title="' + category + '"]'))).click()
            try:
#                WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'{self.order_node_css_dict[category]}>tr>td')))  # 偶发超时，不解？注释掉不影响流程
                text_list = utils.get_operation_field_text(globalvar.GLOBAL_DRIVER, '#orderImmediately>table', f'{self.order_node_css_dict[category]}>tr:nth-child(1)')
                we_first_order = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(f'{self.order_node_css_dict[category]}>tr:nth-child(1)')
                info_dict['oc'] = we_first_order.get_attribute('source_oc_code')
            except StaleElementReferenceException:
                sleep(2)
                text_list = utils.get_operation_field_text(globalvar.GLOBAL_DRIVER, '#orderImmediately>table',
                                                           f'{self.order_node_css_dict[category]}>tr:nth-child(1)')
                we_first_order = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(
                    f'{self.order_node_css_dict[category]}>tr:nth-child(1)')
                info_dict['oc'] = we_first_order.get_attribute('source_oc_code')
            except TimeoutException:
                log.logger.error(f'超时或者没有{category}订单的记录！')
                raise IndexError
        else:
            log.logger.error(f'{category}--不支持的关键字！')
            raise IndexError
        return text_list, info_dict



