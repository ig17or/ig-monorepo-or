N_COINS=None
PRECISION = 10 ** 18
FEE_DENOMINATOR = 10 ** 10
A_PRECISION=100
A_MULTIPLIER=10000
NOISE_FEE=10**5
MIN_GAMMA = 10**10
MAX_GAMMA = 5 * 10**16
A=None
D=None
gamma=None
MIN_A=None
MAX_A=None
initial_A_gamma=None
future_A_gamma=None
initial_A_gamma_time=None
future_A_gamma_time=None
fee_gamma=None
future_fee_gamma=None
mid_fee=None
out_fee=None
order=None
PRECISIONS=None
balances=None
curveIndexes=None
priceScale=None
tokenSupply=None
PRICE_SIZE=None
PRICE_MASK=None

def bitwise_and(x,y):
    return x&y

def shift(x, _shift):
    if _shift >= 0:
        return x << _shift
    else:
        return x >> abs(_shift)

def sort(A0):
    A_ = A0.copy()
    for i in range(1, N_COINS):
        x = A_[i]
        cur = i
        for j_ in range(N_COINS):
            y = A_[cur-1]
            if y > x:
                break
            A_[cur] = y
            cur -= 1
            if cur == 0:
                break
        A_[cur] = x
    return A_

def _geometric_mean(unsorted_x, _sort):
    x = unsorted_x.copy()
    if _sort:
        x = sort(x)
    D = x[0]
    diff = 0
    for i in range(255):
        D_prev = D
        tmp = 10**18
        for _x in x:
            tmp = tmp * _x // D
        D = D * ((N_COINS - 1) * 10**18 + tmp) // (N_COINS * 10**18)
        if D > D_prev:
            diff = D - D_prev
        else:
            diff = D_prev - D
        if diff <= 1 or diff * 10**18 < D:
            return D
    raise ValueError("Did not converge")

