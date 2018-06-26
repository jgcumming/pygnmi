#!/usr/bin/python

##############################################################################
#                                                                            #
#  pygnmi.py                                                                 #
#                                                                            #
#  History Change Log:                                                       #
#                                                                            #
#    1.0  [SW]  2017/06/02    first version                                  #
#    1.1  [SW]  2017/07/06    timeout behavior improved                      #
#    1.2  [SW]  2017/08/08    logging improved, options added                #
#    1.3  [SW]  2017/12/04    support for gNMI v0.4                          #
#    1.4  [JGC] 2018/06/26    separated to allow for more structured         #
#                             development of other gNMI service operations   #
#                                                                            #
#  Objective:                                                                #
#                                                                            #
#    Testing tool for the gNMI (GRPC Network Management Interface) in Python #
#                                                                            #
#  Features supported:                                                       #
#                                                                            #
#    - gNMI Capabilities                                                     #
#    - gNMI Subscribe (Based on Nokia SR OS release 16 feature-set)          #
#    - secure and insecure mode                                              #
#    - multiple subscriptions paths                                          #
#                                                                            #
#  Not yet supported:                                                        #
#                                                                            #
#    - Disable server name verification against TLS cert (opt: noHostCheck)  #
#    - Disable cert validation against root certificate (InsecureSkipVerify) #
#    - gNMI Get                                                              #
#    - gNMI Set                                                              #
#                                                                            #
#  License:                                                                  #
#                                                                            #
#    Licensed under the MIT license                                          #
#    See LICENSE.md delivered with this project for more information.        #
#                                                                            #
#  Author:                                                                   #
#                                                                            #
#    Sven Wisotzky [SW]                                                      #
#    mail:  sven.wisotzky(at)nokia.com                                       #
#                                                                            #
#    James Cumming [JGC]                                                     #
#    mail:  james.cumming(at)nokia.com                                       #
#                                                                            #
##############################################################################


"""
gNMI Subscribe Client in Python Version 1.4
Copyright (C) 2017 Nokia. All Rights Reserved.
"""

__title__   = "gNMI_Subscribe"
__version__ = "1.4"
__status__  = "dev"
__author__  = "James Cumming"
__date__    = "2018 June 26th"

##############################################################################

import argparse
import re
import sys
import os
import time
import grpc_support

##############################################################################

def subscribe(channel, options,log):
    try:
        import grpc
        import gnmi_pb2
    except ImportError as err:
        log.error(str(err))
        quit()

    log.debug("Create gNMI stub")
    stub = gnmi_pb2.gNMIStub(channel)

    req_iterator = grpc_support.gen_request( options, log )
    metadata = [('username',options.username), ('password', options.password)]

    msgs = 0
    upds = 0
    secs = 0
    start = 0

    try:
        responses = stub.Subscribe(req_iterator, options.timeout, metadata=metadata)
        for response in responses:
            if response.HasField('sync_response'):
                log.debug('Sync Response received\n'+str(response))
                secs += time.time() - start
                start = 0
                if options.stats:
                    log.info("%d updates and %d messages within %1.2f seconds", upds, msgs, secs)
                    log.info("Statistics: %5.0f upd/sec, %5.0f msg/sec", upds/secs, msgs/secs)
            elif response.HasField('error'):
                log.error('gNMI Error '+str(response.error.code)+' received\n'+str(response.error.message))
            elif response.HasField('update'):
                if start==0:
                    start=time.time()
                msgs += 1
                upds += len(response.update.update)
                if not options.stats:
                    log.info('Update received\n'+str(response))
            else:
                log.error('Unknown response received:\n'+str(response))

    except KeyboardInterrupt:
        log.info("%s stopped by user", prog)

    except grpc.RpcError as x:
        log.error("grpc.RpcError received:\n%s", x.details)

    except Exception as err:
        log.error(err)

    if (msgs>1):
        log.info("%d update messages received", msgs)

# EOF

