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
dd1 = 'M:/PhD/P2P/branches/General'
dd2 = 'M:/PhD/P2P/trunk'
os.chdir(dd1)
#from central import Central
from agent import Agent
from new_fun import igather, ibcast, ip2p

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

num = str(size)
os.chdir(dd2)
Pmax = sio.loadmat('/Data'+num+'_Pmax.mat')['Pmax'][:,rank-1]
Pmin = sio.loadmat('/Data'+num+'_Pmin.mat')['Pmin'][:,rank-1]
a = sio.loadmat('/Data'+num+'_a.mat')['a'][:,rank-1]
b = sio.loadmat('/Data'+num+'_b.mat')['b'][:,rank-1]
gamma=sio.loadmat(num+'_gamma.mat')['gamma'][:,rank,:]
n = size
s = 5#a.shape[0]
os.chdir(dd1)
max_iter = 10000
max_time = 20
o = 0.5
e = 10**(-8)
e_p = 10**(-5)
zzz = 0.01
L = [0] #, 1200, 600, 300, 200, 150, 120, 100]
S = [0] #,1,2] # mean = 0, max iter = 1 
eps_max = [0] #, 0.001, 0.002, 0.004, 0.006, 0.008, 0.01]
E=0
for e in eps_max:
    for l in L:
        for strategy in S:
            results = []
            for i in range(s):
                res_time = []      
                x = Agent(a[i], b[i], Pmin[i], Pmax[i], n, o, strategy)
                k=0    
                eps = np.random.uniform(low = -e/2, high=e/2)
                comm.barrier()
                t0 = MPI.Wtime()
                while MPI.Wtime()-t0 < np.random.uniform(high=0.01):
                    sleep=0
                t = MPI.Wtime()
                while MPI.Wtime()-t<max_time: #abs(x.residual)>e and k<max_iter: #(abs(x.residual)>e or x.p_res>e_p) 
                    k += 1
                    t_0 = MPI.Wtime()
                    x.optimize()
                    while MPI.Wtime()-t_0 < zzz+eps:
                        sleep=0
                    t_1 = MPI.Wtime()
                    [x.wait_buf, x.ready_buf] = ip2p(MPI, comm, x.power, x.price, x.stopping, x.remaining_neighbours, x.wait_buf, x.msg_size, t, k, l, 0.01)   
                    [x.wait_buf, x.ready_buf] = igather(MPI, comm, x.power, 0, x.wait_buf, x.msg_size, t, k, l)    
                    t_2 = MPI.Wtime()
                    if rank==0:
                        x.update() #Master
                    t_3 = MPI.Wtime()
                    [x.wait_buf, x.ready_buf] = ibcast(MPI, comm, x.msg, 0, x.wait_buf, x.msg_size, t, k, l)   
                    t_4 = MPI.Wtime()
                    if rank != 0:
                        x.update()
                    t_5 = MPI.Wtime()
                    
                    res_time.append([MPI.Wtime()-t, t_1-t_0+t_3-t_2+t_5-t_4, t_2-t_1+t_4-t_3])
                
                if rank==0:
                    print('save', l, strategy, i)    
                comm.barrier()
                re = False
                j=0
                count=0
                buf = bytearray(1<<20)
                while re == False and j<100:
                    re = comm.Iprobe(source= MPI.ANY_SOURCE, tag = MPI.ANY_TAG)
                    j+=1
                    while re:  # go through the buffer stack
                        count+=1
                        requests = comm.Irecv(buf, MPI.ANY_SOURCE, MPI.ANY_TAG)
                        requests.Cancel() #wait()
                        re = comm.Iprobe(source= MPI.ANY_SOURCE, tag = MPI.ANY_TAG)
            #    print(count)        
                comm.barrier()
                if rank!=0:
                    comm.send(k, dest=0, tag = 555)
                    comm.barrier()
                    comm.send(x.power_memory,dest=0,tag=999)
                    comm.barrier()
                    comm.send(res_time,dest=0,tag=777)
                else:
                    k_ag = np.zeros(n+1)
                    k_ag[rank]=k
                    for j in range(n):
                        k_ag[j+1] = comm.recv(source=j+1, tag = 555)
                    k_max = int(max(k_ag))
                    comm.barrier()
                    Power_to_save = np.zeros((k_max,n))
                    res_time_ag = np.zeros((n,k_max,3))
                    for j in range(n):
#                        temp=np.zeros(k_max)
                        temp = comm.recv(source=j+1, tag = 999)
                        temp2 = np.array(temp)
                        cc = temp2.shape[0]
                        Power_to_save[range(cc),j] = temp2
                    comm.barrier()
                    for j in range(n):
#                        tmp=np.zeros((k_max,3))
                        temp = comm.recv(source=j+1, tag = 777)
                        temp2 = np.array(temp)
                        cc = temp2.shape[0]
                        res_time_ag[j,:,:][range(cc),:] = temp2
                    res = {'Time': res_time, 'Price': np.asarray(x.price_memory), 'Power': Power_to_save, 'Time_agent': res_time_ag}
                    results.append(res)
                del x
                
            if rank == 0:
                res_dict = {'Setup_'+str(i+1) : results[i] for i in range(s)}
                name = 'New_Res_CED_asy_'+str(l)+'_'+str(strategy)+'_'+str(E)
                sio.savemat(name, {name: res_dict})
    E+=1