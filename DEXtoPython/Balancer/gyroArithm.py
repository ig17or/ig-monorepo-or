ONE=10**18
ONE_XP = int(1e38)
SQRT_1E_NEG_1 = 316227766016837933
SQRT_1E_NEG_3 = 31622776601683793
SQRT_1E_NEG_5 = 3162277660168379
SQRT_1E_NEG_7 = 316227766016837
SQRT_1E_NEG_9 = 31622776601683
SQRT_1E_NEG_11 = 3162277660168
SQRT_1E_NEG_13 = 316227766016
SQRT_1E_NEG_15 = 31622776601
SQRT_1E_NEG_17 = 3162277660

def mulXpU(a,b):
    return (a * b) // ONE_XP

def divXpU(a,b):
    if b==0:raise ValueError('ZERO_DIVISION')
    return (a * ONE_XP) // b

def mulDownMagU(a,b):
    return (a * b) // ONE

def mulUp(a,b):
    product = a * b
    if not(a == 0 or product // a == b):
        raise ValueError('MUL_OVERFLOW')
    if product==0:return 0
    return ((product - 1) // ONE) + 1

def mulDown(a,b):
    product = a * b
    if not(a==0 or product//a==b):
        raise ValueError('MUL_OVERFLOW')
    return product // ONE

def mulDownU(a,b):
    return (a*b)//ONE

def mulUpU(a,b):
    return ((a*b - 1) // ONE) + 1

def divDownU(a,b):
    return (a * ONE) // b

def divUpU(a,b):
    return ((a * ONE - 1) // b) + 1

def mulDownLargeSmallU(a,b):
    return (a // ONE) * b + mulDownU(a % ONE, b)

def divDownLargeU(a,b,d,e):
    return (a * d) // (1 + (b - 1) // e)

def _intLog2Halved(x):
    n=0
    if x >= 1 << 128:
        x >>= 128
        n += 64
    if x >= 1 << 64:
        x >>= 64
        n += 32
    if x >= 1 << 32:
        x >>= 32
        n += 16
    if x >= 1 << 16:
        x >>= 16
        n += 8
    if x >= 1 << 8:
        x >>= 8
        n += 4
    if x >= 1 << 4:
        x >>= 4
        n += 2
    if x >= 1 << 2:
        x >>= 2
        n += 1
    return n

def _makeInitialGuess(inp):
    if inp>=ONE:
        return (1 << (_intLog2Halved(inp // ONE))) * ONE
    else:
        if (inp <= 10):
            return SQRT_1E_NEG_17
        if (inp <= int(1e2)):
            return int(1e10)
        if (inp <= int(1e3)):
            return SQRT_1E_NEG_15
        if (inp <= int(1e4)):
            return int(1e11)
        if (inp <= int(1e5)):
            return SQRT_1E_NEG_13
        if (inp <= int(1e6)):
            return int(1e12)
        if (inp <= int(1e7)):
            return SQRT_1E_NEG_11
        if (inp <= int(1e8)):
            return int(1e13)
        if (inp <= int(1e9)):
            return SQRT_1E_NEG_9
        if (inp <= int(1e10)):
            return int(1e14)
        if (inp <= int(1e11)):
            return SQRT_1E_NEG_7
        if (inp <= int(1e12)):
            return int(1e15)
        if (inp <= int(1e13)):
            return SQRT_1E_NEG_5
        if (inp <= int(1e14)):
            return int(1e16)
        if (inp <= int(1e15)):
            return SQRT_1E_NEG_3
        if (inp <= int(1e16)):
            return int(1e17)
        if (inp <= int(1e17)):
            return SQRT_1E_NEG_1
        return inp

def sqrt_(inp,tol):
    if inp==0:return 0
    guess = _makeInitialGuess(inp)
    for i in range(7):
        guess = (guess + ((inp * ONE) // guess)) // 2
    guessSquared = mulDown(guess,guess)
    check1=guessSquared<=inp+mulUp(guess,tol)
    check2=guessSquared>=inp-mulUp(guess,tol)
    assert check1==True and check2==True,"_sqrt FAILED"
    return guess

def divDown(a,b):
    if b==0:raise ValueError('ZERO_DIVISION')
    if a==0:return 0
    aInflated = a * ONE
    if not (aInflated / a == ONE):
        raise ValueError('DIV_INTERNAL')
    return aInflated // b

def divDownMagU(a,b):
    if b==0:raise ValueError('ZERO_DIVISION')
    return (a * ONE) // b

def divUpMagU(a,b):
    if b==0:raise ValueError('ZERO_DIVISION')
    if a==0:return 0
    if b<0:
        b = -b
        a = -a
    if a>0:return ((a * ONE - 1) // b) + 1
    return ((a * ONE + 1) // b) - 1

def mulUpMagU(a,b):
    product = a * b
    if (product > 0):return ((product - 1) // ONE) + 1
    elif (product < 0):return ((product + 1) // ONE) - 1
    return 0

def mulDownXpToNpU(a,b):
    b1 = b // int(1e19)
    b2 = b % int(1e19)
    prod1 = a * b1
    prod2 = a * b2
    if prod1 >= 0 and prod2 >= 0:
        return (prod1 + prod2 // int(1e19)) // int(1e19)
    else:
        return (prod1 + prod2 // int(1e19) + 1) // int(1e19) - 1

def mulUpXpToNpU(a,b):
    b1 = b // int(1e19)
    b2 = b % int(1e19)
    prod1 = a * b1
    prod2 = a * b2
    if prod1 <= 0 and prod2 <= 0:
        return (prod1 + prod2 // int(1e19)) // int(1e19)
    else:
        return (prod1 + prod2 // int(1e19) - 1) // int(1e19) + 1

def upscale(amount,scalingFactor):
    return mulDown(amount, scalingFactor)

def downscaleDown(amount,scalingFactor):
    return divDown(amount, scalingFactor)
