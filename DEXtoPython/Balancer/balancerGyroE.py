from collections import namedtuple
from gyroArithm import *

Params=namedtuple('Params',['alpa','beta','c','s','Lambda'])
Vector2=namedtuple('Vector2',['x','y'])
DerivedParams=namedtuple('DerivedParams',['tauAlpha','tauBeta','u','v','w','z','dSq'])
QParams=namedtuple('QParams',['a','b','c'])

_MAX_BALANCES = int(1e34)
_MAX_INVARIANT = int(3e37)

def maxBalances0(p, d, r):
    termXp1=divXpU(d.tauBeta.x-d.tauAlpha.x,d.dSq)
    termXp2=divXpU(d.tauBeta.y-d.tauAlpha.y,d.dSq)
    xp=mulDownXpToNpU(mulDownMagU(mulDownMagU(r.y,p.Lambda),p.c),termXp1)
    if termXp2 > 0:
        xp=xp+mulDownXpToNpU(mulDownMagU(r.y,p.s),termXp2)
    else:
        xp=xp+mulDownXpToNpU(mulUpMagU(r.x,p.s),termXp2)
    return xp

def maxBalances1(p, d, r):
    termXp1=divXpU(d.tauBeta.x-d.tauAlpha.x,d.dSq)
    termXp2=divXpU(d.tauAlpha.y-d.tauBeta.y,d.dSq)
    yp=mulDownXpToNpU(mulDownMagU(mulDownMagU(r.y,p.Lambda),p.s),termXp1)
    if termXp2 > 0:
        yp=yp+mulDownXpToNpU(mulDownMagU(r.y,p.c),termXp2)
    else:
        yp=yp+mulDownXpToNpU(mulUpMagU(r.x,p.c),termXp2)
    return yp

def checkAssetBounds(params, derived, invariant, newBal, assetIndex):
    if (assetIndex == 0):
        xPlus = maxBalances0(params, derived, invariant)
        if not (newBal<=_MAX_BALANCES and newBal<=xPlus):
            raise ValueError('ASSET_BOUNDS_EXCEEDED_0')
    yPlus=maxBalances1(params, derived, invariant)
    if not (newBal<=_MAX_BALANCES and newBal<=yPlus):
        raise ValueError('ASSET_BOUNDS_EXCEEDED_1')

def virtualOffset0(p,d,r):
    termXp=divXpU(d.tauBeta.x,d.dSq)
    if d.tauBeta.x > 0:
        a=mulUpXpToNpU(mulUpMagU(mulUpMagU(r.x,p.Lambda),p.c),termXp)
    else:
        a=mulUpXpToNpU(mulDownMagU(mulDownMagU(r.y,p.Lambda),p.c),termXp)
    a=a+mulUpXpToNpU(mulUpMagU(r.x,p.s),divXpU(d.tauBeta.y,d.dSq))
    return a

def virtualOffset1(p,d,r):
    termXp=divXpU(d.tauAlpha.x,d.dSq)
    if d.tauAlpha.x < 0:
        b=mulUpXpToNpU(mulUpMagU(mulUpMagU(r.x,p.Lambda),p.s),-termXp)
    else:
        b=mulUpXpToNpU(mulDownMagU(mulDownMagU(-r.y,p.Lambda),p.s),termXp)
    b=b+mulUpXpToNpU(mulUpMagU(r.x,p.c),divXpU(d.tauAlpha.y,d.dSq))
    return b

