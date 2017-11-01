# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 09:10:49 2017

@author: fmoret
"""

#import time
from mpi4py import MPI
import os
import numpy as np
import scipy.io as sio
dd1 = '/zhome/81/d/95321/PSCC/CED'
dd2 = '/zhome/81/d/95321/PSCC/Data'
os.chdir(dd1)
from master import Master
from pros import Pros

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

num = str(size-1)
os.chdir(dd2)
Pmax = sio.loadmat(num+'_Pmax.mat')['Pmax'][:,rank-1]
Pmin = sio.loadmat(num+'_Pmin.mat')['Pmin'][:,rank-1]
a = sio.loadmat(num+'_a.mat')['a'][:,rank-1]
b = sio.loadmat(num+'_b.mat')['b'][:,rank-1]
n = size-1
s = a.shape[0]
os.chdir(dd1)
max_iter = 5000
o = 0.5
e = 0.00001
e_p = 0.001

results = []
for i in range(s):
    res_time = []      
    if rank==0:
        x = Master(n, o)
    else:
        x = Pros(a[i], b[i], Pmin[i], Pmax[i], n, o)
    k=0    
    t = MPI.Wtime()
    while abs(x.residual)>e and k<max_iter: #(abs(x.residual)>e or x.p_res>e_p)
        k += 1
        t_0 = MPI.Wtime()
        x.optimize()
        t_1 = MPI.Wtime()
        x.Upower = comm.gather(x.power, root=0)    
        t_2 = MPI.Wtime()
        if rank==0:
            x.update() #Master
        t_3 = MPI.Wtime()
        x.price = comm.bcast(x.price,root=0)
        x.residual = comm.bcast(x.residual, root=0)
        x.sigma = comm.bcast(x.sigma, root=0)
        t_4 = MPI.Wtime()
        if rank==0 or rank==size-1:
            res_time.append([MPI.Wtime()-t, t_1-t_0+t_3-t_2, t_2-t_1+t_4-t_3])
    
        
    comm.Barrier()
    if rank!=0:
        comm.Send(np.asarray(x.power_memory),dest=0,tag=rank)
        if rank==size-1:
            comm.Send(np.asarray(res_time),dest=0,tag=999)
    else:
        Power_to_save = np.zeros((k,n))
        for j in range(n):
            temp=np.zeros(k)
            comm.Recv(temp, source=j+1, tag = j+1)
            Power_to_save[:,j] = temp
        tmp=np.zeros((k,3))
        comm.Recv(tmp, source=size-1, tag = 999)
        res_time_ag = tmp
        res = {'Time': res_time, 'Price': np.asarray(x.price_memory), 'Power': Power_to_save, 'Time_agent': res_time_ag}
        results.append(res)
    x.clean()
    
if rank == 0:
    res_dict = {'Setup_'+str(i+1) : results[i] for i in range(s)}
    name = 'Res_CED_'+num
    sio.savemat(name, {name: res_dict})