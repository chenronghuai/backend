import utils
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import logging
from time import sleep


restore_flag = False


def share_setup(driver, share_src, share_to, flag=True):
    global restore_flag
    we_oc_name = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#ocName')))
    we_oc_name.clear()
    we_oc_name.send_keys(share_src)
    driver.execute_script('$("#datalist>table#data_table>tbody").html("")')
    driver.execute_script('$("#btnQuery").click()')
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '#datalist>table#data_table>tbody>tr')))
    try:
        record_locator = utils.get_record_by_field_value(driver, '#datalist>table#data_table', '名称', share_src)
    except StaleElementReferenceException:
        sleep(1)
        record_locator = utils.get_record_by_field_value(driver, '#datalist>table#data_table', '名称', share_src)
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, record_locator + '>td:nth-child(11)'))).find_element_by_link_text('分享').click()
    driver.switch_to.frame(driver.find_element_by_css_selector('iframe[src^="/operations-center.do?method=ocSharePage"]'))
    we_goal_center = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#operationRight>li[dataname="' + share_to + '"]')))
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
    driver.find_element_by_css_selector('#btnSave').click()
    driver.switch_to.parent_frame()
    sleep(2)


def restore(driver, share_src, share_to):
    global restore_flag
    if restore_flag:
        sleep(2)
        we_oc_name = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#ocName')))
        we_oc_name.clear()
        we_oc_name.send_keys(share_src)
        driver.find_element_by_css_selector('#btnQuery').click()
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#datalist>table#data_table>tbody>tr')))
        try:
            record_locator = utils.get_record_by_field_value(driver, '#datalist>table#data_table', '名称', share_src)
        except StaleElementReferenceException:
            sleep(0.5)
            record_locator = utils.get_record_by_field_value(driver, '#datalist>table#data_table', '名称', share_src)
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, record_locator + '>td:nth-child(11)'))).find_element_by_link_text('分享').click()
        driver.switch_to.frame(
            driver.find_element_by_css_selector('iframe[src^="/operations-center.do?method=ocSharePage"]'))
        we_goal_center = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#operationRight>li[dataname="' + share_to + '"]')))
        we_goal_center.find_element_by_css_selector('input').click()
        driver.find_element_by_css_selector('#btnSave').click()
        driver.switch_to.parent_frame()
        sleep(1)