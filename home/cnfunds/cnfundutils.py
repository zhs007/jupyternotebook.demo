import pandas as pd
import numpy as np
import matplotlib
from matplotlib import font_manager
import matplotlib.pyplot as plt
import json
from datetime import datetime
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def init():
    pd.set_option('max_columns', 1000)
    pd.set_option('max_row', 300)
    pd.set_option('display.float_format', lambda x: '%.5f' % x)

    plt.rcParams['figure.figsize'] = (16.0, 8.0)

    font_dirs = ["/usr/local/share/fonts"]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    hfont = matplotlib.font_manager.FontProperties(
        fname='/usr/local/share/fonts/SourceHanSans-Normal.ttc')
    plt.rcParams['font.family'] = hfont.get_name()


def init2():
    pd.set_option('max_columns', 1000)
    pd.set_option('max_row', 300)
    pd.set_option('display.float_format', lambda x: '%.5f' % x)


def loadFundResult(fn: str) -> pd.DataFrame:
    return pd.read_csv(fn, dtype={"code": "str"})


def loadFundBasicInfo(fn: str) -> pd.DataFrame:
    return pd.read_excel(fn, dtype={"code": "str"})


def getFundBasicInfoType2(df: pd.DataFrame):
    lstType0 = ['开放式', '封闭式', '高风险', '低风险']
    lstType2 = []

    for i in range(len(df)):
        curtags = df.iat[i, 2]
        lsttags = curtags.split(';')
        for j in range(len(lsttags)):
            lsttags[j] = lsttags[j].strip()
            if lsttags[j] not in lstType2 and len(lsttags[j]) > 0 and lsttags[j] not in lstType0:
                lstType2.append(lsttags[j])

    return lstType2


def onProcType2(v, lstType2):
    for i in range(len(lstType2)):
        if v.tags.find(lstType2[i]) >= 0:
            return lstType2[i]

    return '其他'


def procFundBasicInfoTypes(df: pd.DataFrame, et: str):
    """处理dfFunds基本的数据"""

    ett = datetime.strptime(et, '%Y-%m-%d')

    df['type0'] = df.apply(
        lambda x: "开放式" if x.tags.find("开放式") >= 0 else "封闭式", axis=1)
    df['type1'] = df.apply(
        lambda x: "低风险" if x.tags.find("低风险") >= 0 else "高风险", axis=1)

    lstType2 = getFundBasicInfoType2(df)
    df['type2'] = df.apply(lambda x: onProcType2(x, lstType2), axis=1)

    df['createtimey'] = df.apply(
        lambda x: datetime.strptime(x.createtime, '%Y-%m-%d').year, axis=1)
    df['createtimem'] = df.apply(
        lambda x: datetime.strptime(x.createtime, '%Y-%m-%d').month, axis=1)
    df['livedays'] = df.apply(
        lambda x: (ett - datetime.strptime(x.createtime, '%Y-%m-%d')).days, axis=1)
    df['liveyears'] = df.apply(
        lambda x: (ett - datetime.strptime(x.createtime, '%Y-%m-%d')).days / 365.0, axis=1)


def onProcSize(v):
    if type(v['size']) != str:
        return 0

    objSize = json.loads(v['size'])
    if len(objSize) > 0 and 'size' in objSize[len(objSize) - 1].keys():
        return objSize[len(objSize) - 1]['size']

    return 0


def onProcSize1(v):
    if v['size0'] < 1:
        return 5

    if v['size0'] > 10:
        return 50

    return v['size0'] * 5


def procFundBasicInfoSize(df: pd.DataFrame):
    df['size0'] = df.apply(onProcSize, axis=1)
    df['size1'] = df.apply(onProcSize1, axis=1)


def mergeFundResultAndBasic(dfr: pd.DataFrame, dfb: pd.DataFrame) -> pd.DataFrame:
    """合并FundResults和Funds。

    这里考虑了不同版本的数据兼容性。
    """

    if 'tags' in dfr.columns and 'createtime' in dfr.columns:
        return dfr.drop(columns=['tags', 'createtime']).replace([np.inf, -np.inf, np.NaN], 0).join(dfb.set_index('code'), on='code')

    if 'tags' in dfr.columns:
        return dfr.drop(columns=['tags']).replace([np.inf, -np.inf, np.NaN], 0).join(dfb.set_index('code'), on='code')

    return dfr.replace([np.inf, -np.inf, np.NaN], 0).join(dfb.set_index('code'), on='code')


def onProcDayInTotalReturn(v):
    if v['totalReturn'] == 0:
        return 0

    return v['permaxupday'] / v['totalReturn']


