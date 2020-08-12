import matplotlib.pyplot as plt

import math
import sys
import turtle
import string


processor_param=[{'f':0.36,'v':1},{'f':0.56,'v':2},{'f':0.72,'v':3},{'f':0.89,'v':4},{'f':0.97,'v':5}]

#Define Read File    
def readFile(filename):
    T=[]
    with open(filename) as fp:  
        cnt = 1
        line = fp.readline()
        while line:
            temp=(line.replace('\t','\n')).split('\n')
            T.append({'n':cnt,'p':float(temp[0]),'w':float(temp[1]),'e':float(temp[2]),'c':float(temp[2]),'s':0,'i':1})
            line = fp.readline()
            cnt+=1
        return T
#End Read File

#Define print tasks
def printtasks(T):
    for x in T:
        print("Tasks:\t{}\tInstance:{}\t[p:{}\tw:{}\te:{}]".format(x['n'],x['i'],x['p'],x['w'],x['c']))
    print("\n")
#End Print Tasks

# Define EDF test function
def EDF_Test(alpha,T):
    U=0
    for x in T:
       U+= (x['w'])/(x['p'])
    if (U<=alpha):
        return True
    else:
        return False
# End EDF tests

#Define Select Frequency Function
# this assumes the parameters are already sorted w.r.t frequency
def select_Freq(param,T):
    maxf=param[len(param)-1]['f']
    for x in param:
        if EDF_Test((x['f']/maxf),T):
            return x
    return -1
#returns -1 if not schedulable
#End the function

#defined function to append all the instances of a task
#num is the number instances
def append_Instances(T,V):
    Vdd=5
    I=[]
    maxp=max(T,key=lambda k:k['p'])['p']
    period=0
    for x in T:
        period=2*x['p']
        start=x['p']
        i=2
        #print(period)
        while(start<=maxp):
            I.append({'n':x['n'],'p':period,'w':x['w'],'e':x['e'],'s':period-x['p'],'i':i,'c':(Vdd/V)*x['e']})
            start+=x['p']
            period+=x['p']
            i+=1
    return sorted(I,key=lambda k:k['s'])
#End the append function


##define the function for normal EDF scheduling without voltage scaling
#function plots the voltage vs time plot showing which task is running
def EDF_Schedule(T):
    plotX=[]
    plotY=[]
    final_time=0
    Vdd=5
    prevtask=0
    gain=1000
    stoptime=gain*math.ceil((max(T,key=lambda k:k['p'])['p']+max(T,key=lambda k:k['w'])['w']+1))
    stepsize=1
    task_copy=append_Instances(T,5)
    #printtask(task_copy)
    if EDF_Test(1,T):
        print("Voltage Level : 5V")
        for a in T:
            plt.arrow(a['p'],2,0,0-1.7,color='tomato',head_width=0.15)
        plt.arrow(T[0]['s'],0,0,2,color='skyblue',head_width=0.15)
        for a in task_copy:
            plt.arrow(a['p'],2,0,0-1.7,color='tomato',head_width=0.15)
            plt.arrow(a['s'],0,0,2,color='skyblue',head_width=0.15)
        queue=sorted(T,key=lambda k:k['p'])
        #printtask(queue)
        plt.text(0,Vdd,"T"+str(queue[0]['n']),fontsize=8)
        #plt.text(0,Vdd-0.1,"Instance :"+str(queue[0]['i']),fontsize=8)    
        print("At time:0.0\tTask:{}\tInstance:{}\treleased".format(queue[0]['n'],queue[0]['i']))
        plotX.append(0)
        plotY.append(Vdd)
        for current_time in range(0,stoptime,stepsize):
            time=current_time/gain
            if (len(queue)!=0):
                if (queue[0]['c']>0):
                    queue[0]['c']=queue[0]['c']-(stepsize/gain)
                    plotX.append(time)
                    plotY.append(Vdd)
                    #print(time)
                else:
                    print("At time:{}\tTask:{}\tInstance:{}\tCompleted".format(time,queue[0]['n'],queue[0]['i']))
                    plotX.append(time)
                    plotY.append(0)
                    final_time=time
                    if(queue[0]['i']!=1):
                        for z in task_copy:
                            if (queue[0]['n']==z['n']) and (queue[0]['i']==z['i']):
                                task_copy.remove(z) 
                    del queue[0]
                    if(len(queue)!=0):
                        print("At time:{}\tTask:{}\tInstance:{}\treleased".format(time,queue[0]['n'],queue[0]['i']))
                        plt.text(time,Vdd,"T"+str(queue[0]['n']),fontsize=8)
                        #plt.text(time,Vdd-0.1,"Instance :"+str(queue[0]['i']),fontsize=8)
                        plotX.append(time)
                        plotY.append(Vdd)
            if len(task_copy)!=0:
                if taskstart(task_copy,time):
                    if len(queue)!=0:
                        print("At time:{}\tTask:{}\tInstance:{}\tPreempted".format(time,queue[0]['n'],queue[0]['i']))
                        prevtask=queue[0]['n']
                        #plt.text(time,Vdd,"Task :"+str(queue[0]['n']),fontsize=8)
                        #plt.text(time,Vdd-0.1,"Instance :"+str(queue[0]['i']),fontsize=8)
                    for e in task_copy:
                        if (e['s']==time):
                            queue.append(e)
                    #if (prevtask!=queue[0]['n']):
                    queue=sorted(queue,key=lambda k:k['p'])
                    print("At time:{}\tTask:{}\tInstance:{}\treleased".format(time,queue[0]['n'],queue[0]['i']))
                    plt.text(time,Vdd,"T"+str(queue[0]['n']),fontsize=8)
                    #plt.text(time,Vdd-0.1,"Instance :"+str(queue[0]['i']),fontsize=8)
                    plotX.append(time)
                    plotY.append(0)
                    plotX.append(time)
                    plotY.append(Vdd)
        plt.xlabel('Time')
        plt.ylabel('Voltage')
        plt.title('EDF Scheduling')
        lineedf=plt.plot(plotX,plotY,color='black',linewidth=0.5)
        plt.axis([0,final_time,0,6])
        print("\nEDF Engergy Consumed: 1\n")
    else:
        print("The Given Task Set are not Schedulable with EDF")
