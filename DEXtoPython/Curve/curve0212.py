import time

PRECISION=10**18
N_COINS=None
A_PRECISION=None
initial_A=None
future_A=None
initial_A_time=None
future_A_time=None
fee=None
offpeg_fee_multiplier=None
FEE_DENOMINATOR=None
order=None
curveOrder=None
curveOrder=None
_balances=None
PRECISION_MUL=None
token_supply=None

def _A():
    blockTimestamp=time.time()
    t1 = future_A_time
    A1 = future_A         
    if blockTimestamp<t1:                       
        A0 = initial_A
        t0 = initial_A_time
        if A1 > A0:                    
            return A0 + (A1 - A0) * (blockTimestamp - t0) // (t1 - t0)
        else:         
            return A0 - (A0 - A1) * (blockTimestamp - t0) // (t1 - t0)
    else:
        return A1

def get_D(xp,amp):
    S = 0
    for _x in xp:                          
        S += _x                                       
    if S == 0:                                        
        return 0                                                     
    Dprev = 0
    D = S
    Ann = amp * N_COINS
    for _i in range(255):
        D_P = D
        for _x in xp:
            D_P = D_P * D // (_x * N_COINS + 1)
        Dprev = D
        D = (Ann * S // A_PRECISION + D_P * N_COINS) * D // ((Ann - A_PRECISION) * D // A_PRECISION + (N_COINS + 1) * D_P)
        if D > Dprev:
            if D - Dprev <= 1:
                return D
        else:
            if Dprev - D <= 1:
                return D

def get_D_precisions(coin_balances, amp):
    xp = PRECISION_MUL.copy()
    for i in range(N_COINS):
        xp[i] *= coin_balances[i]
    return get_D(xp, amp)

def get_virtual_price():
    D = get_D_precisions(_balances, _A())
    return D * PRECISION // token_supply

def _calc_token_amount(_amounts, is_deposit):
    coin_balances=_balances
    amp = _A()
    D0 = get_D_precisions(coin_balances, amp)
    for i in range(N_COINS):
        if is_deposit:
            coin_balances[i] += _amounts[i]
        else:
            coin_balances[i] -= _amounts[i]
    D1 = get_D_precisions(coin_balances, amp)
    token_amount = token_supply
    diff = 0
    if is_deposit:
        diff = D1 - D0
    else:
        diff = D0 - D1
    return diff * token_amount // D0

def get_y_D(A_, i, xp, D):
    assert i >= 0
    assert i < N_COINS
    Ann = A_ * N_COINS
    c = D
    S_ = 0
    _x = 0
    y_prev = 0
    for _i in range(N_COINS):
        if _i != i:
            _x = xp[_i]
        else:
            continue
        S_ += _x
        c = c * D // (_x * N_COINS)
    c = c * D * A_PRECISION // (Ann * N_COINS)
    b = S_ + D * A_PRECISION // Ann
    y = D
    for _i in range(255):
        y_prev = y
        y = (y*y + c) // (2 * y + b - D)
        if y > y_prev:
            if y - y_prev <= 1:
                return y
        else:
            if y_prev - y <= 1:
                return y
    raise ValueError('get_y_D over')

def _dynamic_fee(xpi, xpj, _fee, _feemul):
    if _feemul <= FEE_DENOMINATOR:
        return _fee
    else:
        xps2 = xpi + xpj
        xps2 *= xps2
        return (_feemul * _fee) // ( (_feemul - FEE_DENOMINATOR) * 4 * xpi * xpj // xps2 + FEE_DENOMINATOR)

def _calc_withdraw_one_coin(_token_amount, i):
    amp = _A()
    xp = _balances.copy()
    precisions = PRECISION_MUL.copy()
    for j in range(N_COINS):
        xp[j] *= precisions[j]
    D0 = get_D(xp, amp)
    D1 = D0 - _token_amount * D0 // token_supply
    new_y = get_y_D(amp, i, xp, D1)
    xp_reduced = xp
    ys = (D0 + D1) // (2 * N_COINS)
    _fee = fee * N_COINS // (4 * (N_COINS - 1))
    feemul = offpeg_fee_multiplier
    for j in range(N_COINS):
        dx_expected = 0
        xavg = 0
        if j == i:
            dx_expected = xp[j] * D1 // D0 - new_y
            xavg = (xp[j] + new_y) // 2
        else:
            dx_expected = xp[j] - xp[j] * D1 // D0
            xavg = xp[j]
        xp_reduced[j] -= _dynamic_fee(xavg, ys, _fee, feemul) * dx_expected // FEE_DENOMINATOR #<<<<<
    dy = xp_reduced[i] - get_y_D(amp, i, xp_reduced, D1)
    return (dy - 1) // precisions[i]

def get_y(i,j,x,xp):
    amp = _A()
    D = get_D(xp, amp)
    Ann = amp * N_COINS
    c = D
    S_ = 0
    _x = 0
    y_prev = 0

    for _i in range(N_COINS):
        if _i == i:
            _x = x
        elif _i != j:
            _x = xp[_i]
        else:
            continue
        S_ += _x
        c = c * D // (_x * N_COINS)
    c = c * D * A_PRECISION // (Ann * N_COINS)
    b = S_ + D * A_PRECISION // Ann
    y = D
    for _i in range(255):
        y_prev = y
        y = (y*y + c) // (2 * y + b - D)
        if y > y_prev:
            if y - y_prev <= 1:
                return y
        else:
            if y_prev - y <= 1:
                return y
    raise RuntimeError("get_y error")

def _get_dy(i,j,dx):
    xp=_balances.copy()
    precisions=PRECISION_MUL.copy()
    for k in range(N_COINS):
        xp[k] *= precisions[k]
    x = xp[i] + dx * precisions[i]
    y = get_y(i, j, x, xp)
    dy = (xp[j] - y) // precisions[j]
    _fee = _dynamic_fee(
            (xp[i] + x) // 2, (xp[j] + y) // 2, fee, offpeg_fee_multiplier
        ) * dy // FEE_DENOMINATOR
    return dy - _fee

def updateGlobals(params):
    global N_COINS,A_PRECISION,initial_A,future_A,initial_A_time,future_A_time,fee,offpeg_fee_multiplier,FEE_DENOMINATOR,order,curveOrder,_balances,PRECISION_MUL,token_supply
    N_COINS=int(params['N_COINS'])
    A_PRECISION=int(params['A_PRECISION'])
    initial_A=int(params['initial_A'])
    future_A=int(params['future_A'])
    initial_A_time=int(params['initial_A_time'])
    future_A_time=int(params['future_A_time'])
    fee=int(params['fee'])
    offpeg_fee_multiplier=int(params['offpeg_fee_multiplier'])
    FEE_DENOMINATOR=int(params['FEE_DENOMINATOR'])
    order=params['order'].split(':')
    curveOrder=params['curveIndexes'].split(':')
    _balances=list(map(int,params['balances'].split(':')))
    PRECISION_MUL=list(map(int,params['precisions'].split(':')))
    token_supply=int(params['token_supply'])

def get_dy0212(tickerIn,amount,tickerOut,params):
    updateGlobals(params)
    return _get_dy(order.index(tickerIn),order.index(tickerOut),amount)

def get_virtual_price0212(params):
    updateGlobals(params)
    return get_virtual_price()

def calc_token_amount0212(ticker,amount,params):
    updateGlobals(params)
    amounts=[]
    for x in range(N_COINS):
        amounts.append(0)
    amounts[order.index(ticker)]=amount
    return _calc_token_amount(amounts,True)

def calc_withdraw_one_coin0212(_token_amount,ticker,params):
    updateGlobals(params)
    iOut=int(curveOrder[order.index(ticker)])
    return _calc_withdraw_one_coin(_token_amount,iOut)
