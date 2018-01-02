# -*- coding: utf-8 -*-
"""
Created on Thu Dec 07 09:02:36 2017
自定义的函数库
@author: Administrator
"""
#%%第三方库
import re
import os#系统操作库
import time#时间处理工具
import datetime as dt#日期时间处理库
import requests#简单易用的HTTP库
import pandas as pd#高效的数据分析库
import smtplib#邮件传输协议
from email.mime.multipart import MIMEMultipart#邮件部件
from email.mime.text import MIMEText#邮件文本

from CTPTrader import *#交易接口
'''
#错误代码映射字典        
Error_dict={110:'Failed to establish a new connection',111:'none data,pleaase check contract',112:'columns from sina has changed',\
            113:'need more data',114:'strategy input error'}
'''
#%%设置
#%%当前目录生成文件夹
#当前目录自动生成日志目录，记录操作
def createdir(create_lt=[]):   
    for filename in create_lt:
        if not os.path.exists(filename):
            os.makedirs(filename)
            printLog("Floder is creating: "+filename)
#%%日志打印函数
#执行日期为索引，同一个执行日期的操作在一个目录下
def printLog(line,file_name='log',date=str(dt.date.today())):
    line=str(line)#强制字符串转化
    print line#打印输出
    f=open(file_name+'/'+date+'.txt','a')#打开文件，添加模式
    f.write(line+'\n')#写入文件
    f.close()#关闭文件
#%%信息头打印函数
def printHead(title):
    printLog('-'*60)
    printLog(title)
    printLog('-'*60)
#%%历史行情下载函数 
def load_his_data(commodity):
    commodity=commodity.upper()#行情下载品种需要大写，强制转换
    #新浪财经期货接口下载数据
    url='http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol='+str(commodity)#请求网址
    try:
        robject = requests.get(url)#获取响应体
    except:
        return 110
    data_json = robject.json()#获取响应体的数据流
    if data_json==None:#数据有无判断
        return 111
    try:#DataFrame对象转换，字段捕获错误
        MarketData=pd.DataFrame(data_json,\
                    columns=['date','open','high','low','close','vol'])
        MarketData.index=MarketData['date']#日期作为索引
    except:
        return 112
    return MarketData
#%%获取实时行情
def tick(commodity):
    commodity=commodity.upper()#行情下载品种需要大写，强制转换
    url_least='http://hq.sinajs.cn/list='+commodity
    least_object = requests.get(url_least)#获取相应体
    least_str=re.findall(r'\"(.*)\"',least_object.text)[0]#匹配字符串
    least_lst=least_str.split(',')[:18]#分割字符串，获取数组
    least_keys=['contract','code','open','high','low','pre_close','buy','sell',\
                'tick','ac_close','pre_ac_close','buy_vol','sell_vol','hold','volume',\
                'exchange_abb','commodity_abb','date']
    least_dict=dict(zip(least_keys,least_lst))
    return least_dict
#%%基于实时行情获取[最新价]
def getLastPrice(commodity,column='tick'):
    tick_data=tick(commodity)
    LastPrice=float(tick_data[column].encode('utf-8'))
    return LastPrice

#%%发送邮件函数
def sendEmail(sender,password,receivers,header,content):
  
    
    printLog('SMTP is waiting...('+str(dt.datetime.now())[:19]+')')
    try:
        smtpObj=smtplib.SMTP('smtp-mail.outlook.com',587)#创建一个SMTP对象
        if smtpObj.ehlo()[0]==250:
            printLog('hello to SMTP')
        if smtpObj.starttls()[0]==220:#开始TLS加密
            printLog('TLS is setting')
    except:
        printLog('try connect fail')
        return
    try:
        login_status=smtpObj.login(sender,password)#登录

        if login_status[0]==235:
            printLog('Login in：'+sender)
       
            
            # 如名字所示： Multipart就是多个部分
            msg = MIMEMultipart()
            msg['Subject'] = header
            msg['From'] = 'Python for DYT'
            msg['To']=receivers

            
            # 下面是文字部分，也就是纯文本
            puretext = MIMEText(content)
            msg.attach(puretext)
            
            error_list=smtpObj.sendmail(sender,receivers,msg.as_string())
            if len(error_list)==0:
                printLog('sen to：'+receivers)
                printLog('datetime: '+str(dt.datetime.now())[:19])
                printLog('content: '+content)
            smtpObj.quit()#断开SMTP服务器
        
    except smtplib.SMTPRecipientsRefused:
        printLog('Recipient refused')
    except smtplib.SMTPAuthenticationError:
        printLog('Auth error')
    except smtplib.SMTPSenderRefused:
        printLog('Sender refused')
    except smtplib.SMTPException,e:
        printLog(e.message)

