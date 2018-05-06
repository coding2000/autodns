#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Author: mark
'''


import os
import sys
import datetime
import json
import requests
import time
import textwrap
import argparse
import logging
import logging.config
from module.ptable import PrettyTable
from config.config import token, ltop, rl, grade_list, status_list


reload(sys)
sys.setdefaultencoding("utf-8")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def lshow(ltop, al='编号'):
    f = PrettyTable(ltop)
    f.align[al] = "l"
    f.padding_width = 1
    return f


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "default": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": os.path.join(LOG_DIR, LOG_FILE),
            'mode': 'w+',
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 20,
            "encoding": "utf8"
        },
    },

    "root": {
        'handlers': ['default'],
        'level': "INFO",
        'propagate': False
    }
}

logging.config.dictConfig(LOGGING)

class DNSPodException(Exception):
    def __init__(self, status, message, url):
        self.status = status
        self.message = message
        self.url = str(url)


def multry(sum=2):
    def _calltry(func):
        def _call(*args, **kwargs):
            for i in range(sum):
                try:
                    res = func(*args, **kwargs)
                except Exception:
                    if i >= sum - 1:
                        raise DNSPodException('error', u'内部错误：调用失败', '')
                    else:
                        time.sleep(1.5)
                else:
                    time.sleep(0.1)
                    break
            return res
        return _call
    return _calltry


class dnspod(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)

    def api_call(self, api, data):
        if not api or not isinstance(data, dict):
            raise DNSPodException('error', u'内部错误：参数错误', '')

        api = 'https://dnsapi.cn/' + api
        data.update({'login_token': token,
                     'format': 'json', 'lang': 'cn', 'error_on_empty': 'no'})

        self.log.info((api, data))
        results = self.post_data(api, data)
        code = int(results.get('status', {}).get('code', 0))

        if code not in [1, 50]:
            raise DNSPodException(
                'error', results.get(
                    'status', {}).get(
                    'message', u'内部错误：未知错误'), '')
        
        self.log.info((results,code))

        return results

    @multry(5)
    def post_data(self, api, data):
        request = requests.Session()
        response = request.post(
            api,
            data=data,
            timeout=30)
        results = json.loads(response.text)
        return results

dnspod_api = dnspod()

def domainlist(func):
    def get_domainlist(*args, **kwargs):
        _domain_list = []
        dt = lshow(ltop)
        res = func(*args, **kwargs)
        response = dnspod_api.api_call('Domain.List', {})
        for domain in response['domains']:
            _domain_list = str(domain['id']), domain['name'], grade_list[domain['grade']
                                                                         ], status_list[domain['status']], domain['records'], domain['updated_on']
            dt.add_row(_domain_list)
        print dt
        return res
    return get_domainlist


@domainlist
def domainremove(domain):
    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)

    response = dnspod_api.api_call(
        'Domain.Remove', {
            'domain': domain})

    if response['status']['code'] == '1':
        print "删除成功"


@domainlist
def domainstatus(domain, status):
    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)
    if not status:
        raise DNSPodException('error', u'参数错误。', -1)

    dnspod_api.api_call('Domain.Status', {'domain': domain,
                                          'status': status})


@domainlist
def domaininfo(domain):
    _domain_info = []

    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)

    _linfo = [
        "id",
        "name",
        "punycode",
        "grade",
        "grade_title",
        "status",
        "ext_status",
        "records",
        "group_id",
        "is_mark",
        "remark",
        "is_vip",
        "searchengine_push",
        "user_id",
        "created_on",
        "updated_on",
        "ttl",
        "cname_speedup",
        "owner",
    ]
    _dt = lshow(_linfo)

    response = dnspod_api.api_call(
        'Domain.Info', {
            'domain': domain})

    _domain_info = response['domain']['id'], response['domain']['name'], response['domain']['punycode'], response['domain']['grade'], response['domain']['grade_title'], response['domain']['status'], response['domain']['ext_status'], response['domain']['records'], response['domain']['group_id'], response['domain'][
        'is_mark'], response['domain']['remark'], response['domain']['is_vip'], response['domain']['searchengine_push'], response['domain']['user_id'], response['domain']['created_on'], response['domain']['updated_on'], response['domain']['ttl'], response['domain']['cname_speedup'], response['domain']['owner']

    _dt.add_row(_domain_info)

    print _dt


def domainlog(domain):
    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)

    response = dnspod_api.api_call(
        'Domain.Log', {
            'domain': domain})

    for linelog in response['log']:
        print linelog


def domainremark(domain, remark):
    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)

    dnspod_api.api_call(
        'Domain.Remark', {
            'domain': domain,
            'remark': remark})


@domainlist
def recordlist(domain):
    _record_list = []
    sr = lshow(rl)
    response = dnspod_api.api_call('Record.List',
                                   {'domain': domain})

    for record in response['records']:
        _record_list = str(
            record['id']), record['name'], record['value'], record['type'], record['line'], u'启用' if int(
            record['enabled']) else u'暂停', record['mx'], record['ttl']
        sr.add_row(_record_list)

    print sr


def recordcreate(**kwargs):
    domain, sub_domain, type, mx, ttl, line, value = None, None, None, None, None, None, None
    for _name, _value in kwargs.items():
        if _name == 'domain':
            domain = _value
        if _name == 'sub_domain':
            sub_domain = _value
        if _name == 'type':
            type = _value
        if _name == 'mx':
            mx = _value
        if _name == 'ttl':
            ttl = _value
        if _name == 'line':
            line = _value
        if _name == 'value':
            value = _value

    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)
    if not value:
        raise DNSPodException('error', u'参数错误。', -1)
    if not sub_domain:
        sub_domain = '@'
    if not type:
        type = u'A'
    if not mx:
        mx = '10'
    if not ttl:
        ttl = u'600'
    if not line:
        line = u'默认'

    dnspod_api.api_call('Record.Create',
                        {'domain': domain,
                         'sub_domain': sub_domain,
                         'record_type': type,
                         'record_line': line,
                         'value': value,
                         'mx': mx,
                         'ttl': ttl}
                        )
    print "添加成功"
    recordlist(domain)


def recordedit(**kwargs):
    domain, record_id, sub_domain, type, line, value = None, None, None, None, None, None
    modifydict = {}
    for _name, _value in kwargs.items():
        if _name == 'domain':
            domain = _value
        if _name == 'sub_domain':
            sub_domain = _value
        if _name == 'type':
            type = _value
        if _name == 'line':
            line = _value
        if _name == 'record_id':
            record_id = _value
        if _name == 'value':
            value = _value
        if _name == 'type':
            _name = 'record_type'
        if _name == 'line':
            _name = 'record_line'
        if _value:
            modifydict[_name] = _value

    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)
    if not sub_domain:
        raise DNSPodException('error', u'参数错误。', -1)
    if not record_id:
        raise DNSPodException('error', u'参数错误。', -1)
    if not value:
        raise DNSPodException('error', u'参数错误。', -1)
    if not type:
        raise DNSPodException('error', u'参数错误。', -1)
    if not line:
        raise DNSPodException('error', u'参数错误。', -1)

    dnspod_api.api_call('Record.Modify', modifydict)
    print "修改成功"
    recordlist(domain)


def recordremove(**kwargs):
    domain, record_id = None, None
    for _name, _value in kwargs.items():
        if _name == 'domain':
            domain = _value
        if _name == 'record_id':
            record_id = _value

    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)
    if not record_id:
        raise DNSPodException('error', u'参数错误。', -1)

    dnspod_api.api_call('Record.Remove',
                        {'domain': domain,
                         'record_id': record_id}
                        )

    print "删除成功"
    recordlist(domain)


def recordeditf(**kwargs):
    _record_info = []
    _infotop = [
        'id',
        'sub_domain',
        'record_type',
        'record_line',
        'record_line_id',
        'value',
        'weight',
        'mx',
        'ttl',
        'enabled',
        'remark',
        'updated_on',
        'domain_id']

    domain, record_id = None, None
    for _name, _value in kwargs.items():
        if _name == 'domain':
            domain = _value
        if _name == 'record_id':
            record_id = _value

    record = dnspod_api.api_call('Record.Info', {'domain': domain,
                                                 'record_id': record_id})

    _info = lshow(_infotop, al='id')

    _record_info = record['record']['id'], record['record']['sub_domain'], record['record']['record_type'], record['record']['record_line'], record['record']['record_line_id'], record['record']['value'], record['record'][
        'weight'], record['record']['mx'], record['record']['ttl'], u'启用' if int(record['record']['enabled']) else u'暂停', record['record']['remark'], record['record']['updated_on'], record['record']['domain_id']

    _info.add_row(_record_info)

    print _info


def recordstatus(**kwargs):
    domain, record_id, status = None, None, None
    for _name, _value in kwargs.items():
        if _name == 'domain':
            domain = _value
        if _name == 'record_id':
            record_id = _value
        if _name == 'status':
            status = _value

    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)
    if not record_id:
        raise DNSPodException('error', u'参数错误。', -1)
    if not status:
        raise DNSPodException('error', u'参数错误。', -1)

    dnspod_api.api_call('Record.Status',
                        {'domain': domain,
                         'record_id': record_id,
                         'status': status}
                        )

    recordlist(domain)


def recordremark(**kwargs):
    domain, record_id, remark = None, None, None
    for _name, _value in kwargs.items():
        if _name == 'domain':
            domain = _value
        if _name == 'record_id':
            record_id = _value
        if _name == 'remark':
            remark = _value

    if not domain:
        raise DNSPodException('error', u'参数错误。', -1)
    if not record_id:
        raise DNSPodException('error', u'参数错误。', -1)
    if not remark:
        raise DNSPodException('error', u'参数错误。', -1)

    dnspod_api.api_call('Record.Remark',
                        {'domain': domain,
                         'record_id': record_id,
                         'remark': remark}
                        )

    print "备注成功"


@domainlist
def domaincreate(domain):
    dnspod_api.api_call(
        'Domain.Create', {
            'domain': domain})


@domainlist
def domainall():
    pass


def usage():
    print textwrap.dedent(
            """
域名操作:
        -s d 选择域名操作

                -a  添加域名

                        python  {0} -s d -a 域名

                -d  删除域名

                        python  {0} -s d -d 域名

                -l  域名日志

                        python  {0} -s d -l 域名

                -i  指定域名详细信息

                        python  {0} -s d -i 域名

                -e -n 启用和暂停

                        python  {0} -s d -n 域名 -e  disable
                        python  {0} -s d -n 域名 -e  ensable

                -k -n 设置域名备注

                        python  {0} -s d -n 域名 -k  备注信息

记录操作:
        -s r 选择记录操作

                记录列表(帮助)
                    python  {0} -s rl

                创建记录(帮助)
                    python  {0} -s rc

                修改记录(帮助)
                    python  {0} -s rm

                删除记录(帮助)
                    python  {0} -s rd

                设置状态(帮助)
                    python  {0} -s rs

                记录备注(帮助)
                    python  {0} -s rk

                记录详细信息(帮助)
                    python  {0} -s ri

	   """.format(sys.argv[0]))


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--select', dest='select', help='选择操作')
    parser.add_argument('-a', '--add', dest='add', help='添加')
    parser.add_argument('-k', '--remark', dest='remark', help='备注信息')
    parser.add_argument('-e', '--able', dest='able', help='启用或暂停')
    parser.add_argument('-d', '--delete', dest='delete', help='删除')
    parser.add_argument('-l', '--log', dest='log', help='域名日志')
    parser.add_argument('-m', '--modify', dest='modify', help='修改')
    parser.add_argument('-i', '--info', dest='info', help='详细信息')
    parser.add_argument('-n', '-name', '--domain', dest='domain', help='域名')
    parser.add_argument('-v', '--value', dest='value', help='记录值')
    parser.add_argument('-sub', '--sub_domain', dest='sub_domain', help='主机记录')
    parser.add_argument('-t', '--type', dest='type', help='记录类型')
    parser.add_argument('-mx', '--mx', dest='mx', help='MX优先级')
    parser.add_argument('-ttl', '--ttl', dest='ttl', help='TTL')
    parser.add_argument('-line', '--line', dest='line', help='记录线路')
    parser.add_argument('-rid', '--record_id', dest='record_id', help='记录ID编号')

    args = parser.parse_args()
    return (args.select, args.add, args.remark, args.able,
            args.delete, args.log, args.modify, args.info, args.domain, args.value,
            args.sub_domain, args.type, args.mx, args.ttl, args.line, args.record_id)


optdomain = {
    '1': lambda domain: domaincreate(domain),
    '2': lambda domain: domainremove(domain),
    '3': lambda domain, status: domainstatus(domain, status),
    '4': lambda domain: domaininfo(domain),
    '5': lambda domain: domainlog(domain),
    '6': lambda domain, remark: domainremark(domain, remark)}


def main():
    select, add, remark, able, delete, log, modify, info, domain, value, sub_domain, type, mx, ttl, line, record_id = getargs()

    if select == 'd' or select == 'domain':
        print "域名操作"
        if add:
            optdomain['1'](add)
        if delete:
            optdomain['2'](delete)
        if domain and able:
            optdomain['3'](domain, able)
        if info:
            optdomain['4'](info)
        if log:
            optdomain['5'](log)
        if domain and remark:
            optdomain['6'](domain, remark)
            optdomain['4'](domain)
        if len(sys.argv) < 4:
            print textwrap.dedent(
                """
                操作命令：

                    -a  添加域名

                            python  {0} -s d -a 域名

                    -d  删除域名

                            python  {0} -s d -d 域名

                    -l  域名日志

                            python  {0} -s d -l 域名

                    -i  指定域名详细信息

                            python  {0} -s d -i 域名

                    -e -n 启用和暂停

                            python  {0} -s d -n 域名 -e  disable
                            python  {0} -s d -n 域名 -e  ensable

                    -k -n 设置域名备注

                            python  {0} -s d -n 域名 -k  备注信息


                """.format(sys.argv[0])
            )
            domainall()

    if select == 'r' or select == 'record':
        print "记录操作"
        if len(sys.argv) < 4:
            print textwrap.dedent(
                """
                操作命令(帮助)：
                    记录列表:
                        python  {0} -s rl

                    创建记录
                        python  {0} -s rc

                    修改记录
                        python  {0} -s rm

                    删除记录
                        python  {0} -s rd

                    设置状态
                        python  {0} -s rs

                    记录备注
                        python  {0} -s rk

                    记录详细信息
                        python  {0} -s ri

                """.format(sys.argv[0])
            )
            domainall()
    if select == 'rl':
        print "记录列表"
        if domain:
            recordlist(domain)
            print textwrap.dedent(
                """
            帮助：
                记录列表: -s rl
                创建记录: -s rc
                修改记录: -s rm
                删除记录: -s rd
                设置状态: -s rs
                记录备注: -s rk
                记录详细信息: -s ri
            """
            )
        else:
            print textwrap.dedent(
                """
                操作命令：
                        python  {0} -s rl -n 域名
                    如：
                        python  {0} -s rl -n cc8890.cn

                """.format(sys.argv[0])
            )
        if not domain:
            domainall()

    if select == 'rc':
        print "记录创建"
        if domain and value:
            if not record_id:
                recordcreate(
                    domain=domain,
                    value=value,
                    sub_domain=sub_domain,
                    type=type,
                    mx=mx,
                    ttl=ttl,
                    line=line)
            print textwrap.dedent(
                """
            帮助：
                记录列表: -s rl
                创建记录: -s rc
                修改记录: -s rm
                删除记录: -s rd
                设置状态: -s rs
                记录备注: -s rk
                记录详细信息: -s ri
            """
            )
        else:
            print textwrap.dedent(
                """
                操作命令：
                        python  {0} -s rc -n 域名 -v 记录值
                    如：
                        python  {0} -s rc -n cc8890.cn -v 192.168.0.1

                """.format(sys.argv[0])
            )
        if domain and not value:
            recordlist(domain)
        if not domain:
            domainall()

    if select == 'rm':
        print "修改记录"
        if domain and record_id and value:
            recordedit(
                domain=domain,
                record_id=record_id,
                value=value,
                sub_domain=sub_domain,
                type=type,
                mx=mx,
                ttl=ttl,
                line=line)
            print textwrap.dedent(
                """
            帮助：
                记录列表: -s rl
                创建记录: -s rc
                修改记录: -s rm
                删除记录: -s rd
                设置状态: -s rs
                记录备注: -s rk
                记录详细信息: -s ri
            """
            )
        else:
            print textwrap.dedent(
                """
                操作命令：

                    编号

                        python {0} -s rm -n 域名

                    操作命令

                        必选
                        python  {0} -s rm -n 域名 -rid 编号 -t 类型 -v  -line 线路 -sub 二级域名

                        设置ttl必须大于(600)
                        python  {0} -s rm -n 域名 -rid 编号 -t 类型 -v  -line 线路 -sub 二级域名 -ttl TTL

                    如：
                        python  {0} -s rm -n cc8890.cn -rid 344885490 -t A -v 192.168.0.3 -line 默认 -sub @
                        python  {0} -s rm -n cc8890.cn -rid 344885490 -t A -v 192.168.0.3 -line 默认 -sub www -ttl 600

                """.format(sys.argv[0])
            )
            print('*' * 50)
            print " Must input args {域名,编号,类型,记录值,线路,MX} "
            print('*' * 50)

        if domain and not value:
            recordlist(domain)
        if not domain:
            domainall()

    if select == 'rd':
        print "删除记录"
        if domain and record_id:
            recordremove(domain=domain, record_id=record_id)
            print textwrap.dedent(
                """
            帮助：
                记录列表: -s rl
                创建记录: -s rc
                修改记录: -s rm
                删除记录: -s rd
                设置状态: -s rs
                记录备注: -s rk
                记录详细信息: -s ri
            """
            )
        else:
            print textwrap.dedent(
                """
                操作命令：
                        python {0} -s rd -n 域名 -rid 编号
                    如:
                        python {0} -s rd -n cc8890.cn -rid 编号

                """.format(sys.argv[0])
            )
        if domain and not record_id:
            recordlist(domain)
        if not domain:
            domainall()
    if select == 'ri':
        print "记录详情信息"
        if domain and record_id:
            recordeditf(domain=domain, record_id=record_id)
            print textwrap.dedent(
                """
            帮助：
                记录列表: -s rl
                创建记录: -s rc
                修改记录: -s rm
                删除记录: -s rd
                设置状态: -s rs
                记录备注: -s rk
                记录详细信息: -s ri
            """
            )
        else:
            print textwrap.dedent(
                """
                操作命令：

                    编号:

                        python {0} -s ri -n 域名

                    操作:

                        python {0} -s ri -n 域名 -rid 编号

                    如:
                        python {0} -s ri -n cc8890.cn -rid 编号

                """.format(sys.argv[0])
            )
        if domain and not record_id:
            recordlist(domain)
        if not domain:
            domainall()

    if select == 'rs':
        print "设置记录的状态"
        if domain and record_id and able:
            recordstatus(domain=domain, record_id=record_id, status=able)
            print textwrap.dedent(
                """
            帮助：
                记录列表: -s rl
                创建记录: -s rc
                修改记录: -s rm
                删除记录: -s rd
                设置状态: -s rs
                记录备注: -s rk
                记录详细信息: -s ri
            """
            )
        else:
            print textwrap.dedent(
                """
                操作命令：

                    编号:

                        python {0} -s rs -n 域名

                    操作:

                        python {0} -s rs -n 域名 -rid 编号 -e disable
                        python {0} -s rs -n 域名 -rid 编号 -e enable

                    如:
                        python {0} -s rs -n cc8890.cn -rid 编号 -e disable
                        python {0} -s rs -n cc8890.cn -rid 编号 -e enable

                """.format(sys.argv[0])
            )
        if domain and not record_id:
            recordlist(domain)
        if not domain:
            domainall()

    if select == 'rk':
        print "设置记录备注"

        if domain and record_id and remark:
            recordremark(domain=domain, record_id=record_id, remark=remark)
            recordeditf(domain=domain, record_id=record_id)
            print textwrap.dedent(
                """
            帮助：
                记录列表: -s rl
                创建记录: -s rc
                修改记录: -s rm
                删除记录: -s rd
                设置状态: -s rs
                记录备注: -s rk
                记录详细信息: -s ri
            """
            )
        else:
            print textwrap.dedent(
                """
                操作命令：

                    编号:

                        python {0} -s rk -n 域名

                    操作:

                        python {0} -s rk -n 域名 -rid 编号 -k 备注信息

                    如:
                        python {0} -s rk -n cc8890.cn -rid 编号 -k备注信息

                """.format(sys.argv[0])
            )
        if domain and not remark:
            recordlist(domain)
        if not domain:
            domainall()

    if len(sys.argv) < 2:
        usage()
        domainall()


if __name__ == '__main__':
    main()
