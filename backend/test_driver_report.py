import unittest
from sys import argv
from ddt import ddt, data, file_data, unpack
import utils
import globalvar
from MonitorManage.func_driver_report import FuncDriverReport


@ddt
class TestDriverReport(unittest.TestCase, metaclass=utils.TestMeta):

    is_phone = True

    @classmethod
    def setUpClass(cls):
        cls.fdr = FuncDriverReport()
        cls.__name__ = cls.__name__ + "（司机报班：司机通过手机号码、车牌号码进行报班，取消报班）"

    @classmethod
    def tearDownClass(cls):
        pass

    test_phone = [13328775856, "361000", "361000"], [13565498722, "361000", "361000"], [13345678968, "361000", "361000"]
    prod_phone = [13345678965, "361000", "361000"], [17700000000, "361000", "361000"]

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_phone if argv[1] == 'TEST' else prod_phone)
    @unpack
    def test_driver_report_by_phone(self, phone, ori_val, des_val):
        report_status = self.fdr.driver_report_by_phone(phone, ori_val, des_val)
        self.assertEqual(report_status, '报班')

    test_car = ["闽D223E5", "13345678965", "361000", "361000"],
    prod_car = ["闽D223E5", "18030142505", "361000", "361000"],

    @unpack
    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @data(*test_car if argv[1] == 'TEST' else prod_car)
    def test_driver_report_by_carnum(self, carnum, phone, ori_val, des_val):
        report_status = self.fdr.driver_report_by_carnum(carnum, phone, ori_val, des_val)
        self.assertEqual(report_status, '报班')

    test_driver = (13565498722,)
    prod_driver = (18030142505,)

    @data(*test_driver if argv[1] == 'TEST' else prod_driver)
    def test_driver_cancel_report(self, phone):
        try:
            report_status = self.fdr.driver_cancel_report(phone)
            self.assertEqual(report_status, '未报班')
        finally:
            self.fdr.driver_report_by_phone(phone, "361000", "361000")

