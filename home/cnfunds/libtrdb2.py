import pandas as pd
import grpc
import trading2_pb2
import tradingdb2_pb2
import tradingdb2_pb2_grpc
import yaml
from datetime import datetime
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
                 paramsInit: trading2_pb2.InitParams) -> pd.DataFrame:
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
