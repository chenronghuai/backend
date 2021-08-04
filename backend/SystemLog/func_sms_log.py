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
        """
        短信日记页面搜索特定电话、时间的短信操作
        :param phone: 电话号码
        :param s_time: 起始时间，格式为：2020-07-28 00:00:00，默认None为当天0点
        :param e_time: 结束时间，格式为：2020-07-28 00:00:00，默认None为当天24点
        :return: 没有返回值
        """
        we_phone = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#mobile')))
        we_phone.clear()
        we_phone.send_keys(phone)
        if s_time is not None:
            we_starttime = self.driver.find_element_by_css_selector('#startTime')
            we_starttime.clear()
            we_starttime.send_keys(s_time)
        if e_time is not None:
            we_endtime = self.driver.find_element_by_css_selector('#endTime')
            we_endtime.clear()
            we_endtime.send_keys(e_time)
        self.driver.execute_script("$('#data_table>tbody').html('')")
        self.driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '#data_table>tbody>tr')))

    def get_content_by_field(self, column=4):
        """
        获取短信日记页的短信内容
        :param column:目标列，数字，第一列为1，依此类推，默认4为短信内容
        :return:字符串，内容累加的结果字符串
        """
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_any_elements_located((By.CSS_SELECTOR, '#data_table>tbody>tr')))

        content_str = ''

        info_text = self.driver.find_element_by_css_selector('#resultHTML>#pagebar>p').text
        page_num = int(re.search(r'.+/(.+)', info_text).group(1))
        setattr(self, 'time_flag', True)
        for i in range(page_num):
            records = self.driver.find_elements_by_css_selector('#data_table>tbody>tr')
            for j in range(1, len(records)+1):
                create_time = utils.get_cell_content(self.driver, '#data_table', j, 6)  # 获取短信创建时间
                if utils.normal_to_datetime(create_time) > utils.normal_to_datetime(globalvar.get_value("start_time")):
                    content_str += utils.get_cell_content(self.driver, '#data_table', j, column)
                else:
                    setattr(self, 'time_flag', False)
                    break  # 时间早于自动化测试开始时间，跳出当前页面循环
            if not getattr(self, 'time_flag'):
                break  # 时间早于自动化测试开始时间，跳出所有页面循环
            if i < page_num-1:
                self.driver.execute_script("$('#pagebar_n_page').click()")
            sleep(1)
        return content_str
