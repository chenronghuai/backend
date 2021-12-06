import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
import log
from utils import OrderType, OrderStatus
from SystemManage.func_user_manage import FuncUserManage
from utils import TestMeta
import globalvar
from sys import argv


@ddt
class TestUserManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        if argv[1] == 'TEST':
            cls.um = FuncUserManage()
        cls.__name__ = cls.__name__ + "（用户管理：用户属性获取、设置等操作）"

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data(['chenzhibing', '不可用', '显示', '显示'], ['chenzhibing', '可用', '隐藏', '隐藏'])
    @unpack
    def test_modify_user(self, account, available, c_phone, d_phone):
        result_txt = self.um.set_user_attr(account, available=available, customer_phone=c_phone, driver_phone=d_phone)
        self.assertEqual(result_txt, '修改成功')

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data(('王天一', 13212344321, '厦门运营中心', '厦门[客服人员]'),)
    @unpack
    def test_add_user(self, name, phone, center, role):
        result_txt = self.um.add_user(name, phone, center, role)
        self.assertIn('新增成功', result_txt)

    @unittest.skipIf(argv[1] != 'TEST', '非测试环境不跑')
    @data(['王天一'],)
    @unpack
    def test_del_user(self, name):
        result_txt = self.um.del_user(name)
        self.assertEqual(result_txt, '删除成功')
