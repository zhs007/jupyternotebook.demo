import json
import os
import string
import pandas as pd
import plotly.graph_objects as go


def loadmsgs(fn):
    if os.path.getsize(fn) <= 0:
        return [], []
    
    lstbg = []
    lstfg = []
    
    with open(fn, "r") as read_file:
        msgs = json.load(read_file)
        curfg = []
        isfg = False
        
        for v in msgs:
            co = json.loads(v)
            
            if 'allowedGameFeatures' not in co and 'error' not in co and 'game' in co:
                if co['game']['mode'] == 'NORMAL' and co['game']['nextMode'] == 'NORMAL':
                    lstbg.append(co)
                
                if co['game']['mode'] == 'NORMAL' and co['game']['nextMode'] == 'FREESPIN':
                    curfg = []
                    curfg.append(co)
                    isfg = True
                
                if isfg and co['game']['mode'] == 'FREESPIN':
                    curfg.append(co)
                    if co['game']['nextMode'] == 'NORMAL':
                        isfg = False
                        lstfg.append(curfg)
                
    
    return lstbg, lstfg

def loadAllFiles():
    lstbg = []
    lstfg = []
    
    dirs = os.listdir('./')
    for v in dirs:
        if v.endswith('.json'):
            clstbg, clstfg = loadmsgs(v)
            lstbg = lstbg + clstbg
            lstfg = lstfg + clstfg
    
    return lstbg, lstfg

def analyzeWins(lstbg, lstfg):
    wins = {}
    
    for v in lstbg:
        if 'realityCheck' in v:
            k = v['realityCheck']['winnings']
            if k in wins:
                wins[k] = wins[k] + 1
            else:
                wins[k] = 1
                
    for arr in lstfg:
        curwin = 0
        
        for v in arr:
            if 'realityCheck' in v:
                curwin = curwin + v['realityCheck']['winnings']
            
        k = curwin
        if k in wins:
            wins[k] = wins[k] + 1
        else:
            wins[k] = 1
    
    return wins

def analyzeReels(lstbg, lstfg, reelnum):
    bgreels = []
    fgreels = []    
    for i in range(reelnum):
        bgreels.append({})
        fgreels.append({})        
    
    for v in lstbg:
        vg = v['game']
        if 'reels' in vg:
            for i in range(len(vg['reels'])):
                reel = vg['reels'][i]

                for s in reel:
                    if s in bgreels[i]:
                        bgreels[i][s] = bgreels[i][s] + 1
                    else:
                        bgreels[i][s] = 1
                            
    for arr in lstfg:
        for i in range(len(arr)):
            vg = arr[i]['game']            
            
            if i == 0:
                if 'reels' in vg:
                    for i in range(len(vg['reels'])):
                        reel = vg['reels'][i]

                        for s in reel:
                            if s in bgreels[i]:
                                bgreels[i][s] = bgreels[i][s] + 1
                            else:
                                bgreels[i][s] = 1
            else:
                if 'reels' in vg:
                    for i in range(len(vg['reels'])):
                        reel = vg['reels'][i]

                        for s in reel:
                            if s in fgreels[i]:
                                fgreels[i][s] = fgreels[i][s] + 1
                            else:
                                fgreels[i][s] = 1                                         
    
    return bgreels, fgreels

def analyzeSymbolWins(lstbg, lstfg):
    bg = {}
    fg = {}
    
    for v in lstbg:
        vg = v['game']
        if 'betWayWins' in vg:
            for win in vg['betWayWins']:
                if win['symbol'] in bg:
                    if win['length'] in bg[win['symbol']]:
                        bg[win['symbol']][win['length']] = bg[win['symbol']][win['length']] + win['numberOfCombinations']
                    else:
                        bg[win['symbol']][win['length']] = win['numberOfCombinations']
                else:
                    bg[win['symbol']] = {}
                    bg[win['symbol']][win['length']] = win['numberOfCombinations']
                        
    for arr in lstfg:
        for i in range(len(arr)):
            vg = arr[i]['game']
            
            if i == 0:
                if 'betWayWins' in vg:
                    for win in vg['betWayWins']:
                        if win['symbol'] in bg:
                            if win['length'] in bg[win['symbol']]:
                                bg[win['symbol']][win['length']] = bg[win['symbol']][win['length']] + win['numberOfCombinations']
                            else:
                                bg[win['symbol']][win['length']] = win['numberOfCombinations']
                        else:
                            bg[win['symbol']] = {}
                            bg[win['symbol']][win['length']] = win['numberOfCombinations']
            else:
                if 'betWayWins' in vg:
                    for win in vg['betWayWins']:
                        if win['symbol'] in fg:
                            if win['length'] in fg[win['symbol']]:
                                fg[win['symbol']][win['length']] = fg[win['symbol']][win['length']] + win['numberOfCombinations']
                            else:
                                fg[win['symbol']][win['length']] = win['numberOfCombinations']
                        else:
                            fg[win['symbol']] = {}
                            fg[win['symbol']][win['length']] = win['numberOfCombinations']                
                        
    return bg, fg

