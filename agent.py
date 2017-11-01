# Import Gurobi Library
import gurobipy as gb
import numpy as np
#import time

# Optimization class
class Agent:
    def __init__(self, a, b, Pmin, Pmax, n, o):    
        self.Pmin = Pmin
        self.Pmax = Pmax
        self.b = b
        self.a = a
        self.sigma = np.array(o,dtype=np.float64)
#        self.weight = 1/n
        self.p_old = 0.0
        self.price = 0.0
        self.residual = 1.0
        self.buf_size = 10
        self.buf_m = np.ones((n+1,self.buf_size),dtype=np.float64)
        self.buf_p = np.ones((self.buf_size,3),dtype=np.float64)
        self.msg = np.array([self.price, self.residual, self.sigma],dtype=np.float64)
        self.power = np.array(Pmin,dtype=np.float64)
        self.power_memory = []
        self.p_res = 1.0
        self._build_model_()        

       
    def optimize(self):
        self._build_objective_()
        self.model.optimize()
        self.pow_old = self.p.x
        self.power = np.array(self.p.x,dtype=np.float64)
        self.power_memory.append(self.p.x)
        return

    def _build_model_(self):
        self.model = gb.Model()
        self.model.setParam('OutputFlag', False)
        self.p = self.model.addVar(lb=self.Pmin, ub=self.Pmax)
        self.model.update()

    def update(self):
        self.price_old = self.price
        self.price = self.buf_p[0,0]
        self.residual = self.buf_p[0,1]
        self.sigma = self.buf_p[0,2]
        self.p_res = abs(self.price-self.price_old)
        
    def _build_objective_(self):
        m = self.model
        price = self.price
        o = self.sigma
        res = self.weight*(self.residual + self.p - self.p_old)
        self.objective = self.b*self.p + self.a/2*(self.p*self.p) + price*res + o/2000*res*res
        m.setObjective(self.objective)
        m.update()
        
    def clean(self):
        del self.model
