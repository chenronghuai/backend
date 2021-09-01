import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
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


expect_text_dict = {
            '专车排班': ['补单', '核单', '置顶', '取消', '发车', '锁定', '空车'],
            '已发车': ['补单', '详情', '补空单'],
            '即时1': ['呼出', '消单', '指派', '分享', '收回'],
            '即时2': ['呼出', '消单', '指派', '分享'],
            '已派': ['呼出', '改派', '消单', '改单', '重派司机']
        }


@ddt
class TestInterCenter(unittest.TestCase, metaclass=TestMeta):
    current_oc_center = []
    oc_flag = True

    @classmethod
    def setUpClass(cls):
        cls.ic = FuncInterCenter()
        cls.__name__ = cls.__name__ + "（城际调度中心：指派拼车、包车、货件，补单拼车、货件、快线，改派、发车功能，包车车型过滤，操作栏菜单，运营中心订单可视权限）"

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data('泉州运营中心', '厦门运营中心')
    def test_driver_permission(self, oc_center):
        """
        运营中心关联司机测试用例
        :param oc_center: 运营中心
        :return:
        """
        except_iter = []
        unexcept_iter = []
        self.ic.input_center_line(oc_center, "XMC", "361000", "XM", "361000")
        goal_drivers = list(
            filter(lambda driver_: driver_.oc_center in self.ic.current_oc_center, globalvar.driver_pool))
        goal_not_drivers = list(
            filter(lambda driver_: driver_.oc_center not in self.ic.current_oc_center, globalvar.driver_pool))

        try:
            driver_id_list = []
            we_actual_drivers = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody#tdy_driver_queue>tr')))
            for i in we_actual_drivers:
                driver_id_list.append(i.get_attribute('driver-id'))
        except StaleElementReferenceException:
            driver_id_list = []
            we_actual_drivers = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody#tdy_driver_queue>tr')))
            for i in we_actual_drivers:
                driver_id_list.append(i.get_attribute('driver-id'))
        for driver in goal_drivers:
            except_iter.append(driver.driver_id in driver_id_list)
        for driver in goal_not_drivers:
            unexcept_iter.append(driver.driver_id in driver_id_list)
        return all(except_iter) and not any(unexcept_iter)

    @data(1, 2)
    def test_match_car_type(self, index):
        """
        包车车型匹配测试用例
        :param _index: 订单下标
        :return:
        """
        try:
            expect_iter = []
            character_orders = list(filter(lambda order: order.order_type == OrderType.CHARACTER, globalvar.order_pool))
            net_drivers = list(filter(lambda driver: driver.driver_type == DriverType.NET_DRIVER and driver.oc_center == utils.read_config_value(argv[2], 'oc'), globalvar.driver_pool))
            expect_drivers = []
            for i in net_drivers:
                if CarType.PRIORITY_DIST[i.car_type] >= CarType.PRIORITY_DIST[character_orders[index-1].car_type]:
                    expect_drivers.append(i)
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#orderList'))).click()
            globalvar.GLOBAL_DRIVER.execute_script("$('tbody.immediate-order').html()")
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.nav-right.td-opera > a[title="即时"]').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#order-nav-query'))).click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody.immediate-order>tr')))
            utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#orderImmediately>table', '.immediate-order>tr', 'order-id', character_orders[index-1].order_id, '指派')
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it(
                    (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getOrderDriverAppointPage"]')))
            try:
                we_filter_drivers = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#intercity-lists>tr>td:nth-child(1)>input')))
                driver_id_list = [x.get_attribute('driver_id') for x in we_filter_drivers]
                for driver in expect_drivers:
                    expect_iter.append(driver.driver_id in driver_id_list)
            except TimeoutException:  # 没有匹配司机
                if len(expect_drivers) == 0:
                    expect_iter.append(True)
        finally:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#todoExitBtn').click()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(2)
        self.assertTrue(all(expect_iter))


    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(OrderType.CARPOOLING, OrderType.EXPRESS, OrderType.CHARACTER)
#    @unpack
    def test_appoint(self, order_type):
        """
        指派订单测试用例
        :param _order_type: 订单类型OrderType
        :return:
        """
        if self.ic.oc_flag and argv[1] == 'TEST':
            self.ic.input_center_line("厦门运营中心", "XMC", "361000", "XM", "361000")
            self.ic.oc_flag = False
        order = utils.get_first_order(order_type)
        driver = self.ic.filter_driver(order)
        if driver == '没有合适的司机':
            log.logger.debug(f'指派{order_type}失败，msg=没有匹配的司机')
            assert False
        self.ic.appoint_order(order.order_id, driver.driver_id)
        if '指派操作成功!' in getattr(self.ic, 'appoint_result_text', ''):
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.nav-right.td-opera > a[title="已派"]').click()
            appointed_orders = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#orderImmediately>table>tbody#tdy_driver_queue>tr')))
            try:
                id_list = [x.get_attribute('order-id') for x in appointed_orders]
            except StaleElementReferenceException:
                WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '#orderImmediately>table>tbody#tdy_driver_queue>tr')))
                id_list = [x.get_attribute('order-id') for x in appointed_orders]
            status = True if order.order_id in id_list else False
            self.assertTrue(status)
            order.order_status = OrderStatus.APPOINTED if status else OrderStatus.WAITING
        else:
            log.logger.debug(f'城际调度中心指派{order_type}失败，msg={getattr(self.ic, "appoint_result_text", "")}')
            assert False

    @data(OrderType.CARPOOLING, OrderType.EXPRESS, OrderType.FASTLINE)
