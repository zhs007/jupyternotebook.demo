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


def showCNFund(cfg, code):
    dffund = getFundValues(
        cfg['servaddr'], cfg['token'], 'cnfunds', code, 0, 0)
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
