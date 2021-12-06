import unittest
from time import sleep
from ddt import ddt, data, file_data, unpack
from utils import TestMeta
from sys import argv
from PriceManage.func_inter_price import FuncInterPrice


@ddt
class TestInterPrice(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.itp = FuncInterPrice()
        cls.__name__ = cls.__name__ + "（城际区域价格：获取、设置各种类型的城际区域价格）"

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data(['厦门市到厦门市', '拼', '所有车型', 21], ['厦门市到厦门市', '包', '网约车/5座/舒适型', 301], ['厦门市到厦门市', '货', '所有车型', 11])
    @unpack
    def test_set_price(self, line_name, order_type, car_type, price):
        ori_price = self.itp.get_price(line_name, order_type, car_type)
        result = self.itp.set_price(line_name, order_type, car_type, price)
        if result == '操作成功!':
            self.itp.set_price(line_name, order_type, car_type, ori_price)
        self.assertEqual(result, '操作成功!')
        sleep(1)
