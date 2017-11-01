# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 10:59:58 2017

@author: fmoret
"""

    for i in range(s):
        os.chdir(dd2)
        Res_CED = sio.loadmat('Res_CED.mat')[0,0]['Size_'+num][0,0]['Setup_'+str(s)][0,0]
        Res_power = Res_CED['Power']
        Res_price = Res_CED['Price']