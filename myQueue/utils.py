from myQueue.Server import *
import math


def runBatchByCust(avgArrTime, avgSrvTime, custPara=(1e3, 2e4, 1e3)):
    '''根据顾客源数目批量运行，获取指标结果'''
    totCustList = []
    curCust = custPara[0]
    for i in range(int((custPara[1] - custPara[0]) // custPara[2])):
        totCustList.append(curCust)
        curCust = curCust + custPara[2]
    # avgSysTime, avgWaitTime, avgSysCustCnt, avgWaitCustCnt, avgUtilRatio
    metrics = [[], [], [], [], []]
    for totCust in totCustList:
        inPara = InputPara(avgArrTime, avgSrvTime, totCust)
        server = Server()
        server.init(inPara)
        metric = server.run(False)
        for i in range(5):
            metrics[i].append(metric[i])

    print(metrics)
    return totCustList, metrics


def computeTheVal(timeList: list):
    '''计算理论值'''
    metrics = []
    for avgArrTime, avgSrvTime, _ in timeList:
        if avgArrTime == avgSrvTime:
            metrics.append(['inf', 'inf', 'inf', 'inf', 1])
            continue
        lamda = 1 / avgArrTime
        mu = 1 / avgSrvTime
        rho = avgSrvTime / avgArrTime
        Ls = lamda / (mu - lamda)
        Lq = Ls - rho
        Ws = 1 / (mu - lamda)
        Wq = Ws - avgSrvTime
        metrics.append([Ws, Wq, Ls, Lq, rho])
    return metrics


def runBatchByTime(timeList: list, totCust=500):
    metrics = []
    for arr, srv, _ in timeList:
        inPara = InputPara(arr, srv, totCust)
        server = Server()
        server.init(inPara)
        metric = server.run(False)
        metrics.append(metric)
    return metrics


def runBatchByCnt(timeList: list, totCust=500):
    metrics = []
    for arr, srv, cnterCnt in timeList:
        inPara = InputPara(arr, srv, totCust, cnterCnt)
        server = Server()
        server.init(inPara)
        metric = server.run(False)
        metrics.append(metric)
    return metrics


def computeTheValCnt(timeList):
    '''计算理论值，服务台个数可变'''
    def factor(n):
        a = 1
        for i in range(1, n+1):
            a *= i
        return a
    metrics = []
    for arr, srv, cnterCnt in timeList:
        lamda = 1 / arr
        mu = 1 / srv
        rho = lamda / (cnterCnt * mu)
        P0 = (1/(1-rho))*(1/factor(cnterCnt))*math.pow((lamda/mu), cnterCnt)
        for k in range(cnterCnt):
            P0 += 1/factor(k)*math.pow((lamda/mu), k)
        P0 = 1/P0
        Lq = P0 * rho * math.pow(cnterCnt*rho, cnterCnt) / \
            factor(cnterCnt) / math.pow(1-rho, 2)
        Ls = Lq + cnterCnt*rho
        Ws = Ls / lamda
        Wq = Lq / lamda
        metrics.append([Ws, Wq, Ls, Lq, rho])
    return metrics


if __name__ == "__main__":
    # totCustList, metrics = runBatchByCust(5,2, custPara=(1e3, 2e5, 1e3))
    # plot(totCustList, metrics)

    # arr, srv, cnterCnt
    timeList = [
        (5, 2, 3), (5, 3, 3), (5, 4, 3),
        (5, 2, 2), (5, 3, 2), (5, 4, 2),
        (5, 2, 4), (5, 3, 4), (5, 4, 4)
    ]
    tm = computeTheValCnt(timeList)
    rm = runBatchByCnt(timeList, totCust=1000)

    def fprint(ll):
        print("[%.3f %.3f %.3f %.3f %.3f]" %
              (ll[0], ll[1], ll[2], ll[3], ll[4]))
    for i in range(len(tm)):
        fprint(tm[i])
        fprint(rm[i])
