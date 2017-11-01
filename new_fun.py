# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 15:04:54 2017

@author: fmoret
"""
import numpy as np
#import sys

def igather(MPI, comm, data, root, wait_buf, msg_size, t, k, l):
    if comm.rank==root:
        ready_buf = [[] for i in range(comm.size-1)]
        for i in [q for q in range(comm.size) if q != root]:
            re = False
            j=0
            count=0
            buf = wait_buf[i-1]
            while re == False and j<10:
                re = comm.Iprobe(source= i, tag = MPI.ANY_TAG)
                j+=1
                while re:  # go through the buffer stack
                    count+=1
                    temp = np.zeros(msg_size, dtype=np.float64)
                    requests = comm.Irecv([temp,msg_size,MPI.DOUBLE], i, MPI.ANY_TAG)
                    requests.wait()
                    buf.append(temp)
                    re = comm.Iprobe(source= i, tag = MPI.ANY_TAG)
            buf_arr = np.array(buf)
            data_ready = []
            data_wait = []
            for j in range(buf_arr.shape[0]):
                if buf_arr[j,0]>0:
                    if MPI.Wtime()-t > buf_arr[j,0]+buf_arr[j,1]:
                        data_ready.append(buf_arr[j,:])
                    else:
                        data_wait.append(buf_arr[j,:])
            ready_buf[i-1] = data_ready
            wait_buf[i-1] = data_wait
        return [wait_buf,ready_buf]
    else:
        if l==0:
            delay=l
        else:
            delay = np.random.exponential(scale=1/l, size=1)
        msg = np.array([MPI.Wtime()-t, delay, k, data], dtype = np.float64)
        comm.Isend([msg, len(msg), MPI.DOUBLE], root, comm.rank)
        return [wait_buf,[]]

        
        
        
def ibcast(MPI, comm, data, root, wait_buf, msg_size, t, k, l):
    if comm.rank==root:
        for i in [q for q in range(comm.size) if q != root]:
            if l==0:
                delay=l
            else:
                delay = np.random.exponential(scale=1/l, size=1)
            msg = np.append(np.array([MPI.Wtime()-t, delay, k]), data)
            comm.Isend([msg, len(msg), MPI.DOUBLE], i, comm.rank)
        return [wait_buf,[]]
    else:
        re = False
        j=0
        count=0
        while re == False and j<10:
            re = comm.Iprobe(source= root, tag = MPI.ANY_TAG)
            j+=1
            while re:  # go through the buffer stack
                count+=1
                temp = np.zeros(msg_size, dtype=np.float64)
                requests = comm.Irecv([temp,msg_size,MPI.DOUBLE], root, MPI.ANY_TAG)
                requests.wait()
                wait_buf.append(temp)
                re = comm.Iprobe(source= root, tag = MPI.ANY_TAG)
        buf_arr = np.array(wait_buf)
        data_ready = []
        data_wait = []
        for j in range(buf_arr.shape[0]):
            if buf_arr[j,0]>0:
                if MPI.Wtime()-t > buf_arr[j,0]+buf_arr[j,1]:
                    data_ready.append(buf_arr[j,:])
                else:
                    data_wait.append(buf_arr[j,:])
        return [data_wait, data_ready]

    
            
def ip2p(MPI, comm, power, price, stop, neighbours, wait_buf, msg_size, t, k, l, zzz):
    for i in neighbours:
        if l==0:
            delay=l
        else:
            delay = np.random.exponential(scale=1/l, size=1)
        msg = np.array([MPI.Wtime()-t, delay, k, power[i], price[i], stop], dtype=np.float64)
        comm.Isend([msg, len(msg), MPI.DOUBLE], i, 77)
    data_ready = [[] for i in range(len(wait_buf))]
    data_wait = [[] for i in range(len(wait_buf))]
    for i in neighbours:
        re = False
        w = wait_buf[i]
        j=0
        count=0
        while re == False and j<10:
            re = comm.Iprobe(source= i, tag = MPI.ANY_TAG)
            j+=1
            while re:  # go through the buffer stack
                count+=1
                temp = np.zeros(msg_size, dtype=np.float64)
                requests = comm.Irecv([temp,msg_size,MPI.DOUBLE], i, 77)
                requests.wait()
                w.append(temp)
                re = comm.Iprobe(source= i, tag = MPI.ANY_TAG)
        buf_arr = np.array(w)
        for j in range(buf_arr.shape[0]):
            if buf_arr[j,0]>0 and buf_arr[j,4]!=0:
                if MPI.Wtime()-t > buf_arr[j,0]+buf_arr[j,1]:
                    data_ready[i].append(buf_arr[j,:])
                else:
                    data_wait[i].append(buf_arr[j,:])
    return [data_wait, data_ready]