def calcXpXpDivLambdaLambda(x,r,Lambda,s,c,tauBeta,dSq):
    sqVars = Vector2(mulXpU(dSq,dSq), mulUpMagU(r.x,r.x))
    q=QParams(0,0,0)
    termXp=divXpU(mulXpU(tauBeta.x,tauBeta.y),sqVars.x)
    if (termXp > 0):
        q=q._replace(a=mulUpMagU(sqVars.y,2 * s))
        q=q._replace(a=mulUpXpToNpU(mulUpMagU(q.a,c),termXp + 7))
    else:
        q=q._replace(a=mulDownMagU(mulDownMagU(r.y,r.y),2 * s))
        q=q._replace(a=mulUpXpToNpU(mulDownMagU(q.a,c),termXp))
    if tauBeta.x < 0:
        q=q._replace(b=mulUpXpToNpU(mulUpMagU(mulUpMagU(r.x,x),2 * c),divXpU(-tauBeta.x,dSq)+3))
    else:
        q=q._replace(b=mulUpXpToNpU(mulDownMagU(mulDownMagU(-r.y,x),2 * c),divXpU(tauBeta.x,dSq)))
    q=q._replace(a=q.a + q.b)
    termXp=divXpU(mulXpU(tauBeta.y,tauBeta.y),sqVars.x)+7
    q=q._replace(b=mulUpMagU(sqVars.y,s))
    q=q._replace(b=mulUpXpToNpU(mulUpMagU(q.b,s),termXp))
    q=q._replace(c=mulUpXpToNpU(mulDownMagU(mulDownMagU(-r.y,x),2 * s),divXpU(tauBeta.y,dSq)))
    q=q._replace(b=q.b+q.c+mulUpMagU(x,x))
    if q.b>0:
        q=q._replace(b=divUpMagU(q.b,Lambda))
    else:
        q=q._replace(b=divDownMagU(q.b,Lambda))
    q=q._replace(a=q.a+q.b)
    if q.a>0:
        q=q._replace(a=divUpMagU(q.a,Lambda))
    else:
        q=q._replace(a=divDownMagU(q.a,Lambda))
    termXp=divXpU(mulXpU(tauBeta.x,tauBeta.x),sqVars.x)+7
    val=mulUpMagU(mulUpMagU(sqVars.y,c),c)
    return mulUpXpToNpU(val,termXp)+q.a

def solveQuadraticSwap(Lambda,x,s,c,r,ab,tauBeta,dSq):
    lamBar=Vector2(0,0)
    lamBar=lamBar._replace(x = ONE_XP - divDownMagU(divDownMagU(ONE_XP,Lambda),Lambda))
    lamBar=lamBar._replace(y = ONE_XP - divUpMagU(divUpMagU(ONE_XP,Lambda),Lambda))
    q=QParams(0,0,0)
    xp = x - ab.x
    if (xp > 0):
        q=q._replace(b=mulUpXpToNpU(mulDownMagU(mulDownMagU(-xp,s),c),divXpU(lamBar.y,dSq)))
    else:
        q=q._replace(b=mulUpXpToNpU(mulUpMagU(mulUpMagU(-xp,s),c),divXpU(lamBar.x,dSq)+1))
    sTerm=Vector2(0,0)
    sTerm=sTerm._replace(x=divXpU(mulDownMagU(mulDownMagU(lamBar.y,s),s),dSq))
    sTerm=sTerm._replace(y=mulUpMagU(lamBar.x,s))
    sTerm=sTerm._replace(y=divXpU(mulUpMagU(sTerm.y,s),dSq+1)+1)
    sTerm=Vector2(ONE_XP - sTerm.x, ONE_XP - sTerm.y)
    q=q._replace(c=-calcXpXpDivLambdaLambda(x, r, Lambda, s, c, tauBeta, dSq))
    q=q._replace(c=q.c+mulDownXpToNpU(mulDownMagU(r.y,r.y),sTerm.y))
    if q.c>0:
        q=q._replace(c=sqrt_(q.c,5))
    else:
        q=q._replace(c=0)
    if (q.b - q.c > 0):
        q=q._replace(a=mulUpXpToNpU(q.b-q.c,divXpU(ONE_XP,sTerm.y)+1))
    else:
        q=q._replace(a=mulUpXpToNpU(q.b-q.c,divXpU(ONE_XP,sTerm.x)))
    return q.a + ab.y

def calcYGivenX(x,params,d,r):
    ab = Vector2(virtualOffset0(params, d, r), virtualOffset1(params, d, r))
    y = solveQuadraticSwap(params.Lambda, x, params.s, params.c, r, ab, d.tauBeta, d.dSq)
    return y

def calcXGivenY(y,params,d,r):
    ba = Vector2(virtualOffset1(params, d, r), virtualOffset0(params, d, r));
    x = solveQuadraticSwap(params.Lambda, y, params.c, params.s, r, ba, Vector2(-d.tauAlpha.x, d.tauAlpha.y), d.dSq)
    return x

def calcOutGivenIn(balances,amountIn,tokenInIsToken0,params,derived,invariant):
    if tokenInIsToken0:
        ixIn = 0
        ixOut = 1
        calcGiven = calcYGivenX
    else:
        ixIn = 1
        ixOut = 0
        calcGiven = calcXGivenY
    balInNew=balances[ixIn]+amountIn
    checkAssetBounds(params, derived, invariant, balInNew, ixIn)
    balOutNew = calcGiven(balInNew, params, derived, invariant)
    amountOut = balances[ixOut]-balOutNew
    return amountOut

