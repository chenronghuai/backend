import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
import time
from utils import TestMeta
import globalvar
from sys import argv
from FlightManage.func_flights_manage import FuncFlightsManage
import log
from selenium.common.exceptions import StaleElementReferenceException


@ddt
class TestFlightsManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        cls.fm = FuncFlightsManage()
        cls.__name__ = cls.__name__ + "（班次管理：班线班次新增、删除）"

    @data({"center":"漳州运营中心", "line":"高林SM专线", "seat_num":"20"} if argv[1] == 'TEST'
          else {"center":"漳州运营中心", "line":"厦门测试班线", "seat_num":"20"})
    @unpack
    def test_add_flihgts(self, center, line, seat_num):
        self.fm.driver.execute_script("$('#addLineFlights').click()")
        sleep(1)
        self.fm.driver.switch_to.frame(
            self.fm.driver.find_element_by_css_selector('iframe[src^="/flights.do?method=editLineFlights"]'))

        secs = time.time() + 1800    # 半小时后
        hour = time.localtime(secs).tm_hour  #time.gmtime(secs).tm_hour + 8
        year = time.localtime(secs).tm_year  #time.gmtime(secs).tm_year
        mon = time.localtime(secs).tm_mon  #time.gmtime(secs).tm_mon
        if mon < 10:
            mon = '0' + str(mon)
        day = time.localtime(secs).tm_mday  #time.gmtime(secs).tm_mday
        if day < 10:
            day = '0' + str(day)
        if hour < 10:
            hour = '0' + str(hour)
        minute = time.localtime(secs).tm_min  #time.gmtime(secs).tm_min
        if minute < 10:
            minute = '0' + str(minute)
        depart_time = str(hour) + ":" + str(minute)
        flight_no = 'CS' + str(hour) + str(minute)
        depart_date = str(year) + '-' + str(mon) + '-' + str(day)
        setattr(TestFlightsManage, 'flight_no', flight_no)

        msg_text = self.fm.add_flight(center, line, flight_no, seat_num, depart_date, depart_time)
        if '操作成功' in msg_text:
            self.fm.driver.switch_to.default_content()
            WebDriverWait(self.fm.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'iframe[src="/flights.do')))
            we_manage = self.fm.driver.find_element_by_css_selector('iframe[src="/flights.do"]')
            self.fm.driver.switch_to.frame(we_manage)
            sleep(2)
            self.fm.driver.execute_script("$('#selCenter').click()")
    #        self.fm.driver.find_element_by_css_selector('#selCenter').click()
            WebDriverWait(self.fm.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
            self.fm.driver.find_element_by_css_selector('.fs-label-wrap>.fs-label').click()
            WebDriverWait(self.fm.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="' + line + '"]'))).click()
            self.fm.driver.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(self.fm.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#flights_table>tbody>tr')))

            flights = self.fm.driver.find_elements_by_css_selector(
                'table#flights_table>tbody>tr')
            depart_time_list = []
            flight_no_list = []
            for i in range(1, len(flights) + 1):
                depart_time_list.append(utils.get_cell_content(self.fm.driver, 'table#flights_table', i, 5))
                flight_no_list.append(utils.get_cell_content(self.fm.driver, 'table#flights_table', i, 3))
            status = True if depart_time in depart_time_list and flight_no in flight_no_list else False
            self.assertTrue(status)
        else:
            log.logger.debug(f'创建班次失败，msg={msg_text}')
            assert False

    @data({"center": "漳州运营中心", "line": "高林SM专线"} if argv[1] == 'TEST'
          else {"center": "漳州运营中心", "line": "厦门测试班线"})
    @unpack
    def test_del_flight(self, center, line):
        goal_flight_no = getattr(TestFlightsManage, 'flight_no', None)
        if goal_flight_no is None:
            raise IndexError

        self.fm.driver.find_element_by_css_selector('#selCenter').click()
        WebDriverWait(self.fm.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
        self.fm.driver.find_element_by_css_selector('.fs-label-wrap>.fs-label').click()
        self.fm.driver.execute_script("""
                    $('.fs-options>div').each(function(inx, obj){if($(this).hasClass('selected')){$(this).removeClass('selected');}});
                   """)
        WebDriverWait(self.fm.driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="' + line + '"]'))).click()
        self.fm.driver.execute_script("$('table#flights_table>tbody').html('')")
        self.fm.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.fm.driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#flights_table>tbody>tr')))
        utils.select_operation_by_field(self.fm.driver, 'table#flights_table', '班次号', self.flight_no, '删除')
        self.fm.driver.switch_to.default_content()
        WebDriverWait(self.fm.driver, 5).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'a.layui-layer-btn0'))).click()
        WebDriverWait(self.fm.driver, 5).until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, 'a.layui-layer-btn0')))
        utils.make_sure_driver(self.fm.driver, '班线管理', '班次管理', '班次管理', 'flights.do')
        msg_text = utils.wait_for_laymsg(self.fm.driver)
        if '操作班次成功!' in msg_text:
            self.fm.driver.execute_script("$('table#flights_table>tbody').html('')")
            sleep(1)  # 貌似以下获取的班次号包含已删除，加等待试试
            self.fm.driver.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(self.fm.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#flights_table>tbody>tr')))
            flights = self.fm.driver.find_elements_by_css_selector('table#flights_table>tbody>tr')

            if len(flights) == 1 and len(flights[0].find_elements_by_css_selector('td')) == 1:
                return True
            flight_no_list = []
            for i in range(1, len(flights) + 1):
                try:
                    flight_no_list.append(utils.get_cell_content(self.fm.driver, 'table#flights_table', i, 3))
                except StaleElementReferenceException:
                    sleep(2)
                    flight_no_list.append(utils.get_cell_content(self.fm.driver, 'table#flights_table', i, 3))
            status = True if goal_flight_no not in flight_no_list else False
            self.assertTrue(status)
        else:
            log.logger.debug(f'删除班次失败，msg={msg_text}')
            assert False







