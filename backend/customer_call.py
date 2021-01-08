import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, strftime
import time
from selenium.webdriver.support.select import Select
from ddt import ddt, data, file_data, unpack
import utils
from utils import OrderType, OrderStatus, CarType
from utils import TestMeta
import globalvar
import logging
from sys import argv
from common import Order


logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

count = 1


@ddt
class TestCustomerCall(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '监控管理', '客户来电', 'customerCall.do')

    def getUserInfo(self, phone):
        self.driver.execute_script("$('#userTypeDiv').html('')")
        we_number = self.driver.find_element_by_css_selector("#phone")
        we_number.clear()
        we_number.send_keys(phone)
        self.driver.execute_script('$("#callOrderPage>table>tbody").html("")')
        self.driver.find_element_by_css_selector("#query_all").click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#userTypeDiv')))
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#callOrderPage>table>tbody>tr')))

    def selectOrderType(self, order_type):
        """
        选择订单类型
        :param order_type: 订单类型
        :return:
        """
        xpath = '//div/label[text()="' + order_type + '"]'
        self.driver.find_element(By.XPATH, xpath).click()
        sleep(1)

    def selectCarType(self, car_type):
        """
        选择订单类型
        :param car_type: 订单类型
        :return:
        """
        xpath = '//div[@id="car-types-div"]/label[text()="' + car_type + '"]'
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="car-types-div"]')))
        self.driver.find_element(By.XPATH, xpath).click()
        sleep(1)

    def input_customer_phone(self, by_phone):
        if by_phone != "":
            self.driver.execute_script('$("#tel").val("' + by_phone + '")')

    def input_receive_phone(self, receive_phone):
        if receive_phone != "":
            self.driver.execute_script('$("#receiveTel").val("' + receive_phone + '")')

    def selectInterOrigin(self, origin_region_index, origin_region, origin_addr=None):
        """
        城际起点方位、地址
        :param origin_region_index: 起点方位简称
        :param origin_region: 起点方位
        :param origin_addr: 起点地址
        :return:
        """
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#startName-suggest>div')))
        self.driver.find_element(By.CSS_SELECTOR, '#startName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest')))
        self.driver.find_element(By.CSS_SELECTOR, '#startName').send_keys(origin_region_index)
        if len(self.driver.find_elements_by_css_selector('#startName-suggest>div')) > 1:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
                '//*[@id="startName-suggest"]/div[@text="' + origin_region + '"]')), '起始方位无法获取').click()
        self.driver.execute_script("$('#endsName-suggest').html('')")
        sleep(0.5)
        we_ori_addr = self.driver.find_element_by_css_selector('#startAddr')
        we_ori_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#start-lists-penal>li')))
        we_ori_addr.send_keys(origin_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')), '起点POI无法获取').click()
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')))
        sleep(0.5)

    def selectInterDestination(self, des_region_index, des_addr):
        """
        城际终点方位、地址
        :param des_region_index: 终点方位简称
        :param des_region: 终点方位
        :param des_addr: 终点地址
        :return:
        """
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
        self.driver.find_element_by_css_selector('#endsName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#endsName-suggest>div')))
        WebDriverWait(self.driver, 5).until(
            lambda x: x.execute_script("return $('#endsName-suggest').css('display')") == 'block')
        self.driver.find_element_by_css_selector('#endsName').send_keys(des_region_index)
        WebDriverWait(self.driver, 10).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')), '起点信息还没消失')
        we_des_addr = self.driver.find_element_by_css_selector('#endAddr')
        we_des_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#end-lists-penal>li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
            '//*[@id="end-lists-penal"]/li[1]')), '终点POI无法获取').click()

    def orderInnerCity(self, city_index, city_region, ori_addr, des_addr):
        """
        市内线路下单
        :param city_index: 市内方位简称
        :param city_region: 市内方位全称
        :param ori_addr: 起始地址
        :param des_addr: 终点地址
        :return:
        """
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="startName-suggest"]/div')))
        self.driver.find_element(By.ID, 'startName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'startName-suggest')))
        self.driver.find_element(By.ID, 'startName').send_keys(city_index)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
                                    '//*[@id="startName-suggest"]/div[@text="' + city_region + '"]')),
                                            '起始方位无法获取').click()
        we_ori_addr = self.driver.find_element_by_id('startAddr')
        we_ori_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        we_ori_addr.send_keys(ori_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点POI无法获取').click()
        WebDriverWait(self.driver, 5).until_not(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点信息还没消失')
        we_des_addr = self.driver.find_element_by_id('endAddr')
        we_des_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="end-lists-penal"]/li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点POI无法获取').click()

    def create_fastline_flight(self):
        utils.switch_frame(self.driver, '班线管理', '班次管理', 'flights.do')
        self.driver.find_element_by_css_selector('#addLineFlights').click()
        sleep(1)
        self.driver.switch_to.frame(self.driver.find_element_by_css_selector('iframe[src^="/flights.do?method=editLineFlights"]'))
        self.driver.find_element_by_css_selector('#selCenter').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
            '//*[@id="selCenter-suggest"]/div[@text="10596|漳州运营中心"]')), '运营中心无法选取').click()
        self.driver.find_element_by_css_selector('#selLine').clear()
        if argv[1] == 'HTTP1':
            self.driver.find_element_by_css_selector('#selLine').send_keys('高林SM专线')
        else:
            self.driver.find_element_by_css_selector('#selLine').send_keys('厦门测试班线')
        self.driver.find_element_by_css_selector('#flightsNo').send_keys('CS001')
        self.driver.find_element_by_css_selector('#saleSeats').send_keys(20)
        self.driver.find_element_by_css_selector('#flightsDate').click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.laydate-btns-confirm'))).click()
        secs = time.time() + 1800
        hour = time.gmtime(secs).tm_hour + 8
        if hour < 10:
            hour = '0' + str(hour)
        minute = time.gmtime(secs).tm_min
        if minute < 10:
            minute = '0' + str(minute)
        time_str = str(hour) + ":" + str(minute)
        self.driver.find_element_by_css_selector('#flightsDispatchedTime').send_keys(time_str)
        self.driver.find_element_by_css_selector('#btnSave').click()
        self.driver.switch_to.parent_frame()
        utils.switch_exist_frame(self.driver, 'flights.do', 'customerCall.do')

    def orderExpress(self, ori_city, ori_addr, des_city, des_addr):
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="startName-suggest"]/div')))
        self.driver.find_element(By.ID, 'startName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'startName-suggest')))
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
         '//*[@id="startName-suggest"]/div[@text="' + ori_city + '"]')), '起始城市无法获取').click()
        we_ori_addr = self.driver.find_element_by_id('startAddr')
        we_ori_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        we_ori_addr.send_keys(ori_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点POI无法获取').click()

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="endsName-suggest"]/div')))
        self.driver.find_element_by_id('endsName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'endsName-suggest')))
        WebDriverWait(self.driver, 5).until_not(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点信息还没消失')
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
        '//*[@id="endsName-suggest"]/div[@text="' + des_city + '"]')), '终点城市无法获取').click()
        we_des_addr = self.driver.find_element_by_id('endAddr')
        we_des_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="end-lists-penal"]/li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点POI无法获取').click()

    def orderHelpDrive(self, city, ori_addr, des_addr):
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="startName-suggest"]/div')))
        self.driver.find_element(By.ID, 'startName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'startName-suggest')))
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
         '//*[@id="startName-suggest"]/div[@text="' + city + '"]')), '起始方位无法获取').click()
        we_ori_addr = self.driver.find_element_by_id('startAddr')
        we_ori_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        we_ori_addr.send_keys(ori_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点POI无法获取').click()
        WebDriverWait(self.driver, 5).until_not(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点推荐信息长时间没消失')
        we_des_addr = self.driver.find_element_by_id('endAddr')
        we_des_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="end-lists-penal"]/li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点POI无法获取').click()

    def selectDate(self, date='今天', time=''):
        """
        选择出行时间
        :param date: 日期
        :param time: 时间
        :return:
        """
        if date != "今天" and date != "":
            xpath = '//div/label[text()=' + "\"" + date + "\"" + ']'
            self.driver.find_element(By.XPATH, xpath).click()
        if time != '':
            self.driver.execute_script("$('#input-time').val('" + time + "')")

    def selectPCount(self, num):
        """
        选择城际、市内人数
        :param num: 人数
        :return:
        """
        xpath = '//span[@id="peopleCount"]/i/input[@value=' + "\"" + str(num) + "\"" + ']'
        self.driver.find_element(By.XPATH, xpath).click()

    def selectECount(self, num):
        """
        快线选人数
        :param num:快线人数
        :return:
        """
        xpath = '//div[@id="fastLinePeopleCount"]/i/input[@value=' + "\"" + str(num) + "\"" + ']'
        self.driver.find_element(By.XPATH, xpath).click()

    def select_time_long(self, id, text):
        s = self.driver.find_element_by_id(id)
        Select(s).select_by_visible_text(text)

    def commit(self, pricetip_flag=True):
        """
        提交订单
        :return:
        """
        if pricetip_flag:
            WebDriverWait(self.driver, 5).until(
                EC.text_to_be_present_in_element((By.XPATH, '//*[@id="priceTips"]'), '预估花费'), '获取价格失败')
#        self.driver.find_element_by_id('submitAll').click()
        self.driver.execute_script("$('#submitAll').click()")
        sleep(1.5)
        '''下面经常性出现超时错误
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        '''

    def checkitem(self, str_filter):
        """
        确认目标订单的位置（当账号有较多的预约订单时【超过5单】有可能获取不到）
        :param str_filter: 订单类型
        :return: 客户来电页订单所在行数，匹配不到返回0
        """
        self.driver.find_element_by_css_selector('#call-see-order').click()
        sleep(1)
        b_match = False
        for i in range(1, len(self.driver.find_elements_by_css_selector('#callOrderPage>table>tbody>tr'))+1):
            if str_filter == utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2):
                b_match = True
                break
        return i if b_match else 0

    def create_order(self, order_id, order_type, appoint_time, car_type=CarType.ANY, count=1):
        new_order = Order(order_id)
        new_order.order_type = order_type
        new_order.appoint_time = appoint_time
        new_order.order_count = int(count)
        new_order.order_status = OrderStatus.WAITING
        new_order.car_type = car_type
        globalvar.add_order(new_order)

    def save_order(self, index, order_type, car_type=CarType.ANY):
        if len(self.driver.find_elements_by_css_selector('#callOrderPage>table>tbody>tr')) > 1:
            css = '#callOrderPage>table>tbody>tr:nth-child({})'.format(index)
        else:
            css = '#callOrderPage>table>tbody>tr'
        order_id = self.driver.find_element_by_css_selector(css).get_attribute('order-id')
        appoint_time = self.driver.find_element_by_css_selector(css + '>td:nth-child(1)').text
        count = self.driver.find_element_by_css_selector(css + '>td:nth-child(3)').text
        self.create_order(order_id, order_type, appoint_time, car_type, count)

    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\order_carpooling1.json')
    def test_order_carpooling(self, phone, by_phone, origin_region_index, origin_region, origin_addr, des_region_index, des_addr, date, time, count, flow):
        assert_dict = {}
        assert_dict["phone"] = phone if by_phone == "" else by_phone
        assert_dict["order_type"] = "拼车"
        assert_dict["date_time"] = utils.get_time(date, time)
        assert_dict["count"] = count
        self.getUserInfo(phone)
        self.selectOrderType('城际拼车')
        self.input_customer_phone(by_phone)
        self.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.selectInterDestination(des_region_index, des_addr)
        self.selectDate(date, time)
        self.selectPCount(count)
        self.commit()
        if flow == 'T':
            i = self.checkitem(assert_dict["order_type"])
            self.save_order(i, OrderType.CARPOOLING)
            rs_date = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 1)
            l1_date = str(rs_date).split(' ')
            l2_date = str(assert_dict['date_time']).split(' ')
            self.assertEqual(l1_date[0], l2_date[0])
            self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
            rs_type = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2)
            self.assertEqual(assert_dict['order_type'], rs_type)
            rs_count = int(utils.get_cell_content(self.driver, '#callOrderPage>table', i, 3))
            self.assertEqual(assert_dict['count'], rs_count)