def calcAtAChi(x,y,p,d):
    dSq2=mulXpU(d.dSq,d.dSq)
    termXp=divXpU(divDownMagU(divDownMagU(d.w,p.Lambda)+d.z,p.Lambda),dSq2)
    val=mulDownXpToNpU(mulDownMagU(x,p.c)-mulDownMagU(y,p.s),termXp)
    termNp=mulDownMagU(mulDownMagU(x,p.Lambda),p.s)+mulDownMagU(mulDownMagU(y,p.Lambda),p.c)
    val=val+mulDownXpToNpU(termNp,divXpU(d.u,dSq2))
    termNp=mulDownMagU(x,p.s)+mulDownMagU(y,p.c)
    val=val+mulDownXpToNpU(termNp,divXpU(d.v,dSq2))
    return val

def calcMinAtxAChiySqPlusAtxSq(x,y,p,d):
    termNp=mulUpMagU(mulUpMagU(mulUpMagU(x,x),p.c),p.c)+mulUpMagU(mulUpMagU(mulUpMagU(y,y),p.s),p.s)
    termNp=termNp-mulDownMagU(mulDownMagU(mulDownMagU(x,y),p.c * 2),p.s)
    termXp=mulXpU(d.u,d.u)+divDownMagU(mulXpU(2*d.u,d.v),p.Lambda)+divDownMagU(divDownMagU(mulXpU(d.v,d.v),p.Lambda),p.Lambda)
    termXp=divXpU(termXp,mulXpU(mulXpU(mulXpU(d.dSq,d.dSq),d.dSq),d.dSq))
    val=mulDownXpToNpU(-termNp,termXp)
    val=val+mulDownXpToNpU(divDownMagU(divDownMagU(termNp-9,p.Lambda),p.Lambda),divXpU(ONE_XP,d.dSq))
    return val

def calc2AtxAtyAChixAChiy(x,y,p,d):
    termNp=mulDownMagU(mulDownMagU(mulDownMagU(x,x)-mulUpMagU(y,y),2 * p.c),p.s)
    xy=mulDownMagU(y,2 * x)
    termNp=termNp+mulDownMagU(mulDownMagU(xy,p.c),p.c)-mulDownMagU(mulDownMagU(xy,p.s),p.s)
    termXp=mulXpU(d.z,d.u)+divDownMagU(divDownMagU(mulXpU(d.w,d.v),p.Lambda),p.Lambda)
    termXp=termXp+divDownMagU(mulXpU(d.w,d.u)+mulXpU(d.z,d.v),p.Lambda)
    termXp=divXpU(termXp,mulXpU(mulXpU(mulXpU(d.dSq,d.dSq),d.dSq),d.dSq))
    val=mulDownXpToNpU(termNp,termXp)
    return val

def calcMinAtyAChixSqPlusAtySq(x,y,p,d):
    termNp=mulUpMagU(mulUpMagU(mulUpMagU(x,x),p.s),p.s)+mulUpMagU(mulUpMagU(mulUpMagU(y,y),p.c),p.c)
    termNp=termNp+mulUpMagU(mulUpMagU(mulUpMagU(x,y),p.s * 2),p.c)
    termXp=mulXpU(d.z,d.z)+divDownMagU(divDownMagU(mulXpU(d.w,d.w),p.Lambda),p.Lambda)
    termXp=termXp+divDownMagU(mulXpU(2*d.z,d.w),p.Lambda)
    termXp=divXpU(termXp,mulXpU(mulXpU(mulXpU(d.dSq,d.dSq),d.dSq),d.dSq))
    val=mulDownXpToNpU(-termNp,termXp)
    val=val+mulDownXpToNpU(termNp-9,divXpU(ONE_XP,d.dSq))
    return val

def calcInvariantSqrt(x,y,p,d):
    val = calcMinAtxAChiySqPlusAtxSq(x, y, p, d) + calc2AtxAtyAChixAChiy(x, y, p, d)
    val = val + calcMinAtyAChixSqPlusAtySq(x, y, p, d)
    err = (mulUpMagU(x,x) + mulUpMagU(y,y)) // int(1e38)
    if val>0:
        val=sqrt_(val,5)
    else:
        val=0
    return val,err

