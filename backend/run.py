from driverreport import TestDriverReport
from pathlib import Path
import unittest
import HTMLTestRunner
from time import sleep, strftime
import utils
import os


if __name__ == '__main__':

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDriverReport))
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


