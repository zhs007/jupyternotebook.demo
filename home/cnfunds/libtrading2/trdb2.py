import grpc
import trading2_pb2
import tradingdb2_pb2
import tradingdb2_pb2_grpc
import yaml
from datetime import datetime
import time


def genSimTradingParams(cfg, title, lstParams: list, ignoreCache: bool = False):
    for i in range(len(lstParams)):
        yield tradingdb2_pb2.RequestSimTrading(
            basicRequest=trading2_pb2.BasicRequestData(
                token=cfg['token'],
            ),
            params=lstParams[i],
            ignoreCache=ignoreCache,
            index=i,
            title=title,
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
