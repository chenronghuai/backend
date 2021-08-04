import utils
from utils import OrderType, DriverType, FoundDriverError, CarType
import globalvar
import re
from sys import argv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from common import Driver
import log


class FuncFlightCenter:

    def __init__(self):
        self.driver = globalvar.get_value('driver')
        utils.make_sure_driver(self.driver, '班线管理', '班次调度中心', '班次调度中心', 'flightsOrderCenter.do')

    def input_center_line(self, center, line):

        WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#selCenter-suggest>div')))
        self.driver.execute_script("$('#selCenter').click()")
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.fs-dropdown>.fs-options>.fs-option>.fs-option-label')))
        self.driver.find_element_by_css_selector('.fs-label-wrap>.fs-label').click()
        self.driver.execute_script("""
            $('.fs-options>div').each(function(inx, obj){if($(this).hasClass('selected')){$(this).removeClass('selected');}});
           """)
        WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="' + line + '"]'))).click()
        self.driver.find_element_by_css_selector('#ipt_line_query').click()

    def new_flight_driver(self, center, line, driver_team, driver_phone):
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#selCenter-suggest>div')))
            self.driver.find_element_by_css_selector('#selCenter').click()
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#selLine-suggest>div')))
            self.driver.find_element_by_css_selector('#selLine').click()
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname$="' + line + '"]'))).click()

            self.driver.find_element_by_css_selector('#flightsDate').click()
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.laydate-btns-confirm'))).click()
            # added 2021-5-20 只有一个班次会自动选择
            try:
                WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'input#selFlights[flights_no="' + globalvar.get_value('FlightNo') + '"]')))

            except:
                self.driver.find_element_by_css_selector('#selFlights').click()
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR,
                     'div#selFlights-suggest>div[dataname="' + globalvar.get_value('FlightNo') + '"]'))).click()

            #            self.driver.find_element_by_css_selector('#chooseDriver').click()
            self.driver.execute_script('$("#chooseDriver").click()')
            WebDriverWait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=toChooseFlightsDriver"]')))
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#selMotorcade-suggest>div')))
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#selMotorcade'))).click()
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'div#selMotorcade-suggest>div[dataname$="' + driver_team + '"]'))).click()
            self.driver.find_element_by_css_selector('#phone1').send_keys(driver_phone)
            self.driver.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#driver_table>tbody>tr')))  # 没有匹配司机该locator也会存在-“暂无数据！”
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
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#driver-lists>tr')))
            # 收集司机信息
            driver_id = self.driver.find_element_by_css_selector('tbody#driver-lists>tr').get_attribute('driver_id')
            max_user = int(
                self.driver.find_element_by_css_selector('tbody#driver-lists>tr').get_attribute('max_passenger'))
            max_package = 0
            car_type = self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(5)').text
            register_phone = self.driver.find_element_by_css_selector('tbody>tr>td:nth-child(3)').text
            oc_center = '漳州运营中心'
            driver = Driver(driver_id, max_user, max_package, car_type, oc_center, register_phone, contact_phone=register_phone, 
                            driver_type=DriverType.BUS_DRIVER)

            self.driver.find_element_by_css_selector('#btnSave').click()
            msg_text = utils.wait_for_laymsg(self.driver)
            if 'success' in msg_text:
                globalvar.add_driver(driver)
            else:
                log.logger.error(f'司机班次报班失败，msg={msg_text}')
                assert False
            self.driver.switch_to.parent_frame()
        finally:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(
                self.driver.find_element(By.CSS_SELECTOR, 'iframe[src="/flightsOrderCenter.do"]'))

        sleep(3)

    def appoint_flight_driver(self, driver_phone):
        WebDriverWait(self.driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/flightsOrderCenter.do?method=toAssignOrChangeOrder"]')))
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#driverPhone'))).send_keys(
            driver_phone)
        self.driver.find_element_by_css_selector('#searchBtn').click()
        sleep(1)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR,
                                              '#service-vue>div>div>table#driver-schedule>tbody#driver-schedule-list>tr:nth-child(1)'))).click()
        self.driver.switch_to.parent_frame()  # 指派与输入电话不在同一iframe，怪异的设计

        tip_text = WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'span.dispatch-tip-info'))).text
        if tip_text == '新增司机排班':
            # 收集司机信息
            self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR,
                                                                 'iframe[src^="/flightsOrderCenter.do?method=toAssignOrChangeOrder"]'))
            driver_id = self.driver.find_element_by_css_selector('tbody#driver-schedule-list>tr').get_attribute(
                'driver-id')
            # 以下信息简单处理，没跟实际车辆相关
            max_user = 4
            max_package = 0
            car_type = '网约车/5座/舒适型'
            oc_center = '漳州运营中心'
            driver_ = Driver(driver_id, max_user, max_package, car_type, oc_center, None, None,
                            driver_type=DriverType.BUS_DRIVER)
            setattr(self, 'new_driver', driver_)
            setattr(self, 'new_driver_flag', True)
            self.driver.switch_to.parent_frame()
        self.driver.find_element_by_css_selector('div>a.layui-layer-btn0').click()
        msg_text = utils.wait_for_laymsg(self.driver)
        if '操作成功' in msg_text:
            if getattr(self, 'new_driver_flag'):
                globalvar.add_driver(getattr(self, 'new_driver'))
        else:
            log.logger.error(f'指派班线订单失败，msg={msg_text}')
            assert False
        sleep(3)

    def add_inter_order(self, order_id):
        """
        补城际订单 - -补单页面操作
        :param  driver:
        :param  order_id: 订单ID
        :return:
        """
        try:
            WebDriverWait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getinterCityDriverAddOrdersPage"]')))
            sleep(1)
            #    utils.input_ori_des(driver, 'XMC', '361000', 'XM', '361000')   #  没有调用该函数，是由于在正式环境中，起点方位有默认值，导致无法输入起点
            we_ori = WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName')))
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#startName-suggest>div')))
            we_ori.click()
            we_ori.send_keys(Keys.BACKSPACE)
            self.driver.execute_script("$('div#endsName-suggest').html('')")
            we_ori.send_keys('XMC')
            WebDriverWait(self.driver, 15).until(
                EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_origin'), '361000'))

            we_des = self.driver.find_element_by_css_selector('#endsName')
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
            sleep(1)
            we_des.send_keys(Keys.BACKSPACE)
            if argv[1] != "TEST":  # 灰度环境只有加了等待，下面点击事件才生效，疑惑！！！
                sleep(2)
            we_des.click()
            WebDriverWait(self.driver, 60).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
            we_des.send_keys('XM')
            WebDriverWait(self.driver, 15).until(
                EC.text_to_be_present_in_element_value((By.CSS_SELECTOR, '#sel_destination'), '361000'))
            sleep(1)
            self.driver.find_element_by_css_selector('#btnQuery').click()

            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
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
                    expect_css = 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li:nth-child({})'.format(
                        index + 1)
                    self.driver.find_element_by_css_selector(expect_css).click()
                    sleep(1)
                    self.driver.find_element_by_css_selector('#orderAddBtn').click()

                    try:
                        msg_text = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, '.layui-layer-content.layui-layer-padding'))).text
                        setattr(self, 'add_result_text', msg_text)
                    except:
                        pass

                    self.driver.switch_to.parent_frame()
                    sleep(1)
                    try:
                        WebDriverWait(self.driver, 1).until(
                            EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn->a.layui-layer-btn0'))).click()
                        try:
                            msg_text = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR, '.layui-layer-content.layui-layer-padding'))).text
                            setattr(self, 'add_result_text', msg_text)
                        except:
                            pass
                    except:
                        pass
                    self.driver.switch_to.frame(
                        self.driver.find_element_by_css_selector(
                            'iframe[src^="/orderCtrl.do?method=getinterCityDriverAddOrdersPage"]'))
                    self.driver.find_element_by_css_selector('#closeBtn').click()
                    break

        except TimeoutException as msg:
            log.logger.debug(f'快线补城际：{msg.args}-{msg.msg}-{msg.stacktrace}')
            self.driver.find_element_by_css_selector('#closeBtn').click()
        finally:
            self.driver.switch_to.parent_frame()
            sleep(2)

    def add_bus_order(self, order_id):
        """
        补定制快线--补单页面操作
        :param driver:
        :param order_id:订单ID
        :return:
        """
        try:
            WebDriverWait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getKbDriverAddOrdersPage"]')))
            WebDriverWait(self.driver, 80).until(EC.visibility_of_all_elements_located(
                (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
            self.driver.find_element_by_css_selector('.fs-label-wrap>.fs-label').click()
            if argv[1] == 'TEST':
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="高林SM专线"]'))).click()
            else:
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="厦门测试班线"]'))).click()
            if argv[1] == 'STAGE':
                sleep(3)
            try:
                self.driver.find_element_by_css_selector('#btnQuery').click()
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li')))
            except:
                sleep(5)
                self.driver.find_element_by_css_selector('#btnQuery').click()
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
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
                    expect_css = 'div#orderDispatchAddLeft>ul#dispatch-list-add-all-rows>li:nth-child({})'.format(
                        index + 1)
                    self.driver.find_element_by_css_selector(expect_css).click()
                    sleep(1)
                    self.driver.find_element_by_css_selector('#orderAddBtn').click()
                    msg_text = utils.wait_for_laymsg(self.driver)
                    if '补单操作成功!' not in msg_text:
                        log.logger.error(f'补班线订单失败，msg={msg_text}')
                        assert False
                    break
            self.driver.find_element_by_css_selector('#closeBtn').click()
        except TimeoutException:
            self.driver.find_element_by_css_selector('#closeBtn').click()
            log.logger.error(f'补班线订单页面超时错误')
            assert False
        finally:
            sleep(1)
            self.driver.switch_to.parent_frame()

    def filter_bus_driver(self, order):
        bus_drivers = list(filter(lambda _driver: _driver.driver_type == DriverType.BUS_DRIVER, globalvar.driver_pool))
        if len(bus_drivers) == 0:
            raise IndexError
        if order.order_type in [OrderType.CARPOOLING, OrderType.FASTLINE]:
            for index, driver in enumerate(bus_drivers):
                if order.order_count <= driver.max_user - driver.appoint_user_count and driver.charter_count == 0:
                    driver.appoint_user_count += order.order_count
                    return driver
                elif index == len(bus_drivers) - 1:
                    raise FoundDriverError(order.order_type)

        elif order.order_type in [OrderType.CHARACTER, OrderType.DAYSCHARACTER]:
            free_drivers = list(filter(lambda x: x.charter_count == 0 and x.appoint_user_count == 0, bus_drivers))
            if len(free_drivers) == 0:
                raise IndexError
            else:
                for index, driver in enumerate(free_drivers):
                    if CarType.PRIORITY_DIST[driver.car_type] >= CarType.PRIORITY_DIST[order.car_type]:
                        driver.charter_count += 1
                        return driver
                    elif index == len(free_drivers) - 1:
                        raise FoundDriverError(order.order_type)

    def search_extract_driver(self, driver_):

        WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#driverList'))).click()
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#intercityDriver>table>#tdy_driver_queue>tr[page_type="driver_queue"]')))
        info_text = self.driver.find_element_by_css_selector('#intercityDriver>#pagebar>p').text
        page_num = int(re.search(r'.+/(.+)', info_text).group(1))
        for i in range(page_num):
            reported_driver_records = WebDriverWait(self.driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#intercityDriver>table>#tdy_driver_queue> tr[page_type="driver_queue"]')))
            for index, record in enumerate(reported_driver_records):
                flight_no_css = f'div#intercityDriver>table>tbody#tdy_driver_queue>tr[page_type="driver_queue"]:nth-child({index + 1})>td:nth-child(2)'
                try:
                    flight_no = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, flight_no_css))).text
                    record_driver_id = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'#intercityDriver>table>#tdy_driver_queue > tr[page_type="driver_queue"]:nth-child({index + 1}'))).get_attribute('driver_id')
                except StaleElementReferenceException:
                    flight_no = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, flight_no_css))).text
                    record_driver_id = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,
                                                        f'#intercityDriver>table>#tdy_driver_queue > tr[page_type="driver_queue"]:nth-child({index + 1}'))).get_attribute('driver_id')
                if record_driver_id == driver_.driver_id and flight_no == globalvar.get_value('FlightNo'):
                    driver_css = f'div#intercityDriver>table>tbody#tdy_driver_queue>tr[page_type="driver_queue"]:nth-child({index + 1})'
                    return driver_css
            self.driver.execute_script("$('#pagebar>a.next').click()")
            sleep(1)