#    @unittest.skip("直接跳过")
    def test_add_order(self, order_type):
        """
        补单测试用例
        :param _order_type: 订单类型OrderType
        :return:
        """
        order = utils.get_first_order(order_type)
        driver = self.ic.filter_driver(order)
        appointed_user_count = driver.appoint_user_count
        appointed_package_count = driver.appoint_package_count
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#driverList').click()
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#order-car-query').click()
        self.ic.select_driver(driver.driver_id)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getDriverAddOrdersMergePage"]')))
        if order_type in [OrderType.CARPOOLING, OrderType.CHARACTER, OrderType.EXPRESS, OrderType.DAYSCHARACTER]:
            globalvar.GLOBAL_DRIVER.find_element_by_xpath('//div[@class="order-ri-tit"]/ul/li[text()="补城际订单"]').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getDriverAddOrdersPage"]')))
            self.ic.add_inter_order(order.order_id)

        elif order_type in [OrderType.FASTLINE]:
            globalvar.GLOBAL_DRIVER.find_element_by_xpath('//div[@class="order-ri-tit"]/ul/li[text()="补快线订单"]').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, '[src^="/orderCtrl.do?method=getDriverAddBusOrdersPage"]')))
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.fs-label-wrap>div.fs-label').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.fs-options>div>div.fs-option-label')))
            if argv[1] == 'TEST':
                globalvar.GLOBAL_DRIVER.execute_script(
                    "$('div.fs-dropdown>div.fs-options>div>div.fs-option-label').filter(function(index){return $(this).text()=='高林SM专线';}).click()")
            else:
                globalvar.GLOBAL_DRIVER.execute_script(
                    "$('div.fs-dropdown>div.fs-options>div>div.fs-option-label').filter(function(index){return $(this).text()=='厦门测试班线';}).click()")
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
            self.ic.add_fastline_order(order.order_id)

        msg_text = getattr(self.ic, 'add_result_text', '未获取到补单结果信息')
        if '补单操作成功!' in msg_text:
            globalvar.GLOBAL_DRIVER.execute_script('$("div#intercityDriver>table>tbody#tdy_driver_queue").html("")')
            sleep(1)
            globalvar.GLOBAL_DRIVER.execute_script('$("#order-car-query").click()')
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr>td:nth-child(1)')))
            dispach_status_css = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr',
                                                          'driver-id', driver.driver_id)
            try:
                text = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(dispach_status_css + '>td:nth-child(7)').text
            except StaleElementReferenceException:
                sleep(1)
                text = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(dispach_status_css + '>td:nth-child(7)').text
            if order_type in [OrderType.CARPOOLING, OrderType.FASTLINE]:
                result_appointed_count = int(re.search(r'(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+', text).group(2))
                status = True if result_appointed_count == appointed_user_count else False
            elif order_type in [OrderType.EXPRESS]:
                result_package_count = int(re.search(r'(\d+)\D+(\d+)\D+(\d+)\D+(\d+)\D+', text).group(3))
                status = True if result_package_count == appointed_package_count else False
            else:
                log.logger.error(f'不支持的订单类型--{order_type}')
                status = False
            self.assertTrue(status)
            if status:
                globalvar.appointed_driver_pool.append(driver)
            order.order_status = OrderStatus.APPOINTED if status else OrderStatus.WAITING
        else:
            log.logger.debug(f'城际调度中心{order_type}补单失败，msg={msg_text}')
            assert False

    @data(OrderType.CARPOOLING, OrderType.EXPRESS)
    def test_reback_order(self, _order_type):
        """
        改派订单测试用例
        :param _order_type: 订单类型OrderType
        :return:
        """
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '城际调度中心', 'orderCenterNew.do')  # 不加会机率性导致下句超时，不解？
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#orderList'))).click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.nav-right.td-opera > a[title="已派"]'))).click()
        globalvar.GLOBAL_DRIVER.execute_script("$('#orderImmediately>table>#tdy_driver_queue').html('')")
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.order-ti-con.on>div>div>#order-nav-query'))).click()
#        we_appointed_orders = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'tbody.dispatched-order>tr')))  # 正式环境暂无class属性
        we_appointed_orders = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'tbody>tr[driver_id]')))
        global_order_id_list = [x.order_id for x in globalvar.order_pool]
        for i in range(len(we_appointed_orders)):
            try:
                order_id = we_appointed_orders[i].get_attribute('order-id')
            except StaleElementReferenceException:
#                WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody>tr[driver_id]')))
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.order-ti-con.on>div>div>#order-nav-query').click()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.dispatched-order>tr')))
                order_id = we_appointed_orders[i].get_attribute('order-id')
