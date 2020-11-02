import pandas as pd
import grpc
import tradingdb2_pb2
import tradingdb2_pb2_grpc
import yaml
from datetime import datetime
import plotly.express as px


def loadConfig(fn: str):
    f = open(fn, 'r', encoding="utf-8")
    fd = f.read()
    f.close()

    cfg = yaml.safe_load(fd)
    return cfg


def getFundValues(servAddr: str, token: str, market: str, symbol: str, tsStart: int, tsEnd: int) -> pd.DataFrame:
    channel = grpc.insecure_channel(servAddr)
    stub = tradingdb2_pb2_grpc.TradingDB2ServiceStub(channel)

    response = stub.getCandles(tradingdb2_pb2.RequestGetCandles(
        token=token,
        market=market,
        symbol=symbol,
        tsStart=tsStart,
        tsEnd=tsEnd
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
