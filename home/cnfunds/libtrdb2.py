import pandas as pd
import grpc
import trading2_pb2
import tradingdb2_pb2
import tradingdb2_pb2_grpc
import yaml
from datetime import datetime
import time
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def loadConfig(fn: str):
    f = open(fn, 'r', encoding="utf-8")
    fd = f.read()
    f.close()

    cfg = yaml.safe_load(fd)
    return cfg


def getFundValues(servAddr: str, token: str, market: str, symbol: str, tsStart: int, tsEnd: int) -> pd.DataFrame:
    channel = grpc.insecure_channel(servAddr)
    stub = tradingdb2_pb2_grpc.TradingDB2Stub(channel)

    response = stub.getCandles(tradingdb2_pb2.RequestGetCandles(
        # token=token,
        market=market,
        symbol=symbol,
        tsStart=tsStart,
        tsEnd=tsEnd,
        basicRequest=trading2_pb2.BasicRequestData(
            token=token,
        ),
    ))

    fv = {'date': [], 'close': []}
    for curres in response:
        for candle in curres.candles.candles:
            fv['date'].append(datetime.fromtimestamp(
                candle.ts).strftime('%Y-%m-%d'))
            fv['close'].append(candle.close / 10000.0)

    return pd.DataFrame(fv)


def showCNFund(cfg, code, start: str, end: str):
    tsStart = int(datetime.timestamp(datetime.strptime(start, '%Y%m%d')))
    tsEnd = int(datetime.timestamp(datetime.strptime(end, '%Y%m%d')))

    dffund = getFundValues(
        cfg['servaddr'], cfg['token'], 'cnfunds', code, tsStart, tsEnd)
    fig = px.line(dffund, x="date", y="close", title=code)
    fig.show()


def showCNFunds(cfg, codes, rows: int, cols: int):
    titles = []
    i = 0
    for row in range(0, rows):
        for col in range(0, cols):
            titles.append(codes[i])
            i += 1

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=titles)

    i = 0
    for row in range(0, rows):
        for col in range(0, cols):
            dffund = getFundValues(
                cfg['servaddr'], cfg['token'], 'cnfunds', codes[i], 0, 0)
            fig.add_trace(go.Scatter(
                x=dffund['date'], y=dffund['close']), row=row+1, col=col+1)
            i += 1

    fig.show(renderer="png")


def str2Asset(asset: str) -> trading2_pb2.Asset:
    arr = asset.split('.', -1)
    if len(arr) != 2:
        raise ValueError

    return trading2_pb2.Asset(
        market=arr[0],
        code=arr[1],
    )


def simTrading(servAddr: str, token: str, assets: list, baselines: list, tsStart: int, tsEnd: int) -> pd.DataFrame:
    channel = grpc.insecure_channel(servAddr)
    stub = tradingdb2_pb2_grpc.TradingDB2Stub(channel)

    lstAssets = []
    for a in assets:
        lstAssets.append(str2Asset(a))

    lstBaselines = []
    for b in baselines:
        lstBaselines.append(str2Asset(b))

    params = trading2_pb2.SimTradingParams(
        assets=lstAssets,
        baselines=lstBaselines,
        startTs=tsStart,
        endTs=tsEnd,
    )

    response = stub.simTrading(tradingdb2_pb2.RequestSimTrading(
        basicRequest=trading2_pb2.BasicRequestData(
            token=token,
        ),
        params=params,
    ))

    fv = {'date': [], 'close': []}
    if len(response.pnl) > 0:
        pnl = response.pnl[0]
        pnlt = pnl.total
        for v in pnlt.values:
            fv['date'].append(datetime.fromtimestamp(
                v.ts).strftime('%Y-%m-%d'))
            fv['close'].append(v.perValue)
            # fv['close'].append(v.perValue)

    return pd.DataFrame(fv)


def showSimTradingPNL(cfg, name: str, codes: list):
    dffund = simTrading(
        cfg['servaddr'], cfg['token'], codes, [], 0, 0)
    fig = px.line(dffund, x="date", y="close", title=name)
    fig.show()


