import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, file_data, unpack
import utils
from utils import OrderType
from utils import TestMeta
import globalvar
from sys import argv
from MonitorManage.func_customer_call import FuncCustomerCall
from MonitorManage.func_order_manage import FuncOrderManage
import log


count = 1
_create_flag = True


@ddt
class TestCustomerCall(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.cc = FuncCustomerCall()
        utils.switch_exist_frame(globalvar.GLOBAL_DRIVER, 'customerCall.do', '客户')  # 打开“客户来电”与“订单管理”2个窗口，把活动窗口切回客户来电”页面
        cls.__name__ = cls.__name__ + "（客户来电下单：城际拼车、城际包车、小件快递、市内用车、多日包车、快线【新增班次】、代驾）"


    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @file_data('.\\testcase\\order_carpooling.json' if argv[3] == 'flow' else '.\\testcase\\order_carpooling1.json')
    def test_order_carpooling(self, phone, by_phone, origin_region_index, origin_region, origin_addr, des_region_index, des_addr, date, time, count, flow):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
        assert_dict = {}
        assert_dict["phone"] = phone if by_phone == "" else by_phone
        assert_dict["order_type"] = "拼车"
        assert_dict["date_time"] = utils.get_time(date, time)
        assert_dict["count"] = count
        self.cc.getUserInfo(phone)
#        self.driver.execute_script("$('#startName-suggest').html('')")  # added by 2021-7-1
        self.cc.selectOrderType('城际拼车')
        self.cc.input_customer_phone(by_phone)
        self.cc.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.cc.selectInterDestination(des_region_index, des_addr)
        self.cc.selectDate(date, time)
        self.cc.selectPCount(count)
        ori, des = self.cc.get_ori_des()
        msg_text = self.cc.commit()
        if '提交订单成功!' in msg_text:
            if flow == 'T':
                i = self.cc.checkitem(assert_dict["order_type"], ori, des, phone)
                self.cc.save_order(i, OrderType.CARPOOLING)
                rs_date = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 8)
                l1_date = str(rs_date).split(' ')
                l2_date = str(assert_dict['date_time']).split(' ')
                self.assertEqual(l1_date[0], l2_date[0])
                self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
                rs_type = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 2)
                self.assertEqual(assert_dict['order_type'], rs_type)
                rs_count = int(utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 6))
                self.assertEqual(assert_dict['count'], rs_count)
        else:
            log.logger.debug(f'拼车订单下单失败，msg={msg_text}')
            assert False

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @file_data('.\\testcase\\order_character.json' if argv[3] == 'flow' else '.\\testcase\\order_character1.json')
    def test_order_charter(self, phone, by_phone, origin_region_index, origin_region, origin_addr, des_region_index,
                               des_addr, car_type, date, time, flow):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
        assert_dict = {}
        assert_dict["phone"] = phone if by_phone == "" else by_phone
        assert_dict["order_type"] = "包车"
        assert_dict["date_time"] = utils.get_time(date, time)
        self.cc.getUserInfo(phone)
#        self.driver.execute_script("$('#startName-suggest').html('')")  # added by 2021-7-1
        sleep(1)
        self.cc.selectOrderType('城际包车')
        self.cc.input_customer_phone(by_phone)
        self.cc.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.cc.selectInterDestination(des_region_index, des_addr)
        self.cc.selectCarType(car_type)
        self.cc.selectDate(date, time)
        ori, des = self.cc.get_ori_des()
        msg_text = self.cc.commit()
        if '提交订单成功!' in msg_text:
            if flow == 'T':
                i = self.cc.checkitem(assert_dict["order_type"], ori, des, phone)
                self.cc.save_order(i, OrderType.CHARACTER, car_type=car_type)
                rs_date = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 8)
                l1_date = str(rs_date).split(' ')
                l2_date = str(assert_dict['date_time']).split(' ')
                self.assertEqual(l1_date[0], l2_date[0])
                self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
                rs_type = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 2)
                self.assertEqual(assert_dict['order_type'], rs_type)
                rs_count = int(utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 6))
                self.assertEqual(1, rs_count)
        else:
            log.logger.debug(f'包车订单下单失败，msg={msg_text}')
            assert False

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
    @file_data('.\\testcase\\order_express.json' if argv[3] == 'flow' else '.\\testcase\\order_express1.json')
    def test_order_express(self, phone, receive_name, receive_phone, origin_region_index, origin_region, origin_addr, des_region_index,
                           des_addr, date, t_time, flow):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "货件"
        assert_dict["date_time"] = utils.get_time(date, t_time)
        self.cc.getUserInfo(phone)
