# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 09:18:07 2017

@author: fmoret
"""

import numpy as np
#import time

class Master:
    def __init__(self, n, o):
        self.num_pros = n
        self.sigma = np.array(o,dtype=np.float64)
        self.sigma_max = o
        self.price = np.array(0.0,dtype=np.float64)
        self.weight = 1/n
        self.Upower = np.ones(n+1)
        self.buf_size = 10
        self.buf_m = np.ones((n+1,self.buf_size),dtype=np.float64)
        self.buf_p = np.ones((self.buf_size,3),dtype=np.float64)
        self.msg_size = 3
        self.msg = np.zeros(self.msg_size,dtype=np.float64)
        self.power = np.array(0.0,dtype=np.float64)
        self.stack = 1000000*np.ones(10)
        self.residual = np.array(1.0,dtype=np.float64)
        self.p_res = 1.0
        self.price_memory = []
            
    def optimize(self):
        return
        
    def update(self):

        #Calculate residulas
        self.residual = np.array(sum(self.Upower),dtype=np.float64)

        if max(abs((self.residual)*np.ones(10)-self.stack))<0.01*abs(self.residual) and self.sigma<self.sigma_max:
            self.sigma = self.sigma*2
            self.stack = 1000000*np.ones(10)
        elif abs(self.residual)-np.mean(self.stack)>0.1*abs(self.residual) and self.sigma>self.sigma_max/1000:
            self.sigma = self.sigma/3
            self.stack = 1000000*np.ones(10)
        elif abs(self.residual-np.mean(self.stack))<0.001*abs(self.residual) and self.sigma>self.sigma_max/1000:
            self.sigma = self.sigma/3
            self.stack = 1000000*np.ones(10)
        self.stack[range(1,10)] = np.copy(self.stack[range(0,9)])
        self.stack[0] = abs(self.residual)
        
        self.price_old = self.price
        #Update price
        self.price = np.array(self.price + self.sigma*self.residual*self.weight,dtype=np.float64)
        self.price_memory.append(self.price) 
        self.msg = np.array([self.price, self.residual, self.sigma], dtype=np.float64)
        self.p_res = abs(self.price-self.price_old)
        
    def clean(self):
        return