def getAllReels(lstbg, lstfg):
    lstreels = {}
    
    for v in lstbg:
        if v['game']['reelsNextSpin'] in lstreels:
            lstreels[v['game']['reelsNextSpin']] = lstreels[v['game']['reelsNextSpin']] + 1
        else:
            lstreels[v['game']['reelsNextSpin']] = 1
            
    for arr in lstfg:
        for v in arr:
            if v['game']['reelsNextSpin'] in lstreels:
                lstreels[v['game']['reelsNextSpin']] = lstreels[v['game']['reelsNextSpin']] + 1
            else:
                lstreels[v['game']['reelsNextSpin']] = 1            
    
    return lstreels

def getAllModes(lstbg, lstfg):
    lstmodes = {}
    
    for v in lstbg:
        if v['game']['mode'] in lstmodes:
            lstmodes[v['game']['mode']] = lstmodes[v['game']['mode']] + 1
        else:
            lstmodes[v['game']['mode']] = 1
            
        if v['game']['nextMode'] in lstmodes:
            lstmodes[v['game']['nextMode']] = lstmodes[v['game']['nextMode']] + 1
        else:
            lstmodes[v['game']['nextMode']] = 1
            
    for arr in lstfg:
        for v in arr:
            if v['game']['mode'] in lstmodes:
                lstmodes[v['game']['mode']] = lstmodes[v['game']['mode']] + 1
            else:
                lstmodes[v['game']['mode']] = 1

            if v['game']['nextMode'] in lstmodes:
                lstmodes[v['game']['nextMode']] = lstmodes[v['game']['nextMode']] + 1
            else:
                lstmodes[v['game']['nextMode']] = 1            
    
    return lstmodes

def findMysterySymbolReveal(lstbg, lstfg):
    bg = {}
    fg = {}
    
    for v in lstbg:
        if v['game']['mysterySymbolReveal'] in bg:
            bg[v['game']['mysterySymbolReveal']] = bg[v['game']['mysterySymbolReveal']] + 1
        else:
            bg[v['game']['mysterySymbolReveal']] = 1
            
    for arr in lstfg:
        for i in range(len(arr)):
            v = arr[i]
            
            if i == 0:
                if v['game']['mysterySymbolReveal'] in bg:
                    bg[v['game']['mysterySymbolReveal']] = bg[v['game']['mysterySymbolReveal']] + 1
                else:
                    bg[v['game']['mysterySymbolReveal']] = 1            
            else:
                if v['game']['mysterySymbolReveal'] in fg:
                    fg[v['game']['mysterySymbolReveal']] = fg[v['game']['mysterySymbolReveal']] + 1
                else:
                    fg[v['game']['mysterySymbolReveal']] = 1                            
    
    return bg, fg

def findMystery(lst):
    lstm = []
    
    for v in lst:
        if v['game']['mysterySymbolReveal'] != '':
            lstm.append(v)
    
    return lstm

def genDataframeModeReels(lstbg, lstfg):
    modes = getAllModes(lstbg, lstfg)
    reels = getAllReels(lstbg, lstfg)
    totalspin = len(lstbg) + len(lstfg)

    data = {'mode':[], 'reels': [], 'spins': [], 'probability': [], 'winnings': [], 'rtp': []}
    
    for k in modes:
        data['mode'].append(k)
        
    for k in reels:
        data['reels'].append(k)
    
    data['spins'].append(len(lstbg))
    data['spins'].append(len(lstfg))
    
    data['probability'].append(len(lstbg) / totalspin)
    data['probability'].append(len(lstfg) / totalspin)    
    
    winnings = 0
    for v in lstbg:
        winnings = winnings + v['realityCheck']['winnings']
        
    data['winnings'].append(winnings)
    data['rtp'].append(winnings / totalspin)
    
    winnings = 0
    for arr in lstfg:
        for v in arr:
            winnings = winnings + v['realityCheck']['winnings']
        
    data['winnings'].append(winnings)
    data['rtp'].append(winnings / totalspin)

    df = pd.DataFrame.from_dict(data)

    return df

