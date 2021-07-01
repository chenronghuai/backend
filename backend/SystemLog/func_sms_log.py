from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import utils
from time import sleep
import globalvar
import log
import re


class FuncSmsLog:

    def __init__(self):
        self.driver = globalvar.get_value('driver')
        utils.make_sure_driver(self.driver,  '系统日志', '短信日志查询', '短信日志查询', 'bbxsms.do')

    def search_log(self, phone, s_time=None, e_time=None):
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#mobile'))).send_keys(phone)
        if s_time is not None:
            self.driver.find_element_by_css_selector('#startTime').send_keys(s_time)
        if e_time is not None:
            self.driver.find_element_by_css_selector('#endTime').send_keys(e_time)
        self.driver.execute_script("$('#data_table>tbody').html('')")
        self.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '#data_table>tbody>tr')))

    def get_content_by_field(self, column):
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '#data_table>tbody>tr')))

        content_str = ''

        info_text = self.driver.find_element_by_css_selector('#resultHTML>#pagebar>p').text
        page_num = int(re.search(r'.+/(.+)', info_text).group(1))
        setattr(self, 'time_flag', True)
        for i in range(page_num):
            records = self.driver.find_elements_by_css_selector('#data_table>tbody>tr')
            for j in range(1, len(records)+1):
                create_time = utils.get_cell_content(self.driver, '#data_table', j, 6)
                if utils.normal_to_datetime(create_time) > utils.normal_to_datetime(globalvar.get_value("start_time")):
                    content_str += utils.get_cell_content(self.driver, '#data_table', j, column)
                else:
                    setattr(self, 'time_flag', False)
                    break
            if not getattr(self, 'time_flag'):
                break
            self.driver.execute_script("$('#pagebar_n_page').click()")
            sleep(1)
        return content_str
