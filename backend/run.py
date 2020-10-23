from driverreport import TestDriverReport
from pathlib import Path
import unittest
import HTMLTestRunner
from time import sleep, strftime
import utils
import os
import login
import globalvar
from customer_call import TestCustomerCall


def action_login():
    driver = login.login('HTTP1', 'USER2')
    globalvar.init()
    globalvar.set_value('driver', driver)


def action_quit():
    globalvar.get_value('driver').quit()


if __name__ == '__main__':

    action_login()
    tt = TestCustomerCall()
    tt.getUserInfo(13328775856)
    '''
    suite = unittest.TestSuite()
#    suite.addTest(unittest.makeSuite(TestDriverReport))
    suite.addTest(unittest.makeSuite(TestCustomerCall))
    now_time = strftime("%Y-%m-%d %H-%M-%S")
    report_path = Path(os.path.join(utils.get_path(), os.path.pardir) + '//testreport//')
    if report_path.exists():
        pass
    else:
        os.mkdir(os.path.join(utils.get_path(), os.path.pardir) + '//testreport//', 0o777)
    file_path = os.path.abspath(os.path.join(utils.get_path(), os.path.pardir)) + "//testreport//" + now_time + "_result.html"
    file_result = open(file_path, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(file_result, 2, u"业务后台测试报告", u"执行概况")
    runner.run(suite)
#    runner.run(suite, 0, 2)
    file_result.close()
    '''
    sleep(5)
    action_quit()



