from gyroArithm import *

def _calculateQuadraticTerms(balances, sqrtAlpha, sqrtBeta):
    a=ONE-divDown(sqrtAlpha,sqrtBeta)
    bterm0=divDown(balances[1],sqrtBeta)
    bterm1=mulDown(balances[0],sqrtAlpha)
    mb=bterm0+bterm1
    mc=mulDown(balances[0],balances[1])
    bSquare=mulDown(mulDown(mulDown(balances[0],balances[0]),sqrtAlpha),sqrtAlpha)
    bSq2=divDown(mulDown(mulDown(mulDown(balances[0],balances[1]),2*ONE),sqrtAlpha),sqrtBeta)
    bSq3=divDown(mulDown(balances[1],balances[1]),mulUp(sqrtBeta,sqrtBeta))
    bSquare=bSquare+bSq2+bSq3
    return a,mb,bSquare,mc

def _calculateQuadratic(a, mb, bSquare, mc):
    denominator=mulUp(a,2*ONE)
    addTerm=mulDown(mulDown(mc,4*ONE),a)
    radicand=bSquare+addTerm
    sqrResult=sqrt_(radicand,5)
    numerator=mb+sqrResult
    invariant=divDown(numerator,denominator)
    return invariant

def _calculateInvariant(balances,sqrtAlpha,sqrtBeta):
    a,mb,bSquare,mc = _calculateQuadraticTerms(balances, sqrtAlpha, sqrtBeta)
    return _calculateQuadratic(a, mb, bSquare, mc)

def _calculateVirtualParameter0(invariant,_sqrtBeta):
    return divDown(invariant,_sqrtBeta)

def _calculateVirtualParameter1(invariant,_sqrtAlpha):
    return mulDown(invariant,_sqrtAlpha)

def _virtualParameters(parameter0,sqrtParam,invariant):
    if parameter0:
        return _calculateVirtualParameter0(invariant, sqrtParam)
    else:
        return _calculateVirtualParameter1(invariant, sqrtParam)

def _getVirtualParameters(sqrtParams,invariant):
    virtualParameters0 = _virtualParameters(True, sqrtParams[1], invariant)
    virtualParameters1 = _virtualParameters(False, sqrtParams[0], invariant)
    return [virtualParameters0,virtualParameters1]

def _calculateCurrentValues(balanceTokenIn,balanceTokenOut,tokenInIsToken0,sqrtParams):
    if tokenInIsToken0:
        balances=[balanceTokenIn,balanceTokenOut]
    else:
        balances=[balanceTokenOut,balanceTokenIn]
    currentInvariant = _calculateInvariant(balances, sqrtParams[0], sqrtParams[1])
    virtualParam = _getVirtualParameters(sqrtParams, currentInvariant)
    if tokenInIsToken0:
        virtualParamIn,virtualParamOut=virtualParam[0],virtualParam[1]
    else:
        virtualParamIn,virtualParamOut=virtualParam[1],virtualParam[0]
    return currentInvariant,virtualParamIn,virtualParamOut

def _calcOutGivenIn(balanceIn,balanceOut,amountIn,virtualOffsetIn,virtualOffsetOut):
    virtInOver = balanceIn+mulUp(virtualOffsetIn,ONE+2)
    virtOutUnder = balanceOut+mulDown(virtualOffsetOut,ONE-1)
    amountOut = divDown(mulDown(virtOutUnder,amountIn),virtInOver+amountIn)
    if not amountOut<=balanceOut:#raise ValueError('ASSET_BOUNDS_EXCEEDED')
        amountOut=0
    return amountOut

def onSwap(balanceTokenIn,scalingFactorTokenIn,balanceTokenOut,scalingFactorTokenOut,tokenInIsToken0,sqrtParams,amount,fee):
    balanceTokenIn=upscale(balanceTokenIn,scalingFactorTokenIn)
    balanceTokenOut=upscale(balanceTokenOut,scalingFactorTokenOut)
    _,virtualParamIn,virtualParamOut=_calculateCurrentValues(balanceTokenIn,balanceTokenOut,tokenInIsToken0,sqrtParams)
    feeAmount=mulUp(amount,fee)
    amount=upscale(amount-feeAmount,scalingFactorTokenIn)
    amountOut=_calcOutGivenIn(balanceTokenIn,balanceTokenOut,amount,virtualParamIn,virtualParamOut)
    return downscaleDown(amountOut, scalingFactorTokenOut)

def calcOutGivenInGy2(tickerIn,amount,tickerOut,params):
    order=params['order'].split(':')              
    iIn=order.index(tickerIn)                                            
    iOut=order.index(tickerOut)
    balances=[int(item) for item in params['balances'].split(':')]
    scalingFactors=[int(item) for item in params['scalingFactors'].split(':')]
    sqrtParameters=[int(item) for item in params['sqrtParameters'].split(':')]
    return onSwap(balances[iIn],
                  scalingFactors[iIn],
                  balances[iOut],
                  scalingFactors[iOut],
                  tickerIn==order[0],
                  sqrtParameters,
                  amount,
                  int(params['fee']))
