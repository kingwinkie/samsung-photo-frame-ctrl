try:
    import netifaces
except ImportError:
    netifaces = None
    pass  # When running the setup.py, netifaces is not yet installed

def getIPList():
    ifaces=netifaces.interfaces()
    if ifaces:
        ifaces.remove("lo")
        addrList = []
        for iface in ifaces:
            ifcAddresses = netifaces.ifaddresses(iface)
            if ifcAddresses:
                ifcInetAddresses = ifcAddresses.get(netifaces.AF_INET)
                if ifcInetAddresses:
                    for inetAddr in ifcInetAddresses:
                        addr = inetAddr.get("addr")
                        if addr:
                            addrList.append(addr)
    return addrList

def getIPStr(addrList : list = None, sep : str = ", "):
    if not addrList:
        addrList = getIPList()
    addrStr = sep.join(addrList)
    return addrStr
