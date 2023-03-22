import time


def DoNothing():
    global xx, yy
    xx = 3
    yy = 4
    return
    # end DoNothing


def WasteMsec(argMsecPeriod=10):
    """WasteMsec routine.
    WasteMsec(argMsecPeriod) returns when done
    """
    rez = time.time()  # get float sec now
    # ShowDebug("WasteLog", "Wasting %7d msec" % (argMsecPeriod))

    while (time.time() - rez) < (argMsecPeriod * 0.001):
        # waste time, just call a do nothing method.
        DoNothing()
    return  # exit after wasting time
    #  end WasteMsec
