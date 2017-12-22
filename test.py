# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 21:20:39 2017
#测试
@author: Administrator
"""
import time
import sys
from CTPTrader import *
trader = CTPTrader()
retLogin = trader.Login()
print retLogin

trader.Login()
trader.InsertOrder('rb1810', QL_D_Buy, QL_OF_Open,\
  QL_OPT_LimitPrice,3500, 1)

trader.Login()
trader.InsertOrder('rb1810', QL_D_Buy, QL_OF_Open,\
  QL_OPT_LimitPrice,3501, 1)


trader.Login()
trader.InsertOrder('i1809', QL_D_Buy, QL_OF_Open,\
  QL_OPT_LimitPrice,502, 1)

