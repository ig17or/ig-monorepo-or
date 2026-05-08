from math import ceil,floor
from gyroArithm import mulDown,upscale,downscaleDown

AMP_PRECISION=None

def calculateInvariant(amplificationParameter,balances):
    Sum=0
    numTokens=len(balances)
    for i in range(numTokens):
        Sum+=balances[i]
    if Sum==0:return 0
    prevInvariant=0
    invariant = Sum
    ampTimesTotal = amplificationParameter * numTokens
    for i in range(255):
        P_D=numTokens*balances[0]
        for j in range(1,numTokens):
            P_D=ceil(((P_D*balances[j])*numTokens)/invariant)
        prevInvariant = invariant
        numerator=((numTokens*invariant)*invariant)+ceil(((ampTimesTotal*Sum)*P_D)/AMP_PRECISION)
        denominator=((numTokens+1)*invariant)+floor(((ampTimesTotal-AMP_PRECISION)*P_D)/AMP_PRECISION)
        invariant=ceil(numerator/denominator)
        if invariant > prevInvariant:
            if invariant - prevInvariant <= 1:
                return invariant
        elif prevInvariant - invariant <= 1:
            return invariant
        elif i>9:
            if abs(100-(invariant*100/prevInvariant))<0.000001:
                return invariant

def getTokenBalanceGivenInvariantAndAllOtherBalances(amplificationParameter,balances,invariant,tokenIndex):
    balancesLen=len(balances)
    ampTimesTotal = amplificationParameter * balancesLen
    Sum = balances[0]
    P_D = balances[0] * balancesLen
    for j in range(1,balancesLen):
        P_D=floor(((P_D*balances[j])*balancesLen)/invariant)
        Sum+=balances[j]
    Sum -= balances[tokenIndex]
    inv2=invariant**2
    c=(ceil(inv2/(ampTimesTotal*P_D))*AMP_PRECISION)*balances[tokenIndex]
    b=Sum+(floor(invariant/ampTimesTotal)*AMP_PRECISION)
    prevTokenBalance = 0
    tokenBalance=ceil((inv2+c)/(invariant+b))
    for i in range(255):
        prevTokenBalance = tokenBalance
        numerator=(tokenBalance**2)+c
        denominator=((tokenBalance*2)+b)-invariant
        tokenBalance=ceil(numerator/denominator)
        if tokenBalance > prevTokenBalance:
            if tokenBalance - prevTokenBalance <= 1:
                return tokenBalance
        elif prevTokenBalance - tokenBalance <= 1:
            return tokenBalance
        elif i>9:
            if abs(100-(tokenBalance*100/prevTokenBalance))<0.000001:
                return tokenBalance

def _calcOutGivenInSt(amplificationParameter,balances,tokenIndexIn,tokenIndexOut,tokenAmountIn,scalingFactors,fee):
    for i in range(len(balances)):
        balances[i]=upscale(balances[i],scalingFactors[i])
    tokenAmountIn=upscale(tokenAmountIn,scalingFactors[tokenIndexIn])
    invariant=calculateInvariant(amplificationParameter,balances)
    balances[tokenIndexIn] += tokenAmountIn
    finalBalanceOut = getTokenBalanceGivenInvariantAndAllOtherBalances(amplificationParameter,balances,invariant,tokenIndexOut)#//precisions[tokenIndexOut]
    unscaled=int((balances[tokenIndexOut]-finalBalanceOut-1)*fee)
    return downscaleDown(unscaled,scalingFactors[tokenIndexOut])

def calcOutGivenInSt(tickerIn,amount,tickerOut,params):
    global AMP_PRECISION
    AMP_PRECISION=1e3
    order=params['order'].split(':')
    _balances=list(map(int,params['balances'].split(':')))
    _scalingFactors=list(map(int,params['scalingFactors'].split(':')))
    if 'rate0' in params:
        AMP_PRECISION=1000
        rates=[int(value) for key,value in sorted(params.items()) if key.startswith('rate')]
        for i in range(len(rates)):
            _scalingFactors[i]=mulDown(_scalingFactors[i],rates[i])
    if 'bpt' in order:
        bptI=order.index('bpt')
        del order[bptI]
        del _balances[bptI]
        del _scalingFactors[bptI]
    return(_calcOutGivenInSt(int(params['amplificationParameter']),
                             _balances,
                             order.index(tickerIn),
                             order.index(tickerOut),
                             amount,
                             _scalingFactors,
                             float(1-(int(params['fee'])/10**18))))