#    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\order_character1.json')
    def test_order_charter(self, phone, by_phone, origin_region_index, origin_region, origin_addr, des_region_index,
                               des_addr, car_type, date, time, flow):
        assert_dict = {}
        assert_dict["phone"] = phone if by_phone == "" else by_phone
        assert_dict["order_type"] = "包车"
        assert_dict["date_time"] = utils.get_time(date, time)
        self.getUserInfo(phone)
        self.selectOrderType('城际包车')
        self.input_customer_phone(by_phone)
        self.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.selectInterDestination(des_region_index, des_addr)
        self.selectCarType(car_type)
        self.selectDate(date, time)
        self.commit()
        if flow == 'T':
            i = self.checkitem(assert_dict["order_type"])
            self.save_order(i, OrderType.CHARACTER, car_type=car_type)
            rs_date = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 1)
            l1_date = str(rs_date).split(' ')
            l2_date = str(assert_dict['date_time']).split(' ')
            self.assertEqual(l1_date[0], l2_date[0])
            self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
            rs_type = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2)
            self.assertEqual(assert_dict['order_type'], rs_type)
            rs_count = int(utils.get_cell_content(self.driver, '#callOrderPage>table', i, 3))
            self.assertEqual(1, rs_count)

    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\order_express.json')
    def test_order_express(self, phone, receive_phone, origin_region_index, origin_region, origin_addr, des_region_index,
                           des_addr, date, t_time, flow):
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "货件"
        assert_dict["date_time"] = utils.get_time(date, t_time)
        self.getUserInfo(phone)
        self.selectOrderType('小件快递')
        self.input_receive_phone(receive_phone)
        self.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.selectInterDestination(des_region_index, des_addr)
        self.selectDate(date, t_time)
        self.commit()
        if flow == 'T':
            i = self.checkitem(assert_dict["order_type"])
            self.save_order(i, OrderType.EXPRESS)
            rs_date = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 1)
            l1_date = str(rs_date).split(' ')
            l2_date = str(assert_dict['date_time']).split(' ')
            self.assertEqual(l1_date[0], l2_date[0])
            self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
            rs_type = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2)
            self.assertEqual(assert_dict['order_type'], rs_type)
            rs_count = int(utils.get_cell_content(self.driver, '#callOrderPage>table', i, 3))
            self.assertEqual(1, rs_count)

    @unittest.skip('直接跳过')
    @file_data('.\\testcase\\order_inner.json')
    def test_order_inner(self, phone, by_phone,  origin_region_index, origin_region, origin_addr, des_addr, t_time, flow):
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "市内叫车"
        assert_dict["by_phone"] = by_phone if by_phone != "" else phone
        self.getUserInfo(phone)
        self.selectOrderType('市内用车')
        self.input_customer_phone(by_phone)
        self.orderInnerCity(origin_region_index, origin_region, origin_addr, des_addr)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#car-types-div')), '没有相应车型或价格')
        self.selectDate('', t_time)
        sleep(1)
        if self.driver.execute_script('return $("#priceShow").val()') == '打表计价':
            sleep(1)
            self.commit(pricetip_flag=False)
        else:
            self.commit()
        i = self.checkitem(assert_dict["order_type"])
        if flow == 'T':
            self.save_order(i, OrderType.INNER)
        assert_dict["date_time"] = utils.get_time('', t_time)
        rs_date = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 1)
        l1_date = str(rs_date).split(' ')
        l2_date = str(assert_dict['date_time']).split(' ')
        self.assertEqual(l1_date[0], l2_date[0])
        self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
        rs_type = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2)
        self.assertEqual(assert_dict['order_type'], rs_type)
        rs_byphone = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 4)
        self.assertEqual(assert_dict['by_phone'], rs_byphone)

    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\order_dayscharter.json')
    def test_order_dayscharter(self, phone, by_phone, origin_region_index, origin_region, origin_addr,
                               des_region_index, time_long, des_addr, car_type, date, time, flow):
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "多日包车(" + str(time_long) + "天)"
        assert_dict["date_time"] = utils.get_time(date, time)
        self.getUserInfo(phone)
        self.selectOrderType('多日包车')
        self.input_receive_phone(by_phone)
        self.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.selectInterDestination(des_region_index, des_addr)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#charterDays')))
        self.selectCarType(car_type)
        self.select_time_long('charterDays', time_long)
        self.selectDate(date, time)
        self.commit()
        if flow == 'T':
            i = self.checkitem(assert_dict["order_type"])
            self.save_order(i, OrderType.DAYSCHARACTER, car_type=car_type)
            rs_date = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 1)
            l1_date = str(rs_date).split(' ')
            l2_date = str(assert_dict['date_time']).split(' ')
            self.assertEqual(l1_date[0], l2_date[0])
            self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
            rs_type = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2)
            self.assertEqual(assert_dict['order_type'], rs_type)
            rs_count = int(utils.get_cell_content(self.driver, '#callOrderPage>table', i, 3))
            self.assertEqual(1, rs_count)

