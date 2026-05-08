def _calcOutGivenInWe(bI,wI,bO,wO,aI):
    return bO*(1-((bI/(bI+aI))**(wI/wO)))
    
def calcOutGivenInWe(tickerIn,amount,tickerOut,params):

    order=params['order'].split(':')
    iI=order.index(tickerIn)
    iO=order.index(tickerOut)
    balances=params['balances'].split(':')
    weights=params['weights'].split(':')
    fee=1-(int(params['fee'])/10**18)

    withoutFee=_calcOutGivenInWe(int(balances[iI]),
                                 int(weights[iI]),
                                 int(balances[iO]),
                                 int(weights[iO]),
                                 amount)
    return int(withoutFee*fee)
