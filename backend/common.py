import utils


class Order(object):
    def __init__(self, id_, ):
        self.__order_id = id_

    @property
    def order_id(self):
        return self.__order_id

    @property
    def appoint_time(self):
        return self.__appoint_time

    @appoint_time.setter
    def appoint_time(self, time):
        self.__appoint_time = time

    @property
    def appoint_driver(self):
        return self.__appoint_driver

    @appoint_driver.setter
    def appoint_driver(self, driver_):
        self.__appoint_driver = driver_

    @property
    def order_time(self):
        return self.__order_time

    @order_time.setter
    def order_time(self, time):
        self.__order_time = time

    @property
    def order_status(self):
        return self.__order_status

    @order_status.setter
    def order_status(self, status):
        self.__order_status =status

    @property
    def order_origin(self):
        return self.__order_origin

    @order_origin.setter
    def order_origin(self, origin):
        self.__order_origin = origin

    @property
    def order_price(self):
        return self.__order_price

    @order_price.setter
    def order_price(self, price):
        self.__order_price = price

    @property
    def order_count(self):
        return self.__order_count

    @order_count.setter
    def order_count(self, count):
        self.__order_count = count

    @property
    def order_type(self):
        return self.__order_type

    @order_type.setter
    def order_type(self, type_):
        self.__order_type = type_

    @property
    def line_id(self):
        return self.__line_id

    @line_id.setter
    def line_id(self, id_):
        self.__line_id = id_

    @property
    def source_oc_code(self):
        return self.__source_oc_code

    @source_oc_code.setter
    def source_oc_code(self, code_):
        self.__source_oc_code = code_

    @property
    def car_type(self):
        return self.__car_type

    @car_type.setter
    def car_type(self, type_):
        self.__car_type = type_

    @property
    def order_phone(self):
        return self.__order_phone

    @order_phone.setter
    def order_phone(self, phone_):
        self.__order_phone = phone_

    @property
    def order_contact_phone(self):
        return self.__order_contact_phone

    @order_contact_phone.setter
    def order_contact_phone(self, phone_):
        self.__order_contact_phone = phone_


class Driver(object):
    def __init__(self, id_, max_user, max_package, car_type, oc_center, register_phone, contact_phone, driver_type=utils.DriverType.NET_DRIVER):
        self.__driver_id = id_
        self.__max_user = max_user
        self.__max_package = max_package
        self.__car_type = car_type
        self.__oc_center = oc_center
        self.__register_phone = register_phone
        self.__contact_phone = contact_phone
        self.__driver_type = driver_type
        self.__appoint_user_count = 0
        self.__appoint_package_count = 0
        self.__charter_count = 0

    @property
    def driver_id(self):
        return self.__driver_id

    @property
    def max_user(self):
        return self.__max_user

    @property
    def max_package(self):
        return self.__max_package

    @property
    def car_type(self):
        return self.__car_type

    @property
    def oc_center(self):
        return self.__oc_center

    @property
    def appoint_user_count(self):
        return self.__appoint_user_count

    @appoint_user_count.setter
    def appoint_user_count(self, user_count):
        self.__appoint_user_count = user_count

    @property
    def appoint_package_count(self):
        return self.__appoint_package_count

    @appoint_package_count.setter
    def appoint_package_count(self, package_count):
        self.__appoint_package_count = package_count

    @property
    def charter_count(self):
        return self.__charter_count

    @charter_count.setter
    def charter_count(self, count):
        self.__charter_count = count

    @property
    def driver_type(self):
        return self.__driver_type

    @driver_type.setter
    def driver_type(self, _type):
        self.__driver_type = _type

    @property
    def register_phone(self):
        return self.__register_phone

    @register_phone.setter
    def register_phone(self, _register_phone):
        self.__register_phone = _register_phone

    @property
    def contact_phone(self):
        return self.__contact_phone

    @contact_phone.setter
    def contact_phone(self, _contact_phone):
        self.__contact_phone = _contact_phone

    @property
    def car_num(self):
        return self.__car_num

    @car_num.setter
    def car_num(self, _car_num):
        self.__car_num = _car_num

