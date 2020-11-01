import grpc
import tradingdb2_pb2
import tradingdb2_pb2_grpc
import yaml


def loadConfig(fn: str):
    f = open(fn, 'r', encoding="utf-8")
    fd = f.read()
    f.close()

    cfg = yaml.safe_load(fd)
    return cfg


def getCandles(servAddr: str, token: str, market: str, symbol: str, tsStart: int, tsEnd: int, tags):
    channel = grpc.insecure_channel(servAddr)
    stub = tradingdb2_pb2_grpc.TradingDB2ServiceStub(channel)

    response = stub.getCandles(tradingdb2_pb2.RequestGetCandles(
        token=token,
        market=market,
        symbol=symbol,
        tsStart=tsStart,
        tsEnd=tsEnd,
        tags=tags
    ))
    for candle in response:
        print(candle)
