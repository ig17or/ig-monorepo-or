import time

N_COINS=None
PRECISION = 10 ** 18
FEE_DENOMINATOR = 10 ** 10
A_PRECISION=100
initial_A=None
future_A=None
initial_A_time=None
future_A_time=None
_fee=None
order=None
rate_multipliers=None
balances=None
tokenSupply=None
stableSwapVers=None

def _xp_mem(_rates, _balances):
    result=[]
    for i in range(N_COINS):
        result.append( _rates[i] * _balances[i] // PRECISION)
    return result

def _A():
    blockTimestamp=time.time()
    t1 = future_A_time
    A1 = future_A
    if blockTimestamp < t1:
        A0 = initial_A
        t0 = initial_A_time
        if A1 > A0:
            return A0 + (A1 - A0) * (blockTimestamp - t0) // (t1 - t0)
        else:
            return A0 - (A0 - A1) * (blockTimestamp - t0) // (t1 - t0)
    else:
        return A1

def get_D0(_xp, _amp):
    S = 0
    for x in _xp:
        S += x
    if S == 0:
        return 0
    D = S
    Ann = _amp * N_COINS
    for i in range(255):
        D_P = D * D // _xp[0] * D // _xp[1] // (N_COINS)**2
        Dprev = D
        D = (Ann * S // A_PRECISION + D_P * N_COINS) * D // ((Ann - A_PRECISION) * D // A_PRECISION + (N_COINS + 1) * D_P)
        if D > Dprev:
            if D - Dprev <= 1:
                return D
        else:
            if Dprev - D <= 1:
                return D
    raise RuntimeError('get_D error')

def get_D1(_xp,_amp):
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
    raise RuntimeError('get_D error')

def get_D(_xp,_amp):
    if stableSwapVers==0:return get_D0(_xp,_amp)
    elif stableSwapVers==1:return get_D1(_xp,_amp)

def get_y(i, j, x, xp):
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
    b = S_ + D * A_PRECISION // Ann  # - D
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
    raise RuntimeError('get_y error')

def _get_dy(i, j, dx):
    rates = rate_multipliers.copy()
    xp = _xp_mem(rates, balances.copy())
    x = xp[i] + (dx * rates[i] // PRECISION)
    y = get_y(i, j, x, xp)
    dy = xp[j] - y - 1
    fee = _fee * dy // FEE_DENOMINATOR
    return (dy - fee) * PRECISION // rates[j]

def updataGlobals(params):
    global N_COINS,initial_A,future_A,initial_A_time,future_A_time,_fee,order,rate_multipliers,balances,tokenSupply,stableSwapVers
    N_COINS=int(params['N_COINS'])
    initial_A=int(params['initial_A'])
    future_A=int(params['future_A'])
    initial_A_time=int(params['initial_A_time'])
    future_A_time=int(params['future_A_time'])
    _fee=int(params['fee'])
    order=params['order'].split(':')
    rate_multipliers=list(map(int,params['rate_multipliers'].split(':')))
    balances=list(map(int,params['balances'].split(':')))
    tokenSupply=int(params['token_supply'])
    stableSwapVers=int(params['stableSwapVers'])

def get_dy0215stable(tickerIn,amount,tickerOut,params):
    updataGlobals(params)
    return _get_dy(order.index(tickerIn),order.index(tickerOut),amount)
