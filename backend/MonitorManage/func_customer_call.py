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
        self.driver = globalvar.get_value('driver')
        utils.make_sure_driver(self.driver, '监控管理', '客户来电', '客户', 'customerCall.do')

    def getUserInfo(self, phone):
        self.driver.execute_script("$('#userTypeDiv').html('')")
        we_number = self.driver.find_element_by_css_selector("#phone")
        we_number.clear()
        we_number.send_keys(phone)
        self.driver.execute_script('$("#callOrderPage>table>tbody").html("")')
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#query_all"))).click()
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#userTypeDiv')))
        try:  # 新用户记录可能为空
            WebDriverWait(self.driver, 3).until(
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
            self.driver.find_element(By.XPATH, xpath).click()
        except StaleElementReferenceException:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath))).click()
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

    def input_receive_phone(self, receive_name, receive_phone):
        self.driver.execute_script('$("#receiveName").val("' + receive_name + '")')
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
        try:  # 超时异常可能是系统刷新时startName-suggest>div为空？使用try试试
            self.driver.find_element(By.CSS_SELECTOR, '#startName').click()
            WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest>div')))
        except TimeoutException:
            self.driver.find_element(By.CSS_SELECTOR, '#startName').click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest>div')))
        self.driver.find_element(By.CSS_SELECTOR, '#startName').send_keys(origin_region_index)
        self.driver.execute_script("$('#endsName-suggest').html('')")  # 20121-7-1 从下一句的后面移到前面
        if len(self.driver.find_elements_by_css_selector('#startName-suggest>div')) > 1:
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
                '//*[@id="startName-suggest"]/div[@text="' + origin_region + '"]')), '起始方位无法获取').click()

        sleep(0.5)
        we_ori_addr = self.driver.find_element_by_css_selector('#startAddr')
#        WebDriverWait(self.driver, 5).until(
#            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#start-lists-penal')))  # 7-9注释，貌似常在
        try:
            we_ori_addr.click()
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#start-lists-penal>li')))
        except TimeoutException:
            we_ori_addr.click()
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#start-lists-penal>li')))
        try:
            we_ori_addr.send_keys(origin_addr)
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')), '起点POI无法获取').click()  # 此行代码偶发超时异常，增加时间试试效果
        except TimeoutException:
            we_ori_addr.send_keys(origin_addr)
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')),
                '起点POI无法获取').click()
        WebDriverWait(self.driver, 5).until(
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
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#endsName-suggest>div')))
        self.driver.find_element(By.CSS_SELECTOR, '#endsName').click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#endsName-suggest>div')))
        WebDriverWait(self.driver, 5).until(
            lambda x: x.execute_script("return $('#endsName-suggest').css('display')") == 'block')
        self.driver.find_element(By.CSS_SELECTOR, '#endsName').send_keys(des_region_index)
        sleep(0.5)
        WebDriverWait(self.driver, 10).until_not(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#start-lists-penal>li:nth-child(1)')), '起点信息还没消失')
        we_des_addr = self.driver.find_element_by_css_selector('#endAddr')
#        WebDriverWait(self.driver, 5).until(
#            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#end-lists-penal')))   # 7-9注释，貌似常在
        try:
            we_des_addr.click()
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#end-lists-penal>li')))
        except TimeoutException:
            we_des_addr.click()
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#end-lists-penal>li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR,
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
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#startName-suggest>div')))
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
        """
        创建新班次，当前时间10分钟后的班次
        :return:
        """
        utils.switch_frame(self.driver, '班线管理', '班次管理', 'flights.do')
        self.driver.find_element_by_css_selector('#addLineFlights').click()
        sleep(1)
        self.driver.switch_to.frame(self.driver.find_element_by_css_selector('iframe[src^="/flights.do?method=editLineFlights"]'))

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

        self.driver.find_element_by_css_selector('#selCenter').click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#selCenter-suggest>div[dataname$="漳州运营中心"]'))).click()
        self.driver.find_element_by_css_selector('#selLine').click()
        if argv[1] == 'TEST':
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname="高林SM专线"]'))).click()
        else:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#selLine-suggest>div[dataname="厦门测试班线"]'))).click()
        self.driver.find_element_by_css_selector('#flightsNo').send_keys(flight_no)
        self.driver.find_element_by_css_selector('#saleSeats').send_keys(20)
        self.driver.find_element_by_css_selector('#flightsDate').send_keys(depart_date)
        self.driver.find_element_by_css_selector('#flightsDispatchedTime').send_keys(depart_time)
        self.driver.find_element_by_css_selector('#btnSave').click()
        globalvar.set_value('FlightNo', flight_no)
        self.driver.switch_to.parent_frame()
        utils.switch_exist_frame(self.driver, 'customerCall.do', '客户')

    def orderExpress(self, ori_city, ori_addr, des_city, des_addr):
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#startName-suggest>div[lotparent]')))
        try:
            self.driver.find_element(By.ID, 'startName').click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest>div[lotparent]')))
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
             '//*[@id="startName-suggest"]/div[@text="' + ori_city + '"]')), '起始城市无法获取').click()
        except TimeoutException:  # 碰到点击城市方位时出来城际方位-->还是会超时异常，疑惑？
            self.driver.find_element_by_id('startAddr').click()
            self.driver.find_element(By.ID, 'startName').click()
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest>div[lotparent]')))
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH,
                                                                                  '//*[@id="startName-suggest"]/div[@text="' + ori_city + '"]')),
                                                '起始城市无法获取').click()
        we_ori_addr = self.driver.find_element_by_id('startAddr')
        try:
            we_ori_addr.click()
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        except TimeoutException:
            we_ori_addr.click()
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="start-lists-penal"]/li')))
        try:
            we_ori_addr.send_keys(ori_addr)
        except StaleElementReferenceException:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(we_ori_addr)).send_keys(ori_addr)
        # 下句偶尔超时异常，未知原因
        WebDriverWait(self.driver, 15).until(
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
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#end-lists-penal')))  # 2021-7-9，添加
        we_des_addr.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="end-lists-penal"]/li')))
        we_des_addr.send_keys(des_addr)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点POI无法获取').click()
        WebDriverWait(self.driver, 5).until(
            EC.invisibility_of_element_located((By.XPATH, '//*[@id="end-lists-penal"]/li[1]')),
            '终点下拉POI超时不消失')

    def orderHelpDrive(self, city, ori_addr, des_addr):
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@id="startName-suggest"]/div')))
        try:
            self.driver.find_element(By.ID, 'startName').click()
            WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest')))
        except TimeoutException:
            self.driver.find_element(By.ID, 'startName').click()
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#startName-suggest')))
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
            WebDriverWait(self.driver, 15).until(
                EC.text_to_be_present_in_element((By.XPATH, '//*[@id="priceTips"]'), '预估花费'), '获取价格失败')
