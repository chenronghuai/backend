from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import utils
from time import sleep
import globalvar


class FuncFlightsManage:

    def __init__(self):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER,  '班线管理', '班次管理', 'flights.do')

    def add_flight(self, center, line, flight_no, seat_num, depart_date, depart_time):
        try:
            globalvar.GLOBAL_DRIVER.execute_script("$('#addLineFlights').click()")
            sleep(1)
            globalvar.GLOBAL_DRIVER.switch_to.frame(
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector(
                    'iframe[src^="/flights.do?method=editLineFlights"]'))
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selCenter').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="' + center + '"]'))).click()
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selLine').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname="' + line + '"]'))).click()
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flightsNo').send_keys(flight_no)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#saleSeats').send_keys(seat_num)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flightsDate').send_keys(depart_date)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flightsDispatchedTime').send_keys(depart_time)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
            msg_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[src^="/flights.do?method=editLineFlights"]')))
            return msg_text
        finally:
            globalvar.GLOBAL_DRIVER.switch_to.default_content()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'iframe[src="/flights.do')))
            we_manage = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('iframe[src="/flights.do"]')
            globalvar.GLOBAL_DRIVER.switch_to.frame(we_manage)
