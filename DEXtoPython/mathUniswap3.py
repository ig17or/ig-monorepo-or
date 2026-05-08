import math

MIN_TICK = -887272
MAX_TICK = -MIN_TICK
MIN_SQRT_RATIO = 4295128739
MAX_SQRT_RATIO = 1461446703485210103287273052203988822378723970342
uint256max=115792089237316195423570985008687907853269984665640564039457584007913129639935
uint160max=1461501637330902918203684832716283019655932542975
uint128max=340282366920938463463374607431768211455
uint64max=18446744073709551615
uint32max=4294967295
uint16max=65535
uint8max=255
RESOLUTION = 96
Q96 = 0x1000000000000000000000000
Q128 = 0x100000000000000000000000000000000
modulus = 2 ** 256
fee2spacing={100:1,500:10,3000:60,10000:200}
wordBitmap=None

def position(tick):
    return tick>>8,tick%256

def mostSignificantBit(x):
    assert x>0
    r=0
    if (x >= 0x100000000000000000000000000000000):
        x >>= 128;
        r += 128;
    if (x >= 0x10000000000000000):
        x >>= 64
        r += 64
    if (x >= 0x100000000):
        x >>= 32
        r += 32
    if (x >= 0x10000):
        x >>= 16
        r += 16
    if (x >= 0x100):
        x >>= 8
        r += 8
    if (x >= 0x10):
        x >>= 4
        r += 4
    if (x >= 0x4):
        x >>= 2
        r += 2
    if (x >= 0x2):
        r += 1
    return r

def leastSignificantBit(x):
    assert x>0
    r = 255
    if (x & uint128max > 0):
        r -= 128
    else:
        x >>= 128
    if (x & uint64max > 0):
        r -= 64
    else:
        x >>= 64
    if (x & uint32max > 0):
        r -= 32
    else:
        x >>= 32
    if (x & uint16max > 0):
        r -= 16
    else:
        x >>= 16
    if (x & uint8max > 0):
        r -= 8
    else:
        x >>= 8
    if (x & 0xf > 0):
        r -= 4
    else:
        x >>= 4
    if (x & 0x3 > 0):
        r -= 2
    else:
        x >>= 2
    if (x & 0x1 > 0):
        r -= 1
    return r

def selfWordPos(wordPos):
    if wordPos in wordBitmap:
        return wordBitmap[wordPos]
    else:
        return 0

def nextInitializedTickWithinOneWord(tick,tickSpacing,lte):
    compressed =int(tick/tickSpacing)
    if tick < 0 and tick % tickSpacing != 0:
        compressed-=1
    if lte:
        wordPos,bitPos = position(compressed)
        mask = (1 << bitPos) - 1 + (1 << bitPos)
        masked = selfWordPos(wordPos)&mask
        initialized = masked != 0
        if initialized:
            Next=(compressed - (bitPos - mostSignificantBit(masked))) * tickSpacing
        else:
            Next=(compressed - bitPos) * tickSpacing
    else:
        wordPos,bitPos = position(compressed + 1)
        mask = ~((1 << bitPos) - 1)
        masked=selfWordPos(wordPos)&mask
        initialized = masked != 0
        if initialized:
            Next=(compressed + 1 + (leastSignificantBit(masked) - bitPos)) * tickSpacing
        else:
            Next=(compressed + 1 + (uint8max - bitPos)) * tickSpacing
    return Next,initialized