#        self.driver.execute_script("$('#startName-suggest').html('')")  # added by 2021-7-1
        sleep(1)
        self.cc.selectOrderType('小件快递')
        self.cc.input_receive_phone(receive_name, receive_phone)
        self.cc.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.cc.selectInterDestination(des_region_index, des_addr)
        self.cc.selectDate(date, t_time)
        ori, des = self.cc.get_ori_des()
        msg_text = self.cc.commit()
        if '提交订单成功!' in msg_text:
            if flow == 'T':
                i = self.cc.checkitem(assert_dict["order_type"], ori, des, phone)
                self.cc.save_order(i, OrderType.EXPRESS)
                rs_date = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 8)
                l1_date = str(rs_date).split(' ')
                l2_date = str(assert_dict['date_time']).split(' ')
                self.assertEqual(l1_date[0], l2_date[0])
                self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
                rs_type = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 2)
                self.assertEqual(assert_dict['order_type'], rs_type)
                rs_count = int(utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 6))
                self.assertEqual(1, rs_count)
        else:
            log.logger.debug(f'小件订单下单失败，msg={msg_text}')
            assert False


    test_case = ["14759250515", "5603293", "XM", "厦门市|XMSmm", "软件园二期", "软件园观日路24号", "商务七座/7座/豪华型", "", "T"],
    prod_case = ["14759250515", "5603293", "XM", "厦门市|XMSN", "软件园二期", "软件园观日路24号", "商务七座/7座/豪华型", "", "T"],

    @unittest.skipIf(argv[3] != 'flow' or argv[1] != 'TEST', '非流程或测试环境不跑')
    @data(*test_case if argv[1] == 'TEST' else prod_case)
    @unpack
#    @file_data('.\\testcase\\order_inner.json')
    def test_order_inner(self, phone, by_phone,  origin_region_index, origin_region, origin_addr, des_addr, car_type, t_time, flow):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "市内叫车"
        assert_dict["by_phone"] = by_phone if by_phone != "" else phone
        self.cc.getUserInfo(phone)
#        self.driver.execute_script("$('#startName-suggest').html('')")  # added by 2021-7-1
        sleep(1)
        self.cc.selectOrderType('市内用车')
        self.cc.input_customer_phone(by_phone)
        self.cc.orderInnerCity(origin_region_index, origin_region, origin_addr, des_addr)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#car-types-div')), '没有相应车型或价格')
        car_type_xpath = '//div/label[text()="' + car_type + '"]'
        globalvar.GLOBAL_DRIVER.find_element(By.XPATH, car_type_xpath).click()
        self.cc.selectDate('', t_time)
