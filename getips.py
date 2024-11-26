#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
try:
    import netifaces
except ImportError:
    netifaces = None
    pass  # When running the setup.py, netifaces is not yet installed

LOCAL_IPS : list [str] = ["lo","127.0.0.1"]

def getIPList():
    addrList = []
    ifaces : list = netifaces.interfaces()
    if ifaces:
        
        for iface in ifaces:
            ifcAddresses = netifaces.ifaddresses(iface)
            if ifcAddresses:
                ifcInetAddresses = ifcAddresses.get(netifaces.AF_INET)
                if ifcInetAddresses:
                    for inetAddr in ifcInetAddresses:
                        addr = inetAddr.get("addr")
                        if addr and addr not in LOCAL_IPS:
                            addrList.append(addr)
    return addrList

def getIPStr(addrList : list = None, sep : str = ", "):
    if not addrList:
        addrList = getIPList()
        addrList.sort()
    addrStr = sep.join(addrList)
    return addrStr

def main():
    IPs : str = getIPStr(sep=os.linesep)
    print( IPs )

if (__name__ == "__main__"):
    main()