def getSqrtRatioAtTick(tick):
    absTick=abs(tick)
    assert absTick<=MAX_TICK
    if absTick & 0x1 != 0 :
        ratio=0xfffcb933bd6fad37aa2d162d1a594001
    else:
        ratio=0x100000000000000000000000000000000
    if (absTick & 0x2 != 0): ratio = (ratio * 0xfff97272373d413259a46990580e213a) >> 128
    if (absTick & 0x4 != 0): ratio = (ratio * 0xfff2e50f5f656932ef12357cf3c7fdcc) >> 128
    if (absTick & 0x8 != 0): ratio = (ratio * 0xffe5caca7e10e4e61c3624eaa0941cd0) >> 128
    if (absTick & 0x10 != 0): ratio = (ratio * 0xffcb9843d60f6159c9db58835c926644) >> 128
    if (absTick & 0x20 != 0): ratio = (ratio * 0xff973b41fa98c081472e6896dfb254c0) >> 128
    if (absTick & 0x40 != 0): ratio = (ratio * 0xff2ea16466c96a3843ec78b326b52861) >> 128
    if (absTick & 0x80 != 0): ratio = (ratio * 0xfe5dee046a99a2a811c461f1969c3053) >> 128
    if (absTick & 0x100 != 0): ratio = (ratio * 0xfcbe86c7900a88aedcffc83b479aa3a4) >> 128
    if (absTick & 0x200 != 0): ratio = (ratio * 0xf987a7253ac413176f2b074cf7815e54) >> 128
    if (absTick & 0x400 != 0): ratio = (ratio * 0xf3392b0822b70005940c7a398e4b70f3) >> 128
    if (absTick & 0x800 != 0): ratio = (ratio * 0xe7159475a2c29b7443b29c7fa6e889d9) >> 128
    if (absTick & 0x1000 != 0): ratio = (ratio * 0xd097f3bdfd2022b8845ad8f792aa5825) >> 128
    if (absTick & 0x2000 != 0): ratio = (ratio * 0xa9f746462d870fdf8a65dc1f90e061e5) >> 128
    if (absTick & 0x4000 != 0): ratio = (ratio * 0x70d869a156d2a1b890bb3df62baf32f7) >> 128
    if (absTick & 0x8000 != 0): ratio = (ratio * 0x31be135f97d08fd981231505542fcfa6) >> 128
    if (absTick & 0x10000 != 0): ratio = (ratio * 0x9aa508b5b7a84e1c677de54f3e99bc9) >> 128
    if (absTick & 0x20000 != 0): ratio = (ratio * 0x5d6af8dedb81196699c329225ee604) >> 128
    if (absTick & 0x40000 != 0): ratio = (ratio * 0x2216e584f5fa1ea926041bedfe98) >> 128
    if (absTick & 0x80000 != 0): ratio = (ratio * 0x48a170391f7dc42444e8fa2) >> 128
    if (tick > 0): ratio = uint256max // ratio
    if ratio % (1 << 32) == 0:
        sqrtPriceX96=(ratio >> 32)+0
    else:
        sqrtPriceX96=(ratio >> 32)+1
    return sqrtPriceX96