def procFundResults(df: pd.DataFrame):
    df['dayInTotalReturn'] = df.apply(onProcDayInTotalReturn, axis=1)


def findFundManagerResult(manager, name):
    if 'results' in manager.keys() and isinstance(manager['results'], list):
        for i in range(len(manager['results'])):
            if manager['results'][i]['name'] == name:
                return manager['results'][i]

    return None


def parseManager(v, data):
    if type(v['managers']) != str:
        return

    objManagers = json.loads(v['managers'])
    for i in range(len(objManagers)):
        if 'name' not in objManagers[i].keys():
            continue

        data['name'].append(objManagers[i]['name'])

        if 'sex' in objManagers[i].keys():
            data['sex'].append(objManagers[i]['sex'])
        else:
            data['sex'].append(True)

        data['education'].append(objManagers[i]['education'])

        if 'country' in objManagers[i].keys():
            data['country'].append(objManagers[i]['country'])
        else:
            data['country'].append('未知')

        data['resume'].append(objManagers[i]['resume'])

        dtEnd = datetime.now()
        if 'endTime' in objManagers[i].keys():
            dtEnd = datetime.fromtimestamp(objManagers[i]['endTime'])
            data['endDate'].append(dtEnd.strftime('%Y%m%d'))
        else:
            data['endDate'].append(99999999)

        if 'startTime' in objManagers[i].keys():
            dtStart = datetime.fromtimestamp(objManagers[i]['startTime'])
            data['startDate'].append(dtStart.strftime('%Y%m%d'))
            data['workdays'].append((dtEnd - dtStart).days)
        else:
            data['startDate'].append('0')
            data['workdays'].append(0)

        data['fundcode'].append(v['code'])
        data['fundname'].append(v['name'])
        data['company'].append(v['company'])

        result0 = findFundManagerResult(objManagers[i], 'full')
        if result0 == None:
            data['maxdrawdown'].append(0)
            data['sharpe'].append(0)
            data['annualizedreturns'].append(0)
            data['annualizedvolatility'].append(0)
            data['totalreturns'].append(0)
        else:
            if 'maxDrawdown' in result0.keys():
                data['maxdrawdown'].append(result0['maxDrawdown'])
            else:
                data['maxdrawdown'].append(0)

            if 'sharpe' in result0.keys():
                data['sharpe'].append(result0['sharpe'])
            else:
                data['sharpe'].append(0)

            if 'annualizedReturns' in result0.keys():
                data['annualizedreturns'].append(result0['annualizedReturns'])
            else:
                data['annualizedreturns'].append(0)

            if 'annualizedVolatility' in result0.keys():
                data['annualizedvolatility'].append(
                    result0['annualizedVolatility'])
            else:
                data['annualizedvolatility'].append(0)

            if 'totalReturns' in result0.keys():
                data['totalreturns'].append(result0['totalReturns'])
            else:
                data['totalreturns'].append(0)

            data['endDate'][-1] = datetime.fromtimestamp(
                result0['endTime']).strftime('%Y%m%d')

        result1 = findFundManagerResult(objManagers[i], 'off_3m')
        if result1 == None:
            data['maxdrawdown3m'].append(0)
            data['sharpe3m'].append(0)
            data['annualizedreturns3m'].append(0)
            data['annualizedvolatility3m'].append(0)
            data['totalreturns3m'].append(0)
        else:
            if 'maxDrawdown' in result1.keys():
                data['maxdrawdown3m'].append(result1['maxDrawdown'])
            else:
                data['maxdrawdown3m'].append(0)

            if 'sharpe' in result1.keys():
                data['sharpe3m'].append(result1['sharpe'])
            else:
                data['sharpe3m'].append(0)

            if 'annualizedReturns' in result1.keys():
                data['annualizedreturns3m'].append(
                    result1['annualizedReturns'])
            else:
                data['annualizedreturns3m'].append(0)

            if 'annualizedVolatility' in result1.keys():
                data['annualizedvolatility3m'].append(
                    result1['annualizedVolatility'])
            else:
                data['annualizedvolatility3m'].append(0)

            if 'totalReturns' in result1.keys():
                data['totalreturns3m'].append(result1['totalReturns'])
            else:
                data['totalreturns3m'].append(0)

    return


def getManagers(df: pd.DataFrame):
    data = {'name': [], 'sex': [], 'education': [], 'country': [], 'resume': [],
            'startDate': [], 'endDate': [], 'fundcode': [], 'fundname': [], 'company': [],
            'maxdrawdown': [], 'sharpe': [], 'annualizedreturns': [], 'annualizedvolatility': [],
            'totalreturns': [], 'maxdrawdown3m': [], 'sharpe3m': [], 'annualizedreturns3m': [],
            'annualizedvolatility3m': [], 'totalreturns3m': [], 'workdays': []}

    for index, row in df.iterrows():
        carr = parseManager(row, data)

    return data