def genDataframeWinnings(lstbg, lstfg):
    wins = analyzeWins(lstbg, lstfg)
    
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
    
def genDataframeSymbols(lstbg, lstfg):
    bg, fg = analyzeReels(lstbg, lstfg, 5)
    
    symbols = {}
    for i in range(5):
        for k in bg[i]:
            if k not in symbols:
                symbols[k] = 1
                
        for k in fg[i]:
            if k not in symbols:
                symbols[k] = 1                
    
    data = {'Symbol': []}
    for k in symbols:
        data['Symbol'].append(k)
    
    for i in range(5):
        data['BASE_REELSET[{}] probability'.format(i)] = []
        
        t = 0
        for k in bg[i]:
            t = t + bg[i][k]
            
        for k in symbols:
            if k in bg[i]:
                data['BASE_REELSET[{}] probability'.format(i)].append(bg[i][k] / t)
            else:
                data['BASE_REELSET[{}] probability'.format(i)].append(0)
                
    for i in range(5):
        data['FREESPIN_REELSET[{}] probability'.format(i)] = []
        
        t = 0
        for k in fg[i]:
            t = t + fg[i][k]
            
        for k in symbols:
            if k in fg[i]:
                data['FREESPIN_REELSET[{}] probability'.format(i)].append(fg[i][k] / t)
            else:
                data['FREESPIN_REELSET[{}] probability'.format(i)].append(0)                
        
    df = pd.DataFrame.from_dict(data)
    
    return df    

def genSymbolWins(lstbg, lstfg):
    bg, fg = analyzeSymbolWins(lstbg, lstfg)
    
    symbols = {}
    for k in bg:
        if k not in symbols:
            symbols[k] = 1

    for k in fg:
        if k not in symbols:
            symbols[k] = 1
            
    nums = {}
    for k in bg:
        for nk in bg[k]:
            if nk not in nums:
                nums[nk] = 1
    
    data = {' Symbol': []}
    
    for k in nums:
        data['BG - X{}'.format(k)] = []
        data['FG - X{}'.format(k)] = []
        
    for k in symbols:
        data[' Symbol'].append(k)
        
        if k in bg:
            for nk in nums:
                if nk in bg[k]:
                    data['BG - X{}'.format(nk)].append(bg[k][nk])
                else:
                    data['BG - X{}'.format(nk)].append(0)
        else:
            for nk in nums:
                data['BG - X{}'.format(nk)].append(0)
                
        if k in fg:
            for nk in nums:
                if nk in fg[k]:
                    data['FG - X{}'.format(nk)].append(fg[k][nk])
                else:
                    data['FG - X{}'.format(nk)].append(0)
        else:
            for nk in nums:
                data['FG - X{}'.format(nk)].append(0)                
    
        
    df = pd.DataFrame.from_dict(data)
    
    return df   

def genMysterySymbolReveal(lstbg, lstfg):
    bg, fg = findMysterySymbolReveal(lstbg, lstfg)
    
    symbols = {}
    bgt = 0
    fgt = 0
    
    for k in bg:
        if k not in symbols and k != '':
            symbols[k] = 1
        
        if k != '':
            bgt = bgt + bg[k]

    for k in fg:
        if k not in symbols and k != '':
            symbols[k] = 1
            
        if k != '':
            fgt = fgt + fg[k]            
    
    
    data = {'MysterySymbolReveal': [], 'BG probability': [], 'FG probability': []}  
    for k in symbols:
        data['MysterySymbolReveal'].append(k)
        
        if k in bg:
            data['BG probability'].append(bg[k] / bgt)
        else:
            data['BG probability'].append(0)            
            
        if k in fg:
            data['FG probability'].append(fg[k] / fgt)            
        else:
            data['FG probability'].append(0)            
    
    df = pd.DataFrame.from_dict(data)
    
    return df   
    