#        sleep(1)
#        self.driver.find_element(By.XPATH, '//div/label[text()="一口价（元）"]').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until((EC.element_to_be_clickable((By.XPATH, '//div/label[text()="一口价（元）"]')))).click()
        sleep(1.5)  # 等待，使得下单各要素齐全，否则无法提交成功
        ori, des = self.cc.get_ori_des()
        msg_text = self.cc.commit(pricetip_flag=False)

        if '提交订单成功!' in msg_text:
            i = self.cc.checkitem(assert_dict["order_type"], ori, des, phone)
            if flow == 'T':
                self.cc.save_order(i, OrderType.INNER)
            assert_dict["date_time"] = utils.get_time('', t_time)
            rs_date = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 8)
            l1_date = str(rs_date).split(' ')
            l2_date = str(assert_dict['date_time']).split(' ')
            self.assertEqual(l1_date[0], l2_date[0])
            self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
            rs_type = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 2)
            self.assertEqual(assert_dict['order_type'], rs_type)
            rs_byphone = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 4)
            self.assertEqual(assert_dict['by_phone'], rs_byphone)
        else:
            log.logger.debug(f'市内订单下单失败，msg={msg_text}')
            assert False

    @unittest.skipIf(argv[3] != 'flow' or argv[1] != 'TEST', '非流程或测试环境不跑')
    @file_data('.\\testcase\\order_dayscharter.json')
    def test_order_dayscharter(self, phone, by_phone, origin_region_index, origin_region, origin_addr,
                               des_region_index, time_long, des_addr, car_type, date, time, flow):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "多日包车(" + str(time_long) + "天)"
        assert_dict["date_time"] = utils.get_time(date, time)
        self.cc.getUserInfo(phone)
#        self.driver.execute_script("$('#startName-suggest').html('')")  # added by 2021-7-1
        sleep(1)
        self.cc.selectOrderType('多日包车')
        globalvar.GLOBAL_DRIVER.execute_script('$("#receiveTel").val("' + by_phone + '")')
        self.cc.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.cc.selectInterDestination(des_region_index, des_addr)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#charterDays')))
        self.cc.selectCarType(car_type)
        globalvar.GLOBAL_DRIVER.execute_script("$('#price').val('')")  # 7.14 add
        self.cc.select_time_long('charterDays', time_long)
        self.cc.selectDate(date, time)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(lambda x: x.execute_script("return $('#price').val()") != '')  # 7.14 add，js提交时需判断价格要素是否不为空
        ori, des = self.cc.get_ori_des()
        msg_text = self.cc.commit()
        if '提交订单成功!' in msg_text:
            if flow == 'T':
                i = self.cc.checkitem(assert_dict["order_type"], ori, des, phone)
                self.cc.save_order(i, OrderType.DAYSCHARACTER, car_type=car_type)
                rs_date = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 8)
                l1_date = str(rs_date).split(' ')
                l2_date = str(assert_dict['date_time']).split(' ')
                self.assertEqual(l1_date[0], l2_date[0])
                self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
                rs_type = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 2)
                self.assertEqual(assert_dict['order_type'], rs_type)
                rs_count = int(utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 6))
                self.assertEqual(1, rs_count)
        else:
            log.logger.debug(f'多日包车订单下单失败，msg={msg_text}')
            assert False
    
    test_case = ["14759250515", "13328775856", "福建省|厦门市|350200", "高林", "福建省|厦门市|350200", "中医院", "1", "T"],
    prod_case = ["14759250515", "13328775856", "福建省|三明市|350400", "大田汽车站", "福建省|三明市|350400", "大田行政服务中心", "1", "T"],

    @unittest.skipIf(argv[3] != 'flow', '非流程不跑')
