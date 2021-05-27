import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from ddt import ddt, data, unpack
import utils
from utils import OrderType
from utils import TestMeta
import globalvar
from sys import argv


@ddt
class TestFlightsManage(unittest.TestCase, metaclass=TestMeta):

    @classmethod
    def setUpClass(cls):
        cls.driver = globalvar.get_value('driver')
        utils.switch_frame(cls.driver,  '班线管理', '班次管理', 'flights.do')
        globalvar.opened_window_pool.append('flights.do')

    def add_flight(self, center, line, flight_no, seat_num, depart_date, depart_time):
        self.driver.find_element_by_css_selector('#selCenter').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
        self.driver.find_element_by_css_selector('#selLine').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname="' + line + '"]'))).click()
        self.driver.find_element_by_css_selector('#flightsNo').send_keys(flight_no)
        self.driver.find_element_by_css_selector('#saleSeats').send_keys(seat_num)
        self.driver.find_element_by_css_selector('#flightsDate').send_keys(depart_date)
        self.driver.find_element_by_css_selector('#flightsDispatchedTime').send_keys(depart_time)
        self.driver.find_element_by_css_selector('#btnSave').click()
        WebDriverWait(self.driver, 5).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[src^="/flights.do?method=editLineFlights"]')))

    @data({"center":"漳州运营中心", "line":"高林SM专线", "flight_no":"CS008", "seat_num":"20", "depart_date":"2020-12-03", "depart_time":"11:40"} if argv[1] == 'http1'
          else {"center":"漳州运营中心", "line":"厦门测试班线", "flight_no":"CS001", "seat_num":"20", "depart_date":"2020-12-01", "depart_time":"17:40"})
    @unpack
    def test_add_flihgts(self, center, line, flight_no, seat_num, depart_date, depart_time):
        self.driver.find_element_by_css_selector('#addLineFlights').click()
        sleep(1)
        self.driver.switch_to.frame(
            self.driver.find_element_by_css_selector('iframe[src^="/flights.do?method=editLineFlights"]'))
        self.add_flight(center, line, flight_no, seat_num, depart_date, depart_time)
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'iframe[src="/flights.do')))
        we_manage = self.driver.find_element_by_css_selector('iframe[src="/flights.do"]')
        self.driver.switch_to.frame(we_manage)
        sleep(2)
        self.driver.find_element_by_css_selector('#selCenter').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
        self.driver.find_element_by_css_selector('.fs-label-wrap>.fs-label').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="fs-options"]/div[@class="fs-option"]/div[text()="' + line + '"]'))).click()
        self.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#flights_table>tbody>tr')))

        flights = self.driver.find_elements_by_css_selector(
            'table#flights_table>tbody>tr')
        depart_time_list = []
        flight_no_list = []
        for i in range(1, len(flights) + 1):
            depart_time_list.append(utils.get_cell_content(self.driver, 'table#flights_table', i, 5))
            flight_no_list.append(utils.get_cell_content(self.driver, 'table#flights_table', i, 3))
        logging.critical(flight_no_list)
        logging.critical(depart_time_list)
        status = True if depart_time in depart_time_list and flight_no in flight_no_list else False
        self.assertTrue(status)




