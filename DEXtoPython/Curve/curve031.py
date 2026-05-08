PRECISION=10**18
MIN_GAMMA=10**10
MAX_GAMMA=2*10**16
A_MULTIPLIER=10000
NOISE_FEE=10**5
order=None
curveIndexes=None
N_COINS=None
balances=None
precisions=None
MIN_A=None
MAX_A=None
Price_scale=None
D_=None
A=None
gamma=None
future_A_gamma_time=None
fee_gamma=None
mid_fee=None
out_fee=None
token_supply=None

def _xp():
    return [balances[0]*precisions[0],balances[1]*precisions[1]*Price_scale//PRECISION]

def geometric_mean(unsorted_x, sort):
    x = unsorted_x
    if sort and x[0] < x[1]:
        x = [unsorted_x[1], unsorted_x[0]]
    D = x[0]
    diff = 0
    for i in range(255):
        D_prev = D
        D = (D + x[0] * x[1] // D) // N_COINS
        if D > D_prev:
            diff = D - D_prev
        else:
            diff = D_prev - D
        if diff <= 1 or diff * 10**18 < D:
            return D
    raise ValueError("Did not converge")

def newton_D(ANN, gamma, x_unsorted):
    assert ANN > MIN_A - 1 and ANN < MAX_A + 1
    assert gamma > MIN_GAMMA - 1 and gamma < MAX_GAMMA + 1
    x = x_unsorted
    if x[0] < x[1]:
        x = [x_unsorted[1], x_unsorted[0]]
    assert x[0] > 10**9 - 1 and x[0] < 10**15 * 10**18 + 1
    assert x[1] * 10**18 // x[0] > 10**14-1
    D = N_COINS * geometric_mean(x, False)
    S = x[0] + x[1]
    for i in range(255):
        D_prev = D
        K0 = (10**18 * N_COINS**2) * x[0] // D * x[1] // D
        _g1k0: uint256 = gamma + 10**18
        if _g1k0 > K0:
            _g1k0 = _g1k0 - K0 + 1
        else:
            _g1k0 = K0 - _g1k0 + 1
        mul1 = 10**18 * D // gamma * _g1k0 // gamma * _g1k0 * A_MULTIPLIER // ANN
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
    x_j = x[1 - i]
    y = D**2 // (x_j * N_COINS**2)
    K0_i = (10**18 * N_COINS) * x_j // D
    assert (K0_i > 10**16*N_COINS - 1) and (K0_i < 10**20*N_COINS + 1)
    convergence_limit = max(max(x_j // 10**14, D // 10**14), 100)
    for j in range(255):
        y_prev = y
        K0 = K0_i * y * N_COINS // D
        S = x_j + y
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

def _fee(xp):
    f = xp[0] + xp[1]
    f = fee_gamma * 10**18 // ( fee_gamma + 10**18 - (10**18 * N_COINS**N_COINS) * xp[0] // f * xp[1] // f )
    return (mid_fee * f + out_fee * (10**18 - f)) // 10**18

def get_dy(i, j, dx):
    assert i != j
    assert i < N_COINS
    assert j < N_COINS
    price_scale = Price_scale * precisions[1]
    xp = balances.copy()
    D = D_
    if future_A_gamma_time > 0:
        D = newton_D(A, gamma, _xp())
    xp[i] += dx
    xp = [xp[0] * precisions[0], xp[1] * price_scale // PRECISION]
    y = newton_y(A, gamma, xp, D, j)
    dy = xp[j] - y - 1
    xp[j] = y
    if j > 0:
        dy = dy * PRECISION // price_scale
    else:
        dy //= precisions[0]
    dy -= _fee(xp) * dy // 10**10
    return dy

def _calc_token_fee(amounts, xp):
    fee = _fee(xp) * N_COINS // (4 * (N_COINS-1))
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

def calc_token_amount(amounts):
    price_scale = Price_scale * precisions[1]
    xp = _xp()
    amountsp = [amounts[0] * precisions[0], amounts[1] * price_scale // PRECISION]
    D0 = D_
    if future_A_gamma_time > 0:
        D0 = newton_D(A, gamma, xp)
    xp[0] += amountsp[0]
    xp[1] += amountsp[1]
    D = newton_D(A, gamma, xp)
    d_token = token_supply * D // D0 - token_supply
    d_token -= _calc_token_fee(amountsp, xp) * d_token // 10**10 + 1
    return d_token

def calc_withdraw_one_coin(token_amount, i):
    assert token_amount <= token_supply
    assert i < N_COINS
    xx = balances.copy()
    D0 = 0
    price_scale_i = Price_scale * precisions[1]
    xp = [xx[0] * precisions[0], xx[1] * price_scale_i // PRECISION]
    if i == 0:
        price_scale_i = PRECISION * precisions[0]
    D = D_
    fee = _fee(xp)
    dD = token_amount * D // token_supply
    D -= (dD - (fee * dD // (2 * 10**10) + 1))
    y = newton_y(A, gamma, xp, D, i)
    dy = (xp[i] - y) * PRECISION // price_scale_i
    return dy

def updateGlobals(params):
    global order,curveIndexes,N_COINS,balances,precisions,MIN_A,MAX_A,Price_scale,D_,A,gamma,future_A_gamma_time,fee_gamma,mid_fee,out_fee,token_supply
    order=params['order'].split(':')
    curveIndexes=[int(item) for item in params['curveIndexes'].split(':')]
    N_COINS=int(params['N_COINS'])
    balances=[int(item) for item in params['balances'].split(':')]
    precisions=[int(item) for item in params['precisions'].split(':')]
    MIN_A = N_COINS**N_COINS * A_MULTIPLIER // 10
    MAX_A = N_COINS**N_COINS * A_MULTIPLIER * 100000
    Price_scale=int(params['price_scale'])
    D_=int(params['D'])
    A=int(params['A'])
    gamma=int(params['gamma'])
    future_A_gamma_time=int(params['future_A_gamma_time'])
    fee_gamma=int(params['fee_gamma'])
    mid_fee=int(params['mid_fee'])
    out_fee=int(params['out_fee'])
    token_supply=int(params['token_supply'])

def get_dy031(tickerIn,amount,tickerOut,params):
    updateGlobals(params)
    return get_dy(curveIndexes[order.index(tickerIn)],curveIndexes[order.index(tickerOut)],amount)

def get_dy031indexes(i,dx,j,params):
    updateGlobals(params)
    return get_dy(i,j,dx)

def calc_token_amount031(tickerIn,amount,params):
    updateGlobals(params)
    amounts=[] 
    for i in range(N_COINS):amounts.append(0)
    iIn=curveIndexes[order.index(tickerIn)]
    amounts[iIn]=amount
    return calc_token_amount(amounts)

def calc_withdraw_one_coin031(amount,tickerOut,params):
    updateGlobals(params)
    iOut=curveIndexes[order.index(tickerOut)]
    return calc_withdraw_one_coin(amount, iOut)
