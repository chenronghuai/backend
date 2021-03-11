import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, file_data, data, unpack
import utils
from utils import OrderType
from utils import TestMeta, OrderStatus
import globalvar


@ddt
class TestOrderManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.inter_orders = list(filter(
            lambda order: order.order_type in [OrderType.CARPOOLING, OrderType.CHARACTER, OrderType.EXPRESS,
                                               OrderType.DAYSCHARACTER], globalvar.order_pool))
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '监控管理', '订单管理', 'orderManage.do')
        utils.input_ori_des(cls.driver, "XMC", "361000", "XM", "361000")

    def operate_dialog(self, driver, button_css_locator, iframe_src, operator_css_locator):
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, button_css_locator))).click()
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, iframe_src)))
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, operator_css_locator))).click()
        driver.switch_to.parent_frame()

    @data(1, 2, 3, 4, 5, 6)
    def test_complete_order(self, index):
        self.driver.find_element_by_css_selector('#btnQuery').click()
        order = self.inter_orders[index-1]
        css = utils.get_record_by_attr(self.driver, 'table#data_table>tbody>tr', 'order-list-id', order.order_id)

        if order.order_status == OrderStatus.APPOINTED:
            css_oncar = css + '>td:nth-child(21)>a[name="order-oncar"]'  # "上车"
            self.operate_dialog(self.driver, css_oncar, '[src^="/orderManage.do?method=getOrderManageOnCar"]', '#todoSureBtn')

            css_offcar = css + '>td:nth-child(21)>a[name="order-offcar"]'  # "下车"
            self.operate_dialog(self.driver, css_offcar, '[src^="/orderManage.do?method=getOrderManageOffCar"]', '#todoSureBtn')

            css_offline = css + '>td:nth-child(21)>a[name="order-offlinefinish"]'  # "线下"
            self.operate_dialog(self.driver, css_offline, '[src^="/orderManage.do?method=getOrderManageOffline"]', '#todoSureBtn')

            css_assert = css + '>td:nth-child(17)'
            self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  #清空表内容，同步最新的订单状态
            text_str = WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, css_assert))).text
            self.assertEqual(text_str, '已完成')

        elif order.order_status == OrderStatus.WAITING:
            css_cancel = css + '>td:nth-child(21)>a[name="order-cancel"]'   # "消单"
            WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, css_cancel))).click()
            utils.cancel_order(self.driver, '联系不上司机')
            sleep(1)
            css_assert = css + '>td:nth-child(17)'
#            self.driver.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，同步最新的订单状态
            text_str = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_assert))).text
            self.assertEqual(text_str, '客服取消')
