

域名操作:
        -s d 选择域名操作

                -a  添加域名

                        python  dnspod.py -s d -a 域名

                -d  删除域名

                        python  dnspod.py -s d -d 域名

                -l  域名日志

                        python  dnspod.py -s d -l 域名

                -i  指定域名详细信息

                        python  dnspod.py -s d -i 域名

                -e -n 启用和暂停

                        python  dnspod.py -s d -n 域名 -e  disable
                        python  dnspod.py -s d -n 域名 -e  ensable

                -k -n 设置域名备注

                        python  dnspod.py -s d -n 域名 -k  备注信息

记录操作:
        -s r 选择记录操作

                记录列表(帮助)
                    python  dnspod.py -s rl

                创建记录(帮助)
                    python  dnspod.py -s rc

                修改记录(帮助)
                    python  dnspod.py -s rm

                删除记录(帮助)
                    python  dnspod.py -s rd

                设置状态(帮助)
                    python  dnspod.py -s rs

                记录备注(帮助)
                    python  dnspod.py -s rk

                记录详细信息(帮助)
                    python  dnspod.py -s ri


    +----------+------------------+------------+------+------+---------------------+
    |   编号   |       域名       |    等级    | 状态 | 记录 |         更新        |
    +----------+------------------+------------+------+------+---------------------+
    | 53997247 |  lofkeji.hk   | 新免费套餐 | 启用 |  5   | 2017-02-09 10:06:42 |
    | 53997157 |  lofkeji.vip  | 新免费套餐 | 启用 |  3   | 2017-02-09 10:01:12 |
    | 51822935 |  cc8890.cn    | 企业创业版 | 启用 | 150  | 2016-12-16 15:03:18 |
    | 51481932 |  lofkeji.me   | 新免费套餐 | 启用 |  9   | 2016-12-09 14:46:30 |
    +----------+------------------+------------+------+------+---------------------+


