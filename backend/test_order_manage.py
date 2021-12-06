import unittest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, file_data, data, unpack
import utils
import log
import globalvar
from utils import OrderType
from utils import TestMeta, OrderStatus
from sys import argv
from MonitorManage.func_order_manage import FuncOrderManage
from selenium.common.exceptions import StaleElementReferenceException


@ddt
class TestOrderManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.om = FuncOrderManage()
        cls.__name__ = cls.__name__ + "（网约订单管理：订单上车、下车、现金等操作）"

    test_order = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    prod_order = (1, 2, 3, 4, 5, 6, 7)

    @data(*test_order if argv[1] == 'TEST' else prod_order)
    def test_complete_order(self, index):

        order = self.om.orders[index - 1]
        if getattr(TestOrderManage, 'init', True):
            utils.input_ori_des(globalvar.GLOBAL_DRIVER, "XMC", "361000", "XM", "361000")
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#moreSpan').click()
            we_phone = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#phone')))
            we_phone.clear()
            we_phone.send_keys(order.order_phone)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#moreSpan').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnQuery'))).click()
            setattr(TestOrderManage, 'init', False)
        if order.order_type in [OrderType.INNER, OrderType.HELPDRIVE]:  # 处理市内及代驾订单
            self.om.input_customer_phone(14759250515)
            globalvar.GLOBAL_DRIVER.execute_script("$('table#data_table>tbody').html('')")
            sleep(1)
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnQuery'))).click()
        css = utils.get_record_by_attr(globalvar.GLOBAL_DRIVER, 'table#data_table>tbody>tr', 'order-list-id', order.order_id)

        if order.order_status == OrderStatus.APPOINTED:

            css_oncar = css + '>td:nth-child(21)>a[name="order-oncar"]'  # "上车"
            operate_oncar_text = self.om.operate_dialog(css_oncar, '[src^="/orderManage.do?method=getOrderManageOnCar"]', '#todoSureBtn')
            if '操作成功!' not in operate_oncar_text:
                log.logger.error(f'上车操作失败，msg={operate_oncar_text}')
                assert False

            css_offcar = css + '>td:nth-child(21)>a[name="order-offcar"]'  # "下车"
            try:
                operate_offcar_text = self.om.operate_dialog(css_offcar, '[src^="/orderManage.do?method=getOrderManageOffCar"]', '#todoSureBtn')
            except TimeoutError:  # 10.09，灰度环境碰到超时
                operate_offcar_text = self.om.operate_dialog(css_offcar, '[src^="/orderManage.do?method=getOrderManageOffCar"]', '#todoSureBtn')
            if '操作成功!' not in operate_offcar_text:
                log.logger.error(f'下车操作失败，msg={operate_offcar_text}')
                assert False

            css_offline = css + '>td:nth-child(21)>a[name="order-offlinefinish"]'  # "线下"
            operate_offline_text = self.om.operate_dialog(css_offline, '[src^="/orderManage.do?method=getOrderManageOffline"]', '#todoSureBtn')
            if '已支付成功!' not in operate_offline_text:
                log.logger.error(f'线下支付操作失败，msg={operate_offline_text}')
                assert False

            css_assert = css + '>td:nth-child(17)'
            globalvar.GLOBAL_DRIVER.execute_script('$("table#data_table>tbody>tr").html("")')  #清空表内容，同步最新的订单状态
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnQuery'))).click()
            try:
                text_str = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, css_assert))).text
            except StaleElementReferenceException:
                text_str = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, css_assert))).text
            self.assertEqual(text_str, '已完成')

        elif order.order_status in [OrderStatus.WAITING, OrderStatus.REWAITING]:
            # 市内及代驾订单开启自动调度，超过规定时间会由系统自动取消，需增加判断
            text_str = WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css + '>td:nth-child(17)'))).text
            if text_str == "客服取消":
                if order.order_type in [OrderType.INNER, OrderType.HELPDRIVE] and time.time()-order.order_time > 180:
                    return True
                else:
                    raise IndexError
            else:
                css_cancel = css + '>td:nth-child(21)>a[name="order-cancel"]'   # "消单"
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, css_cancel))).click()
                cancel_result_text = utils.cancel_order(globalvar.GLOBAL_DRIVER, '联系不上司机', 'orderManage.do')
                if '已成功取消订单!' in cancel_result_text or '乘客已经服务结束或者已经取消订单' in cancel_result_text:
                    order.order_status = OrderStatus.CANCEL
                    css_assert = css + '>td:nth-child(17)'
                    globalvar.GLOBAL_DRIVER.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，同步最新的订单状态
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
                    text_str = WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, css_assert))).text
                    self.assertEqual(text_str, '客服取消')
                else:
                    log.logger.error(f'取消订单失败，msg={cancel_result_text}')
                    assert False

