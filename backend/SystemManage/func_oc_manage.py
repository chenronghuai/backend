import utils
import unittest
from utils import TestMeta
from ddt import ddt
import globalvar
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import logging
from time import sleep


restore_flag = False


class FuncOcManage:

    def share_setup(self, share_src, share_to, flag=True):
        """
        设置运营中心共享
        :param share_src: 源运营中心，分享给别人（字符串）
        :param share_to: 目标运营中心（字符串）
        :param flag: 标志位，True（分享）False（不分享）
        :return:
        """

        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '系统管理', '运营中心管理', 'operations-center.do')

        global restore_flag
        we_oc_name = WebDriverWait(globalvar.GLOBAL_DRIVER, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#ocName')))
        we_oc_name.clear()
        we_oc_name.send_keys(share_src)
        globalvar.GLOBAL_DRIVER.execute_script('$("#datalist>table#data_table>tbody").html("")')
        globalvar.GLOBAL_DRIVER.execute_script('$("#btnQuery").click()')
        WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#datalist>table#data_table>tbody>tr')))
        try:
            record_locator = utils.get_record_by_field_value(globalvar.GLOBAL_DRIVER, '#datalist>table#data_table', '名称', share_src)
        except StaleElementReferenceException:
            sleep(1)
            record_locator = utils.get_record_by_field_value(globalvar.GLOBAL_DRIVER, '#datalist>table#data_table', '名称', share_src)
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, record_locator + '>td:nth-child(11)'))).find_element_by_link_text('分享').click()
        globalvar.GLOBAL_DRIVER.switch_to.frame(globalvar.GLOBAL_DRIVER.find_element_by_css_selector('iframe[src^="/operations-center.do?method=ocSharePage"]'))
        we_goal_center = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#operationRight>li[dataname="' + share_to + '"]')))
        if flag:
            if int(we_goal_center.get_attribute('datacheck')) == 0:
                restore_flag = True
                we_goal_center.find_element_by_css_selector('input').click()
            else:
                restore_flag = False
        else:
            if int(we_goal_center.get_attribute('datacheck')) == 1:
                restore_flag = True
                we_goal_center.find_element_by_css_selector('input').click()
            else:
                restore_flag = False
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(2)

    def restore(self, share_src, share_to):

        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '系统管理', '运营中心管理', 'operations-center.do')

        global restore_flag
        if restore_flag:
            sleep(2)
            we_oc_name = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#ocName')))
            we_oc_name.clear()
            we_oc_name.send_keys(share_src)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#datalist>table#data_table>tbody>tr')))
            try:
                record_locator = utils.get_record_by_field_value(globalvar.GLOBAL_DRIVER, '#datalist>table#data_table', '名称', share_src)
            except StaleElementReferenceException:
                sleep(0.5)
                record_locator = utils.get_record_by_field_value(globalvar.GLOBAL_DRIVER, '#datalist>table#data_table', '名称', share_src)
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, record_locator + '>td:nth-child(11)'))).find_element_by_link_text('分享').click()
            globalvar.GLOBAL_DRIVER.switch_to.frame(
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('iframe[src^="/operations-center.do?method=ocSharePage"]'))
            we_goal_center = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#operationRight>li[dataname="' + share_to + '"]')))
            we_goal_center.find_element_by_css_selector('input').click()
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
            sleep(1)