import utils
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from sys import argv
import globalvar
import log


class FuncLine:

    def __init__(self):
#        self.driver = globalvar.get_value('driver')
        utils.make_sure_driver(globalvar.GLOBAL_DRIVER, '人员车辆管理', '线路管理', 'line.do')

    def newInner(self, **kwargs):
        """
        添加市内新线路。用法：newInner(driver, linename='南安市内', innername='3505831', c_phone='95170', d_phone='95170')。灰度和正式不跑，无法删除线路。线路已存在将不会有任何作用
        :param driver:
        :param kwargs: 4个必须的关键字参数，分别为线路名称、起终点方位ID、乘客客服电话、司机客服电话
        :return:
        """
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=editLineway&pagetype=add"]')))

        for k, v in kwargs.items():
            if k == 'linename':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#lineName').send_keys(v)
            elif k == 'innername':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#startEndName').click()
                inner_css = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#startEndName-suggest>div[dataval="' + v + '"]')
                inner_css.click()
            elif k == 'c_phone':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#serviceHotline').send_keys(v)
            elif k == 'd_phone':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#driverServiceHotline').send_keys(v)

        route_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#lineRouterIp')
        Select(route_sel).select_by_index(1)

        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnEsc'))).click()
        except:
            pass
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(2)


    def newInter(self, **kwargs):
        """
        添加城际新线路。用法：newInter(driver, startname='362300', endsname='352000', c_phone='95170', d_phone='95170', distance=90)。灰度和正式不跑，无法删除线路。线路已存在将不会有任何作用
        :param driver:
        :param kwargs: 5个必须的关键字参数，分别为起点方位ID、终点方位ID、乘客客服电话、司机客服电话、线路长度（公里）
        :return:
        """
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=editLineway"]')))

        for k, v in kwargs.items():
            if k == 'startname':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#startName').click()
                startname_css = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#startName-suggest>div[dataval="' + v + '"]')
                startname_css.click()
            elif k == 'endsname':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#endsName').click()
                endsname_css = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#endsName-suggest>div[dataval="' + v + '"]')
                endsname_css.click()
            elif k == 'c_phone':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#serviceHotline').send_keys(v)
            elif k == 'd_phone':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#driverServiceHotline').send_keys(v)
            elif k == 'distance':
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#lineMileage').send_keys(v)
        route_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#lineRouterIp')
        Select(route_sel).select_by_index(1)
        sleep(1)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnEsc'))).click()
        except:
            pass
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(2)

    def newExpress(self, *args):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=addLineCustom"]')))
        tup1 = args[0]
        tup2 = args[1]
        tup3 = args[2]
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.modifyN-item.modifyN-item-long:nth-child(1)>span>input:nth-child(3)').send_keys(tup1[0])
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector(
            'div.modifyN-item.modifyN-item-long:nth-child(2)>span>input:nth-child(1)').send_keys(tup1[1])
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector(
            'div.modifyN-item.modifyN-item-long:nth-child(4)>span>input:nth-child(1)').send_keys(tup1[2])
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector(
            'div.modifyN-item.modifyN-item-long:nth-child(5)>span>input:nth-child(1)').send_keys(tup1[3])

        for i in range(len(args)-2):
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#setRouteSite').click()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=lineCustomChoose"]')))
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selProvince').click()
            province_css = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selProvince-suggest>div[dataname="' + tup2[0] + '"]')
            province_css.click()
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selCity').click()
            city_css = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selCity-suggest>div[dataname="' + tup2[1] + '"]')
            city_css.click()
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#stationName').send_keys(tup2[2])
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input[value="查询"]').click()
            sleep(1)
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#datalist>tbody>tr[stationname="' + tup2[2] + '"]').click()
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.btnDiv>input[value="确定"]').click()

            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(5)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('div.btnDiv>input[value="取消"]').click()

        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(2)

    def queryLine(self, type_='请选择', line_num='', line_name='', line_status='全部'):
        """
        搜索线路。用法：queryLine（driver,关键字参数）
        :param driver:
        :param type_:线路类型，市内、城际...
        :param line_num:线路ID，361000_to_361000
        :param line_name:线路名称
        :param line_status:线路状态，可以或不可用
        :return:
        """
        type_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#selIncity')
        Select(type_sel).select_by_visible_text(type_)
        we_lineid = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#lineId')
        we_lineid.clear()
        we_lineid.send_keys(line_num)
        we_linename = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#lineName')
        we_linename.clear()
        we_linename.send_keys(line_name)
        status_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#isDel')
        Select(status_sel).select_by_visible_text(line_status)
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnQuery').click()
        sleep(1)

    def modifyInterLine(self, **kwargs):
        """
        修改线路基本属性。用法：modifyInterLine(driver, 可变关键字参数)
        :param driver:
        :param kwargs: 可变关键字参数，支持【show（是否前端显示）、c_phone（乘客客服电话）、d_phone（司机客服电话）、cash_pay（是否现金支付）、advance_pay（是否预支付）】关键字
        :return:
        """
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=editLineway"]')))
        for k, v in kwargs.items():
            if k == 'show':
                show_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#isShow')
                Select(show_sel).select_by_visible_text(v)
            elif k == 'c_phone':
                phone_css = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#serviceHotline')
                phone_css.clear()
                phone_css.send_keys(v)
            elif k == 'd_phone':
                phone_css = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#driverServiceHotline')
                phone_css.clear()
                phone_css.send_keys(v)
            elif k == 'cash_pay':
                cash_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#cash')
                Select(cash_sel).select_by_visible_text(v)
            elif k == 'advance_pay':
                advance_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#prePay')
                if '是' in v:
                    pay_list = v.split(',')
                    Select(advance_sel).select_by_visible_text(pay_list[0])
                    WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#preCountDown'))).send_keys(pay_list[1])
                else:
                    Select(advance_sel).select_by_visible_text(v)
            else:
                raise TypeError('{} got an unsupport argument {}'.format('modifyInterLine()', k))
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(1.5)

    def setRoute(self, level='调度1.0'):
        """
        开关路由及设置调度级别。禁用状态下等于开路由，level参数有效，开通状态下等于关路由，level参数无效
        :param driver:
        :param level: 默认参数'调度1.0'，可设置为'调度2.0'
        :return:
        """
        globalvar.GLOBAL_DRIVER.switch_to.default_content()
        title_text = WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="layui-layer-title"]'))).text
        if title_text == '操作开启':
            WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.XPATH, '//div[@id="dispatchAlogrithm"]/p/label[text()="' + level + '"]'))).click()
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('a.layui-layer-btn0').click()
        line_iframe = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('iframe[src="/line.do"]')
        globalvar.GLOBAL_DRIVER.switch_to.frame(line_iframe)

    def setCarType(self, *args, flag=True):
        """
        设置线路车型。用法：setCarType(driver,'新能源/5座',...,flag=True)
        :param driver:
        :param args: 字符串，车型名称，必须在车型列表的车型
        :param flag:True时添加，False时删除
        :return:
        """
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=lineCarClassPage"]')))
        globalvar.GLOBAL_DRIVER.execute_script("$('select>option').each(function(inx,obj){$(this).removeAttr('selected')})")  # 取消默认选中

        if flag:
            left_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#sel_left')
            for car in args:
                Select(left_sel).select_by_visible_text(car)
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btn_2').click()
                sleep(1)
        else:
            right_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#sel_right')
            for car in args:
                Select(right_sel).select_by_visible_text(car)
                globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btn_3').click()
                sleep(1)

        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        try:
            globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))).click()
        except:
            pass
        sleep(2)  # 测试与灰度正式的移除车型流程有差异，测试少了移除车型清除价格的弹窗
        try:
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))).click()
        except:
            pass
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))

    def setCommission(self, **kwargs):
        """
        设置线路手续费。用法：setCommission(driver,character='3',carpool='5%',...)，带%号为设置百分比，否则为金额
        :param driver:
        :param kwargs: 可变参数，共支持4个关键字: 【拼车】carpool【多日包车】dayscharacter【包裹】express【包车】character，包车暂统一处理不按车型区分
        :return:
        """
        assert_dict = {}
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/lineCommission.do"]')))
        for k, v in kwargs.items():
            assert isinstance(v, str), '参数值必须为字符串'

            if k == 'carpool':
                if v.find('%') != -1:
                    v = v[:v.find('%')]
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input[name="pinCheRadio"][value="1"]').click()
                    css_percent = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input#pinCheRadio_Text1')
                    css_percent.clear()
                    css_percent.send_keys(v)
                    assert_dict['#pinCheRadio_Text1'] = v
                else:
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input[name="pinCheRadio"][value="2"]').click()
                    css_amount = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input#pinCheRadio_Text2')
                    css_amount.clear()
                    css_amount.send_keys(v)
                    assert_dict['#pinCheRadio_Text2'] = v

            elif k == 'dayscharacter':
                if v.find('%') != -1:
                    v = v[:v.find('%')]
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input[name="duoRiBaoCheRadio"][value="1"]').click()
                    css_percent = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input#duoRiBaoCheRadio_Text1')
                    css_percent.clear()
                    css_percent.send_keys(v)
                    assert_dict['#duoRiBaoCheRadio_Text1'] = v
                else:
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input[name="duoRiBaoCheRadio"][value="2"]').click()
                    css_amount = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input#duoRiBaoCheRadio_Text2')
                    css_amount.clear()
                    css_amount.send_keys(v)
                    assert_dict['#duoRiBaoCheRadio_Text2'] = v

            elif k == 'express':
                if v.find('%') != -1:
                    v = v[:v.find('%')]
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input[name="baoGuoRadio"][value="1"]').click()
                    css_percent = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input#baoGuoRadio_Text1')
                    css_percent.clear()
                    css_percent.send_keys(v)
                    assert_dict['#baoGuoRadio_Text1'] = v
                else:
                    globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input[name="baoGuoRadio"][value="2"]').click()
                    css_amount = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('input#baoGuoRadio_Text2')
                    css_amount.clear()
                    css_amount.send_keys(v)
                    assert_dict['#baoGuoRadio_Text2'] = v

            elif k == 'character':
                if v.find('%') != -1:
                    v = v[:v.find('%')]
                    all_percent_radioes = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('tr>td>input[type="radio"][value="1"]')
                    for i in all_percent_radioes:
                        i.click()
                    css_percents = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('tr>td>input[id$="Text1"]')
                    for i in css_percents:
                        i.clear()
                        i.send_keys(v)
                else:
                    all_amount_radioes = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('tr>td>input[type="radio"][value="2"]')
                    for i in all_amount_radioes:
                        i.click()
                    css_amounts = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('tr>td>input[id$="Text2"]')
                    for i in css_amounts:
                        i.clear()
                        i.send_keys(v)

            else:
                raise TypeError('{} got an unsupport argument-{}'.format('setCommission()', k))
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))
        return assert_dict

    def setCancelTicket(self, *args):
        """
        设置退票手续费。用法：setCancelTicket(driver, （30，30)...)，最多3组元组参数
        :param driver:
        :param args: 每一个参数为一组退票时间和收取手续费组成的元组，（60，20）表示60分钟内，收取20%手续费
        :return:
        """
        index = 0
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=cancelTicketCommissionPage')))
        if len(args) > 3:
            raise IndexError('length of kwargs can not greater than 3')

        all_input_cells = globalvar.GLOBAL_DRIVER.find_elements_by_css_selector('span>input')
        for i in all_input_cells:
            i.clear()

        for i in args:
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#cancelTicketTime' + str(index)).send_keys(i[0])
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#cancelTicketCommission' + str(index)).send_keys(i[1])
            index += 1

        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))

    def setServeTime(self, **kwargs):
        """
        设置服务时间。用法：setServeTime(driver, carpool='10:30-13:30'...)，时间为字符串格式，时分中间有冒号，起止中间有破折号
        :param driver:
        :param kwargs: 可变关键字参数，可接受：all（所有）、carpool（拼车）、character（包车）、express（快递）、plane（接送机），其中all只能单独存在，其它4项一次最多只能取3项
        :return:
        """
        index = 0
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=toSetServeTimesPage"]')))

        if len(kwargs) > 3:
            raise IndexError('length of kwargs can not greater than 3')

        for i in range(3):
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#timeStart' + str(i)).clear()
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#timeEnd' + str(i)).clear()

        for k, v in kwargs.items():
            type_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#serveType' + str(index))
            time_list = v.split('-')
            if k == 'carpool':
                Select(type_sel).select_by_visible_text('城际拼车')
            elif k == 'character':
                Select(type_sel).select_by_visible_text('城际包车')
            elif k == 'express':
                Select(type_sel).select_by_visible_text('跨城闪送')
            elif k == 'all':
                Select(type_sel).select_by_visible_text('=所有=')
            elif k == 'plane':
                Select(type_sel).select_by_visible_text('接送机')
            else:
                raise TypeError('{} got an unsupport argument--{}'.format('setServeTime()', k))
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#timeStart' + str(index)).send_keys(time_list[0])
            globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#timeEnd' + str(index)).send_keys(time_list[1])
            index += 1
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSave').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]')))
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.layui-layer-shade')))

    def setSafePhone(self, province='福建省', city='厦门市', flag=True):
        """
        设置安全号码。用法：setSafePhone(driver, province='福建省', city='厦门市', flag=True)
        :param driver:
        :param province: 字符串，省份名称
        :param city: 字符串，市名称
        :param flag: True为设置安全号码，False为取消设置
        :return:
        """
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=securityNumberPage"]')))

        switch_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#isSafeNumber')
        province_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#bakProvince')
        city_sel = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#bakCity')

        if flag:
            Select(switch_sel).select_by_visible_text('是')
            try:
                globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div>a.layui-layer-btn0'))).click()
            except:
                pass
            WebDriverWait(globalvar.GLOBAL_DRIVER, 3).until(
                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=securityNumberPage"]')))
            Select(province_sel).select_by_visible_text(province)
            sleep(0.5)
            Select(city_sel).select_by_visible_text(city)
        else:
            Select(switch_sel).select_by_visible_text('否')
            Select(province_sel).select_by_visible_text('请选择省份')
            Select(city_sel).select_by_visible_text('请选择城市')

    #    driver.find_element_by_css_selector('#btnSecSave').click()
        globalvar.GLOBAL_DRIVER.execute_script("$('#btnSecSave').click()")

        msg_text = utils.wait_for_laymsg(globalvar.GLOBAL_DRIVER)
        if msg_text != '保存成功':
            log.logger.error(f'保存安全号码设置失败，msg={msg_text}')
            raise IndexError

        globalvar.GLOBAL_DRIVER.switch_to.default_content()
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do"]')))
#        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()  # 此句理论上与上面2句同效果，不知为何此句会有问题
        sleep(1.5)


    def getSafePhone(self):
        WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '[src^="/line.do?method=securityNumberPage"]')))
        safe_dict = {}
        sleep(2)
        issafe_text = globalvar.GLOBAL_DRIVER.execute_script("return $('#isSafeNumber').val()")
        province_text = globalvar.GLOBAL_DRIVER.execute_script("return $('#bakProvince').val()")
        city_text = globalvar.GLOBAL_DRIVER.execute_script("return $('#bakCity').val()")
        safe_dict['isSafe'] = issafe_text
        safe_dict['province'] = province_text
        safe_dict['city'] = city_text
        globalvar.GLOBAL_DRIVER.find_element_by_css_selector('#btnSecCancel').click()
        globalvar.GLOBAL_DRIVER.switch_to.parent_frame()
        sleep(1.5)
        return safe_dict

    def toggleLineStatus(self, line_id, *args):
        """
        设置城际线路开关量
        :param driver:
        :param line_id: 线路ID,比如361000_to_361000
        :param args: 可变参数，可输入【'关闭', '启用', '下线', '上线', '设为人民币', '设为港币', '开启乘客上车确认', '关闭乘客上车确认'】
        :return: 线路状态列表
        """
        line_info_list = []
        self.queryLine(line_num=line_id)
        opera_text = utils.get_opera_text(globalvar.GLOBAL_DRIVER, '.td-opera>a')
        for v in args:
            assert v in ['关闭', '启用', '下线', '上线', '设为人民币', '设为港币', '开启乘客上车确认', '关闭乘客上车确认'], "关键字错误！"
            if v not in opera_text:
                continue

            utils.select_operation_by_attr(globalvar.GLOBAL_DRIVER, '#line_table', '#line_table>tbody>tr', 'data-line-id', line_id, v)
            globalvar.GLOBAL_DRIVER.execute_script("$('#line_table>tbody').html('')")
            if v in ['关闭', '启用', '下线', '上线', '设为人民币', '设为港币']:
                globalvar.GLOBAL_DRIVER.switch_to.default_content()
                WebDriverWait(globalvar.GLOBAL_DRIVER, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[type="dialog"]>div>a.layui-layer-btn0'))).click()
                line_iframe = globalvar.GLOBAL_DRIVER.find_element_by_css_selector('iframe[src="/line.do"]')
                globalvar.GLOBAL_DRIVER.switch_to.frame(line_iframe)
            if argv[1] != 'TEST':
                sleep(3)
            else:
                sleep(1.5)

        we_tds = WebDriverWait(globalvar.GLOBAL_DRIVER, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#line_table>tbody>tr>td')))
        for element in we_tds:
            line_info_list.append(element.text)
        return line_info_list