def onProcWorkDays0(v):
    days = 0
    if v['endDate'] == 99999999:
        if v['startDate'] > 0:
            days = (datetime.now() -
                    datetime.strptime(str(v['startDate']), '%Y%m%d')).days
    else:
        if v['startDate'] > 0:
            days = (datetime.strptime(str(
                v['endDate']), '%Y%m%d') - datetime.strptime(str(v['startDate']), '%Y%m%d')).days

    return days


def procManagersWorkDays(dfManagers: pd.DataFrame):
    dfManagers[['startDate', 'endDate']] = dfManagers[[
        'startDate', 'endDate']].astype(int)
    dfNew = dfManagers.groupby(['name']).agg({'annualizedreturns': np.mean, 'fundcode': pd.Series.nunique, 'company': pd.Series.nunique,
                                              'workdays': np.sum, 'totalreturns': np.sum, 'startDate': np.min, 'endDate': np.max}).reset_index()
    dfNew['workdays0'] = dfNew.apply(onProcWorkDays0, axis=1)

    return dfNew


def showCNFundsType2(dfFunds: pd.DataFrame, isStaticImg: bool):
    """分别根据数量和规模来显示饼图"""

    titles = ['按基金数量统计', '按基金规模统计']

    fig = make_subplots(rows=1, cols=2, subplot_titles=titles, specs=[
                        [{'type': 'domain'}, {'type': 'domain'}]])

    df0 = dfFunds.groupby('type2').size(
    ).sort_values().reset_index(name='Count')
    df1 = dfFunds.groupby('type2').agg({'size0': np.sum}).reset_index()

    fig.add_trace(go.Pie(labels=df0['type2'],
                         values=df0['Count'], name="按基金数量统计"), row=1, col=1)
    fig.add_trace(go.Pie(labels=df1['type2'],
                         values=df1['size0'], name="按基金规模统计"), row=1, col=2)

    if isStaticImg:
        fig.show(renderer="png")
    else:
        fig.show()


def showInvalidCNFundsType2(dfFunds: pd.DataFrame):
    """筛选出type2数据不合理的记录"""

    return dfFunds.loc[(dfFunds['type2'] != '混合型') & (dfFunds['type2'] != '债券型') & (dfFunds['type2'] != '股票型') & (dfFunds['type2'] != '货币型') & (dfFunds['type2'] != 'ETF联接基金') & (dfFunds['type2'] != 'FOF') & (dfFunds['type2'] != '其他')]


def showCNFundResultsScatter(dfFundResults: pd.DataFrame, isStaticImg: bool):
    """显示基金的回报、年限、规模、类型散点图"""

    fig = go.Figure()
    arrType2 = ['混合型', '债券型', '股票型', '货币型', 'ETF联接基金', 'FOF', '其他']

    for t2 in arrType2:
        cdf = dfFundResults.loc[dfFundResults['type2'] == t2]

        # fig.add_trace(go.Scatter(x=dfFundResults['liveyears'], y=dfFundResults['totalReturn'],
        #                          mode='markers',
        #                          name=t2, marker=dict(size=dfFundResults['size1'])))
        fig.add_trace(go.Scatter(x=cdf['durationYear'], y=cdf['totalReturn'],
                                 mode='markers',
                                 name=t2, marker=dict(size=dfFundResults['size1'])))

    if isStaticImg:
        fig.show(renderer="png")
    else:
        fig.show()


def showCNFundResultsScatterEx(dfFundResults: pd.DataFrame, x: str, y: str, s: str, isStaticImg: bool):
    """显示基金散点图"""

    fig = go.Figure()
    arrType2 = ['混合型', '债券型', '股票型', '货币型', 'ETF联接基金', 'FOF', '其他']

    for t2 in arrType2:
        cdf = dfFundResults.loc[dfFundResults['type2'] == t2]

        # fig.add_trace(go.Scatter(x=dfFundResults['liveyears'], y=dfFundResults['totalReturn'],
        #                          mode='markers',
        #                          name=t2, marker=dict(size=dfFundResults['size1'])))
        if s != '':
            fig.add_trace(go.Scatter(x=cdf[x], y=cdf[y],
                                     mode='markers',
                                     name=t2, marker=dict(size=dfFundResults[s])))
        else:
            fig.add_trace(go.Scatter(x=cdf[x], y=cdf[y],
                                     mode='markers',
                                     name=t2))

    if isStaticImg:
        fig.show(renderer="png")
    else:
        fig.show()
