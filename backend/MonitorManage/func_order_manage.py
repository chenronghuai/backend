from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import utils
from utils import OrderType
import globalvar
import log


class FuncOrderManage:

    def __init__(self):
        self.orders = list(filter(
            lambda order: order.order_type in [OrderType.CARPOOLING, OrderType.CHARACTER, OrderType.EXPRESS,
                                               OrderType.INNER, OrderType.HELPDRIVE,
                                               OrderType.DAYSCHARACTER], globalvar.order_pool))
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '订单管理', 'orderManage.do')

    def input_customer_phone(self, phone):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#moreSpan'))).click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnClean'))).click()
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#phone').send_keys(phone)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#moreSpan').click()

    def operate_dialog(self, button_css_locator, iframe_src, operator_css_locator):

        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, button_css_locator))).click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, iframe_src)))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, operator_css_locator))).click()
        operate_result_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
#        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()  # 该语句不生效，是否因为该iframe已经不在DOM？
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '订单管理', 'orderManage.do')
        return operate_result_text
        