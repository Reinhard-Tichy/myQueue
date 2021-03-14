# -*- coding: utf-8 -*-
from enum import Enum
import random
import math

ctrStatus = Enum("CounterStatus", ("idle", "busy"))


class Counter(object):
    cnt = 0

    def __init__(self):
        self.id = Counter.cnt           # 柜台id
        Counter.cnt += 1
        self.cust = None                # 正在服务的顾客
        self.status = ctrStatus.idle    # 柜台状态
        self.totCust = 0                # 该柜台总服务的顾客数

    def addCust(self, cust):
        self.cust = cust
        self.totCust += 1
        self.status = ctrStatus.busy

    def removeCust(self):
        self.cust = None
        self.status = ctrStatus.idle


evtType = Enum("EventType", ("arrive", "leave", "end"))


class Customer(object):
    cnt = 0

    def __init__(self):
        self.id = Customer.cnt  # 顾客id
        Customer.cnt += 1
        self.status = None      # 顾客状态(刚刚到达or即将离开)
        self.arriveTime = None  # 到达时间
        self.serveTime = None   # 接受服务时间 = 到达时间 + 等待时间
        self.leaveTime = None   # 离开时间 = 接受服务时间 + 服务时间
        self.sortTime = None    # 事件队列排序依据(为到达时间和离开时间之一)
        self.serveCtrId = -1    # 接受服务的柜台id


class Event(object):  # 用于GUI事件轴绘制
    def __init__(self, type, custId, time) -> None:
        self.type = type
        self.custId = custId
        self.time = time


class InputPara(object):
    def __init__(self, avgArrTime, avgSrvTime,
                 totCust=100, ctrCnt=1, queLimit='inf'):
        self.avgArrTime = avgArrTime  # 平均到达时间
        self.avgSrvTime = avgSrvTime  # 平均服务时间
        self.totCust = totCust  # 总顾客数
        self.ctrCnt = ctrCnt    # 总柜台数
        if queLimit == 'inf':
            self.queLimit = float('inf')   # 等待队列上限
        else:
            self.queLimit = queLimit


class OutputPara(object):
    def __init__(self, ctrCnt) -> None:
        self.totSysTime = 0.0       # 总逗留时间 (离开 - 到达)
        self.totWaitTime = 0.0      # 总等待时间 (服务 - 到达)
        self.totSysCustCnt = 0.0    # 总队列长度 (等待队列 + 忙碌柜台数)*dt
        self.totWaitCustCnt = 0.0   # 总等待队列长度 (等待队列)*dt
        self.utiRatios = [0.0] * ctrCnt  # 各柜台总利用率 (是否忙碌)*dt
        self.totServedCustCnt = 0   # 总服务过的顾客数(接受服务后离开)
        self.totArriveCustCnt = 0   # 总到达的顾客数(包括来了就走的顾客)
        self.curTime = 0.0
        self.ctrCnt = ctrCnt

    def tick(self, cust, server):
        '''
            每当时钟变化时，调用此函数进行更新
        '''
        if cust.status == evtType.arrive:
            self.totArriveCustCnt += 1
        else:
            self.totServedCustCnt += 1
            self.totSysTime += cust.leaveTime - cust.arriveTime
            self.totWaitTime += cust.serveTime - cust.arriveTime
        self.totSysCustCnt += (len(server.waitQueue) +
                               len(server.busyCtrs)) * (server.curTime - self.curTime)
        self.totWaitCustCnt += len(server.waitQueue) * \
            (server.curTime - self.curTime)
        for i in range(self.ctrCnt):
            if (server.ctrList[i].status == ctrStatus.busy):
                self.utiRatios[i] += server.curTime - self.curTime
        self.curTime = server.curTime

    def report(self, needPrint=True):
        if self.totServedCustCnt != 0:
            avgSysTime = self.totSysTime / self.totServedCustCnt
            avgWaitTime = self.totWaitTime / self.totServedCustCnt
        else:
            avgSysTime = 0.0
            avgWaitTime = 0.0
        avgSysCustCnt = self.totSysCustCnt / self.curTime
        avgWaitCustCnt = self.totWaitCustCnt / self.curTime
        avgUtilRatio = sum(self.utiRatios) / (self.ctrCnt * self.curTime)
        if needPrint:
            print("----------------- 实时数据信息 -----------------")
            print("当前总到达顾客数: %d \t 当前已服务顾客数: %d" %
                  (self.totArriveCustCnt, self.totServedCustCnt))
            print("平均逗留时间: %.3f \t 平均等待时间: %.3f" %
                  (avgSysTime, avgWaitTime))  # 均不考虑直接离开未服务的顾客
            print("平均队列长度: %.3f \t 平均等待队列长度: %.3f" %
                  (avgSysCustCnt, avgWaitCustCnt))
            print("系统总平均利用率: %.3f%%" % (avgUtilRatio * 100))
            print("--------------------- End ---------------------")

        return [avgSysTime, avgWaitTime, avgSysCustCnt, avgWaitCustCnt, avgUtilRatio]