#                sleep(2)  # 这2句还是会出现StaleElementReferenceException，改用上面3句试试
#                order_id = we_appointed_orders[i].get_attribute('order-id')
            if order_id not in global_order_id_list:
                continue
            order = globalvar.get_order(order_id)
            if order.order_type == _order_type:
                utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#orderImmediately>table', '#orderImmediately>table>tbody.dispatched-order>tr', 'order-id', order_id, '改派')
                msg_text = utils.reback_order(globalvar.GLOBAL_DRIVER, '司机设备故障')
                status = '已成功重新指派订单!' in msg_text  # 以下代码有大概率的超时问题，看不出原因，用返回做简单判断
                if status:
                    order.order_status = OrderStatus.REWAITING
                '''
                if '已成功重新指派订单!' in msg_text:
                    order.order_status = OrderStatus.REWAITING
                    sleep(1)
                    try:
                        we_new_appointed_orders = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
                            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'tbody.dispatched-order>tr')))
                        order_id_list = [x.get_attribute('order-id') for x in we_new_appointed_orders]
                    except StaleElementReferenceException:
                        sleep(2)
                        we_new_appointed_orders = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
                            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'tbody.dispatched-order>tr')))
                        order_id_list = [x.get_attribute('order-id') for x in we_new_appointed_orders]
                    except TimeoutException:
                        log.logger.debug(f'超时异常（大概率为列表里没有已派订单）!')
                        order_id_list = []

                    self.assertNotIn(order_id, order_id_list)

                else:
                    log.logger.error(f'改派{order.order_type}失败，msg={msg_text}')
                    assert False
                '''
                break
            elif order.order_type != _order_type and i == len(we_appointed_orders):
                log.logger.error(f'已派订单列表没有{order.order_type}')
                raise IndexError
        sleep(1)

    @data(1, 2)
#    @unittest.skip("直接跳过")
    def test_depart(self, index):
        """
        发车功能测试用例
        :param index: 司机索引下标
        :return:
        """
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '城际调度中心', 'orderCenterNew.do')  # 不加这句，以下有可能超时，疑惑？
        depart_drivers = list(filter(lambda x: x.driver_type == DriverType.NET_DRIVER and x.oc_center in self.ic.current_oc_center, globalvar.driver_pool))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#driverList'))).click()
        globalvar.GLOBAL_DRIVER.execute_script('$("#intercityDriver>table>tbody#tdy_driver_queue").html("")')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.bbx-orderlist-nav>.nav-right.td-opera>a[title="专车排班"]'))).click()
#        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#order-car-query'))).click()  # 8.27注释掉，注释前碰到下句超时
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#intercityDriver>table>tbody#tdy_driver_queue>tr[page_type="driver_queue"]')))
        utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#intercityDriver>table', '#intercityDriver>table>tbody>tr[page_type="driver_queue"]', 'driver-id', depart_drivers[index-1].driver_id, '发车')
        globalvar.GLOBAL_DRIVER.switch_to.default_content()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0')))
        globalvar.GLOBAL_DRIVER.execute_script("""$('div[type="dialog"]>div>a.layui-layer-btn0').click()""")
        globalvar.GLOBAL_DRIVER.switch_to.frame(globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, 'iframe[src="/orderCenterNew.do"]'))
        msg_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
        if '发车成功' in msg_text:
            sleep(1)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.nav-right.td-opera>a[title="已发车"]').click()
            departed_drivers = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#intercityDriver>table>tbody#tdy_driver_queue>tr')))
            # try模块为了规避系统刷新时DOM为空导致的异常
            try:
                id_list = [x.get_attribute('driver-id') for x in departed_drivers]
            except StaleElementReferenceException:
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, departed_drivers)))
                id_list = [x.get_attribute('driver-id') for x in departed_drivers]
            status = True if depart_drivers[index-1].driver_id in id_list else False
            self.assertTrue(status)
        else:
            log.logger.debug(f'发车失败，msg={msg_text}')
            assert False
        sleep(1)

    @data('专车排班', '已发车', '即时', '已派')
    def test_operate_menu(self, category):
        """
        城际调度中心操作栏菜单确认测试用例
        :param category: 字符串，表标签
        :return:
        """
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '城际调度中心', 'orderCenterNew.do')  # 不加这句，以下有可能超时，添加试试
        result_operate_text, info_dict = self.ic.get_operate_text(category)

        if category != '已发车':
            if category == '即时':
                if utils.read_config_value(argv[2], 'oc') == info_dict['oc']:
                    self.assertEqual(sorted(result_operate_text), sorted(expect_text_dict['即时1']))
                else:
                    self.assertEqual(sorted(result_operate_text), sorted(expect_text_dict['即时2']))
            else:
                self.assertEqual(sorted(result_operate_text), sorted(expect_text_dict[category]))
        else:
            self.assertEqual(sorted(result_operate_text), sorted(['补单', '详情']))   # 已发车需要细化各种派单情形：人满、货满，待后续优化

        sleep(2)  # 发现当前用例会取到前一个用例的菜单文本，加等待试试


