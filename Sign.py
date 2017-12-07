# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 08:05:24 2017
#期货信号接口，包含行情接口
@author: Administrator
"""

#%%导入模块框架
import Functions as fun#自定义函数库  

#%%文件配置

#执行文件参数(可定制)
current_dir='E:/PythonScripts'#当前目录
sign_dir='BlackSign'#信号文件目录,在当前目录下生成
cache_dir='BlackCache'#执行缓存目录,在当前目录下生成

#设置当前目录和生成配置日志文件夹
fun.os.chdir(current_dir)
if not fun.os.path.exists('log'):
    fun.os.makedirs('log')  
    
##日志信息头
fun.printHead('1[sign].SCRIPT SETTING')
fun.printLog('currentdir is: '+current_dir)

#生成需要目录

setting=fun.createdir([sign_dir,cache_dir])
#%%全局变量定义
    
#关注的月份和品种（可定制）

Focus_dates=['1801','1805','1809']#关注的合约月份
Focus_commoditys=['I','J','JM']#关注的商品期货
contracts=[]#合约总数
for Focus_commodity in Focus_commoditys:
    for Focus_date in Focus_dates:
        contracts.append(Focus_commodity+Focus_date)
contracts.extend(['RB1805','RB1810','RB1801'])

#日志信息头
fun.printHead('2[sign].GLOBAL VAR')

today=fun.dt.datetime.now() #获取当前时间
fun.printLog('date is: ' +str(today)[:19])
fun.printLog('focus contracts: ' +str(contracts))            
#%%时间监控

#日志信息头
fun.printHead('3[sign].DEADLINE ALERT')

#检查关注月份的剩余天数：少于30天邮件发送提醒
for Focus_date in Focus_dates:#遍历关注月份
    deadline=fun.dt.datetime.strptime(Focus_date+'10','%y%m%d')
    deadline_detal=deadline-today
    if deadline_detal.days<30:
        alert_info=Focus_date+' deadline is: '+str(deadline_detal.days)+'(less than 30)'
        fun.printLog(alert_info)
        fun.sendEmail('bdml_dyt@outlook.com','dyt520shenghuo',\
              '727379993@qq.com','Alert',alert_info)
    else:
        fun.printLog(Focus_date+' deadline is: '+str(deadline_detal.days))
        
#%%主程序
def main():            
      
    #日志信息头
    fun.printHead('4[sign].SIGN GENERATE')
    
    #更新信号,信号目录下生成信号并缓存最新信号
    Sign_message=fun.generate_sign(contracts,sign_dir,cache_dir)          
    
    #日志信息头 
    fun.printHead('5[sign].SIGN SEND')
    
    #发送信号

    if len(Sign_message)==0:
        fun.printLog('It is time to rest...')
    else:
        fun.sendEmail('bdml_dyt@outlook.com','dyt520shenghuo',\
                  '727379993@qq.com','TradeSign',str(Sign_message))
 
#%%执行程序
if __name__ == '__main__':
    main()
