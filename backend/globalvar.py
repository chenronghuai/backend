from sys import argv
from PaVManage.func_line import FuncLine
import utils
import log


global_dict = {}
order_pool = []
driver_pool = []
opened_window_pool = []
appointed_driver_pool = []
GLOBAL_DRIVER = None

CLASSIC_PHONE_NUMBER = '66666663'

TEST_INTERLINE_ID = "361000_to_361000"
PROD_INTERLINE_ID = "361000_to_361000"
INTERLINE_ID = TEST_INTERLINE_ID if argv[1] == 'TEST' else PROD_INTERLINE_ID

TEST_FASTLINE_ID = "350200_to_350200048"
PROD_FASTLINE_ID = "350400_to_350400001"
FASTLINE_ID = TEST_FASTLINE_ID if argv[1] == 'TEST' else PROD_FASTLINE_ID


def init():
    global global_dict, order_pool, driver_pool, opened_window_pool, appointed_driver_pool, GLOBAL_DRIVER
    global_dict = {}
    order_pool = []
    driver_pool = []
    appointed_driver_pool = []
    opened_window_pool = []
    GLOBAL_DRIVER = None


def init_line():
    lm = FuncLine()
    lm.queryLine(line_num=INTERLINE_ID)
    utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                   INTERLINE_ID, '安全号码')
    safe_info_dict = lm.get_safe_phone()
    if safe_info_dict['isSafe'] == '0':  # 确保安全号码处于开启状态
        utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                       INTERLINE_ID, '安全号码')
        lm.set_safe_phone(flag=True, city='福州市')
        set_value('INTER_RESUME_FLAG', True)

    utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                   INTERLINE_ID, '修改')
    set_value('INTER_AUTH_FLAG', lm.get_inter_line_attr()['auth'])

    lm.queryLine(line_num=FASTLINE_ID)
    utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                   FASTLINE_ID, '安全号码')
    safe_info_dict = lm.get_safe_phone()
    if safe_info_dict['isSafe'] == '0':  # 确保安全号码处于开启状态
        utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                       FASTLINE_ID, '安全号码')
        lm.set_safe_phone(flag=True, city='福州市')
        set_value('FAST_RESUME_FLAG', True)
    # 关闭班线线路的身份认证，确保班线流程顺畅
    utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                   FASTLINE_ID, '修改')
    if '是' == lm.get_fast_line_attr()['auth']:
        utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                       FASTLINE_ID, '修改')
        lm.modify_fast_line(identity_auth='否')
        set_value('FAST_AUTH_FLAG', True)


def teardown_line():  # 恢复线路到原来的状态
    lm = FuncLine()
    utils.make_sure_driver(GLOBAL_DRIVER, '人员车辆管理', '线路管理', 'line.do')
    # 恢复城际线路的安全号码状态（关闭状态）
    if get_value('INTER_RESUME_FLAG'):
        lm.queryLine(line_num=INTERLINE_ID)
        utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                      INTERLINE_ID, '安全号码')
        lm.set_safe_phone(flag=False)
    # 恢复班线线路的安全号码状态（关闭状态）
    if get_value('FAST_RESUME_FLAG'):
        lm.queryLine(line_num=FASTLINE_ID)
        utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                       FASTLINE_ID, '安全号码')
        lm.set_safe_phone(flag=False)
    #  如果身份认证被关闭，恢复开启
    if get_value('FAST_AUTH_FLAG'):
        lm.queryLine(line_num=FASTLINE_ID)
        utils.select_operation_by_attr(GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id',
                                       FASTLINE_ID, '修改')
        lm.modify_fast_line(identity_auth='是')


def set_value(key, value):
    global global_dict
    global_dict[key] = value

'''
def get_driver():
    return GLOBAL_DRIVER
'''


def get_value(key, defval=None):
    global global_dict
    try:
        return global_dict[key]
    except KeyError:
        return defval


def add_order(order):
    global order_pool
    order_pool.append(order)


def del_order(order):
    try:
        global order_pool
        order_pool.remove(order)
    except ValueError:
        raise IndexError


def get_order(id_):
    global order_pool
    for order in order_pool:
        if id_ == order.order_id:
            return order


def add_driver(driver):
    global driver_pool
    driver_pool.append(driver)


def del_driver(driver):
    try:
        global driver_pool
        driver_pool.remove(driver)
    except ValueError:
        raise IndexError


def get_driver(id_):
    global driver_pool
    for driver in driver_pool:
        if id_ == driver.driver_id:
            return driver


