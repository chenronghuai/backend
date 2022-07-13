from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep, strftime
import log
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import utils
import globalvar
import re
from common import Driver


class FuncDriverReport:

    is_phone = True

    def __init__(self):
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '监控管理', '司机报班', 'driverReport.do')

    def report_action(self, ori_val, des_val):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(lambda x: x.find_element_by_id('driverUid').get_attribute('value') != '')
        globalvar.GLOBAL_DRIVER.execute_script('$("#sel_origin").val("' + ori_val + '")')
        globalvar.GLOBAL_DRIVER.execute_script('$("#sel_destination").val("' + des_val + '")')
        we_location = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#location_name')
        sleep(1)
        we_location.clear()
        we_location.send_keys('厦门市思明区前埔北路')  # 2022-03-15，防止后台取不到司机位置导致报班失败
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#tangram-suggestion--TANGRAM__1p-item0 > i'))).click()
        sleep(1)
        globalvar.GLOBAL_DRIVER.execute_script('$("table#data_table>tbody>tr").html("")')
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#report').click()
        msg_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)

        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr')))
            return True
        except TimeoutException:
            log.logger.debug(f'司机报班失败---{msg_text}!')
            return False

    def driver_report_by_phone(self, phone, ori_val, des_val):
        we_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#phone')
        we_phone.clear()
        globalvar.GLOBAL_DRIVER.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        we_phone.send_keys(phone)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))  # 等待蒙层消失
        globalvar.GLOBAL_DRIVER.find_element(By.CSS_SELECTOR, '#query_driver').click()
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(lambda x: len(x.find_elements_by_css_selector('tbody>tr>td')) > 1)
        except TimeoutException:
            log.logger.error(f'列表找不到号码为{phone}的司机')
            raise ValueError
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'tbody>tr>td:nth-child(15)>a[name="btnReport"]'))).click()
#        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(15)>a[name="btnReport"]').click()
        if not self.report_action(ori_val, des_val):
            return '报班失败'

        # 添加司机进池
        driver_id = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr').get_attribute('data-uid')
        car_num = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(3)').text
        license_text = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(11)').text
        max_user = int(re.search(r'(\d+)\D+(\d+)\D+', license_text).group(1))
        max_package = int(re.search(r'(\d+)\D+(\d+)\D+', license_text).group(2))
        contact_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(4)').text
        register_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(5)').text
        car_type = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(7)').text
        oc_center = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(14)').text
        driver = Driver(driver_id, max_user, max_package, car_type, oc_center, register_phone, contact_phone)
        driver.car_num = car_num
        globalvar.add_driver(driver)
        return globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(10)').text

    def driver_report_by_carnum(self, carnum, phone, ori_val, des_val):
        self.is_phone = False
        self.b_driver = False
        we_carnum = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selCar_text')
        we_carnum.clear()
        globalvar.GLOBAL_DRIVER.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        globalvar.GLOBAL_DRIVER.execute_script('$("#phone").val("")')
#        globalvar.GLOBAL_DRIVER.execute_script('$("#selCar_text").val("' + carnum + '")')
        we_carnum.click()
        we_carnum.send_keys(carnum)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'ul.sp_results>li[pkey="' + carnum + '"]'))).click()
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#query_carno').click()  # 车牌查询
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'table#data_table>tbody>tr'))
            )
        except:
            log.logger.error(f'找不到该车牌{carnum}关联的任何司机')
            return None
        records = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('table#data_table>tbody>tr')
        for i in range(1, len(records)+1):
            css = '#data_table>tbody>tr:nth-child(%s)>td:nth-child(5)' % i
            try:
                phone_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css
                                                                                                 ))).text
            except StaleElementReferenceException:
                sleep(1)
                phone_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css
                                                      ))).text
            if phone_text == phone:
                self.b_driver = True
                css_report = '#data_table>tbody>tr:nth-child(%s)>td:nth-child(15)>a[name="btnReport"]' % i
                #  不加try块，在灰度环境会出现StaleElementReferenceException，不解！！！
                try:
                    WebDriverWait(globalvar.GLOBAL_DRIVER, 5, ignored_exceptions=[StaleElementReferenceException]).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, css_report))).click()
                except:
                    WebDriverWait(globalvar.GLOBAL_DRIVER, 5, ignored_exceptions=[StaleElementReferenceException]).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, css_report))).click()

                break
        if not self.b_driver:
            log.logger.error(f'找不到{carnum}-{phone}关联的司机！')
            return False

        if not self.report_action(ori_val, des_val):
            return '报班失败'

        # 添加司机进池
        css_record = 'tbody>tr:nth-child({})'.format(i)
        driver_id = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css_record).get_attribute('data-uid')
        car_num = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(3)').text
        license_text = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css_record+'>td:nth-child(11)').text
        max_user = int(re.search(r'(\d+)\D+(\d+)\D+', license_text).group(1))
        max_package = int(re.search(r'(\d+)\D+(\d+)\D+', license_text).group(2))
        contact_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css_record+'>td:nth-child(4)').text
        register_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css_record + '>td:nth-child(5)').text
        car_type = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css_record+'>td:nth-child(7)').text
        oc_center = globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css_record+'>td:nth-child(14)').text
        driver = Driver(driver_id, max_user, max_package, car_type, oc_center, register_phone=register_phone, contact_phone=contact_phone)
        driver.car_num = car_num
        globalvar.add_driver(driver)
        css_goal = css_record+'>td:nth-child(10)'
        return globalvar.GLOBAL_DRIVER.find_element_by_css_selector(css_goal).text

    def driver_cancel_report(self, phone):
        we_phone = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#phone')
        we_carnum = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selCar_text')
        we_phone.clear()
        we_carnum.clear()
        globalvar.GLOBAL_DRIVER.execute_script('$("table#data_table>tbody>tr").html("")')  # 清空表内容，避免用例交叉
        we_phone.send_keys(phone)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#query_driver').click()
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody>tr')))
        except:
            return '找不到司机'
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr>td:nth-child(15)>a:nth-child(2)').click()
        driver_id = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('tbody>tr').get_attribute('data-uid')
        globalvar.GLOBAL_DRIVER.execute_script('$("table#data_table>tbody>tr").html("")')  # added by 2021-7-5
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div.layui-layer-btn.layui-layer-btn- > a.layui-layer-btn0'))).click()
        globalvar.GLOBAL_DRIVER.switch_to.frame(globalvar.GLOBAL_DRIVER.find_element_by_css_selector('iframe[src="/driverReport.do"]'))

        result_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)  # modified by 2021-7-15
        if '已成功取消' in result_text:
            cancel_driver = globalvar.get_driver(driver_id)
            globalvar.del_driver(cancel_driver)
            return WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'tbody>tr>td:nth-child(10)'))).text  
        else:
            log.logger.debug(f'{phone}取消报班失败，msg={result_text}')
            raise IndexError