#        sleep(0.5)  # added by 2021-7-5 市内订单偶发下单不成功情形
        self.driver.execute_script("$('#submitAll').click()")
        msg_text = utils.wait_for_laymsg(self.driver)
        return msg_text

    def checkitem(self, str_filter, by_phone = None):
        """
        确认目标订单的位置（当账号有较多的预约订单时【超过5单】有可能获取不到）
        :param str_filter: 订单类型
        :return: 客户来电页订单所在行数，匹配不到返回0
        """
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#call-see-order'))).click()
        except StaleElementReferenceException:
            sleep(0.5)
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#call-see-order'))).click()
        sleep(2)
        b_match = False
        for i in range(1, len(self.driver.find_elements_by_css_selector('#callOrderPage>table>tbody>tr'))+1):
            if str_filter != '快巴':
                if str_filter == utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2):
                    b_match = True
                    break
            else:
                if str_filter == utils.get_cell_content(self.driver, '#callOrderPage>table', i, 2) and by_phone == utils.get_cell_content(self.driver, '#callOrderPage>table', i, 4):
                    b_match = True
                    break
        return i if b_match else 0

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
        css = '#callOrderPage>table>tbody>tr:nth-child({})'.format(index)
        '''
        if len(self.driver.find_elements_by_css_selector('#callOrderPage>table>tbody>tr')) > 1:
            css = '#callOrderPage>table>tbody>tr:nth-child({})'.format(index)
        else:
            css = '#callOrderPage>table>tbody>tr'
        '''
        order_id = self.driver.find_element_by_css_selector(css).get_attribute('order-id')
        appoint_time = self.driver.find_element_by_css_selector(css + '>td:nth-child(1)').text
        count = self.driver.find_element_by_css_selector(css + '>td:nth-child(3)').text
        phone = self.driver.find_element_by_css_selector(css + '>td:nth-child(4)').text
        self.create_order(order_id, order_type, appoint_time, phone, car_type, count)