def newton_D(ANN, _gamma, x_unsorted):
    assert ANN > MIN_A - 1 and ANN < MAX_A + 1
    assert _gamma > MIN_GAMMA - 1 and _gamma < MAX_GAMMA + 1
    x = sort(x_unsorted)
    assert x[0] > 10**9 - 1 and x[0] < 10**15 * 10**18 + 1
    for i in range(1, N_COINS):
        frac = x[i] * 10**18 // x[0]
        assert frac > 10**11-1
    D = N_COINS * _geometric_mean(x, False)
    S = 0
    for x_i in x:
        S += x_i
    for i in range(255):
        D_prev = D
        K0 = 10**18
        for _x in x:
            K0 = K0 * _x * N_COINS // D
        _g1k0 = _gamma + 10**18
        if _g1k0 > K0:
            _g1k0 = _g1k0 - K0 + 1
        else:
            _g1k0 = K0 - _g1k0 + 1
        mul1 = 10**18 * D // _gamma * _g1k0 // _gamma * _g1k0 * A_MULTIPLIER // ANN
        mul2 = (2 * 10**18) * N_COINS * K0 // _g1k0
        neg_fprime = (S + S * mul2 // 10**18) + mul1 * N_COINS // K0 - mul2 * D // 10**18
        D_plus = D * (neg_fprime + S) // neg_fprime
        D_minus = D*D // neg_fprime
        if 10**18 > K0:
            D_minus += D * (mul1 // neg_fprime) // 10**18 * (10**18 - K0) // K0
        else:
            D_minus -= D * (mul1 // neg_fprime) // 10**18 * (K0 - 10**18) // K0
        if D_plus > D_minus:
            D = D_plus - D_minus
        else:
            D = (D_minus - D_plus) // 2
        diff = 0
        if D > D_prev:
            diff = D - D_prev
        else:
            diff = D_prev - D
        if diff * 10**14 < max(10**16, D):
            for _x in x:
                frac = _x * 10**18 // D
                assert (frac > 10**16 - 1) and (frac < 10**20 + 1)
            return D
    raise ValueError("Did not converge")

def newton_y(ANN, gamma, x, D, i):
    assert ANN > MIN_A - 1 and ANN < MAX_A + 1
    assert gamma > MIN_GAMMA - 1 and gamma < MAX_GAMMA + 1
    assert D > 10**17 - 1 and D < 10**15 * 10**18 + 1
    for k in range(3):
        if k != i:
            frac = x[k] * 10**18 // D
            assert (frac > 10**16 - 1) and (frac < 10**20 + 1)
    y = D // N_COINS
    K0_i = 10**18
    S_i = 0
    x_sorted = x.copy()
    x_sorted[i] = 0
    x_sorted = sort(x_sorted)
    convergence_limit = max(max(x_sorted[0] // 10**14, D // 10**14), 100)
    for j in range(2, N_COINS+1):
        _x = x_sorted[N_COINS-j]
        y = y * D // (_x * N_COINS)
        S_i += _x
    for j in range(N_COINS-1):
        K0_i = K0_i * x_sorted[j] * N_COINS // D
    for j in range(255):
        y_prev = y
        K0 = K0_i * y * N_COINS // D
        S = S_i + y
        _g1k0 = gamma + 10**18
        if _g1k0 > K0:
            _g1k0 = _g1k0 - K0 + 1
        else:
            _g1k0 = K0 - _g1k0 + 1
        mul1 = 10**18 * D // gamma * _g1k0 // gamma * _g1k0 * A_MULTIPLIER // ANN
        mul2 = 10**18 + (2 * 10**18) * K0 // _g1k0
        yfprime = 10**18 * y + S * mul2 + mul1
        _dyfprime = D * mul2
        if yfprime < _dyfprime:
            y = y_prev // 2
            continue
        else:
            yfprime -= _dyfprime
        fprime = yfprime // y
        y_minus = mul1 // fprime
        y_plus = (yfprime + 10**18 * D) // fprime + y_minus * 10**18 // K0
        y_minus += 10**18 * S // fprime
        if y_plus < y_minus:
            y = y_prev // 2
        else:
            y = y_plus - y_minus
        diff = 0
        if y > y_prev:
            diff = y - y_prev
        else:
            diff = y_prev - y
        if diff < max(convergence_limit, y // 10**14):
            frac = y * 10**18 // D
            assert (frac > 10**16 - 1) and (frac < 10**20 + 1)
            return y
    raise ValueError("Did not converge")

def reduction_coefficient(x, _fee_gamma):
    K = 10**18
    S = 0
    for x_i in x:
        S += x_i
    for x_i in x:
        K = K * N_COINS * x_i // S
    if _fee_gamma > 0:
        K = _fee_gamma * 10**18 // (_fee_gamma + 10**18 - K)
    return K

def fee_calc(xp):
    f = reduction_coefficient(xp, fee_gamma)
    return (mid_fee * f + out_fee * (10**18 - f)) // 10**18

def _calc_token_fee(amounts, xp):
    fee = fee_calc(xp) * N_COINS // (4 * (N_COINS-1))
    S = 0
    for _x in amounts:
        S += _x
    avg = S // N_COINS
    Sdiff = 0
    for _x in amounts:
        if _x > avg:
            Sdiff += _x - avg
        else:
            Sdiff += avg - _x
    return fee * Sdiff // S + NOISE_FEE

def get_dy(i, j, dx):
    assert i != j and i < N_COINS and j < N_COINS, "coin index out of range"
    assert dx > 0, "do not exchange 0 coins"
    precisions = PRECISIONS.copy()
    price_scale=priceScale.copy()
    xp=balances.copy()
    xp[i] += dx
    xp[0] *= precisions[0]
    for k in range(N_COINS-1):
        xp[k+1] = xp[k+1] * price_scale[k] * precisions[k+1] // PRECISION
    y = newton_y(A, gamma, xp, D, j)
    dy = xp[j] - y - 1
    xp[j] = y
    if j > 0:
        dy = dy * PRECISION // price_scale[j-1]
    dy //= precisions[j]
    dy -= fee_calc(xp) * dy // 10**10
    return dy

def calc_token_amount(amounts,deposit=True):
    precisions = PRECISIONS.copy()
    token_supply = tokenSupply
    xp = balances.copy()
    price_scale=priceScale.copy()
    amountsp = amounts.copy()
    if deposit:
        for k in range(N_COINS):
            xp[k] += amounts[k]
    else:
        for k in range(N_COINS):
            xp[k] -= amounts[k]
    xp[0] *= precisions[0]
    amountsp[0] *= precisions[0]
    for k in range(N_COINS-1):
        p = price_scale[k] * precisions[k+1]
        xp[k+1] = xp[k+1] * p // PRECISION
        amountsp[k+1] = amountsp[k+1] * p // PRECISION
    _D = newton_D(A, gamma, xp)
    d_token = token_supply * _D // D
    if deposit:
        d_token -= token_supply
    else:
        d_token = token_supply - d_token
    d_token_fee = d_token - _calc_token_fee(amountsp, xp) * d_token // 10**10 + 1
    return d_token,d_token_fee

def reverseTokenAmount(desired_y, i):
    amounts=[]
    for _i in range(N_COINS):amounts.append(0)
    amounts[i]=balances[i]
    current_y,current_y_fee = calc_token_amount(amounts)
    fee=current_y_fee/current_y
    prevDelta=0
    notChanging=0
    for i_ in range(30):
        delta=desired_y/current_y_fee
        if prevDelta==delta:
            notChanging+=1
        else:
            prevDelta=delta
        if 0.999<delta<1.0001:
            return int(amounts[i]*fee)
        amounts[i]=int(amounts[i]*delta)
        _,current_y_fee=calc_token_amount(amounts)
    if notChanging>20 and 0.9<delta<1.01:
        return int(amounts[i]*fee)
    else:
        return 1

def updateGlobals(params):
    global N_COINS,A,D,gamma,MIN_A,MAX_A,initial_A_gamma,future_A_gamma,initial_A_gamma_time,future_A_gamma_time,fee_gamma,future_fee_gamma,mid_fee,out_fee,order,PRECISIONS,balances,curveIndexes,priceScale,tokenSupply,PRICE_SIZE,PRICE_MASK
    N_COINS=int(params['N_COINS'])
    A=int(params['A'])
    D=int(params['D'])
    gamma=int(params['gamma'])
    MIN_A=N_COINS**N_COINS * A_MULTIPLIER // 100
    MAX_A=N_COINS**N_COINS * A_MULTIPLIER * 1000
    initial_A_gamma=int(params['initial_A_gamma'])
    future_A_gamma=int(params['future_A_gamma'])
    initial_A_gamma_time=int(params['initial_A_gamma_time'])
    future_A_gamma_time=int(params['future_A_gamma_time'])
    fee_gamma=int(params['fee_gamma'])
    future_fee_gamma=int(params['future_fee_gamma'])
    mid_fee=int(params['mid_fee'])
    out_fee=int(params['out_fee'])
    order=params['order'].split(':')
    PRECISIONS=[int(item) for item in params['PRECISIONS'].split(':')]
    balances=[int(item) for item in params['balances'].split(':')]
    curveIndexes=[int(item) for item in params['curveIndexes'].split(':')]
    priceScale=[int(item) for item in params['price_scale'].split(':')]
    tokenSupply=int(params['token_supply'])
    PRICE_SIZE = 256 // (N_COINS-1)
    PRICE_MASK = 2**PRICE_SIZE - 1

def get_dy0215crypto(tickerIn,amount,tickerOut,params):
    updateGlobals(params)
    return get_dy(curveIndexes[order.index(tickerIn)],curveIndexes[order.index(tickerOut)],amount)

def get_dy0215cryptoIndexes(i,a,j,params):
    updateGlobals(params)
    return get_dy(i,j,a)

def calc_token_amount0215crypto(tickerIn,amount,params):
    updateGlobals(params)
    amounts=[]
    for i in range(N_COINS):amounts.append(0)
    iIn=curveIndexes[order.index(tickerIn)]
    amounts[iIn]=amount
    return calc_token_amount(amounts)[1]

def calc_withdraw_one_coin0215crypto(amount,tickerOut,params):
    updateGlobals(params)
    iOut=curveIndexes[order.index(tickerOut)]
    return reverseTokenAmount(amount, iOut)
