from test_driver_report import TestDriverReport
from pathlib import Path
import unittest
import HTMLTestRunner
from time import sleep, strftime
import utils
import os
from sys import argv
import login
import globalvar
import log
from test_customer_call import TestCustomerCall
from test_inter_center import TestInterCenter
from test_order_manage import TestOrderManage
from test_flight_center import TestFlightCenter
from test_flight_order_manage import TestFlightOrderManage
from test_permission import TestPermission
from test_price import TestPrice
from EmailConfig.email import SendEmail
from test_flights_manage import TestFlightsManage
from test_line import TestLine
from test_sms import TestSms
from datetime import datetime
import time


def action_login():
    if len(argv) < 4:
        print('正确用法：python run.py 环境 用户 类型，共4个参数')
        exit(1)
    else:
        globalvar.init()
        globalvar.set_value('start_time',
                            f'{time.gmtime().tm_year}-{time.gmtime().tm_mon}-{time.gmtime().tm_mday} {time.gmtime().tm_hour + 8}:{time.gmtime().tm_min}:{time.gmtime().tm_sec}')  # 用于过滤短信时间
        login.login(argv[1], argv[2])


def action_quit():
    globalvar.get_value('driver').quit()


if __name__ == '__main__':
    try:
        now_time = strftime("%Y-%m-%d %H-%M-%S")

        report_path = Path(os.path.join(utils.get_path(), os.path.pardir) + '//testreport//')
        if report_path.exists():
            pass
        else:
            os.mkdir(os.path.join(utils.get_path(), os.path.pardir) + '//testreport//', 0o777)

        log_path = Path(os.path.join(utils.get_path(), os.path.pardir) + '//log//')
        if log_path.exists():
            pass
        else:
            os.mkdir(os.path.join(utils.get_path(), os.path.pardir) + '//log//', 0o777)

        file_path = os.path.abspath(
            os.path.join(utils.get_path(), os.path.pardir)) + "//testreport//" + now_time + "_result.html"
        file_result = open(file_path, 'wb')

        envir_str = '未知环境'
        if argv[1] == 'TEST':
            envir_str = '测试环境'
        elif argv[1] == 'STAGE':
            envir_str = '灰度环境'
        elif argv[1] == 'PROD':
            envir_str = '正式环境'
        my_list = now_time.split(' ')[1].split('-')
        new_str = now_time.split(' ')[0] + ' ' + my_list[0] + ':' + my_list[1]
        envir_str = envir_str + '【' + new_str + '】'
        title = f'业务后台{envir_str}自动化测试报告'

        runner = HTMLTestRunner.HTMLTestRunner(file_result, 2, title, u"执行概况", tester='陈荣怀')

        action_login()

        suite_flow = unittest.TestSuite()
        suite_one = unittest.TestSuite()
        suite_all = unittest.TestSuite()

        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestDriverReport))
        '''
        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestCustomerCall))

        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestInterCenter))

        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestFlightCenter))

        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestSms))

        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestOrderManage))

        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestFlightOrderManage))

        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestFlightsManage))
        
        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestLine))

        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestPermission))
        
        suite_flow.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestPrice))
        '''
        suite_one.addTest(utils.SequentialTestLoader().loadTestsFromTestCase(TestCustomerCall))

        if argv[3] == 'auto':
            runner.run(suite_one)
        elif argv[3] == 'flow':
            runner.run(suite_flow)
        elif argv[3] == 'all':
            runner.run(suite_all)
    #    runner.run(suite, 0, 2)

        file_result.close()

        #  发送邮件
        if utils.read_config_value('EMAIL', 'on_off') == 'on':
            recv_str = utils.read_config_value('EMAIL', 'receive')
            recv_list = recv_str.split(',')
            send_mail = SendEmail(
                recv=recv_list,
                title=f'业务后台{envir_str}自动化测试报告',
                content=f'Hi,\r\n\r\n    业务后台{envir_str}自动化测试报告邮件，请查阅！',
                file=file_path,
                ssl=True,
            )
            send_mail.send_email()

        sleep(1)
    finally:
        action_quit()



