# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 17:46:06 2017
#定点最高价和最低价缓存
@author: Administrator
"""
#%%导入模块框架
import Functions as fun
#%%文件配置

#设置文件目录
current_dir='E:/PythonScripts'#当前目录
HLCache='HLCache'#定时最高价和最低价缓存
cache_dir='BlackCache'#持仓和最新信号缓存目录

#设置当前目录和生成配置日志文件夹
fun.os.chdir(current_dir)
if not fun.os.path.exists('log'):
    fun.os.makedirs('log')  
    
##日志信息头
fun.printHead('1[HLCache].SCRIPT SETTING')
fun.printLog('currentdir is: '+current_dir)

#生成需要目录
setting=fun.createdir([HLCache,cache_dir])

#%%全局变量定义

#关注的月份和品种（可定制）
contracts=['RB1810','I1809','JM1805']#合约总数，建议大写
contracts_hand={'RB1810':1,'I1809':1,'JM1805':1}#合约手数映射,需要大写


#日志信息头
fun.printHead('2[HLCache].GLOBAL VAR')

today=fun.dt.datetime.now() #获取当前时间
fun.printLog('date is: ' +str(today)[:19])
fun.printLog('focus contracts: ' +str(contracts))  
#%%生成最新的最高价和最低价缓存
HLdict_new={}#高低价新缓存
for contract in contracts:
    current_data=fun.tick(contract.upper())#获取最新实时行情
    high=float(current_data['high'].encode('utf-8'))
    low=float(current_data['low'].encode('utf-8'))
    date=str(current_data['date'].encode('utf-8'))
    HLdict_new[contract]={'date':date,'high':high,'low':low}
#%%判断本地保存
#日志信息头
fun.printHead('3[HLCache].SAVE HLCACHE')
today_str=str(fun.dt.date.today())
if HLdict_new[contracts[0]]['date']==today_str:
    #生成高低价缓存并获取最新高低价缓存
    f=open(cache_dir+'/HLCache.txt','w')
    f.write(str(HLdict_new))
    f.close()
    fun.printLog('HLdict is updated')
else:
    fun.printLog('It is time to rest')
