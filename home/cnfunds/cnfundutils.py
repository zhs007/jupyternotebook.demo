import pandas as pd
import numpy as np
import matplotlib
from matplotlib import font_manager
import matplotlib.pyplot as plt
import json
from datetime import datetime


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

    return ''


def procFundBasicInfoTypes(df: pd.DataFrame):
    df['type0'] = df.apply(
        lambda x: 1 if x.tags.find("开放式") >= 0 else 0, axis=1)
    df['type1'] = df.apply(
        lambda x: 1 if x.tags.find("低风险") >= 0 else 0, axis=1)

    lstType2 = getFundBasicInfoType2(df)
    df['type2'] = df.apply(lambda x: onProcType2(x, lstType2), axis=1)

    df['createtimey'] = df.apply(
        lambda x: datetime.strptime(x.createtime, '%Y-%m-%d').year, axis=1)
    df['createtimem'] = df.apply(
        lambda x: datetime.strptime(x.createtime, '%Y-%m-%d').month, axis=1)


def onProcSize(v):
    if type(v['size']) != str:
        return 0

    objSize = json.loads(v['size'])
    if len(objSize) > 0 and 'size' in objSize[len(objSize) - 1].keys():
        return objSize[len(objSize) - 1]['size']

    return 0


def procFundBasicInfoSize(df: pd.DataFrame):
    df['size0'] = df.apply(onProcSize, axis=1)


def mergeFundResultAndBasic(dfr: pd.DataFrame, dfb: pd.DataFrame) -> pd.DataFrame:
    if 'tags' in dfr.columns and 'createtime' in dfr.columns:
        return dfr.drop(columns=['tags', 'createtime']).replace([np.inf, -np.inf, np.NaN], 0).join(dfb.set_index('code'), on='code')

    if 'tags' in dfr.columns:
        return dfr.drop(columns=['tags']).replace([np.inf, -np.inf, np.NaN], 0).join(dfb.set_index('code'), on='code')

    return dfr.replace([np.inf, -np.inf, np.NaN], 0).join(dfb.set_index('code'), on='code')


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

        if 'startTime' in objManagers[i].keys():
            data['startDate'].append(datetime.fromtimestamp(
                objManagers[i]['startTime']).strftime('%Y%m%d'))
        else:
            data['startDate'].append('0')

        if 'endTime' in objManagers[i].keys():
            data['endDate'].append(datetime.fromtimestamp(
                objManagers[i]['endTime']).strftime('%Y%m%d'))
        else:
            data['endDate'].append('99999999')

        data['fundcode'].append(v['code'])
        data['fundname'].append(v['name'])
        data['company'].append(v['company'])

    return


def getManagers(df: pd.DataFrame):
    data = {'name': [], 'sex': [], 'education': [], 'country': [], 'resume': [
    ], 'startDate': [], 'endDate': [], 'fundcode': [], 'fundname': [], 'company': []}

    for index, row in df.iterrows():
        carr = parseManager(row, data)

    return data
