import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
from utils import OrderStatus, DriverType
from sys import argv
from utils import TestMeta
import globalvar
from utils import OrderType, Node
import log
import time
import re
from time import strftime
from SystemLog.func_sms_log import FuncSmsLog


@ddt
class TestSms(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.sl = FuncSmsLog()
        start_time = globalvar.get_value('start_time')
        end_time = strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))  # 当前时间
        cls.sl.search_log(14759250515, start_time, end_time)  # 输入确切时间段，防止跨日取不到前一天的短信
        cls.sms_content = cls.sl.get_content_by_field()  # 因乘客下单电话都为同一个号码，简单获取该号码下的短信内容
        cls.__name__ = cls.__name__ + "（短信日志验证：乘客下单、指派、改派、消单，司机派单、安全号码等短信节点）"

    @data((OrderType.CARPOOLING, Node.ORDERED), (OrderType.CARPOOLING, Node.APPOINTED), (OrderType.CARPOOLING, Node.CANCELED), (OrderType.CARPOOLING, Node.REAPPOINTED), (OrderType.EXPRESS, Node.ORDERED), (OrderType.EXPRESS, Node.APPOINTED), (OrderType.EXPRESS, Node.CANCELED), (OrderType.FASTLINE, Node.ORDERED), (OrderType.FASTLINE, Node.APPOINTED))
    @unpack
    def test_customer_sms(self, order_type, order_node):
        """
        乘客端短信测试用例
        :param order_type: 订单类型，OrderType
        :param order_node: 节点类型，Node
        :return:
        """