def simTradingAIP(servAddr: str, token: str, assets: list, baselines: list, tsStart: int, tsEnd: int, tt: str, val: int) -> list:
    channel = grpc.insecure_channel(servAddr)
    stub = tradingdb2_pb2_grpc.TradingDB2Stub(channel)

    lstAssets = []
    for a in assets:
        lstAssets.append(str2Asset(a))

    lstBaselines = []
    for b in baselines:
        lstBaselines.append(str2Asset(b))

    buy0 = trading2_pb2.CtrlCondition(
        indicator=tt,
        vals=[val],
    )

    paramsbuy = trading2_pb2.BuyParams(
        aipMoney=10000,
    )

    s0 = trading2_pb2.Strategy(
        name="aip",
        asset=str2Asset(assets[0]),
        buy=[buy0],
        paramsBuy=paramsbuy,
    )

    params = trading2_pb2.SimTradingParams(
        assets=lstAssets,
        baselines=lstBaselines,
        startTs=tsStart,
        endTs=tsEnd,
        strategies=[s0],
    )

    response = stub.simTrading(tradingdb2_pb2.RequestSimTrading(
        basicRequest=trading2_pb2.BasicRequestData(
            token=token,
        ),
        params=params,
    ))

    fv0 = {'date': [], 'close': []}
    if len(response.pnl) > 0:
        pnl = response.pnl[0]
        pnlt = pnl.total
        for v in pnlt.values:
            fv0['date'].append(datetime.fromtimestamp(
                v.ts).strftime('%Y-%m-%d'))
            fv0['close'].append(v.perValue)

    fv1 = {'date': [], 'close': []}
    if len(response.baseline) > 0:
        pnl = response.baseline[0]
        pnlt = pnl.total
        for v in pnlt.values:
            fv1['date'].append(datetime.fromtimestamp(
                v.ts).strftime('%Y-%m-%d'))
            fv1['close'].append(v.perValue)

    return [pd.DataFrame(fv0), pd.DataFrame(fv1)]


def showSimTradingPNLAIP(cfg, name: str, codes: list, tt: str, val: int):
    dffund = simTradingAIP(
        cfg['servaddr'], cfg['token'], codes, codes, 0, 0, tt, val)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dffund[0]['date'], y=dffund[0]['close'],
                             mode='lines',
                             name=name))
    fig.add_trace(go.Scatter(x=dffund[1]['date'], y=dffund[1]['close'],
                             mode='lines',
                             name='baseline'))
    fig.show()


def simTrading(servAddr: str, token: str, assets: list, baselines: list, tsStart: int, tsEnd: int, tt: str, buyval: float, sellval: float) -> list:
    channel = grpc.insecure_channel(servAddr)
    stub = tradingdb2_pb2_grpc.TradingDB2Stub(channel)

    lstAssets = []
    for a in assets:
        lstAssets.append(str2Asset(a))

    lstBaselines = []
    for b in baselines:
        lstBaselines.append(str2Asset(b))

    buy0 = trading2_pb2.CtrlCondition(
        indicator=tt,
        vals=[buyval],
    )

    sell0 = trading2_pb2.CtrlCondition(
        indicator=tt,
        vals=[sellval],
    )

    paramsbuy = trading2_pb2.BuyParams(
        perHandMoney=1,
    )

    paramssell = trading2_pb2.SellParams(
        perVolume=1,
    )

    paramsinit = trading2_pb2.InitParams(
        money=10000,
    )

    s0 = trading2_pb2.Strategy(
        name="normal",
        asset=str2Asset(assets[0]),
        buy=[buy0],
        sell=[sell0],
        paramsBuy=paramsbuy,
        paramsSell=paramssell,
        paramsInit=paramsinit
    )

    params = trading2_pb2.SimTradingParams(
        assets=lstAssets,
        baselines=lstBaselines,
        startTs=tsStart,
        endTs=tsEnd,
        strategies=[s0],
    )

    response = stub.simTrading(tradingdb2_pb2.RequestSimTrading(
        basicRequest=trading2_pb2.BasicRequestData(
            token=token,
        ),
        params=params,
    ))

    fv0 = {'date': [], 'close': []}
    if len(response.pnl) > 0:
        pnl = response.pnl[0]
        pnlt = pnl.total
        for v in pnlt.values:
            fv0['date'].append(datetime.fromtimestamp(
                v.ts).strftime('%Y-%m-%d'))
            fv0['close'].append(v.perValue)

    fv1 = {'date': [], 'close': []}
    if len(response.baseline) > 0:
        pnl = response.baseline[0]
        pnlt = pnl.total
        for v in pnlt.values:
            fv1['date'].append(datetime.fromtimestamp(
                v.ts).strftime('%Y-%m-%d'))
            fv1['close'].append(v.perValue)

    return [pd.DataFrame(fv0), pd.DataFrame(fv1)]


