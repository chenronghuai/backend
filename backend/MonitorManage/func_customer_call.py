from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import time
from selenium.webdriver.support.select import Select
import utils
from utils import OrderType, OrderStatus, CarType
import globalvar
import log
from sys import argv
from common import Order
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

count = 1
_create_flag = True


class FuncCustomerCall:

    def __init__(self):
#        self.driver = globalvar.get_value('driver')
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '客户来电', 'customerCall.do')

    def getUserInfo(self, phone):
        globalvar.GLOBAL_DRIVER.execute_script("$('#userTypeDiv').html('')")
        we_number = globalvar.GLOBAL_DRIVER.find_element_by_css_selector("#phone")
        we_number.clear()
        we_number.send_keys(phone)
        globalvar.GLOBAL_DRIVER.execute_script('$("#callOrderPage>table>tbody").html("")')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#query_all"))).click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#userTypeDiv')))
        try:  # 新用户记录可能为空
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#callOrderPage>table>tbody>tr')))
        except:
            pass

    def selectOrderType(self, order_text):
        """
        选择订单类型
        :param order_type: 订单类型
        :return:
        """
        xpath = '//div/label[text()="' + order_text + '"]'
        try:
            globalvar.GLOBAL_DRIVER.find_element(By.XPATH, xpath).click()
        except StaleElementReferenceException:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_element_located((By.XPATH, xpath))).click()
        sleep(1)

    def selectCarType(self, car_type):
        """
        选择订单类型
        :param car_type: 订单类型
        :return:
        """
        xpath = '//div[@id="car-types-div"]/label[text()="' + car_type + '"]'
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="car-types-div"]')))
        globalvar.GLOBAL_DRIVER.find_element(By.XPATH, xpath).click()
        sleep(1)

    def input_customer_phone(self, by_phone):
        if by_phone != "":
            globalvar.GLOBAL_DRIVER.execute_script('$("#tel").val("' + by_phone + '")')

    def input_receive_phone(self, receive_name, receive_phone):
        globalvar.GLOBAL_DRIVER.execute_script('$("#receiveName").val("' + receive_name + '")')
        globalvar.GLOBAL_DRIVER.execute_script('$("#receiveTel").val("' + receive_phone + '")')

    def selectInterOrigin(self, origin_region_index, origin_region, origin_addr=None):
        """
        城际起点方位、地址
        :param origin_region_index: 起点方位简称
        :param origin_region: 起点方位
        :param origin_addr: 起点地址
        :return:
        """
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#startName-suggest>div')))
        try:  # 超时异常可能是系统刷新时startName-suggest>div为空？使用try试试
            globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#startName').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest>div')))
        except TimeoutException:
            globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#startName').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest>div')))
        globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#startName').send_keys(origin_region_index)
        globalvar.GLOBAL_DRIVER.execute_script("$('#endsName-suggest').html('')")  # 20121-7-1 从下一句的后面移到前面
        if len(globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('#startName-suggest>div')) > 1:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.XPATH,
                '//*[@id="startName-suggest"]/div[@text="' + origin_region + '"]')), '起始方位无法获取').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            lambda x: x.find_element_by_id('sel_origin').get_attribute('value') != '')  # 等待起点城市方位出现
        sleep(0.5)  # 出现点击地址框没有弹出的几率性问题
        we_ori_addr = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#startAddr')
        try:
            we_ori_addr.click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#start-lists-penal>li')))
        except TimeoutException:
            we_ori_addr.click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#start-lists-penal>li')))
        try:
            we_ori_addr.send_keys(origin_addr)
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')), '起点POI无法获取').click()  # 此行代码偶发超时异常，增加时间试试效果
        except TimeoutException:
            we_ori_addr.send_keys(origin_addr)
            WebDriverWait(globalvar.GLOBAL_DRIVER, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')),
                '起点POI无法获取').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')))
        if argv[1] != 'STAGE':
            sleep(0.5)
        else:
            sleep(3.5)  # 灰度环境响应慢，需要等待更长时间

    def selectInterDestination(self, des_region_index, des_addr):
        """
        城际终点方位、地址
        :param des_region_index: 终点方位简称
        :param des_region: 终点方位
        :param des_addr: 终点地址
        :return:
        """
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
        try:
            globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#endsName').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#endsName-suggest>div')))
        except TimeoutException:
            globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#endsName').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#endsName-suggest>div')))
