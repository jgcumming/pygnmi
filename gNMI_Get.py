#!/usr/bin/python

##############################################################################
#                                                                            #
#  gNMI_Get.py                                                               #
#                                                                            #
#  History Change Log:                                                       #
#                                                                            #
#    1.0  [JGC]  2018/06/26    first version                                 #
#                                                                            #
#  Objective:                                                                #
#                                                                            #
#    gNMI Get (GRPC Network Management Interface) in Python                  #
#                                                                            #
#  License:                                                                  #
#                                                                            #
#    Licensed under the MIT license                                          #
#    See LICENSE.md delivered with this project for more information.        #
#                                                                            #
#  Author:                                                                   #
#                                                                            #
#    James Cumming [JGC]                                                     #
#    mail:  james.cumming(at)nokia.com                                       #
#                                                                            #
##############################################################################

"""
gNMI Get in Python Version 1.0
Copyright (C) 2018 Nokia. All Rights Reserved.
"""

__title__   = "gNMI_Get"
__version__ = "1.0"
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

def gen_request( opt, log ):
    import gnmi_pb2
    mypaths = []
    for path in opt.xpaths:
        mypath = grpc_support.path_from_string(path)
        mypaths.append(mypath)

    if opt.prefix:
        myprefix = path_from_string(opt.prefix)
    else:
        myprefix = None

    if opt.qos:
        myqos = gnmi_pb2.QOSMarking(marking=opt.qos)
    else:
        myqos = None

    return gnmi_pb2.GetRequest(path=mypaths)
   

def get(channel, options, log, prog):
    try:
        import grpc
        import gnmi_pb2
    except ImportError as err:
        log.error(str(err))
        quit()

    log.debug("Create gNMI stub")
    stub = gnmi_pb2.gNMIStub(channel)

    req_iterator = gen_request( options, log )
    metadata = [('username',options.username), ('password', options.password)]

    msgs = 0
    upds = 0
    secs = 0
    start = 0

    try:
        response = gnmi_pb2.GetResponse()
        response = stub.Get(req_iterator, options.timeout, metadata=metadata)

#        if response.HasField('notification'):
#            log.debug('Sync Response received\n'+str(response))
#            secs += time.time() - start
#            start = 0
#            if options.stats:
#                log.info("%d updates and %d messages within %1.2f seconds", upds, msgs, secs)
#                log.info("Statistics: %5.0f upd/sec, %5.0f msg/sec", upds/secs, msgs/secs)
#        elif response.HasField('error'):
#            log.error('gNMI Error '+str(response.error.code)+' received\n'+str(response.error.message))
#        elif response.HasField('update'):
#            if start==0:
#                start=time.time()
#            msgs += 1
#            upds += len(response.update.update)
#            if not options.stats:
#                log.info('Update received\n'+str(response))
#        else:
#            log.error('Unknown response received:\n'+str(response))

    except KeyboardInterrupt:
        log.info("%s stopped by user", prog)

    except grpc.RpcError as x:
        log.error("grpc.RpcError received:\n%s", x.details)

    except Exception as err:
        log.error(err)

    if (msgs>1):
        log.info("%d update messages received", msgs)
        return msgs

    return response

# EOF