def showSimTrading(cfg, name: str, codes: list, tt: str, buyval: float, sellval: float):
    dffund = simTrading(
        cfg['servaddr'], cfg['token'], codes, codes, 0, 0, tt, buyval, sellval)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dffund[0]['date'], y=dffund[0]['close'],
                             mode='lines',
                             name=name))
    fig.add_trace(go.Scatter(x=dffund[1]['date'], y=dffund[1]['close'],
                             mode='lines',
                             name='baseline'))
    fig.show()


def simTradingEx(cfg, assets: list, tsStart: int, tsEnd: int,
                 ccBuy: trading2_pb2.CtrlCondition, ccSell: trading2_pb2.CtrlCondition,
                 paramsBuy: trading2_pb2.BuyParams, paramsSell: trading2_pb2.SellParams,
                 paramsInit: trading2_pb2.InitParams, paramsAIP: trading2_pb2.AIPParams) -> pd.DataFrame:
    channel = grpc.insecure_channel(cfg['servaddr'])
    stub = tradingdb2_pb2_grpc.TradingDB2Stub(channel)

    lstAssets = []
    for a in assets:
        lstAssets.append(str2Asset(a))

    s0 = trading2_pb2.Strategy(
        name="normal",
        asset=str2Asset(assets[0]),
    )

    if ccBuy != None:
        s0.buy.extend([ccBuy])

    if ccSell != None:
        s0.sell.extend([ccSell])

    if paramsBuy != None:
        s0.paramsBuy.CopyFrom(paramsBuy)

    if paramsSell != None:
        s0.paramsSell.CopyFrom(paramsSell)

    if paramsInit != None:
        s0.paramsInit.CopyFrom(paramsInit)

    if paramsAIP != None:
        s0.paramsAIP.CopyFrom(paramsAIP)

    params = trading2_pb2.SimTradingParams(
        assets=lstAssets,
        startTs=tsStart,
        endTs=tsEnd,
        strategies=[s0],
    )

    response = stub.simTrading(tradingdb2_pb2.RequestSimTrading(
        basicRequest=trading2_pb2.BasicRequestData(
            token=cfg['token'],
        ),
        params=params,
    ))

    fv0 = {'date': [], 'close': []}
    if len(response.pnl) > 0:
        pnl = response.pnl[0]
        pnlt = pnl.total
        for v in pnlt.values:
            fv0['date'].append(datetime.fromtimestamp(
                v.ts).strftime('%Y-%m-%d'))
            fv0['close'].append(v.perValue)

    return pd.DataFrame(fv0)


def simTradingEx2(cfg, assets: list, tsStart: int, tsEnd: int,
                  lstBuy: list, lstSell: list,
                  paramsBuy: trading2_pb2.BuyParams, paramsSell: trading2_pb2.SellParams,
                  paramsInit: trading2_pb2.InitParams, paramsAIP: trading2_pb2.AIPParams) -> pd.DataFrame:
    channel = grpc.insecure_channel(cfg['servaddr'])
    stub = tradingdb2_pb2_grpc.TradingDB2Stub(channel)

    lstAssets = []
    for a in assets:
        lstAssets.append(str2Asset(a))

    s0 = trading2_pb2.Strategy(
        name="normal",
        asset=str2Asset(assets[0]),
    )

    if lstBuy != None:
        s0.buy.extend(lstBuy)

    if lstSell != None:
        s0.sell.extend(lstSell)

    if paramsBuy != None:
        s0.paramsBuy.CopyFrom(paramsBuy)

    if paramsSell != None:
        s0.paramsSell.CopyFrom(paramsSell)

    if paramsInit != None:
        s0.paramsInit.CopyFrom(paramsInit)

    if paramsAIP != None:
        s0.paramsAIP.CopyFrom(paramsAIP)

    params = trading2_pb2.SimTradingParams(
        assets=lstAssets,
        startTs=tsStart,
        endTs=tsEnd,
        strategies=[s0],
    )

    response = stub.simTrading(tradingdb2_pb2.RequestSimTrading(
        basicRequest=trading2_pb2.BasicRequestData(
            token=cfg['token'],
        ),
        params=params,
    ))

    fv0 = {'date': [], 'close': []}
    if len(response.pnl) > 0:
        pnl = response.pnl[0]
        pnlt = pnl.total
        for v in pnlt.values:
            fv0['date'].append(datetime.fromtimestamp(
                v.ts).strftime('%Y-%m-%d'))
            fv0['close'].append(v.perValue)

    return pd.DataFrame(fv0)