#    @data({"phone":"14759250515","by_phone": "13328775856", "origin_city":"福建省|三明市|350400", "origin_addr": "大田县汽车站","des_city": "福建省|三明市|350400","des_addr": "大田出口", "customer_count":"3", "flow":"T"})
#    @unpack
    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\order_fastline.json')
    def test_order_fastline(self, phone, by_phone, origin_city, origin_addr, des_city, des_addr, customer_count, flow):
        if flow == 'T':
            self.create_fastline_flight()
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "快巴"
        self.getUserInfo(phone)
        self.selectOrderType('快线')
        self.input_customer_phone(by_phone)
        self.orderExpress(origin_city, origin_addr, des_city, des_addr)
        self.selectECount(customer_count)
        if flow == 'F':
            global count
            sleep(1)
            self.driver.find_element_by_css_selector('#flightsAll').click()
            WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#flightsAll-suggest>div')))
            css = '#flightsAll-suggest>div:nth-child({})'.format(count)
            self.driver.find_element_by_css_selector(css).click()
            sleep(1)
            self.driver.find_element_by_css_selector('#submitAll').click()
            sleep(2)
            if len(self.driver.find_elements_by_css_selector('#flightsAll-suggest>div')) > count:
                count += 1
            else:
                count = 1
            sleep(0.5)
        if flow == 'T':
            WebDriverWait(self.driver, 5).until(lambda driver: driver.find_element_by_css_selector
            ('div#suggest>ul>li#suggest0').is_displayed(), '没有合适班线线路')
            WebDriverWait(self.driver, 5).until(
                lambda driver: str(self.driver.execute_script('return $("#flightsAll").val()')) != '')
            assert_dict['date'] = str(self.driver.execute_script('return $("#appoint_time_bus").val()'))[5:]
            assert_dict['time'] = str(self.driver.execute_script('return $("#flightsAll").val()'))[:5]
            sleep(2)  # 暂停确保同步
            self.commit(pricetip_flag=False)
            i = self.checkitem(assert_dict["order_type"])
            self.save_order(i, OrderType.FASTLINE)
            rs_date = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 1)
            l1_date = str(rs_date).split(' ')
            self.assertEqual(assert_dict['date'], l1_date[0])
            self.assertEqual(assert_dict['time'], l1_date[1])
            rs_type = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2)
            self.assertEqual(assert_dict['order_type'], rs_type)
            rs_count = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 3)
            self.assertEqual(customer_count, rs_count)

    @unittest.skip("直接跳过")
    @file_data('.\\testcase\\order_helpdrive.json')
    def test_order_helpdrive(self, phone, receive_phone, city, origin_addr, des_addr, flow):
        assert_dict = {}
        assert_dict["phone"] = phone
        assert_dict["order_type"] = "代驾"
        assert_dict["date_time"] = utils.get_time("", "")
        self.getUserInfo(phone)
        self.selectOrderType('代驾')
        self.input_receive_phone(receive_phone)
        self.orderHelpDrive(city, origin_addr, des_addr)
        self.commit()
        if flow == 'T':
            i = self.checkitem(assert_dict["order_type"])
            self.save_order(i, OrderType.HELPDRIVE)
            rs_date = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 1)
            l1_date = str(rs_date).split(' ')
            l2_date = str(assert_dict['date_time']).split(' ')
            self.assertEqual(l1_date[0], l2_date[0])
            self.assertAlmostEqual(utils.convert_to_minute(l1_date[1]), utils.convert_to_minute(l2_date[1]), delta=4)
            rs_type = utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2)
            self.assertEqual(assert_dict['order_type'], rs_type)
            rs_count = int(utils.get_cell_content(self.driver, '#callOrderPage>table', i, 3))
            self.assertEqual(1, rs_count)









