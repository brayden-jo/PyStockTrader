import os
import sys
import warnings
import numpy as np
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utility.setting import ui_num, DICT_SET
from utility.static import now, strf_time, timedelta_sec
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


class CollectorKiwoom:
    def __init__(self, gubun, qlist):
        """
                    0        1       2        3       4       5       6       7      8      9
        qlist = [windowQ, soundQ, query1Q, query2Q, teleQ, receivQ, stockQ, coinQ, sstgQ, cstgQ,
                 tick1Q, tick2Q, tick3Q, tick4Q, tick5Q]
                   10       11      12     13      14
        """
        self.windowQ = qlist[0]
        self.soundQ = qlist[1]
        self.query2Q = qlist[3]
        self.teleQ = qlist[4]
        self.gubun = gubun
        if self.gubun == 1:
            self.tickQ = qlist[10]
        elif self.gubun == 2:
            self.tickQ = qlist[11]
        elif self.gubun == 3:
            self.tickQ = qlist[12]
        elif self.gubun == 4:
            self.tickQ = qlist[13]

        self.dict_df = {}
        self.dict_dm = {}
        self.time_info = now()
        self.str_tday = strf_time('%Y%m%d')
        self.Start()

    def Start(self):
        while True:
            tick = self.tickQ.get()
            if type(tick) == list:
                self.UpdateTickData(tick[0], tick[1], tick[2], tick[3], tick[4], tick[5], tick[6], tick[7],
                                    tick[8], tick[9], tick[10], tick[11], tick[12], tick[13], tick[14],
                                    tick[15], tick[16], tick[17], tick[18], tick[19], tick[20], tick[21], tick[22])
            elif tick == '틱데이터저장':
                self.query2Q.put([1, self.dict_df])
                break

        self.windowQ.put([ui_num['S단순텍스트'], '시스템 명령 실행 알림 - 콜렉터를 종료합니다.'])
        if DICT_SET['알림소리1']:
            self.soundQ.put('주식 콜렉터를 종료합니다.')
        self.teleQ.put('주식 콜렉터를 종료하였습니다.')

    def UpdateTickData(self, code, c, o, h, low, per, dm, ch, vp, bids, asks, vitime, vid5,
                       s2hg, s1hg, b1hg, b2hg, s2jr, s1jr, b1jr, b2jr, d, receiv_time):
        try:
            hlm = round((h + low) / 2)
            hlmp = round((c / hlm - 1) * 100, 2)
        except ZeroDivisionError:
            return

        try:
            predm = self.dict_dm[code]
        except KeyError:
            predm = dm

        self.dict_dm[code] = dm
        sm = dm - predm
        d = self.str_tday + d

        if code not in self.dict_df.keys():
            self.dict_df[code] = pd.DataFrame(
                [[c, o, h, per, hlmp, sm, dm, ch, vp, bids, asks, vitime, vid5,
                  s2hg, s1hg, b1hg, b2hg, s2jr, s1jr, b1jr, b2jr]],
                columns=['현재가', '시가', '고가', '등락율', '고저평균대비등락율', '거래대금', '누적거래대금', '체결강도',
                         '전일거래량대비', '매수수량', '매도수량', 'VI발동시간', '상승VID5가격',
                         '매도호가2', '매도호가1', '매수호가1', '매수호가2',
                         '매도잔량2', '매도잔량1', '매수잔량1', '매수잔량2'],
                index=[d])
        else:
            self.dict_df[code].at[d] = \
                c, o, h, per, hlmp, sm, dm, ch, vp, bids, asks, vitime, vid5,\
                s2hg, s1hg, b1hg, b2hg, s2jr, s1jr, b1jr, b2jr

        if now() > self.time_info:
            if self.gubun == 4:
                gap = (now() - receiv_time).total_seconds()
                self.windowQ.put([ui_num['S단순텍스트'], f'콜렉터 수신 기록 알림 - 수신시간과 기록시간의 차이는 [{gap}]초입니다.'])
            self.query2Q.put([1, self.dict_df])
            self.dict_df = {}
            self.time_info = timedelta_sec(10)