def showSimTradingEx(title: str, lst: list, isStaticImg: bool):
    fig = go.Figure()

    for v in lst:
        fig.add_trace(go.Scatter(x=v['df']['date'], y=v['df']['close'],
                                 mode='lines',
                                 name=v['title']))

    if isStaticImg:
        fig.show(renderer="png")
    else:
        fig.show()


def str2timestamp(strTime: str, strFormat: str) -> int:
    tm = time.strptime(strTime, strFormat)
    return int(time.mktime(tm))


def simTradingEx3(cfg, assets: list, tsStart: int, tsEnd: int,
                  lstBuy: list, lstSell: list,
                  paramsBuy: trading2_pb2.BuyParams, paramsSell: trading2_pb2.SellParams,
                  paramsInit: trading2_pb2.InitParams, paramsAIP: trading2_pb2.AIPParams, ignoreCache: bool = False) -> trading2_pb2.PNLAssetData:
    channel = grpc.insecure_channel(cfg['servaddr'])
    stub = tradingdb2_pb2_grpc.TradingDB2Stub(channel)

    lstAssets = []
    for a in assets:
        lstAssets.append(str2Asset(a))

    s0 = trading2_pb2.Strategy(
        name="normal",
        asset=str2Asset(assets[0]),
    )

    if lstBuy != None:
        s0.buy.extend(lstBuy)

    if lstSell != None:
        s0.sell.extend(lstSell)

    if paramsBuy != None:
        s0.paramsBuy.CopyFrom(paramsBuy)

    if paramsSell != None:
        s0.paramsSell.CopyFrom(paramsSell)

    if paramsInit != None:
        s0.paramsInit.CopyFrom(paramsInit)

    if paramsAIP != None:
        s0.paramsAIP.CopyFrom(paramsAIP)

    params = trading2_pb2.SimTradingParams(
        assets=lstAssets,
        startTs=tsStart,
        endTs=tsEnd,
        strategies=[s0],
    )

    response = stub.simTrading(tradingdb2_pb2.RequestSimTrading(
        basicRequest=trading2_pb2.BasicRequestData(
            token=cfg['token'],
        ),
        params=params,
        ignoreCache=ignoreCache,
    ))

    if len(response.pnl) > 0:
        pnl = response.pnl[0]
        return pnl.total

    return None


def nextWeekDay(cday: int, offday: int, startday: int = 1, endday: int = 5) -> int:
    """
    nextWeekDay - 计算周几向后偏移，譬如周1的2天后是周3，周5的2天后是周2
    """

    if cday < startday:
        cday = startday

    offday = offday % 7

    if cday + offday > endday:
        cday += offday + 2
    else:
        cday += offday

    while cday > 6:
        cday -= 7

    return cday


def asset2str(asset: trading2_pb2.Asset) -> str:
    return asset.market + '.' + asset.code