#    @data(*test_case if argv[1] == 'TEST' else prod_case)
#    @unpack
    @file_data('.\\testcase\\order_fastline.json' if argv[3] == 'flow' and argv[1] == 'TEST' else '.\\testcase\\order_fastline1.json')
    def test_order_fastline(self, phone, by_phone, origin_city, origin_addr, des_city, des_addr, customer_count, flow):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
        global _create_flag
        if flow == 'T' and _create_flag:
            self.cc.create_fastline_flight()
            _create_flag = False
            sleep(1)  # 等待，增加新建班次有效性
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "快巴"
        self.cc.getUserInfo(phone)
        sleep(1)
        self.cc.selectOrderType('快线')
        self.cc.input_customer_phone(by_phone)
        self.cc.orderExpress(origin_city, origin_addr, des_city, des_addr)
        self.cc.selectECount(customer_count)
        if flow == 'F':
            global count
            sleep(1)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flightsAll').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#flightsAll-suggest>div')))
            css = '#flightsAll-suggest>div:nth-child({})'.format(count)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css).click()
            sleep(1)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#submitAll').click()
            msg_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
            if '提交订单成功!' in msg_text:
                if len(globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('#flightsAll-suggest>div')) > count:
                    count += 1
                else:
                    count = 1
                sleep(0.5)
            else:
                log.logger.debug(f'快线订单下单失败，msg={msg_text}')
                assert False
        if flow == 'T':
            WebDriverWait(globalvar.GLOBAL_DRIVER, 20).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#availableSeats'), "当前余票"))
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flightsAll').click()
            flight_no = globalvar.get_value('FlightNo')
            WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'#flightsAll-suggest>div[flights_no="{flight_no}"]'))).click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(lambda driver: driver.find_element_by_css_selector
            ('div#suggest>ul>li#suggest0').is_displayed(), '没有合适班线线路')
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                lambda driver: str(globalvar.GLOBAL_DRIVER.execute_script('return $("#flightsAll").val()')) != '')
            assert_dict['date'] = str(globalvar.GLOBAL_DRIVER.execute_script('return $("#appoint_time_bus").val()'))[5:]
            assert_dict['time'] = str(globalvar.GLOBAL_DRIVER.execute_script('return $("#flightsAll").val()'))[:5]
            sleep(2)  # 暂停确保同步
            ori, des = self.cc.get_ori_des()
            msg_text = self.cc.commit(pricetip_flag=False)
            if '提交订单成功!' in msg_text:
                i = self.cc.checkitem_bus(flight_no, phone, by_phone)
                self.cc.save_order(i, OrderType.FASTLINE)
                rs_date = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 8)
                l1_date = str(rs_date).split(' ')
                l1_date[0] = l1_date[0][5:]
                l1_date[1] = l1_date[1][:5]
                self.assertEqual(assert_dict['date'], l1_date[0])
                self.assertEqual(assert_dict['time'], l1_date[1])
                rs_count = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 5)
                self.assertEqual(customer_count, rs_count)
            else:
                log.logger.debug(f'快线订单下单失败，msg={msg_text}')
                assert False
    
    test_case = ["14759250515", "5603293", "厦门市|xmsndj",  "软件园二期", "软件园观日路24号", "T"],
    prod_case = ["14759250515", "5603293", "厦门市|xmsdj",  "软件园二期", "软件园观日路24号", "T"],

    @unittest.skipIf(argv[3] != 'flow' or argv[1] != 'TEST', '非流程或测试环境不跑')
    @data(*test_case if argv[1] == 'TEST' else prod_case)
    @unpack
#    @file_data('.\\testcase\\order_helpdrive.json')
    def test_order_helpdrive(self, phone, receive_phone, city, origin_addr, des_addr, flow):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "代驾"
        assert_dict["date_time"] = utils.get_time("", "")
        self.cc.getUserInfo(phone)
#        self.driver.execute_script("$('#startName-suggest').html('')")  # added by 2021-7-1
        sleep(1)  # 代驾几率性碰到类型点击后再被置为城际拼车
        self.cc.selectOrderType('代驾')
        globalvar.GLOBAL_DRIVER.execute_script('$("#receiveTel").val("' + receive_phone + '")')
        self.cc.orderHelpDrive(city, origin_addr, des_addr)
        ori, des = self.cc.get_ori_des()
        msg_text = self.cc.commit()
        if '提交订单成功!' in msg_text:
            if flow == 'T':
                i = self.cc.checkitem(assert_dict["order_type"], ori, des, phone)
                self.cc.save_order(i, OrderType.HELPDRIVE)
                rs_date = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 8)
                l1_date = str(rs_date).split(' ')
                l2_date = str(assert_dict['date_time']).split(' ')
                self.assertEqual(l1_date[0], l2_date[0])
                self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
                rs_type = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 2)
                self.assertEqual(assert_dict['order_type'], rs_type)
                rs_count = int(utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 6))
                self.assertEqual(1, rs_count)
        else:
            log.logger.debug(f'代驾订单下单失败，msg={msg_text}')
            assert False













