import json
import os
import string
import pandas as pd
import plotly.graph_objects as go


def loadjson(fn):
    if os.path.getsize(fn) <= 0:
        return None
    
    f = open(fn)
    stats = json.load(f)
    
    stats['wins'] = stats['totalWins']
    
    return stats

def genRTPs(stats):
    data = {'gamemodule':[], 'rtp': []}
    
    data['gamemodule'].append('base game')
    data['rtp'].append(float(stats['baseGame']['rtp']) * 100)
    
    data['gamemodule'].append('ligntning in base game')
    data['rtp'].append(float(stats['lightningBase']['rtp']) * 100)
    
    data['gamemodule'].append('free game')
    data['rtp'].append(float(stats['freeGame']['rtp']) * 100)
    
    data['gamemodule'].append('ligntning in free game')
    data['rtp'].append(float(stats['lightningFree']['rtp']) * 100)
    
    data['gamemodule'].append('total')
    data['rtp'].append(float(stats['rtp']) * 100)

    df = pd.DataFrame.from_dict(data)

    return df

def genMystery(stats, gamemod):
    data = {'symbol':[], 'weight': []}
    
    for v in stats[gamemod]['mysteryWeights']:
        data['symbol'].append(v['Symbol'])
        data['weight'].append(float(v['Weight']))

    df = pd.DataFrame.from_dict(data)

    return df

def genLightning(stats, gamemod):
    data = {'type':[], 'value':[], 'weight': []}
    
    for v in stats[gamemod]['symbolValue']:
        data['type'].append(v['Symbol'])
        data['value'].append(v['Value'])
        data['weight'].append(float(v['Weight']))

    df = pd.DataFrame.from_dict(data)

    return df

def analyzeWins(stats, gamemod):
    wins = {}
    
    cs = stats
    if gamemod in stats:
        cs = stats[gamemod]
    
    for v in cs['wins']:
        w = float(v['Winnings'])
        if w in wins:
            wins[w] = wins[w] + v['Times']
        else:
            wins[w] = v['Times']
    
    return wins

def mergeWins(objVal, lst):
    nObjVal = {}
    
    for k in objVal:
        k = float(k)
        nk = float(lst[0])
        
        if k > nk:
            for nv in lst:
                if k >= nv:
                    nk = nv
                else:
                    break
        
        if nk in nObjVal:
            nObjVal[nk] = nObjVal[nk] + objVal[k]
        else:
            nObjVal[nk] = objVal[k]
    
    return nObjVal

def genDataframeWinnings(stats, gamemod):
    wins = analyzeWins(stats, gamemod)
    
    data = {'winnings':[], 'times': []}
    for k in wins:
        data['winnings'].append(k)
        data['times'].append(wins[k])
        
    df = pd.DataFrame.from_dict(data)
    
    return df

def genDataframeWinningsEx(stats, gamemod, lstrange):
    wins = analyzeWins(stats, gamemod)
    wins = mergeWins(wins, lstrange)
    
    data = {'winnings':[], 'times': []}
    for k in wins:
        data['winnings'].append(k)
        data['times'].append(wins[k])
        
    df = pd.DataFrame.from_dict(data)
    
    return df

def showWinningsPie(df):
    fig = go.Figure(data=[go.Pie(labels=df['winnings'], values=df['times'])])
    fig.update_layout(title_text='Probability Of Winnings')
    fig.show()
    
def genSymbolWins(stats, gamemod):
    obj = {}
    data = {'symbol': [], 'x1':[], 'x2': [], 'x3': [], 'x4': [], 'x5': []}
    
    for v in stats[gamemod]['winLines']:
        if v['symbol'] in obj:
            obj[v['symbol']]['x' + str(v['matchCount'])] = v['totalCount']
        else:
            obj[v['symbol']] = {'symbol': v['symbol']}
            
    for k in obj:
        data['symbol'].append(k)
        
        if 'x1' in obj[k]:
            data['x1'].append(obj[k]['x1'])
        else:
            data['x1'].append(0)
            
        if 'x2' in obj[k]:
            data['x2'].append(obj[k]['x2'])
        else:
            data['x2'].append(0)
            
        if 'x3' in obj[k]:
            data['x3'].append(obj[k]['x3'])
        else:
            data['x3'].append(0)
            
        if 'x4' in obj[k]:
            data['x4'].append(obj[k]['x4'])
        else:
            data['x4'].append(0)
            
        if 'x5' in obj[k]:
            data['x5'].append(obj[k]['x5'])
        else:
            data['x5'].append(0)
        
    df = pd.DataFrame.from_dict(data)
    
    return df    