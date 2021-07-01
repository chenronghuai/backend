import unittest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, file_data, data, unpack
import utils
from utils import OrderType
from utils import TestMeta, OrderStatus
from sys import argv
from MonitorManage.func_order_manage import FuncOrderManage


@ddt
class TestOrderManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.om = FuncOrderManage()
        cls.__name__ = cls.__name__ + "（网约订单管理：订单上车、下车、现金等操作）"

    test_order = (1, 2, 3, 4, 5, 6, 7, 8, 9)
    prod_order = (1, 2, 3, 4, 5, 6)

    @data(*test_order if argv[1] == 'TEST' else prod_order)
    def test_complete_order(self, index):

        order = self.om.orders[index - 1]
        if getattr(TestOrderManage, 'init', True):
            utils.input_ori_des(self.om.driver, "XMC", "361000", "XM", "361000")
            self.om.driver.find_element_by_css_selector('#moreSpan').click()
            we_phone = WebDriverWait(self.om.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#phone')))
            we_phone.clear()
            we_phone.send_keys(order.order_phone)
            self.om.driver.find_element_by_css_selector('#moreSpan').click()
            WebDriverWait(self.om.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnQuery'))).click()
            setattr(TestOrderManage, 'init', False)
        if order.order_type in [OrderType.INNER, OrderType.HELPDRIVE]:  # 处理市内及代驾订单
            self.om.input_customer_phone(14759250515)
            self.om.driver.execute_script("$('table#data_table>tbody>tr').html('')")
            sleep(3)
            WebDriverWait(self.om.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnQuery'))).click()
        css = utils.get_record_by_attr(self.om.driver, 'table#data_table>tbody>tr', 'order-list-id', order.order_id)

        if order.order_status == OrderStatus.APPOINTED:
            css_oncar = css + '>td:nth-child(21)>a[name="order-oncar"]'  # "上车"
            self.om.operate_dialog(self.om.driver, css_oncar, '[src^="/orderManage.do?method=getOrderManageOnCar"]', '#todoSureBtn')

            css_offcar = css + '>td:nth-child(21)>a[name="order-offcar"]'  # "下车"
            self.om.operate_dialog(self.om.driver, css_offcar, '[src^="/orderManage.do?method=getOrderManageOffCar"]', '#todoSureBtn')

            css_offline = css + '>td:nth-child(21)>a[name="order-offlinefinish"]'  # "线下"
            self.om.operate_dialog(self.om.driver, css_offline, '[src^="/orderManage.do?method=getOrderManageOffline"]', '#todoSureBtn')

            css_assert = css + '>td:nth-child(17)'
            self.om.driver.execute_script('$("table#data_table>tbody>tr").html("")')  #清空表内容，同步最新的订单状态
            text_str = WebDriverWait(self.om.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, css_assert))).text
            self.assertEqual(text_str, '已完成')

        elif order.order_status == OrderStatus.WAITING:
            # 市内及代驾订单，超过规定时间会由系统自动取消，需增加判断
            text_str = WebDriverWait(self.om.driver, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css + '>td:nth-child(17)'))).text
            if text_str == "客服取消":
                if order.order_type in [OrderType.INNER, OrderType.HELPDRIVE] and time.time()-order.order_time > 180:
                    return True
                else:
                    raise IndexError
            else:
                css_cancel = css + '>td:nth-child(21)>a[name="order-cancel"]'   # "消单"
                WebDriverWait(self.om.driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, css_cancel))).click()
                utils.cancel_order(self.om.driver, '联系不上司机')
                sleep(1)
                css_assert = css + '>td:nth-child(17)'
                text_str = WebDriverWait(self.om.driver, 15).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, css_assert))).text
                self.assertEqual(text_str, '客服取消')