def buildPNLReport(lstpnl: list) -> pd.DataFrame:
    """
    buildPNLReport - 将PNL列表转换为pandas.DataFrame，方便计算
    """
    fv0 = {
        'title': [],
        'asset': [],
        'maxDrawdown': [],
        'maxDrawdownStart': [],
        'maxDrawdownEnd': [],
        'maxDrawup': [],
        'maxDrawupStart': [],
        'maxDrawupEnd': [],
        'sharpe': [],
        'annualizedReturns': [],
        'annualizedVolatility': [],
        'totalReturns': [],
        'variance': [],
        'buyTimes': [],
        'sellTimes': [],
        'stoplossTimes': [],
        'maxUpDay': [],
        'maxPerUpDay': [],
        'maxDownDay': [],
        'maxPerDownDay': [],
        'maxUpWeek': [],
        'maxPerUpWeek': [],
        'maxDownWeek': [],
        'maxPerDownWeek': [],
        'maxUpMonth': [],
        'maxPerUpMonth': [],
        'maxDownMonth': [],
        'maxPerDownMonth': [],
        'maxUpYear': [],
        'maxPerUpYear': [],
        'maxDownYear': [],
        'maxPerDownYear': [],
    }

    for v in lstpnl:
        fv0['title'].append(v['title'])

        fv0['asset'].append(asset2str(v['pnl'].asset))

        fv0['maxDrawdown'].append(v['pnl'].maxDrawdown)
        fv0['maxDrawdownStart'].append(datetime.fromtimestamp(
            v['pnl'].maxDrawdownStartTs).strftime('%Y-%m-%d'))
        fv0['maxDrawdownEnd'].append(datetime.fromtimestamp(
            v['pnl'].maxDrawdownEndTs).strftime('%Y-%m-%d'))

        fv0['maxDrawup'].append(v['pnl'].maxDrawup)
        fv0['maxDrawupStart'].append(datetime.fromtimestamp(
            v['pnl'].maxDrawupStartTs).strftime('%Y-%m-%d'))
        fv0['maxDrawupEnd'].append(datetime.fromtimestamp(
            v['pnl'].maxDrawupEndTs).strftime('%Y-%m-%d'))

        fv0['sharpe'].append(v['pnl'].sharpe)
        fv0['annualizedReturns'].append(v['pnl'].annualizedReturns)
        fv0['annualizedVolatility'].append(v['pnl'].annualizedVolatility)
        fv0['totalReturns'].append(v['pnl'].totalReturns)
        fv0['variance'].append(v['pnl'].variance)

        fv0['buyTimes'].append(v['pnl'].buyTimes)
        fv0['sellTimes'].append(v['pnl'].sellTimes)
        fv0['stoplossTimes'].append(v['pnl'].stoplossTimes)

        fv0['maxUpDay'].append(datetime.fromtimestamp(
            v['pnl'].maxUpDayTs).strftime('%Y-%m-%d'))
        fv0['maxPerUpDay'].append(v['pnl'].maxPerUpDay)
        fv0['maxDownDay'].append(datetime.fromtimestamp(
            v['pnl'].maxDownDayTs).strftime('%Y-%m-%d'))
        fv0['maxPerDownDay'].append(v['pnl'].maxPerDownDay)

        fv0['maxUpWeek'].append(datetime.fromtimestamp(
            v['pnl'].maxUpWeekTs).strftime('%Y-%m-%d'))
        fv0['maxPerUpWeek'].append(v['pnl'].maxPerUpWeek)
        fv0['maxDownWeek'].append(datetime.fromtimestamp(
            v['pnl'].maxDownWeekTs).strftime('%Y-%m-%d'))
        fv0['maxPerDownWeek'].append(v['pnl'].maxPerDownWeek)

        fv0['maxUpMonth'].append(datetime.fromtimestamp(
            v['pnl'].maxUpMonthTs).strftime('%Y-%m-%d'))
        fv0['maxPerUpMonth'].append(v['pnl'].maxPerUpMonth)
        fv0['maxDownMonth'].append(datetime.fromtimestamp(
            v['pnl'].maxDownMonthTs).strftime('%Y-%m-%d'))
        fv0['maxPerDownMonth'].append(v['pnl'].maxPerDownMonth)

        fv0['maxUpYear'].append(datetime.fromtimestamp(
            v['pnl'].maxUpYearTs).strftime('%Y-%m-%d'))
        fv0['maxPerUpYear'].append(v['pnl'].maxPerUpYear)
        fv0['maxDownYear'].append(datetime.fromtimestamp(
            v['pnl'].maxDownYearTs).strftime('%Y-%m-%d'))
        fv0['maxPerDownYear'].append(v['pnl'].maxPerDownYear)

    return pd.DataFrame(fv0)


def genSimTradingParams(cfg, lstParams: list, ignoreCache: bool = False):
    for i in range(len(lstParams)):
        yield tradingdb2_pb2.RequestSimTrading(
            basicRequest=trading2_pb2.BasicRequestData(
                token=cfg['token'],
            ),
            params=lstParams[i],
            ignoreCache=ignoreCache,
            index=i,
        )


def simTradings(cfg, lstParams: list, ignoreCache: bool = False) -> list:
    channel = grpc.insecure_channel(cfg['servaddr'])
    stub = tradingdb2_pb2_grpc.TradingDB2Stub(channel)

    lstRes = []
    responses = stub.simTrading2(
        genSimTradingParams(cfg, lstParams, ignoreCache))
    for response in responses:
        if len(response.pnl) > 0:
            pnl = response.pnl[0]
            lstRes.append({'title': pnl.title, 'pnl': pnl.total})

    return lstRes
