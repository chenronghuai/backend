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
from sys import argv


@ddt
class TestOrderManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.orders = list(filter(
            lambda order: order.order_type in [OrderType.CARPOOLING, OrderType.CHARACTER, OrderType.EXPRESS, OrderType.INNER, OrderType.HELPDRIVE,
                                               OrderType.DAYSCHARACTER], globalvar.order_pool))
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '监控管理', '订单管理', 'orderManage.do')
        globalvar.opened_window_pool.append('orderManage.do')
        utils.input_ori_des(cls.driver, "XMC", "361000", "XM", "361000")
#        cls.input_customer_phone(14759250515)
        WebDriverWait(cls.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnQuery'))).click()
        cls.__name__ = cls.__name__ + "（网约订单管理：订单上车、下车、现金等操作）"

    @classmethod
    def input_customer_phone(cls, phone):
        WebDriverWait(cls.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#moreSpan'))).click()
        WebDriverWait(cls.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnClean'))).click()
        cls.driver.find_element_by_css_selector('#phone').send_keys(phone)
        cls.driver.find_element_by_css_selector('#moreSpan').click()

    def operate_dialog(self, driver, button_css_locator, iframe_src, operator_css_locator):
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, button_css_locator))).click()
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, iframe_src)))
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, operator_css_locator))).click()
        driver.switch_to.parent_frame()

    test_order = (1, 2, 3, 4, 5, 6, 7, 8, 9)
    prod_order = (1, 2, 3, 4, 5, 6)

    @data(*test_order if argv[1] == 'TEST' else prod_order)
    def test_complete_order(self, index):
        order = self.orders[index-1]
        if order.order_type in [OrderType.INNER, OrderType.HELPDRIVE]:  # 处理市内及代驾订单
            self.driver.find_element_by_css_selector('#btnClean').click()
            TestOrderManage.input_customer_phone(14759250515)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnQuery'))).click()
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
            # 市内及代驾订单，超过规定时间会由系统自动取消，需增加判断
            text_str = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css + '>td:nth-child(17)'))).text
            if text_str == "客服取消":
                raise IndexError
            else:
                css_cancel = css + '>td:nth-child(21)>a[name="order-cancel"]'   # "消单"
                WebDriverWait(self.driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, css_cancel))).click()
                utils.cancel_order(self.driver, '联系不上司机')
                sleep(1)
                css_assert = css + '>td:nth-child(17)'
                text_str = WebDriverWait(self.driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, css_assert))).text
                self.assertEqual(text_str, '客服取消')
