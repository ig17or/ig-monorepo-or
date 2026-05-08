def getAmountOut(tickerIn,amount,tickerOut,params):

    def _getAmountOut(amount_in,reserve_in,reserve_out):
        amount_in_with_fee = amount_in * 997
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in * 1000 + amount_in_with_fee
        return numerator // denominator

    order=params['order'].split(':')
    balances=params['balances'].split(':')
    return _getAmountOut(amount,
                         int(balances[order.index(tickerIn)]),
                         int(balances[order.index(tickerOut)]))
