# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 21:16:29 2017
#发送最后的下单报告到邮箱
@author: Administrator
"""
#%%导入模块框架
import Functions as fun
#%%文件配置

#设置文件目录
import os
current_dir='E:/PythonScripts'#当前目录
order_dir='BlackOrder'#下单记录目录


#设置当前目录和生成配置日志文件夹
fun.os.chdir(current_dir)
if not fun.os.path.exists('log'):
    fun.os.makedirs('log')  


##日志信息头
fun.printHead('1[send].SCRIPT SETTING')
fun.printLog('currentdir is: '+current_dir)

#获取最新下单，发送当日持仓报告
if fun.os.path.exists(order_dir+'/'+str(fun.dt.date.today())+'.txt'):
    f=open(order_dir+'/'+str(fun.dt.date.today())+'.txt')
    orderLog=f.read()
    f.close()
    fun.sendEmail('bdml_dyt@outlook.com','dyt520shenghuo',\
                  '727379993@qq.com','Order',orderLog)
    fun.printLog('new orderLog is send')
else:
    fun.printLog('have no new orderLog')
