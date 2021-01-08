
global_dict = {}
order_pool = []
driver_pool = []


def init():
    global global_dict, order_pool, driver_pool
    global_dict = {}
    order_pool = []
    driver_pool = []


def set_value(key, value):
    global global_dict
    global_dict[key] = value


def get_value(key, defval=None):
    global global_dict
    try:
        return global_dict[key]
    except KeyError:
        return defval


def add_order(order):
    global order_pool
    order_pool.append(order)


def get_order(id_):
    global order_pool
    for order in order_pool:
        if id_ == order.__order_id:
            return order


def add_driver(driver):
    global driver_pool
    driver_pool.append(driver)


def get_driver(id_):
    global driver_pool
    for driver in driver_pool:
        if id_ == driver.__driver_id:
            return driver


