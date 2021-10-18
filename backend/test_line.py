import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from ddt import ddt, unpack, data
from time import sleep
import utils
from utils import TestMeta
from PaVManage.func_line import FuncLine
import globalvar
from sys import argv


@ddt
class TestLine(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.lf = FuncLine()
        cls.__name__ = cls.__name__ + "（线路管理：线路开关量【启用/关闭、上线/下线、上车确认...】设置，安全号码、手续费、线路车型...设置）"

    test_toggle = ['361000_to_362300', '关闭', '下线', '开启乘客上车确认'], ['361000_to_362300', '启用', '上线', '关闭乘客上车确认']
    prod_toggle = ['361000_to_361000', '关闭', '下线', '开启乘客上车确认'], ['361000_to_361000', '启用', '上线', '关闭乘客上车确认']

    @unpack
    @data(*test_toggle if argv[1] == 'TEST' else prod_toggle)
    def test_toggle_param(self, line_id, *args):
        line_info_list = self.lf.toggleLineStatus(line_id, *args)
        expect_open_status = '不可用' if args[0] == '关闭' else '可用'
        self.assertEqual(line_info_list[11], expect_open_status)
        self.assertIn(args[1], line_info_list[13])
        self.assertNotIn(args[2], line_info_list[14])

    test_line = ['361000_to_362300', '福建省', '漳州市', True], ['361000_to_362300', '', '', False], ['361000_to_362300', '福建省', '厦门市', True]
    prod_line = ['361000_to_361000', '福建省', '漳州市', True],

    @unpack
    @data(*test_line if argv[1] == 'TEST' else prod_line)
    def test_safe_phone(self, *args):
        self.lf.queryLine(line_num=args[0])
        utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr',  'data-line-id', args[0], '安全号码')
        self.lf.setSafePhone(args[1], args[2], args[3])
        utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr',  'data-line-id', args[0], '安全号码')
        safe_dict = self.lf.getSafePhone()
        self.assertEqual(safe_dict['province'], args[1])
        self.assertEqual(safe_dict['city'], args[2])
    
    test_line = ['361000_to_362300', '5%', '6', '2', '5'], ['361000_to_362300', '10%', '5', '10%', '10%']
    prod_line = ['361000_to_361000', '3', '5', '2', '5'], ['361000_to_361000', '10%', '10%', '10%', '10%']

    @unpack
    @data(*test_line if argv[1] == 'TEST' else prod_line)
    def test_commission(self, *args):
        self.lf.queryLine(line_num=args[0])
        utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id', args[0], '手续费')
        result = self.lf.setCommission(carpool=args[1], dayscharacter=args[2], express=args[3], character=args[4])
        utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                       args[0], '手续费')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/lineCommission.do"]')))
        for i, k in result.items():
            self.assertIn(globalvar.GLOBAL_DRIVER.execute_script('return $("' + i + '").val()'), k)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnEsc').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))

    test_car = ['361000_to_362300', '商务中巴/8座', '新能源/5座', True], ['361000_to_362300', '商务中巴/8座', '新能源/5座', False]
    prod_car = ['361000_to_361000',  '商务中巴/8座', '新能源/5座', True], ['361000_to_361000', '商务中巴/8座', '新能源/5座', False]

    @unpack
    @data(*test_car if argv[1] == 'TEST' else prod_car)
    def test_car_type(self, *args):
        result_car_list = []
        self.lf.queryLine(line_num=args[0])
        utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id', args[0],
                                       '车型')
        car_args = args[1:-1]
        self.lf.setCarType(*car_args, flag=args[-1])
        utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id', args[0],
                                       '车型')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=lineCarClassPage"]')))
        we_result_cars = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('select#sel_right>option')
        for e in we_result_cars:
            result_car_list.append(e.text)
        for car in car_args:
            if args[-1]:
                self.assertIn(car, result_car_list)
            else:
                self.assertNotIn(car, result_car_list)

        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnEsc').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))

