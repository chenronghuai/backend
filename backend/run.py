from driverreport import TestDriverReport
from pathlib import Path
import unittest
import HTMLTestRunner
from time import sleep, strftime
import utils
import os
from sys import argv
import login
import globalvar
from customer_call import TestCustomerCall


def action_login():
    if len(argv) < 3:
        print('正确用法：python run.py 环境 用户，共3个参数')
        exit(1)
    else:
        driver = login.login(argv[1], argv[2])
        globalvar.init()
        globalvar.set_value('driver', driver)


def action_quit():
    globalvar.get_value('driver').quit()


if __name__ == '__main__':

    action_login()
    '''
    tt = TestCustomerCall()
    tt.getUserInfo(13328775856)
    tt.selectOrderType('快线')
#    tt.selectInterOrigin('XM', '厦门市|XMCJ', '软件园二期')
#    tt.selectInterDestination('XM', '第一中学')
    tt.selectECount(3)
    tt.orderExpress('厦门市', '中医院', '厦门市', '第一医院')
#    tt.selectDate(date='明天')
#    tt.commit()
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

    sleep(5)
    action_quit()