#End the EDF schedule Function

#function finds if any task in the list if started at time
def taskstart(T,time):
    for x in T:
        if x['s']==time:
            return True
    return False
#End of the taskstart function


##define the function for Static Voltage Scaling EDF scheduling without voltage scaling
#function plots the voltage vs time plot showing which task is running at static voltage
def Static_EDF_Schedule(param,T):
    plotX=[]
    plotY=[]
    final_time=0
    Vdd=5
    prevtask=0
    gain=1000
    stoptime=gain*math.ceil((max(T,key=lambda k:k['p'])['p']+max(T,key=lambda k:k['w'])['w']+1))
    stepsize=1
    #printtask(task_copy)
    if select_Freq(param,T)!=-1:
        V=select_Freq(param,T)['v']
        for i in range(0,len(T)):
            T[i]['c']=(Vdd/V)*T[i]['e']
        task_copy=append_Instances(T,V)
        print("Voltage Level : {}V".format(V))
        for a in T:
            plt.arrow(a['p'],2,0,0-1.7,color='tomato',head_width=0.15)
        plt.arrow(T[0]['s'],0,0,2,color='skyblue',head_width=0.15)
        for a in task_copy:
            plt.arrow(a['p'],2,0,0-1.7,color='tomato',head_width=0.15)
            plt.arrow(a['s'],0,0,2,color='skyblue',head_width=0.15)
        queue=sorted(T,key=lambda k:k['p'])
        plt.text(0,V,"T"+str(queue[0]['n']),fontsize=8)
        print("At time:0.0\tTask:{}\tInstance:{}\treleased".format(queue[0]['n'],queue[0]['i']))
        plotX.append(0)
        plotY.append(V)
        for current_time in range(0,stoptime,stepsize):
            time=current_time/gain
            if (len(queue)!=0):
                if (queue[0]['c']>0):
                    queue[0]['c']=((queue[0]['c'])-(stepsize/gain))
                    plotX.append(time)
                    plotY.append(V)
                    #print(time)
                else:
                    print("At time:{}\tTask:{}\tInstance:{}\tcompleted".format(time,queue[0]['n'],queue[0]['i']))
                    plotX.append(time)
                    plotY.append(0)
                    final_time=time
                    if(queue[0]['i']!=1):
                        for z in task_copy:
                            if (queue[0]['n']==z['n']) and (queue[0]['i']==z['i']):
                                task_copy.remove(z)
                    del queue[0]
                    if(len(queue)!=0):
                        print("At time:{}\tTask:{}\tInstance:{}\treleased".format(time,queue[0]['n'],queue[0]['i']))
                        plt.text(time,V,"T"+str(queue[0]['n']),fontsize=8)
                        plotX.append(time)
                        plotY.append(V)
            if len(task_copy)!=0:
                
                if taskstart(task_copy,time):
                    #printtasks(task_copy)
                    if len(queue)!=0:
                        print("At time:{}\tTask:{}\tInstance:{}\tPreempted".format(time,queue[0]['n'],queue[0]['i']))
                        prevtask=queue[0]['n']
                        #plt.text(time,V,"Task :"+str(queue[0]['n']),fontsize=8)
                    for e in task_copy:
                        if (e['s']==time):
                            queue.append(e)
                    #if (prevtask!=queue[0]['n']):
                    queue=sorted(queue,key=lambda k:k['p'])
                    print("At time:{}\tTask:{}\tInstance:{}\treleased".format(time,queue[0]['n'],queue[0]['i']))
                    plt.text(time,V,"T"+str(queue[0]['n']),fontsize=8)
                    plotX.append(time)
                    plotY.append(0)
                    plotX.append(time)
                    plotY.append(V)
        plt.xlabel('Time')
        plt.ylabel('Voltage')
        plt.title('Static Voltage Scaling EDF Scheduling')
        linestaticedf=plt.plot(plotX,plotY,color='black',linewidth=0.5)
        plt.axis([0,final_time,0,6])
        print("\nStatic EDF Engergy Consumed: {}\n".format(V/Vdd))
    else:
        print("The Given Task Set are not Schedulable with EDF")  
