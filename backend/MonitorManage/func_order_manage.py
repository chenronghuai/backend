from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import utils
from utils import OrderType
import globalvar


class FuncOrderManage:

    def __init__(self):
        self.driver = globalvar.get_value('driver')
        self.orders = list(filter(
            lambda order: order.order_type in [OrderType.CARPOOLING, OrderType.CHARACTER, OrderType.EXPRESS,
                                               OrderType.INNER, OrderType.HELPDRIVE,
                                               OrderType.DAYSCHARACTER], globalvar.order_pool))
        utils.make_sure_driver(self.driver, '监控管理', '订单管理', '订单管理', 'orderManage.do')

    def input_customer_phone(self, phone):
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#moreSpan'))).click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnClean'))).click()
        self.driver.find_element_by_css_selector('#phone').send_keys(phone)
        self.driver.find_element_by_css_selector('#moreSpan').click()

    def operate_dialog(self, driver, button_css_locator, iframe_src, operator_css_locator):
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, button_css_locator))).click()
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, iframe_src)))
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, operator_css_locator))).click()
        driver.switch_to.parent_frame()