from driverreport import TestDriverReport
import login
import unittest
import HTMLTestRunner
from time import sleep, strftime
import utils
import os


if __name__ == '__main__':
    '''
    for i in range(2):
        driver = login.login('HTTP1', 'USER1')
    #    utils.switch_frame(driver, '监控管理', '客户来电', 'customerCall.do')
    #    utils.switch_frame(driver, '监控管理', '司机报班', 'driverReport.do')
        sleep(2)
        driver.quit()
    '''
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDriverReport))
    now_time = strftime("%Y-%m-%d %H-%M-%S")
#    file_path = utils.get_path() + "//testreport//" + now_time + "_result.html"
    file_path = os.path.abspath(os.path.join(utils.get_path(), os.path.pardir)) + "//testreport//" + now_time + "_result.html"
    file_result = open(file_path, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(file_result, 2, u"业务后台测试报告", u"执行概况")
#    runner.run(suite)
    runner.run(suite, 0, 2)
    file_result.close()