#%%策略1：SMA(1,30)
def strategy(commodity):
    '''
    参数：品种，可重定义
    返回：返回DataFrame对象，索引为日期，字段为sign
    '''
    MarketData=load_his_data(commodity)
    #计算指标
    N1=1#短周期均线
    N2=30#长周期均线
    MA1=MarketData['close'].rolling(window=N1).mean()#计算MA1
    MA2=MarketData['close'].rolling(window=N2).mean()#计算MA2
    if len(MA1.dropna())==0 or len(MA2.dropna())==0:
        return 113
    
    #生成信号
    SignLog=[]#信号列表
    for i,MA in enumerate(zip(MA1,MA2)):
        if i>=N2-1:#从次日开始
            sign=None
            if MA[0]>MA[1] and MA1[i-1]<MA2[i-1]:
                sign=1
            elif MA[0]<MA[1] and MA1[i-1]>MA2[i-1]:
                sign=-1
            else:
                sign=0
            SignLog.append(sign)#添加到列表
        else:
            SignLog.append(None)
    SignLog_df=pd.DataFrame(SignLog,index=MarketData.index,columns=['sign'])
    
    return SignLog_df 
#%%根据策略生成信号
#获取所有合约的信号字典
def generate_sign(contracts,sign_dir,cache_dir):

    SignData_dict={}#信号数据字典
    for contract in contracts:#遍历关注品种
        try:
            return_result=strategy(contract)#执行信号更新，获取返回
        except:
            return_result=114
        if isinstance(return_result,int):
            printLog(contract+' ErrorCode is: '+str(return_result))#信息报错
        else:
            SignData_dict[contract]=return_result
            printLog( contract+' sign data has updated')
            return_result.to_csv(sign_dir+'/'+contract+'_sign.csv')
        
    #筛选最新的信号组合字典
    Sign_message={}#信号信息字典
    for key in SignData_dict.keys():#遍历信号数据
        if SignData_dict[key].index[-1]==dt.datetime.today().strftime('%Y-%m-%d'):
            Sign_message[key]=SignData_dict[key]['sign'].iloc[-1]
        
    #最新信号打印并保存
    if len(Sign_message)==0:
        printLog('new sign group is: None')
    else:
        printLog('new sign group is:\n '+str(Sign_message))

    #最新信号加入缓存
    f=open(cache_dir+'/new_sign.txt','w')
    f.write(str(Sign_message))  
    f.close() 
    
    return Sign_message