#        order_status_list = [order.order_status for order in globalvar.order_pool]
        for index, order in enumerate(globalvar.order_pool):
            if order_node == Node.ORDERED and order.order_status in [OrderStatus.WAITING, OrderStatus.APPOINTED]:
                if order_type == OrderType.CARPOOLING:
                    self.assertIn('已为您下单成功，正在为您指派附近车辆', self.sms_content)
                    break
                elif order_type == OrderType.EXPRESS:
                    self.assertIn('寄件订单已下单成功', self.sms_content)
                    break
                elif order_type == OrderType.FASTLINE:
                    if argv[1] == "TEST":
                        return True
                    else:
                        self.assertIn('请上车后扫车上二维码及时完成付款，祝您出行愉快', self.sms_content)
                    break

            elif order_node == Node.APPOINTED and order.order_status in [OrderStatus.APPOINTED]:
                if order_type == OrderType.CARPOOLING:
                    if argv[1] == "TEST":
                        self.assertIn('微信关注“帮邦行”公号或下载帮邦行APP', self.sms_content)
                    else:
                        self.assertIn('若需开票请线上支付（出租车向司机索要）', self.sms_content)
                    break
                elif order_type == OrderType.EXPRESS:
                    self.assertIn('若需开票请线上支付', self.sms_content)
                    break
                elif order_type == OrderType.FASTLINE:
                    if argv[1] == "TEST":
                        self.assertIn('您乘坐的', self.sms_content)
                    else:
                        return True
                    break

            elif order_node == Node.REAPPOINTED:  # 因短信用例在订单流程最后才跑，改派订单的状态已被改为OrderStatus.CANCEL,故先不做状态判断
                self.assertIn('马上为您改派最近的车辆', self.sms_content)
                break

            elif order_node == Node.CANCELED and order.order_status in [OrderStatus.CANCEL]:
                if order_type == OrderType.CARPOOLING:
                    self.assertIn('客服已帮您取消订单', self.sms_content)
                elif order_type == OrderType.EXPRESS:
                    self.assertIn('寄件订单已取消', self.sms_content)
                break

            elif index == len(globalvar.order_pool) - 1:
                log.logger.warning(f'短信日志：订单池里没有{order_type}、{order_node}节点类型的订单')
                raise IndexError

    @data((OrderType.CARPOOLING, Node.APPOINTED),(OrderType.FASTLINE, Node.APPOINTED))
    @unpack
    def test_safenum_sms(self, order_type, order_node):
        for index, order in enumerate(globalvar.order_pool):
            if order_node == Node.APPOINTED and order.order_status in [OrderStatus.APPOINTED]:
                if order_type == OrderType.CARPOOLING:
                    if argv[1] == 'TEST':
                        actual_num = re.search(r'已指派司机.*手机号(.*)为您服务.*', self.sms_content).group(1)
                    else:
                        actual_num = re.search(r'已指派司机.*师傅(.*?)，.*', self.sms_content).group(1)
                    self.assertNotEqual(actual_num, order.appoint_driver.contact_phone)
                    break
                elif order_type == OrderType.FASTLINE:
                    if argv[1] == 'TEST':
                        actual_num = re.search(r'您乘坐的.*手机号(.*)为您服务.*', self.sms_content).group(1)
                    else:
                        actual_num = re.search(r'您乘坐的.*，.*?，(.*)为您服务.*', self.sms_content).group(1)
                    self.assertNotEqual(actual_num, order.appoint_driver.contact_phone)
                    break
            elif index == len(globalvar.order_pool) - 1:
                log.logger.warning(f'短信日志：订单池里没有{order_type}、{order_node}节点类型的订单')
                raise IndexError

    @data((OrderType.CARPOOLING, Node.APPOINTED), (OrderType.EXPRESS, Node.APPOINTED), (OrderType.FASTLINE, Node.APPOINTED))
    @unpack
    def test_carnum_sms(self, order_type, order_node):
        goal_orders = list(filter(lambda order_: order_.order_contact_phone == '14759250515' and order_.order_status == OrderStatus.APPOINTED, globalvar.order_pool))
        for index, order in enumerate(goal_orders):
            if order_node == Node.APPOINTED:
                if order_type == OrderType.CARPOOLING:
                    if argv[1] == 'TEST':
                        expect_sms = f"已指派司机.+?，车牌{order.appoint_driver.car_num}，手机号\d+?为您服务"
                    else:
                        expect_sms = f"已指派司机.+?，{order.appoint_driver.car_num}，\d+?为您服务"
                    result = re.search(expect_sms, self.sms_content)
                    self.assertTrue(result)
                    break

                elif order_type == OrderType.EXPRESS:
                    if argv[1] == 'TEST':
                        expect_sms = f"已指派司机.+，{order.appoint_driver.car_num}为您服务"
                    else:
                        expect_sms = f"已指派司机.+，{order.appoint_driver.car_num}为您服务"
                    result = re.search(expect_sms, self.sms_content)
                    self.assertTrue(result)
                    break

                elif order_type == OrderType.FASTLINE:
                    if argv[1] == 'TEST':
                        expect_sms = f"您乘坐的.+，车牌{order.appoint_driver.car_num}，手机号\d+?为您服务"
                    else:
                        expect_sms = f"您乘坐的.+，{order.appoint_driver.car_num}，\d+?为您服务"
                    result = re.search(expect_sms, self.sms_content)
                    self.assertTrue(result)
                    break
            elif index == len(globalvar.order_pool) - 1:
                log.logger.warning(f'短信日志：订单池里没有{order_type}、{order_node}节点类型的订单')
                raise IndexError

    @data((DriverType.NET_DRIVER, Node.APPOINTED),)
    @unpack
    def test_driver_sms(self, driver_type, order_node):
        """
        司机端短信测试用例
        :param drier_type: 司机类型，DriverType
        :param order_node: 节点类型，Node
        :return:
        """
        try:
            driver_phone = globalvar.appointed_driver_pool[0].register_phone
            self.sl.search_log(driver_phone)
            result_sms = self.sl.get_content_by_field(4)
            if driver_type == DriverType.NET_DRIVER and order_node == Node.APPOINTED:
                if argv[1] == 'TEST':
                    self.assertIn('已为您指派', result_sms)
                else:
                    self.assertIn('师傅您好！已指派', result_sms)
        except IndexError:
            log.logger.error(f'没找到已指派的司机')
            raise IndexError
