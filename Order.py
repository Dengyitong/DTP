# -*- coding: utf-8 -*-
"""
Created on Wed Dec 06 16:28:28 2017
#黑色系列期货的下单
@author: Administrator
"""

#%%导入模块框架
import Functions as fun
#%%文件配置

#设置文件目录
import os
current_dir='E:/PythonScripts'#当前目录
order_dir='BlackOrder'#下单记录目录
cache_dir='BlackCache'#持仓和最新信号缓存目录


#设置当前目录和生成配置日志文件夹
fun.os.chdir(current_dir)
if not fun.os.path.exists('log'):
    fun.os.makedirs('log')  
    
##日志信息头
fun.printHead('1[order].SCRIPT SETTING')
fun.printLog('currentdir is: '+current_dir)

#生成需要目录
setting=fun.createdir([order_dir,cache_dir])

#生成持仓报告并获取最新持仓
if not fun.os.path.exists(cache_dir+'/holds.txt'):
    f=open(cache_dir+'/holds.txt','w')
    f.write('{}')
    f.close()
f=open(cache_dir+'/holds.txt')
holds=eval(f.read())
f.close()
#%%全局变量定义

#关注的月份和品种（可定制）
'''
Focus_dates=['1805','1809']#关注的合约月份
Focus_commoditys=['I','JM']#关注的商品期货
commoditys_hand={'I':1,'JM':1}#商品期货的交易手数
for Focus_commodity in Focus_commoditys:
    for Focus_date in Focus_dates:
        contract=Focus_commodity+Focus_date
        contracts.append(contract)
        contracts_hand[contract]=commoditys_hand[Focus_commodity]
'''
contracts=['RB1810','I1809']#合约总数，建议大写
contracts_hand={'RB1810':1,'I1809':1}#合约手数映射,需要大写


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

    trade_log=fun.trade_sign_order(trade_sign,contracts_hand,holds)
    
    if not len(trade_log)==0:#不为空，更新下单和持仓，并发送报告到邮箱
        
        #更新下单记录表
        f=open(order_dir+'/'+str(fun.dt.date.today())+'.txt','w')
        f.write(trade_log)
        f.close()
        fun.printHead('orderLog is updated')
        
        #更新持仓报告
        new_holds=fun.update_holds(trade_log,holds)
        f=open(cache_dir+'/holds.txt','w')
        f.write(str(new_holds))
        f.close()
        fun.printHead('holds is updated')
 
#%%执行程序
if __name__ == '__main__':
    main()