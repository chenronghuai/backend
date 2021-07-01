import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
from utils import OrderStatus
from sys import argv
from utils import TestMeta
import globalvar
from utils import OrderType
import log
from SystemLog.func_sms_log import FuncSmsLog


@ddt
class TestSms(unittest.TestCase, metaclass=TestMeta):

    class Node:
        ORDERED = '下单'
        APPOINTED = '指派'
        CANCELED = '取消'
        REAPPOINTED = '改派'

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        cls.sl = FuncSmsLog()
        cls.__name__ = cls.__name__ + "（短信日志验证：下单、指派等短信节点）"

    @data((OrderType.CARPOOLING, Node.ORDERED), (OrderType.CARPOOLING, Node.APPOINTED), (OrderType.EXPRESS, Node.ORDERED), (OrderType.EXPRESS, Node.APPOINTED), (OrderType.FASTLINE, Node.ORDERED), (OrderType.FASTLINE, Node.APPOINTED))
    @unpack
    def test_sms(self, order_type, order_node):
        for index, order in enumerate(globalvar.order_pool):
            if order_node == self.Node.ORDERED and order.order_status in [OrderStatus.WAITING, OrderStatus.APPOINTED]:
                self.sl.search_log(order.order_phone)
                if order_type == OrderType.CARPOOLING:
                    self.assertIn('已为您下单成功，正在为您指派附近车辆', self.sl.get_content_by_field(4))
                    break
                elif order_type == OrderType.EXPRESS:
                    self.assertIn('寄件订单已下单成功', self.sl.get_content_by_field(4))
                    break
                elif order_type == OrderType.FASTLINE:
                    if argv[1] == "TEST":
                        return True
                    else:
                        self.assertIn('请上车后扫车上二维码及时完成付款，祝您出行愉快', self.sl.get_content_by_field(4))
                    break

            elif order_node == self.Node.APPOINTED and order.order_status in [OrderStatus.APPOINTED]:
                self.sl.search_log(order.order_phone)
                if order_type == OrderType.CARPOOLING:
                    if argv[1] == "TEST":
                        self.assertIn('微信关注“帮邦行”公号或下载帮邦行APP', self.sl.get_content_by_field(4))
                    else:
                        self.assertIn('若需开票请线上支付（出租车向司机索要）', self.sl.get_content_by_field(4))
                    break
                elif order_type == OrderType.EXPRESS:
                    self.assertIn('若需开票请线上支付', self.sl.get_content_by_field(4))
                    break
                elif order_type == OrderType.FASTLINE:
                    if argv[1] == "TEST":
                        self.assertIn('您乘坐的', self.sl.get_content_by_field(4))
                    else:
                        return True
                    break

            elif index == len(globalvar.order_pool) - 1:
                log.logger.warning(f'短信日志：订单池里没有{order_type}类型的订单')
                raise IndexError
