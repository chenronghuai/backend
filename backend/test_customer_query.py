import unittest
from ddt import ddt, data
from CustomerManage.func_customer_query import FuncCustomerQuery
from utils import TestMeta
from sys import argv


@ddt
class TestCustomerQuery(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.cq = FuncCustomerQuery()
        cls.__name__ = cls.__name__ + "（客户查询：客户拉黑、漂白等操作）"

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data("13328775856", )
    def test_set_black(self, phone):
        result_text = self.cq.set_black(phone)
        self.assertEqual(result_text, '已成功把用户拉黑!')

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data("13328775856", )
    def test_set_white(self, phone):
        result_text = self.cq.set_white(phone)
        self.assertEqual(result_text, '已成功把用户漂白!')