class Server(object):
    '''
        排队系统主类
    '''

    def __init__(self):
        self.curTime = 0.0  # 当前时间
        self.waitQueue = []  # 顾客等待队列
        self.eventList = []  # 事件调度列表(以顾客作为事件)
        self.inPara = None  # 输入参数
        self.ctrList = []   # 所有柜台
        self.idleCtrs = []  # 空闲柜台编号
        self.busyCtrs = []  # 忙碌柜台编号
        self.curTotArvCust = 0  # 当前到达顾客数
        self.outPara = None

    def init(self, inPara: InputPara):
        self.inPara = inPara
        self.outPara = OutputPara(self.inPara.ctrCnt)
        self.makeCounters()
        if self.curTotArvCust < self.inPara.totCust:
            self.addEvent(self.makeNewCust())

    def reset(self):
        self.curTime = 0.0
        self.waitQueue.clear()
        self.eventList.clear()
        self.inPara = self.outPara = None
        self.ctrList.clear()
        self.idleCtrs.clear()
        self.busyCtrs.clear()
        self.curTotArvCust = 0

    def stepByGUI(self):
        '''
            GUI界面更新调用函数，每次返回一个事件及相关输出统计数据
        '''
        eveInfos = []
        avgStats = []
        if len(self.eventList) != 0:
            cust = self.getEvent()
            self.curTime = cust.sortTime
            self.outPara.tick(cust, self)
            avgStats = self.outPara.report(needPrint=False)
            curEve = Event(cust.status, cust.id, self.curTime)
            if cust.status == evtType.arrive:  # 到达
                eveInfo = "[arriving] curTime %.1f a new customer %d has arrived." % (
                    cust.arriveTime, cust.id)
                # print(eveInfo)
                eveInfos.append(eveInfo)
                if len(self.idleCtrs) == 0:  # 忙碌
                    if len(self.waitQueue) < self.inPara.queLimit:
                        self.waitQueue.append(cust)
                    else:  # 等待队列容量达到上限
                        # self.curTotArvCust -= 1 # 如果关心实际服务的顾客数则需-1，否则如果只关心总到达的顾客数则这行应删去
                        eveInfo = "[leaving] curTime %.1f a new customer %d has just left without being served." % (
                            self.curTime, cust.id)
                        # print(eveInfo)
                        eveInfos.append(eveInfo)
                else:
                    assert(len(self.waitQueue) == 0)
                    ctrId = self.idleCtrs.pop(0)
                    eveInfo = "[serving] curTime %.1f customer %d is being served at ctr %d." % (
                        self.curTime, cust.id, ctrId)
                    # print(eveInfo)
                    eveInfos.append(eveInfo)
                    self.busyCtrs.append(ctrId)
                    self.ctrList[ctrId].addCust(cust)
                    self.serveCust(cust, ctrId)
                    self.addEvent(cust)
                # 添加新顾客
                if self.curTotArvCust < self.inPara.totCust:
                    self.addEvent(self.makeNewCust())

            else:  # 离开
                ctrId = cust.serveCtrId
                eveInfo = "[leaving] curTime %.1f customer %d has left after being served at ctr %d." % (
                    self.curTime, cust.id, ctrId)
                # print(eveInfo)
                eveInfos.append(eveInfo)
                assert(ctrId != -1)
                self.ctrList[ctrId].removeCust()
                if len(self.waitQueue) != 0:  # 有人等待
                    waitCust = self.getWaitCust()
                    eveInfo = "[serving] curTime %.1f customer %d is being served at ctr %d." % (
                        self.curTime, waitCust.id, ctrId)
                    # print(eveInfo)
                    eveInfos.append(eveInfo)
                    self.ctrList[ctrId].addCust(waitCust)
                    self.serveCust(waitCust, ctrId)
                    self.addEvent(waitCust)
                else:  # 无人等待，则该柜台空闲
                    self.busyCtrs.remove(ctrId)
                    self.idleCtrs.append(ctrId)
        else:
            curEve = Event(evtType.end, -1, self.curTime)

        return curEve, eveInfos, avgStats

    def run(self, needPrint=True):
        '''
            模拟仿真主函数(控制台直接运行)
        '''
        while len(self.eventList) != 0:
            cust = self.getEvent()
            self.curTime = cust.sortTime
            self.outPara.tick(cust, self)
            self.outPara.report(needPrint)
            if cust.status == evtType.arrive:  # 到达
                if len(self.idleCtrs) == 0:  # 忙碌
                    if len(self.waitQueue) < self.inPara.queLimit:
                        self.waitQueue.append(cust)
                    else:  # 等待队列容量达到上限
                        self.curTotArvCust -= 1  # 如果关心实际服务的顾客数则需-1，否则如果只关心总到达的顾客数则这行应删去
                        if needPrint:
                            print("a new cust %d has just left without being served at %.1f" % (
                                cust.id, self.curTime))
                else:
                    assert(len(self.waitQueue) == 0)
                    ctrId = self.idleCtrs.pop(0)
                    if needPrint:
                        print("serving curTime %.1f curCust %d ctr %d" %
                              (self.curTime, cust.id, ctrId))
                    self.busyCtrs.append(ctrId)
                    self.ctrList[ctrId].addCust(cust)
                    self.serveCust(cust, ctrId)
                    self.addEvent(cust)
                # 添加新顾客
                if self.curTotArvCust < self.inPara.totCust:
                    self.addEvent(self.makeNewCust())

            else:  # 离开
                ctrId = cust.serveCtrId
                if needPrint:
                    print("leaving curTime %.1f curCust %d ctr %d" %
                          (self.curTime, cust.id, ctrId))
                assert(ctrId != -1)
                self.ctrList[ctrId].removeCust()
                if len(self.waitQueue) != 0:  # 有人等待
                    waitCust = self.getWaitCust()
                    if needPrint:
                        print("serving curTime %.1f curCust %d ctr %d" %
                              (self.curTime, waitCust.id, ctrId))
                    self.ctrList[ctrId].addCust(waitCust)
                    self.serveCust(waitCust, ctrId)
                    self.addEvent(waitCust)
                else:  # 无人等待，则该柜台空闲
                    self.busyCtrs.remove(ctrId)
                    self.idleCtrs.append(ctrId)
        return self.outPara.report()

    def serveCust(self, cust, ctrId):
        '''
            在特定柜台为该顾客进行服务
        '''
        cust.serveCtrId = ctrId
        cust.serveTime = self.curTime
        cust.leaveTime = cust.serveTime + \
            self.getTimeInterval(self.inPara.avgSrvTime)
        cust.sortTime = cust.leaveTime
        cust.status = evtType.leave

    def addEvent(self, cust):
        self.eventList.append(cust)

    def getWaitCust(self):
        '''取当前最早到达的顾客'''
        idx = self.waitQueue.index(
            min(self.waitQueue, key=lambda x: x.sortTime))
        return self.waitQueue.pop(idx)

    def getEvent(self):
        '''取当前时间最小的事件'''
        idx = self.eventList.index(
            min(self.eventList, key=lambda x: x.sortTime))  # 纯粹秀一波操作，其实for循环还更快...
        return self.eventList.pop(idx)

    def makeNewCust(self):
        '''创建一个新顾客'''
        self.curTotArvCust += 1
        cust = Customer()
        cust.status = evtType.arrive
        cust.arriveTime = self.curTime + \
            self.getTimeInterval(self.inPara.avgArrTime)
        cust.sortTime = cust.arriveTime
        # print("a new customer %d will arrive at %.1f"%(cust.id, cust.arriveTime))
        return cust

    def makeCounters(self):
        '''构造所有柜台'''
        for i in range(self.inPara.ctrCnt):
            ctr = Counter()
            self.ctrList.append(ctr)
            self.idleCtrs.append(i)

    def getTimeInterval(self, revLambda):
        '''
            $t = -\\frac{1}{lambda}ln(1-y)$
        '''
        return -revLambda * math.log(random.random())


if __name__ == "__main__":
    inPara = InputPara(1, 0.5, totCust=500, ctrCnt=2, queLimit='inf')
    server = Server()
    server.init(inPara)
    server.run()
    # print(server.curTime)
    pass