#        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
#            lambda x: x.execute_script("return $('#endsName-suggest').css('display')") == 'block')
        globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#endsName').send_keys(des_region_index)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(lambda x: x.find_element_by_id('sel_destination').get_attribute('value') != '')  # 9.10,等待终点城市方位出现
        sleep(0.5)  # 等待0.5秒还会出现点击地址框没有弹出的几率性问题，增加到1秒看看效果
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')), '起点信息还没消失')
        we_des_addr = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#endAddr')
        try:
            we_des_addr.click()
            # 下句偶尔超时异常，未知原因
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#end-lists-penal>li')))
        except TimeoutException:
            globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#endsName').send_keys(Keys.BACKSPACE)
            globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#endsName').send_keys(des_region_index)
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                lambda x: x.find_element_by_id('sel_destination').get_attribute('value') != '')
            we_des_addr.click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#end-lists-penal>li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
            '#end-lists-penal>li:nth-child(1)')), '终点POI无法获取').click()

    def orderInnerCity(self, city_index, city_region, ori_addr, des_addr):
        """
        市内线路下单
        :param city_index: 市内方位简称
        :param city_region: 市内方位全称
        :param ori_addr: 起始地址
        :param des_addr: 终点地址
        :return:
        """
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#startName-suggest>div')))
        globalvar.GLOBAL_DRIVER.find_element(By.ID, 'startName').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.ID, 'startName-suggest')))
        globalvar.GLOBAL_DRIVER.find_element(By.ID, 'startName').send_keys(city_index)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.XPATH,
                                    '//*[@id="startName-suggest"]/div[@text="' + city_region + '"]')),
                                            '起始方位无法获取').click()
        we_ori_addr = globalvar.GLOBAL_DRIVER.find_element_by_id('startAddr')
        we_ori_addr.click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        we_ori_addr.send_keys(ori_addr)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点POI无法获取').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until_not(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点信息还没消失')
        we_des_addr = globalvar.GLOBAL_DRIVER.find_element_by_id('endAddr')
        we_des_addr.click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="end-lists-penal"]/li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点POI无法获取').click()

    def create_fastline_flight(self):
        """
        创建新班次，当前时间10分钟后的班次
        :return:
        """
        utils.switch_frame(globalvar.GLOBAL_DRIVER, '班线管理', '班次管理', 'flights.do')
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#addLineFlights').click()
        sleep(1)
        globalvar.GLOBAL_DRIVER.switch_to.frame(globalvar.GLOBAL_DRIVER.find_element_by_css_selector('iframe[src^="/flights.do?method=editLineFlights"]'))

        secs = time.time() + 600  # 时间戳，10分钟后
        hour = time.localtime(secs).tm_hour
        year = time.localtime(secs).tm_year
        mon = time.localtime(secs).tm_mon
        if mon < 10:
            mon = '0' + str(mon)
        day = time.localtime(secs).tm_mday
        if day < 10:
            day = '0' + str(day)
        if hour < 10:
            hour = '0' + str(hour)
        minute = time.localtime(secs).tm_min  
        if minute < 10:
            minute = '0' + str(minute)
        depart_time = str(hour) + ":" + str(minute)
        flight_no = 'CS' + str(hour) + str(minute)
        depart_date = str(year) + '-' + str(mon) + '-' + str(day)
        sleep(1)

        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selCenter').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="漳州运营中心"]'))).click()
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selLine').click()
        if argv[1] == 'TEST':
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname="高林SM专线"]'))).click()
        else:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname="厦门测试班线"]'))).click()
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flightsNo').send_keys(flight_no)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#saleSeats').send_keys(20)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flightsDate').send_keys(depart_date)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#flightsDispatchedTime').send_keys(depart_time)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        globalvar.set_value('FlightNo', flight_no)
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        utils.switch_exist_frame(globalvar.GLOBAL_DRIVER, 'customerCall.do', '客户')

    def orderExpress(self, ori_city, ori_addr, des_city, des_addr):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#startName-suggest>div[lotparent]')))
        try:
            globalvar.GLOBAL_DRIVER.find_element(By.ID, 'startName').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest>div[lotparent]')))
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.XPATH,
             '//*[@id="startName-suggest"]/div[@text="' + ori_city + '"]')), '起始城市无法获取').click()
        except TimeoutException:  # 碰到点击城市方位时出来城际方位-->还是会超时异常，疑惑？
            globalvar.GLOBAL_DRIVER.find_element_by_id('startAddr').click()
            globalvar.GLOBAL_DRIVER.find_element(By.ID, 'startName').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest>div[lotparent]')))
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.XPATH,
                                                                                  '//*[@id="startName-suggest"]/div[@text="' + ori_city + '"]')),
                                                '起始城市无法获取').click()
        we_ori_addr = globalvar.GLOBAL_DRIVER.find_element_by_id('startAddr')
        try:
            we_ori_addr.click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        except TimeoutException:
            we_ori_addr.click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        try:
            we_ori_addr.send_keys(ori_addr)
        except StaleElementReferenceException:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.presence_of_element_located(we_ori_addr)).send_keys(ori_addr)
        # 下句偶尔超时异常，未知原因
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点POI无法获取').click()

        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="endsName-suggest"]/div')))
        globalvar.GLOBAL_DRIVER.find_element_by_id('endsName').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.ID, 'endsName-suggest')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until_not(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点信息还没消失')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.XPATH,
        '//*[@id="endsName-suggest"]/div[@text="' + des_city + '"]')), '终点城市无法获取').click()
        we_des_addr = globalvar.GLOBAL_DRIVER.find_element_by_id('endAddr')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#end-lists-penal')))  # 2021-7-9，添加
        we_des_addr.click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="end-lists-penal"]/li')))
        we_des_addr.send_keys(des_addr)
        # 下句偶尔超时异常，未知原因
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点POI无法获取').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.invisibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点下拉POI超时不消失')

    def orderHelpDrive(self, city, ori_addr, des_addr):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="startName-suggest"]/div')))
        try:
            globalvar.GLOBAL_DRIVER.find_element(By.ID, 'startName').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest')))
        except TimeoutException:
            globalvar.GLOBAL_DRIVER.find_element(By.ID, 'startName').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.XPATH,
         '//*[@id="startName-suggest"]/div[@text="' + city + '"]')), '起始方位无法获取').click()
        we_ori_addr = globalvar.GLOBAL_DRIVER.find_element_by_id('startAddr')
        we_ori_addr.click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        we_ori_addr.send_keys(ori_addr)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点POI无法获取').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until_not(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="start-lists-penal"]/li[1]')), '起点推荐信息长时间没消失')
        we_des_addr = globalvar.GLOBAL_DRIVER.find_element_by_id('endAddr')
        we_des_addr.click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="end-lists-penal"]/li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
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
            globalvar.GLOBAL_DRIVER.find_element(By.XPATH, xpath).click()
        if time != '':
            globalvar.GLOBAL_DRIVER.execute_script("$('#input-time').val('" + time + "')")

    def selectPCount(self, num):
        """
        选择城际、市内人数
        :param num: 人数
        :return:
        """
        xpath = '//span[@id="peopleCount"]/i/input[@value=' + "\"" + str(num) + "\"" + ']'
        globalvar.GLOBAL_DRIVER.find_element(By.XPATH, xpath).click()

    def selectECount(self, num):
        """
        快线选人数
        :param num:快线人数
        :return:
        """
        xpath = '//div[@id="fastLinePeopleCount"]/i/input[@value=' + "\"" + str(num) + "\"" + ']'
        globalvar.GLOBAL_DRIVER.find_element(By.XPATH, xpath).click()

    def select_time_long(self, id, text):
        s = globalvar.GLOBAL_DRIVER.find_element_by_id(id)
        Select(s).select_by_visible_text(text)

    def commit(self, pricetip_flag=True):
        """
        提交订单
        :return:
        """
        if pricetip_flag:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
                EC.text_to_be_present_in_element((By.XPATH, '//*[@id="priceTips"]'), '预估花费'), '获取价格失败')