def calcAChiAChiInXp(p,d):
    dSq3=mulXpU(mulXpU(d.dSq,d.dSq),d.dSq)
    val=mulUpMagU(p.Lambda,divXpU(mulXpU(2*d.u,d.v),dSq3))
    val=val+mulUpMagU(mulUpMagU(divXpU(mulXpU(d.u+1,d.u+1),dSq3),p.Lambda),p.Lambda)
    val=val+divXpU(mulXpU(d.v,d.v),dSq3)
    termXp=divUpMagU(d.w,p.Lambda)+d.z
    val=val+divXpU(mulXpU(termXp,termXp),dSq3)
    return val

def calculateInvariantWithError(balances,params,derived):
    x,y=balances[0],balances[1]
    assert x+y<=_MAX_BALANCES,'MAX_ASSETS_EXCEEDED'
    AtAChi = calcAtAChi(x, y, params, derived)
    sqrt,err=calcInvariantSqrt(x, y, params, derived)
    if sqrt>0:
        err = divUpMagU(err+1,2*sqrt)
    else:
        if err>0:
            err=sqrt_(err,5)
        else:
            err=int(1e9)
    err=((mulUpMagU(params.Lambda,x+y)//ONE_XP)+err+1)*20
    mulDenominator=divXpU(ONE_XP,calcAChiAChiInXp(params, derived) - ONE_XP)
    invariant=mulDownXpToNpU(AtAChi+sqrt-err,mulDenominator)
    err=mulUpXpToNpU(err,mulDenominator)
    err=err+((mulUpXpToNpU(invariant,mulDenominator)*((params.Lambda*params.Lambda)//int(1e36)))*40)//ONE_XP+1
    assert invariant+err<=_MAX_INVARIANT,'MAX_INVARIANT_EXCEEDED'
    return invariant,err

def _upscale(amount,scalingFactor):
    return mulDown(amount, scalingFactor)

def _downscaleDown(amount,scalingFactor):
    return divDown(amount, scalingFactor)

def _balancesFromTokenInOut(balanceTokenIn,balanceTokenOut,tokenInIsToken0):
    if tokenInIsToken0:
        return [balanceTokenIn,balanceTokenOut]
    else:
        return [balanceTokenOut,balanceTokenIn]

def onSwap(amount,tokenInIsToken0,balanceTokenIn,balanceTokenOut,scalingFactorTokenIn,scalingFactorTokenOut,eclpParams,derivedECLPParams,fee):
    balanceTokenIn = _upscale(balanceTokenIn, scalingFactorTokenIn)
    balanceTokenOut = _upscale(balanceTokenOut, scalingFactorTokenOut)
    balances = _balancesFromTokenInOut(balanceTokenIn, balanceTokenOut, tokenInIsToken0)
    currentInvariant,invErr = calculateInvariantWithError(balances, eclpParams, derivedECLPParams)
    invariant = Vector2(currentInvariant + 2 * invErr, currentInvariant)
    feeAmount=mulUp(amount,fee)
    amount=_upscale(amount-feeAmount, scalingFactorTokenIn)
    amountOut= calcOutGivenIn(balances, amount, tokenInIsToken0, eclpParams, derivedECLPParams, invariant)
    return _downscaleDown(amountOut, scalingFactorTokenOut)

def calcOutGivenInGyE(tickerIn,amount,tickerOut,params):
    order=params['order'].split(':')
    iIn=order.index(tickerIn)
    iOut=order.index(tickerOut)
    balances=[int(item) for item in params['balances'].split(':')]
    scalingFactors=[int(item) for item in params['scalingFactors'].split(':')]
    rates=[int(item) for item in params['rates'].split(':')]
    for i in range(len(rates)):
        scalingFactors[i]=mulDown(scalingFactors[i],rates[i])
    d=[int(item) for item in params['d'].split(':')]
    tauAlpha=Vector2(d[0],d[1])
    tauBeta=Vector2(d[2],d[3])
    return onSwap(amount,
                  tickerIn==order[0],
                  balances[iIn],
                  balances[iOut],
                  scalingFactors[iIn],
                  scalingFactors[iOut],
                  Params._make([int(item) for item in params['params'].split(':')]),
                  DerivedParams(tauAlpha,tauBeta,d[4],d[5],d[6],d[7],d[8]),
                  int(params['fee']))
