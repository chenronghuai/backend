import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, strftime
import datetime
from selenium import webdriver
from ddt import ddt, data, file_data, unpack
import utils
import globalvar


@ddt
class TestCustomerCall(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver, '监控管理', '客户来电', 'customerCall.do')
    '''
    def __init__(self):
        self.driver = globalvar.get_value('driver')
        utils.switch_frame(self.driver, '监控管理', '客户来电', 'customerCall.do')
    '''
    def getUserInfo(self, phone):
        self.driver.execute_script("$('#userTypeDiv').html('')")
        we_number = self.driver.find_element_by_css_selector("#phone")
        we_number.clear()
        we_number.send_keys(phone)
        self.driver.find_element_by_css_selector("#query_all").click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#userTypeDiv')))

    def selectOrderType(self, order_type):
        """
        选择订单类型
        :param order_type: 订单类型
        :return:
        """
        xpath = '//div/label[text()=' + "\"" + order_type + "\"" + ']'
        self.driver.find_element(By.XPATH, xpath).click()
        sleep(1)

    def selectInterOrigin(self, origin_region_index, origin_region, origin_addr=None):
        """
        城际起点方位、地址
        :param origin_region_index: 起点方位简称
        :param origin_region: 起点方位
        :param origin_addr: 起点地址
        :return:
        """
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="startName-suggest"]/div')))
        self.driver.find_element(By.ID, 'startName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'startName-suggest')))
        self.driver.find_element(By.ID, 'startName').send_keys(origin_region_index)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
                '//*[@id="startName-suggest"]/div[@text="' + origin_region + '"]')), '起始方位无法获取').click()
        we_ori_addr = self.driver.find_element_by_id('startAddr')
        we_ori_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        we_ori_addr.send_keys(origin_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点POI无法获取').click()

    def selectInterDestination(self, des_region_index, des_addr):
        """
        城际终点方位、地址
        :param des_region_index: 终点方位简称
        :param des_region: 终点方位
        :param des_addr: 终点地址
        :return:
        """
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="endsName-suggest"]/div')))
        self.driver.find_element_by_id('endsName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'endsName-suggest')))
        self.driver.find_element_by_id('endsName').send_keys(des_region_index)
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

    def orderExpress(self, ori_city, ori_addr, des_city, des_addr):
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="startName-suggest"]/div')))
        self.driver.find_element(By.ID, 'startName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'startName-suggest')))
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
         '//*[@id="startName-suggest"]/div[@dataname="' + ori_city + '"]')), '起始方位无法获取').click()
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
        '//*[@id="endsName-suggest"]/div[@dataname="' + des_city + '"]')), '起始方位无法获取').click()
        we_des_addr = self.driver.find_element_by_id('endAddr')
        we_des_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="end-lists-penal"]/li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点POI无法获取').click()

    def selectDate(self, date='今天', time=None):
        """
        选择出行时间
        :param date: 日期
        :param time: 时间
        :return:
        """
        xpath = '//div/label[text()=' + "\"" + date + "\"" + ']'
        self.driver.find_element(By.XPATH, xpath).click()

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

    def commit(self):
        """
        提交订单
        :return:
        """
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.XPATH, '//*[@id="priceTips"]'), '预估花费'),
            '获取价格失败')
        self.driver.find_element_by_id('submitAll').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))

    @file_data('.\\testcase\\order_carpooling.json')
    def test_order_carpooling(self, phone, origin_region_index, origin_region, origin_addr, des_region_index, des_addr, date, count):
        self.getUserInfo(phone)
        self.selectOrderType('城际拼车')
        self.selectInterOrigin(origin_region_index, origin_region, origin_addr)
        self.selectInterDestination(des_region_index, des_addr)
        self.selectDate(date)
        self.selectPCount(count)
        self.commit()
        self.assertEqual(True, True)


