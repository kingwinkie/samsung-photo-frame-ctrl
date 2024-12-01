#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import logging as LOGGER
try:
    import netifaces
except ImportError:
    netifaces = None
    pass  # When running the setup.py, netifaces is not yet installed


LOCAL_IPS : list [str] = ["lo","127.0.0.1"]

def getIPList():
    addrList = []
    if netifaces:
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
    parser = argparse.ArgumentParser(exit_on_error=True,
                    prog='getips',
                    description='Returns IP adress(es) if format useful for txt2img',
                    epilog="""
                    """)

    parser.add_argument('-th','--textheader', help="Header text")
    parser.add_argument('-v', '--verbose', help="Show Info messages", action='store_true') 
    
    args = parser.parse_args()
    logLevel : LOGGER = LOGGER.DEBUG if args.verbose else LOGGER.ERROR
    LOGGER.basicConfig(level=logLevel)
    LOGGER.info("Starting")
    IPs : str = getIPStr(sep=os.linesep)
    output : str = None
    if args.textheader:
        output = args.textheader + os.linesep + IPs
    else:
        output = IPs
    print( output )

if (__name__ == "__main__"):
    main()
