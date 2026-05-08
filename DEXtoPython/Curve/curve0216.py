from time import time
from curve0212 import get_virtual_price0212

r=None
BASE_POOL=None
rate_multiplier=None
balances=None
PRECISION=10**18
FEE_DENOMINATOR=10**10
fee=None
N_COINS=2
future_A_time=None
future_A=None
initial_A_time=None
initial_A=None
A_PRECISION=100
order=None
curveIndexes=None
totalSupply=None

def BASE_POOL_get_virtual_price():
    return get_virtual_price0212(r.hgetall(BASE_POOL))

def _xp_mem(_rates, _balances):
    result=[]
    for i in range(N_COINS):
        result.append(_rates[i] * _balances[i] // PRECISION)
    return result

def _A():
    t1 = future_A_time
    A1 = future_A
    blockTimestamp=int(time())
    if blockTimestamp < t1:
        A0 = initial_A
        t0 = initial_A_time
        if A1 > A0:
            return A0 + (A1 - A0) * (blockTimestamp - t0) // (t1 - t0)
        else:
            return A0 - (A0 - A1) * (blockTimestamp - t0) // (t1 - t0)
    else:
        return A1

def get_D(_xp, _amp):
    S = 0
    Dprev = 0
    for x in _xp:
        S += x
    if S == 0:
        return 0
    D = S
    Ann = _amp * N_COINS
    for i in range(255):
        D_P = D
        for x in _xp:
            D_P = D_P * D // (x * N_COINS)
        Dprev = D
        D = (Ann * S // A_PRECISION + D_P * N_COINS) * D // ((Ann - A_PRECISION) * D // A_PRECISION + (N_COINS + 1) * D_P)
        if D > Dprev:
            if D - Dprev <= 1:
                return D
        else:
            if Dprev - D <= 1:
                return D
    raise ValueError('get_D error')

def get_y(i, j, x, xp):
    assert i != j
    assert j >= 0
    assert j < N_COINS
    assert i >= 0
    assert i < N_COINS
    amp = _A()
    D = get_D(xp, amp)
    S_ = 0
    _x = 0
    y_prev = 0
    c = D
    Ann = amp * N_COINS
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
    raise ValueError('get_y error')

def get_dy(i, j, dx):
    rates = [rate_multiplier, BASE_POOL_get_virtual_price()]
    xp = _xp_mem(rates, balances)
    x = xp[i] + (dx * rates[i] // PRECISION)
    y = get_y(i, j, x, xp)
    dy = xp[j] - y - 1
    Fee = fee * dy // FEE_DENOMINATOR
    return (dy - Fee) * PRECISION // rates[j]

def get_D_mem(_rates, _balances, _amp):
    xp = _xp_mem(_rates, _balances)
    return get_D(xp, _amp)

def calc_token_amount(_amounts, _is_deposit=True):
    amp = _A()
    rates = [rate_multiplier, BASE_POOL_get_virtual_price()]
    D0 = get_D_mem(rates, balances, amp)
    for i in range(N_COINS):
        amount = _amounts[i]
        if _is_deposit:
            balances[i] += amount
        else:
            balances[i] -= amount
    D1 = get_D_mem(rates, balances, amp)
    diff = 0
    if _is_deposit:
        diff = D1 - D0
    else:
        diff = D0 - D1
    return diff * totalSupply // D0

def get_y_D(A, i, xp, D):
    assert i >= 0
    assert i < N_COINS
    S_ = 0
    _x = 0
    y_prev = 0
    c = D
    Ann = A * N_COINS
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
    raise ValueError('get_y_D')

def _calc_withdraw_one_coin(_burn_amount, i):
    amp = _A()
    rates = [rate_multiplier, BASE_POOL_get_virtual_price()]
    xp = _xp_mem(rates, balances)
    D0 = get_D(xp, amp)
    total_supply = totalSupply
    D1 = D0 - _burn_amount * D0 // total_supply
    new_y = get_y_D(amp, i, xp, D1)
    base_fee = fee * N_COINS // (4 * (N_COINS - 1))
    xp_reduced=[]
    for j in range(N_COINS):
        dx_expected = 0
        xp_j = xp[j]
        if j == i:
            dx_expected = xp_j * D1 // D0 - new_y
        else:
            dx_expected = xp_j - xp_j * D1 // D0
        xp_reduced.append( xp_j - base_fee * dx_expected // FEE_DENOMINATOR )
    dy = xp_reduced[i] - get_y_D(amp, i, xp_reduced, D1)
    #dy_0 = (xp[i] - new_y) * PRECISION / rates[i]  # w/o fees
    dy = (dy - 1) * PRECISION // rates[i]
    return dy

def updateGlobals(params):
    global r,BASE_POOL,rate_multiplier,balances,fee,future_A_time,future_A,initial_A_time,initial_A,order,curveIndexes,totalSupply
    r=params['r']
    BASE_POOL=params['BASE_POOL']
    rate_multiplier=10**(36-int(params['dec']))
    balances=list(map(int,params['balances'].split(':')))
    fee=int(params['fee'])
    future_A_time=int(params['future_A_time'])
    future_A=int(params['future_A'])
    initial_A_time=int(params['initial_A_time'])
    initial_A=int(params['initial_A'])
    order=params['order'].split(':')
    curveIndexes=list(map(int,params['curveIndexes'].split(':')))
    totalSupply=int(params['token_supply'])

def get_dy0216(tickerIn,amount,tickerOut,params):
    updateGlobals(params)
    return get_dy(curveIndexes[order.index(tickerIn)],curveIndexes[order.index(tickerOut)],amount)

def calc_token_amount0216(tickerIn,amount,params):
    updateGlobals(params)
    amounts=[]
    for i in range(N_COINS):amounts.append(0)
    iIn=curveIndexes[order.index(tickerIn)]
    amounts[iIn]=amount
    return calc_token_amount(amounts)

def calc_withdraw_one_coin0216(amount,tickerOut,params):
    updateGlobals(params)
    iOut=curveIndexes[order.index(tickerOut)]
    return _calc_withdraw_one_coin(amount,iOut)