#End of the StatiC EDF Voltage Scaling

#define select frequency for cycle conserving
def select_Freq_CC(param,U):
    Ut=round(sum(U),3)
    maxf=(param[len(param)-1]['f'])
    for x in param:
        #print(round((x['f']/maxf)))
        if Ut<=(round((x['f']/maxf),3)):
            return x['v']
    return -1
#end the CC select freq function

##define the function for Dynamic Voltage Scaling EDF Cycle conserving scheduling without voltage scaling
#function plots the voltage vs time plot showing which task is running at dynamic voltage change
def CC_EDF_Schedule(param,T):
    plotX=[]
    plotY=[]
    exe_prev_time=0
    exe_start_time=0
    final_time=0
    Vdd=5
    V=5
    sumofV=0
    sumofT=0
    prevtask=0
    queue=[]
    temp=0
    gain=1000
    stoptime=gain*math.ceil((max(T,key=lambda k:k['p'])['p']+max(T,key=lambda k:k['w'])['w']+1))
    stepsize=1
    U=[0]*len(T)
    for i in range(0,len(T)):
        T[i]['c']=T[i]['e']
    for s in range(0,len(T)):
        U[s]=round(T[s]['w']/T[s]['p'],3)
    task_copy=append_Instances(T,5)
    printtasks(task_copy)
    #printtasks(task_copy)
    if EDF_Test(1,T):
        for a in T:
            plt.arrow(a['p'],2,0,0-1.7,color='tomato',head_width=0.15)
        plt.arrow(T[0]['s'],0,0,2,color='skyblue',head_width=0.15)
        for a in task_copy:
            plt.arrow(a['p'],2,0,0-1.7,color='tomato',head_width=0.15)
            plt.arrow(a['s'],0,0,2,color='skyblue',head_width=0.15)
        queue=sorted(T,key=lambda k:k['p'])
        #print(sum(U))
        #print(queue)
        V=select_Freq_CC(param,U)
        plotX.append(0)
        plotY.append(V)
        print("At time:0.0\tTask:{}\tInstance:{}\treleased\tat Voltage Level:{}V".format(queue[0]['n'],queue[0]['i'],V))
        #print( U[(queue[0]['n']-1)])
        #print(sum(U))
        plt.text(0,V,"T"+str(queue[0]['n']),fontsize=8)
        #Select Frequency Get Voltage
        #upon task release
        for current_time in range(0,stoptime,stepsize):
            time=current_time/gain
            sumofV+=V
            if (len(queue)!=0):
                #sumofV+=V
                #sumofT+=0.001
                if (queue[0]['c']>0):
                    queue[0]['c']=((queue[0]['c'])-((V*stepsize)/(Vdd*gain)))#Vdd/V)+exe_prev_time
                    plotX.append(time)
                    plotY.append(V)
                else:
                    #Select Frequency Get Voltage
                    #upon task release
                    print("At time:{}\tTask:{}\tInstance:{}\tcompleted\tat Voltage Level:{}V".format(time,queue[0]['n'],queue[0]['i'],V))
                    U[(queue[0]['n']-1)]=round(queue[0]['e']/(queue[0]['p']/queue[0]['i']),3)
                    #print(queue[0]['p'])
                    #print( U[(queue[0]['n']-1)])
                    #print(sum(U))
                    V=select_Freq_CC(param,U)
                    plotX.append(time)
                    plotY.append(0)
                    final_time=time
                    if(queue[0]['i']!=1):
                        for z in task_copy:
                            if (queue[0]['n']==z['n']) and (queue[0]['i']==z['i']):
                                task_copy.remove(z) 
                    del queue[0]
                    exe_prev_time=time
                    if(len(queue)!=0):
                        #Select Frequency Get Voltage
                        #upon task release
                        print("At time:{}\tTask:{}\tInstance:{}\treleased\tat Voltage Level:{}V".format(time,queue[0]['n'],queue[0]['i'],V))
                        U[(queue[0]['n']-1)]=round(queue[0]['w']/(queue[0]['p']/queue[0]['i']),3)
                        #print(queue[0]['p'])
                        #print( U[(queue[0]['n']-1)])
                        #print(sum(U))
                        V=select_Freq_CC(param,U)
                        plt.text(time,V,"T"+str(queue[0]['n']),fontsize=8)
                        plotX.append(time)
                        plotY.append(V)
            if len(task_copy)!=0:
                if taskstart(task_copy,time):
                    if len(queue)!=0:
                        print("At time:{}\tTask:{}\tInstance:{}\tPreempted".format(time,queue[0]['n'],queue[0]['i']))
                        prevtask=queue[0]['n']
                    for e in task_copy:
                        if (e['s']==time):
                            queue.append(e)
                    queue=sorted(queue,key=lambda k:k['p'])
                    print("At time:{}\tTask:{}\tInstance:{}\treleased\tat Voltage Level:{}V".format(time,queue[0]['n'],queue[0]['i'],V))
                    exe_prev_time=time
                    #if (prevtask!=queue[0]['n']):
                    #print(queue[0]['p'])
                    U[(queue[0]['n']-1)]=round(queue[0]['w']/(queue[0]['p']/queue[0]['i']),3)
                    #print( U[(queue[0]['n']-1)])
                    #print(sum(U))
                    V=select_Freq_CC(param,U)
                    #Select Frequency Get Voltage
                    #upon task release
                    plt.text(time,V,"T"+str(queue[0]['n']),fontsize=8)
                    plotX.append(time)
                    plotY.append(0)
                    plotX.append(time)
                    plotY.append(V)
        plt.xlabel('Time')
        plt.ylabel('Voltage')
        plt.title('Cycle Conserving EDF Scheduling')
        plt.subplots_adjust(hspace=0.5)
        lineedf_cc=plt.plot(plotX,plotY,color='black',linewidth=0.5)
        plt.axis([0,final_time,0,6])
        print("Cycle Conserving EDF Engergy Consumed: {}\n".format(0.001*(sumofV/time)/Vdd))
    else:
        print("The Given Task Set are not Schedulable with EDF")            
            



