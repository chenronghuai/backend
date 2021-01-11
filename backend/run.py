from driver_report import TestDriverReport
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
import logging
from inter_center import TestInterCenter
from order_manage import TestOrderManage
from flight_center import TestFlightCenter
from flight_order_manage import TestFlightOrderManage
from flights_manage import TestFlightsManage

logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def action_login():
    if len(argv) < 4:
        print('正确用法：python run.py 环境 用户 类型，共4个参数')
        exit(1)
    else:
        driver = login.login(argv[1], argv[2])
        globalvar.init()
        globalvar.set_value('driver', driver)


def action_quit():
    globalvar.get_value('driver').quit()


if __name__ == '__main__':

    action_login()

    suite_flow = unittest.TestSuite()
    suite_one = unittest.TestSuite()
    suite_all = unittest.TestSuite()

    suite_flow.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDriverReport))
    suite_flow.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCustomerCall))
    suite_flow.addTest(unittest.TestLoader().loadTestsFromTestCase(TestInterCenter))
    suite_flow.addTest(unittest.TestLoader().loadTestsFromTestCase(TestOrderManage))
    suite_flow.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFlightCenter))
    suite_flow.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFlightOrderManage))

    suite_one.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCustomerCall))

#    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestFlightsManage))

    now_time = strftime("%Y-%m-%d %H-%M-%S")
    report_path = Path(os.path.join(utils.get_path(), os.path.pardir) + '//testreport//')
    if report_path.exists():
        pass
    else:
        os.mkdir(os.path.join(utils.get_path(), os.path.pardir) + '//testreport//', 0o777)
    file_path = os.path.abspath(os.path.join(utils.get_path(), os.path.pardir)) + "//testreport//" + now_time + "_result.html"
    file_result = open(file_path, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(file_result, 2, u"业务后台测试报告", u"执行概况")
    if argv[3] == 'auto':
        runner.run(suite_one)
    elif argv[3] == 'flow':
        runner.run(suite_flow)
    elif argv[3] == 'all':
        runner.run(suite_all)
#    runner.run(suite, 0, 2)
    file_result.close()

    sleep(1)
    action_quit()