#        sleep(0.5)  # added by 2021-7-5 市内订单偶发下单不成功情形
        globalvar.GLOBAL_DRIVER.execute_script("$('#submitAll').click()")
        msg_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
        return msg_text

    def checkitem(self, order_type, ori, des, customer_phone, by_phone=None):
        """
        确认目标订单的位置（当账号有较多的预约订单时【超过5单】有可能获取不到）
        :param order_type: 订单类型
        :param customer_phone: 下单电话
        :param by_phone: 乘客电话
        :return: 客户来电页订单所在行数，匹配不到返回0
        """
        i = 0
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '订单管理', 'orderManage.do')
        if argv[1] != 'TEST':  # 8.16晚，灰度和正式环境在没有输入线路下，搜索效率很低
            if not getattr(self, 'input_od_flag', False):
                utils.input_ori_des(globalvar.GLOBAL_DRIVER, "XMC", "361000", "XM", "361000")
                setattr(self, 'input_od_flag', True)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#more1>div>div.layui-input-inline>input#phone')))
        globalvar.GLOBAL_DRIVER.execute_script("$('#phone').val(" + customer_phone + ")")
        globalvar.GLOBAL_DRIVER.execute_script("$('#btnQuery').click()")
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#data_table>tbody>tr')))
        for i in range(1, len(globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('#data_table>tbody>tr')) + 1):
            actual_type = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 2)
            actual_ori = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 9)
            actual_des = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 10)
            if order_type == actual_type and ori in actual_ori and des in actual_des:
                setattr(self, "b_match", True)
                break
        return i if getattr(self, "b_match", False) else 0

    def checkitem_bus(self, flight_no, customer_phone, by_phone):
        """
        确认班线目标订单的位置（当账号有较多的预约订单时【超过5单】有可能获取不到）
        :param flight_no: 班次号
        :param customer_phone: 下单电话
        :param by_phone: 乘客电话
        :return: 客户来电页订单所在行数，匹配不到返回0
        """
        i = 0
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER,  '班线管理', '班线订单管理', 'flightsOrderManager.do')
        if argv[1] != 'TEST':  # 8.16晚
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selLine').click()  # 8.16晚
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname$="厦门测试班线"]'))).click()  # 8.16晚
        we_phone = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#phone')))
        we_phone.clear()
        we_phone.send_keys(customer_phone)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#data_table>tbody>tr')))
        for i in range(1, len(globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('#data_table>tbody>tr')) + 1):
            actual_flight_no = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 7)
            actual_by_phone = utils.get_cell_content(globalvar.GLOBAL_DRIVER, '#data_table', i, 4)
            if flight_no == actual_flight_no and by_phone == actual_by_phone:
                break
            elif i == len(globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('#data_table>tbody>tr')):
                log.logger.error(f'班线列表里没有找到对应的订单！')
                i = 0
        return i

    def create_order(self, order_id, order_type, appoint_time, phone, car_type=CarType.ANY, count=1):
        new_order = Order(order_id)
        new_order.order_type = order_type
        new_order.appoint_time = appoint_time
        new_order.order_time = time.time()
        new_order.order_count = int(count)
        new_order.order_status = OrderStatus.WAITING
        new_order.order_phone = phone
        new_order.car_type = car_type
        new_order.source_oc_code = utils.read_config_value(argv[2], 'oc')
        globalvar.add_order(new_order)

    def save_order(self, index, order_type, car_type=CarType.ANY):
        assert index != 0, f'列表里没有指定的{order_type}新订单'
        css = '#data_table>tbody>tr:nth-child({})'.format(index)
        order_id = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css).get_attribute('order-list-id')
        appoint_time = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css + '>td:nth-child(8)').text
        phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css + '>td:nth-child(3)').text
        if order_type != '快巴':
            count_ = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css + '>td:nth-child(6)').text
        else:
            count_ = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css + '>td:nth-child(5)').text
        self.create_order(order_id, order_type, appoint_time, phone, car_type, count_)
        '''
        css = '#callOrderPage>table>tbody>tr:nth-child({})'.format(index)
        order_id = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css).get_attribute('order-id')
        appoint_time = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css + '>td:nth-child(1)').text
        count = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css + '>td:nth-child(3)').text
        phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css + '>td:nth-child(4)').text
        self.create_order(order_id, order_type, appoint_time, phone, car_type, count)
        '''

    def get_ori_des(self):
        ori = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startAddr'))).get_attribute('addr_hidden')
        des = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#endAddr'))).get_attribute('addr_hidden')
        return ori, des