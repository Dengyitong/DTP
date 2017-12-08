# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 16:28:28 2017
#黑色系列期货的下单
@author: Administrator
"""
#%%导入模块框架
import Functions as fun
#%%文件配置

#设置当前目录
import os
current_dir='E:/PythonScripts'
order_dir='BlackOrder'
cache_dir='BlackCache'


#设置当前目录和生成配置日志文件夹
fun.os.chdir(current_dir)
if not fun.os.path.exists('log'):
    fun.os.makedirs('log')  
    
##日志信息头
fun.printHead('1[order].SCRIPT SETTING')
fun.printLog('currentdir is: '+current_dir)

#生成需要目录

setting=fun.createdir([order_dir,cache_dir])
#%%全局变量定义

#关注的月份和品种（可定制）
Focus_dates=['1805']#关注的合约月份
Focus_commoditys=['I','JM']#关注的商品期货
commoditys_hand={'I':1,'JM':1}#商品期货的交易手数
contracts=[]#合约总数
contracts_hand={}#合约手数映射
for Focus_commodity in Focus_commoditys:
    for Focus_date in Focus_dates:
        contract=Focus_commodity+Focus_date
        contracts.append(contract)
        contracts_hand[contract]=commoditys_hand[Focus_commodity]

contracts.extend(['RB1805','RB1810'])
contracts_hand['RB1805']=1
contracts_hand['RB1810']=1

#日志信息头
fun.printHead('2[order].GLOBAL VAR')

today=fun.dt.datetime.now() #获取当前时间
fun.printLog('date is: ' +str(today)[:19])
fun.printLog('focus contracts: ' +str(contracts))         
#%%主程序
def main():
    
    #日志信息头
    fun.printHead('3[order].SIGN LOAD')
    
    #读取最新信号缓存
    f=open(cache_dir+'/new_sign.txt')
    new_signs=eval(f.read())#读取今日信号,转换为字典
    f.close()
    
    #信号信息打印
    fun.printLog('new sign is: '+str(new_signs))
    new_keys=set(contracts)&set(new_signs.keys())#可以进行交易的合约：有信号和关注
    trade_sign={k:v for k,v in new_signs.items() if k in new_keys and v !=0}#最终交易信号
    fun.printLog('trade sign is: None' if len(trade_sign)==0 else 'trade sign is: '+str(trade_sign))
    
    #信号下单
    #日志信息头
    fun.printHead('4[order].SIGN ORDER')

    trade_log=fun.trade_sign_order(trade_sign,contracts_hand)
    if not len(trade_log)==0:#不为空，发送下单报告到邮箱
        f=open(order_dir+'/'+str(fun.dt.date.today())+'.txt','a')
        f.write(trade_log)
        f.close()
        fun.sendEmail('bdml_dyt@outlook.com','dyt520shenghuo',\
        '727379993@qq.com','OrderLog',str(trade_log))
 
#%%执行程序
if __name__ == '__main__':
    main()