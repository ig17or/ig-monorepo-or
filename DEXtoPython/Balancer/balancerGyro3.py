from gyroArithm import *

_L_VS_LPLUS_MIN = int(1.3e18)
_L_MAX = int(1e34)
_L_THRESHOLD_SIMPLE_NUMERICS = int(2e31)
_INVARIANT_MIN_ITERATIONS = 5
_INVARIANT_SHRINKING_FACTOR_PER_STEP = 8
_MAX_BALANCES = int(1e29)

def _calculateCubicTerms(balances, root3Alpha):
    a=ONE-mulDownU(mulDownU(root3Alpha,root3Alpha),root3Alpha)
    bterm=balances[0] + balances[1] + balances[2]
    mb=mulDownU(mulDownU(bterm,root3Alpha),root3Alpha)
    cterm=mulDownU(balances[0],balances[1])+mulDownU(balances[1],balances[2])+mulDownU(balances[2],balances[0])
    mc=mulDownU(cterm,root3Alpha)
    md=mulDownU(mulDownU(balances[0],balances[1]),balances[2])
    return a,mb,mc,md

def _calculateCubicStartingPoint(a, mb, mc, md):
    radic=mulUpU(mb,mb)+mulUpU(a,mc*3)
    lplus=divUpU(mb+sqrt_(radic,5),a*3)
    alpha=ONE - a
    if alpha>=int(0.5e18):
        l0=mulUpU(lplus,int(1.5e18))
    else:
        l0=mulUpU(lplus,int(2e18))
    l_lower=mulUpU(lplus,_L_VS_LPLUS_MIN)
    return l_lower,l0

def _calcNewtonDelta(mb, mc, md, root3Alpha, l_lower, rootEst):
    if rootEst>_L_MAX:raise ValueError('INVARIANT_TOO_LARGE_NEWTON')
    if rootEst<l_lower:raise ValueError('INVARIANT_UNDERFLOW')
    rootEst2 = mulDownU(rootEst,rootEst)
    dfRootEst = mulDownU(rootEst*3,rootEst)
    dfRootEst = dfRootEst - mulDownU(mulDownU(mulDownU(dfRootEst,root3Alpha),root3Alpha),root3Alpha)
    dfRootEst = dfRootEst - 2 * mulDownU(rootEst,mb) - mc
    deltaMinus=0
    deltaPlus=0
    if (rootEst <= _L_THRESHOLD_SIMPLE_NUMERICS):
        deltaMinus = mulDownU(rootEst2,rootEst);
        deltaMinus = deltaMinus - mulDownU(mulDownU(mulDownU(deltaMinus,root3Alpha),root3Alpha),root3Alpha)
        deltaMinus = divDownU(deltaMinus,dfRootEst)
        deltaPlus = mulDownU(rootEst2,mb)
        deltaPlus = divDownU(deltaPlus + mulDownU(rootEst,mc),dfRootEst)
        deltaPlus = deltaPlus + divDownU(md,dfRootEst)
    else:
        deltaMinus=mulDownLargeSmallU(rootEst2,rootEst)
        deltaMinus = deltaMinus - mulDownLargeSmallU(mulDownLargeSmallU(mulDownLargeSmallU(deltaMinus,root3Alpha),root3Alpha),root3Alpha)
        deltaPlus = deltaPlus + mulDownU(mc,rootEst);
        deltaPlus = divDownLargeU(deltaPlus,dfRootEst, int(1e12), int(1e6));
        deltaPlus = deltaPlus + divDownU(md,dfRootEst)
    deltaIsPos = (deltaPlus >= deltaMinus)
    if deltaIsPos:
        deltaAbs=deltaPlus - deltaMinus
    else:
        deltaAbs=deltaMinus - deltaPlus
    return deltaAbs,deltaIsPos

def _runNewtonIteration(mb, mc, md, root3Alpha, l_lower, rootEst):
    deltaAbsPrev = 0
    for iteration in range(255):
        deltaAbs,deltaIsPos = _calcNewtonDelta(mb, mc, md, root3Alpha, l_lower, rootEst)
        if (deltaAbs <= 1):return rootEst
        if (iteration >= _INVARIANT_MIN_ITERATIONS and deltaIsPos):return rootEst
        if (iteration >= _INVARIANT_MIN_ITERATIONS and deltaAbs >= deltaAbsPrev // _INVARIANT_SHRINKING_FACTOR_PER_STEP):return rootEst
        deltaAbsPrev = deltaAbs
        if (deltaIsPos):rootEst = rootEst+deltaAbs
        else:rootEst = rootEst-deltaAbs
    raise ValueError('INVARIANT_DIDNT_CONVERGE')

def _calculateCubic(a, mb, mc, md, root3Alpha):
    l_lower, rootEst = _calculateCubicStartingPoint(a, mb, mc, md)
    rootEst = _runNewtonIteration(mb, mc, md, root3Alpha, l_lower, rootEst)
    if rootEst>_L_MAX:raise ValueError('INVARIANT_TOO_LARGE_CUBIC')
    return rootEst

def _calculateInvariant(balances,root3Alpha):
    for b in balances:
        if b>_MAX_BALANCES:raise ValueError('BALANCES_TOO_LARGE')
    a,mb,mc,md = _calculateCubicTerms(balances, root3Alpha)
    return _calculateCubic(a, mb, mc, md, root3Alpha)

def _calculateVirtualOffset(balances,root3Alpha):
    invariant=_calculateInvariant(balances,root3Alpha)
    return mulDownU(invariant,root3Alpha)

def _calcOutGivenIn(balanceIn,balanceOut,amountIn,virtualOffset):
    virtInOver = balanceIn + mulUpU(virtualOffset,ONE + 2)
    virtOutUnder = balanceOut + mulDownU(virtualOffset,ONE - 1)
    amountOut=divDownU(mulDownU(virtOutUnder,amountIn),virtInOver+amountIn)
    if amountOut>balanceOut:raise ValueError('ASSET_BOUNDS_EXCEEDED')
    return amountOut

def calcOutGivenInGy3(tickerIn,amount,tickerOut,params):
    fee=1-(int(params['fee'])/10**18)
    order=params['order'].split(':')
    iIn=order.index(tickerIn)
    iOut=order.index(tickerOut)
    balances=[int(b) for b in params['balances'].split(':')]
    scalingFactors=[int(sf) for sf in params['scalingFactors'].split(':')]
    balancesScaled=[mulDownU(balances[i],scalingFactors[i]) for i in range(len(balances))]
    virtOffs=_calculateVirtualOffset(balancesScaled,int(params['root3Alpha']))
    amountOutScaled=_calcOutGivenIn(balancesScaled[iIn],balancesScaled[iOut],mulDownU(amount,scalingFactors[iIn]),virtOffs)
    return int(divDownU(amountOutScaled,scalingFactors[iOut])*fee)
