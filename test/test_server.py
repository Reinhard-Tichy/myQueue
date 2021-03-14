
from myQueue.utils import *
import sys
import os
sys.path.append(
    (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))))


class Test_base:
    # 函数级开始
    def setup(self):
        self.timeList = [
            (5, 2, 3), (5, 3, 3), (5, 4, 3),
            (5, 2, 2), (5, 3, 2), (5, 4, 2),
            (5, 2, 4), (5, 3, 4), (5, 4, 4)
        ]
        print("------->start testing server<-------")

    # 函数级结束
    def teardown(self):
        print("------->end testing server<-------")

    @staticmethod
    def fprint(ll):
        print("[%.3f %.3f %.3f %.3f %.3f]" %
              (ll[0], ll[1], ll[2], ll[3], ll[4]))

    def test_cnt(self):
        print('Running test_cnt')
        tm = computeTheValCnt(self.timeList)
        rm = runBatchByCnt(self.timeList, totCust=2000)
        eps = 0.
        for i in range(len(tm)):
            self.fprint(tm[i])
            self.fprint(rm[i])
            eps += abs(tm[i][-1] - rm[i][-1])
        eps /= len(tm)
        print(f'eps: {eps}')
        assert eps < 0.01

    def test_time(self):
        print('Running test_time')
        tm = computeTheVal(self.timeList)
        rm = runBatchByTime(self.timeList, totCust=2000)
        eps = 0.
        for i in range(len(tm)):
            self.fprint(tm[i])
            self.fprint(rm[i])
            eps += abs(tm[i][-1] - rm[i][-1])
        eps /= len(tm)
        print(f'eps: {eps}')
        assert eps < 0.02