#%%信号下单
def trade_sign_order(trade_sign={},contracts_hand={},holds={}):#根据交易信号下单
    order_send=''#获取下单的综合表单
    if len(trade_sign)==0:
        printLog('no need to trade')
    else: 
        #登录   
        trader = CTPTrader()   #交易接口类赋值给变量
        retLogin = trader.Login()

        if retLogin==0:
            printLog('success to login in')
        else:
            printLog('fail to login in')
            return order_send
            
        #执行信号单
        for key in trade_sign.keys():
            if trade_sign[key]==1:#多信号
                key=key.lower()#下单需要小写，强制转换
                if key in holds.keys():
                    Short=holds[key]['sell']
                else:
                    Short=0
                   
                if Short>0:#存在空单：平仓并多单
                    
                    price=getLastPrice(key.upper(),'sell') 
                    
                    #平
                    retLogin=trader.Login()
                    OrderRef=trader.InsertOrder(key, QL_D_Buy, QL_OF_CloseYesterday,\
                        QL_OPT_LimitPrice,price,Short)
            
                    #开
                    retLogin=trader.Login()
                    OrderRef=trader.InsertOrder(key, QL_D_Buy, QL_OF_Open,\
                        QL_OPT_LimitPrice, price, contracts_hand[key.upper()])
            
        
                    message1=key+',long,close,'+str(Short)+','+\
                        str(getLastPrice(key.upper(),'sell'))+','+\
                        str(dt.datetime.today())[:19]
                    printLog(message1)
                    order_send=order_send+message1+';\n'
                    

                    message2=key+',long,open,'+str(contracts_hand[key.upper()])+','+str(getLastPrice(key.upper(),'sell'))+','+\
                           str(dt.datetime.today())[:19]
                    printLog(message2)
                    order_send=order_send+message2+';\n'
                    
                else :#不存在空单，开多单
                    price=getLastPrice(key.upper(),'sell')
                    #开
                    retLogin=trader.Login()
                    OrderRef=trader.InsertOrder(key, QL_D_Buy, QL_OF_Open,\
                        QL_OPT_LimitPrice,price, contracts_hand[key.upper()])
           
                    message=key+',long,open,'+str(contracts_hand[key.upper()])+','+str(getLastPrice(key.upper(),'sell'))+','+\
                           str(dt.datetime.today())[:19]
                    printLog(message)
                    order_send=order_send+message+';\n'
                    
            elif trade_sign[key]==-1:#空信号
                key=key.lower()#下单需要小写，强制转换
                if key in holds.keys():
                    Long=holds[key]['buy']
                else:
                    Long=0
                if Long>0:#存在多单：平仓并空单
                    price=getLastPrice(key.upper(),'buy')
                    #平
                    retLogin=trader.Login()
                    OrderRef=trader.InsertOrder(key, QL_D_Sell, QL_OF_CloseYesterday,\
                        QL_OPT_LimitPrice,price,Long)
            
                    #开
                    retLogin=trader.Login()
                    OrderRef=trader.InsertOrder(key, QL_D_Sell, QL_OF_Open,\
                        QL_OPT_LimitPrice, price, contracts_hand[key.upper()])
            
                    message1=key+',short,close,'+str(Long)+','+\
                             str(getLastPrice(key.upper(),'buy'))+','+\
                             str(dt.datetime.today())[:19]
                    printLog(message1)
                    order_send=order_send+message1+';\n'

                    message2=key+',short,open,'+str(contracts_hand[key.upper()])+','+str(getLastPrice(key.upper(),'buy'))+','+\
                        str(dt.datetime.today())[:19]
                    printLog(message2)
                    order_send=order_send+message2+';\n'
                else :#不存在多单，开空单
                    price=getLastPrice(key.upper(),'buy')
                    #开
                    retLogin=trader.Login()
                    OrderRef=trader.InsertOrder(key, QL_D_Sell, QL_OF_Open,\
                        QL_OPT_LimitPrice,price,contracts_hand[key.upper()])

                    message=key+',short,open,'+str(contracts_hand[key.upper()])+','+str(getLastPrice(key.upper(),'buy'))+','+\
                        str(dt.datetime.today())[:19]
                    printLog(message)
                    order_send=order_send+message+';\n'
            else:
                printLog('The sign is error,stop trade')
                
    return order_send
#%%更新持仓
def update_holds(trade_log='',holds={}):
    new_holds=holds
    order_group=trade_log.split('\n')
    for order in order_group:
        if not len(order)==0:
            order_lst=order.split(',')
            if order_lst[0] in new_holds.keys():
                if order_lst[1]=='long' and order_lst[2]=='open':
                    new_holds[order_lst[0]]['buy']=\
                    new_holds[order_lst[0]]['buy']+int(order_lst[3])
                elif order_lst[1]=='long' and order_lst[2]=='close':
                    new_holds[order_lst[0]]['sell']=\
                    new_holds[order_lst[0]]['sell']-int(order_lst[3])
                elif order_lst[1]=='short' and order_lst[2]=='open':
                    new_holds[order_lst[0]]['sell']=\
                    new_holds[order_lst[0]]['sell']+int(order_lst[3])
                elif order_lst[1]=='short' and order_lst[2]=='close':
                    new_holds[order_lst[0]]['buy']=\
                    new_holds[order_lst[0]]['buy']-int(order_lst[3])
                else:
                    pass
            else:
                new_holds[order_lst[0]]={'buy':0,'sell':0}
                if order_lst[1]=='long' and order_lst[2]=='open':
                    new_holds[order_lst[0]]['buy']=\
                    new_holds[order_lst[0]]['buy']+int(order_lst[3])
                elif order_lst[1]=='short' and order_lst[2]=='open':
                    new_holds[order_lst[0]]['sell']=\
                    new_holds[order_lst[0]]['sell']+int(order_lst[3])
                else:
                    pass
    return new_holds