def getTickAtSqrtRatio(sqrtPriceX96):
    if not (MIN_SQRT_RATIO <= sqrtPriceX96 < MAX_SQRT_RATIO):
        raise ValueError('R')
    ratio = sqrtPriceX96 << 32
    r = ratio
    msb = 0
    f = shl(7, gt(r, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF))
    msb = _or(msb, f)
    r = shr(f, r)
    f = shl(6, gt(r, 0xFFFFFFFFFFFFFFFF))                                                                            
    msb = _or(msb, f)                                                                                                     
    r = shr(f, r)                                                                                                        
    f = shl(5, gt(r, 0xFFFFFFFF))                                                                                    
    msb = _or(msb, f)                                                                                                     
    r = shr(f, r)                                                                                                        
    f = shl(4, gt(r, 0xFFFF))                                                                                       
    msb = _or(msb, f)                                                                                                     
    r = shr(f, r)                                                                                                        
    f = shl(3, gt(r, 0xFF))                                                                                          
    msb = _or(msb, f)                                                                                                     
    r = shr(f, r)
    f = shl(2, gt(r, 0xF))                                                                                           
    msb = _or(msb, f)                                                                                                     
    r = shr(f, r)                                                                                                        
    f = shl(1, gt(r, 0x3))                                                                                           
    msb = _or(msb, f)                                                                                                     
    r = shr(f, r)                                                                                                        
    f = gt(r, 0x1)                                                                                                   
    msb = _or(msb, f)
    if (msb >= 128):
        r = ratio >> (msb - 127)
    else:
        r = ratio << (127 - msb)
    log_2 = (msb - 128) << 64
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(63, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(62, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(61, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(60, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(59, f))                                                                                        
    r = shr(f, r)
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(58, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(57, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(56, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(55, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(54, f))                                                                                        
    r = shr(f, r)
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(53, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(52, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(51, f))                                                                                        
    r = shr(f, r)                                                                                                        
    r = shr(127, mul(r, r))                                                                                              
    f = shr(128, r)                                                                                                  
    log_2 = _or(log_2, shl(50, f))
    log_sqrt10001 = log_2 * 255738958999603826347141
    tickLow = (log_sqrt10001 - 3402992956809132418596140100660247210) >> 128
    tickHi = (log_sqrt10001 + 291339464771989622907027621153398088495) >> 128
    if tickLow==tickHi:                                                                                                       
        tick=tickLow
    else:
        if getSqrtRatioAtTick(tickHi) <= sqrtPriceX96:
            tick=tickHi
        else:
            tick=tickLow
    return tick

def shl(x,y):
    return y<<x

def shr(x,y):
    return y>>x

def _or(x,y):
    return x|y

def sub(x,y):
    return x-y

def gt(x,y):
    if x>y:return 1
    else:return 0

def lt(x,y):
    if x<y:return 1
    else:return 0

def mulmod(x,y,m):
    return (x * y) % m

def mod(x, y):
    return x%y

def mul(x,y):
    return (x*y)%modulus

def div(x,y):
    return x//y

def add(x,y):
    return x+y

def addDelta(x,y):
    if y<0:
        z = x - (-y)
        if z >= x:
            raise ValueError('LS')
    else:
        z = x + y
        if z < x:
            raise ValueError('LA')
    return z

def mulDiv(a,b,denominator):
    mm = mulmod(a, b, uint256max)
    prod0 = mul(a, b)
    prod1 = sub(sub(mm, prod0), lt(mm, prod0))
    if (prod1 == 0):
        assert denominator > 0
        result = div(prod0,denominator)
        return result
    assert denominator > prod1
    remainder = mulmod(a,b,denominator)
    prod1 = sub(prod1, gt(remainder, prod0))
    prod0 = sub(prod0, remainder)
    twos = -denominator & denominator
    denominator = div(denominator, twos)
    prod0 = div(prod0, twos)
    if twos==0:
        twos=1
    else:
        twos=div(modulus,twos)
    prod0 |= mul(prod1,twos)
    inv = (3 * denominator) ^ 2
    inv = mul(inv,(2 - mul(denominator,inv)))
    inv = mul(inv,(2 - mul(denominator,inv)))
    inv = mul(inv,(2 - mul(denominator,inv)))
    inv = mul(inv,(2 - mul(denominator,inv)))
    inv = mul(inv,(2 - mul(denominator,inv)))
    inv = mul(inv,(2 - mul(denominator,inv)))
    result = mul(prod0,inv)
    return result

def divRoundingUp(x,y):
    return add(div(x, y), gt(mod(x, y), 0))

def mulDivRoundingUp(a,b,denominator):
    result = mulDiv(a, b, denominator)
    if (mulmod(a, b, denominator) > 0):
        assert result<uint256max
        result+=1
    return result

def getAmount0Delta(sqrtRatioAX96,sqrtRatioBX96,liquidity,roundUp):
    if (sqrtRatioAX96 > sqrtRatioBX96):
        (sqrtRatioAX96, sqrtRatioBX96) = (sqrtRatioBX96, sqrtRatioAX96)
    numerator1 = liquidity << RESOLUTION
    numerator2 = sqrtRatioBX96 - sqrtRatioAX96
    assert sqrtRatioAX96 > 0
    if roundUp:
        return divRoundingUp(mulDivRoundingUp(numerator1, numerator2, sqrtRatioBX96),sqrtRatioAX96)
    else:
        return mulDiv(numerator1, numerator2, sqrtRatioBX96) // sqrtRatioAX96

def getAmount1Delta(sqrtRatioAX96,sqrtRatioBX96,liquidity,roundUp):
    if (sqrtRatioAX96 > sqrtRatioBX96):
        (sqrtRatioAX96, sqrtRatioBX96) = (sqrtRatioBX96, sqrtRatioAX96)
    if roundUp:
        return mulDivRoundingUp(liquidity, sqrtRatioBX96 - sqrtRatioAX96, Q96)
    else:
        return mulDiv(liquidity, sqrtRatioBX96 - sqrtRatioAX96, Q96)

def getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96,liquidity,amount,add):
    if (amount == 0):
        return sqrtPX96
    numerator1 = liquidity << RESOLUTION
    if add:
        product = amount * sqrtPX96
        if (product // amount == sqrtPX96):
            denominator = numerator1 + product
            if (denominator >= numerator1):
                return mulDivRoundingUp(numerator1, sqrtPX96, denominator)
        return divRoundingUp(numerator1, (numerator1 // sqrtPX96)+amount)
    else:
        product = amount * sqrtPX96
        assert product//amount==sqrtPX96 and numerator1>product
        denominator = numerator1 - product
        return mulDivRoundingUp(numerator1, sqrtPX96, denominator)

def getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96,liquidity,amount,add):
    if add:
        if amount <= uint160max:
            quotient=(amount << RESOLUTION) // liquidity
        else:
            quotient=mulDiv(amount, Q96, liquidity)
        return sqrtPX96+quotient
    else:
        if amount <= uint160max:
            divRoundingUp(amount<<RESOLUTION, liquidity)
        else:
            mulDivRoundingUp(amount, Q96, liquidity)
        assert sqrtPX96 > quotient
        return sqrtPX96 - quotient

def getNextSqrtPriceFromInput(sqrtPX96,liquidity,amountIn,zeroForOne):
    assert sqrtPX96 > 0
    assert liquidity > 0
    if zeroForOne:
        return getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountIn, True)
    else:
        return getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountIn, True)

def computeSwapStep(sqrtRatioCurrentX96,sqrtRatioTargetX96,liquidity,amountRemaining,feePips):
    zeroForOne = sqrtRatioCurrentX96 >= sqrtRatioTargetX96
    exactIn = amountRemaining >= 0
    if exactIn:
        amountRemainingLessFee = mulDiv(amountRemaining, int(1e6)-feePips, int(1e6))
        if zeroForOne:
            amountIn=getAmount0Delta(sqrtRatioTargetX96, sqrtRatioCurrentX96, liquidity, True)
        else:
            amountIn=getAmount1Delta(sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, True)
        if (amountRemainingLessFee>=amountIn):
            sqrtRatioNextX96 = sqrtRatioTargetX96;
        else:
            sqrtRatioNextX96 = getNextSqrtPriceFromInput(sqrtRatioCurrentX96,liquidity,amountRemainingLessFee,zeroForOne)
    Max = sqrtRatioTargetX96 == sqrtRatioNextX96
    if zeroForOne:
        if Max and exactIn:
            amountIn=amountIn
        else:
            amountIn=getAmount0Delta(sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, True)
        if Max and not exactIn:
            amountOut=amountOut
        else:
            amountOut=getAmount1Delta(sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, False)
    else:
        if Max and exactIn:
            amountIn=amountIn
        else:
            amountIn=getAmount1Delta(sqrtRatioCurrentX96, sqrtRatioNextX96, liquidity, True)
        if Max and not exactIn:
            amountOut=amountOut
        else:
            amountOut=getAmount0Delta(sqrtRatioCurrentX96, sqrtRatioNextX96, liquidity, False)
    if not exactIn and amountOut > -amountRemaining:
        amountOut = -amountRemaining
    if exactIn and sqrtRatioNextX96 != sqrtRatioTargetX96:
        feeAmount = amountRemaining - amountIn
    else:
        feeAmount = mulDivRoundingUp(amountIn, feePips,int(1e6)-feePips)
    return sqrtRatioNextX96,amountIn,amountOut,feeAmount

def swap(zeroForOne,amountSpecified,sqrtPriceLimitX96,sqrtPriceX96,startTick,liquidity,ticksLiq,tickSpacing,fee):
    exactInput=True
    state_amountSpecifiedRemaining=amountSpecified
    state_amountCalculated=0
    state_sqrtPriceX96=sqrtPriceX96
    state_tick=startTick
    state_liquidity=liquidity
    while (state_amountSpecifiedRemaining != 0 and state_sqrtPriceX96 != sqrtPriceLimitX96):
        step_sqrtPriceStartX96=state_sqrtPriceX96
        step_tickNext,step_initialized=nextInitializedTickWithinOneWord(state_tick,tickSpacing,zeroForOne)
        if step_tickNext < MIN_TICK:
            step_tickNext = MIN_TICK
        elif step_tickNext > MAX_TICK:
            step_tickNext = MAX_TICK
        step_sqrtPriceNextX96 = getSqrtRatioAtTick(step_tickNext)
        if zeroForOne:
            if step_sqrtPriceNextX96 < sqrtPriceLimitX96:
                LimNext = sqrtPriceLimitX96
            else:
                LimNext = step_sqrtPriceNextX96
        else:
            if step_sqrtPriceNextX96 > sqrtPriceLimitX96:
                LimNext = sqrtPriceLimitX96
            else:
                LimNext = step_sqrtPriceNextX96
        state_sqrtPriceX96,step_amountIn,step_amountOut,step_feeAmount = computeSwapStep(
            state_sqrtPriceX96,LimNext,state_liquidity,state_amountSpecifiedRemaining,fee)
        state_amountSpecifiedRemaining-=(step_amountIn+step_feeAmount)
        state_amountCalculated-=step_amountOut
        if state_sqrtPriceX96==step_sqrtPriceNextX96:
            if step_initialized:
                liquidityNet=ticksLiq[step_tickNext]
                if zeroForOne:
                    liquidityNet = -liquidityNet
                state_liquidity=addDelta(state_liquidity,liquidityNet)
            if zeroForOne:
                state_tick=step_tickNext-1
            else:
                state_tick=step_tickNext
        elif state_sqrtPriceX96!=step_sqrtPriceStartX96:
            state_tick=getTickAtSqrtRatio(state_sqrtPriceX96)
    return -state_amountCalculated

def strToDict(Str):
    result={}
    for aabb in Str.split(','):
        if aabb!='':
            aa,bb=aabb.split(':')
            result[int(aa)]=int(bb)
    return result

def quoteExactInputSingle(tickerIn,amount,tickerOut,params):
    global wordBitmap
    wordBitmap=strToDict(params['wordBitmap'])
    order=params['order'].split(':')
    zeroForOne=tickerIn==order[0]
    fee=int(params['fee'])
    if zeroForOne:
        sqrtPriceLimitX96=MIN_SQRT_RATIO+1
    else:
        sqrtPriceLimitX96=MAX_SQRT_RATIO-1
    return swap(
        zeroForOne,
        amount,
        sqrtPriceLimitX96,
        int(params['sqrtPriceX96']),
        int(params['tick']),
        int(params['liquidity']),
        strToDict(params['tickLiq']),
        fee2spacing[fee],
        fee)