def main():
    print("\n")
    print("Enter the Name for the Text File:")
    filename=str(input())
    tasks=readFile(filename)
    print("----------------------------------------------------------------------------------- ")
    print("START")
    print("----------------------------------------------------------------------------------- ")
    printtasks(tasks)
    print("----------------------------------------------------------------------------------- ")
    print("EDF Algorithm Scheduling for periodic Tasks: ")
    print("----------------------------------------------------------------------------------- ")
    plt.subplot(2, 2, 1)
    EDF_Schedule(tasks)
    print("----------------------------------------------------------------------------------- ")
    print("Static Voltage Scaling EDF based Algorithm Scheduling for periodic Tasks: ")
    print("----------------------------------------------------------------------------------- ")
    plt.subplot(2, 2, 2)
    Static_EDF_Schedule(processor_param,tasks)
    print("-------------------------------------------------------------------------------------- ")
    print("Cycle Conserving Dynamic Voltage Scaling EDF based Algorithm Scheduling for periodic Tasks: ")
    print("-------------------------------------------------------------------------------------- ")
    plt.subplot(2, 2, 3)
    CC_EDF_Schedule(processor_param,tasks)
    print("----------------------------------------------------------------------------------- ")
    print("END")
    print("----------------------------------------------------------------------------------- ")
    plt.show()

if __name__ == '__main__':
    main()
      

