#!/usr/bin/python

##############################################################################
#                                                                            #
#  grpc_support.py                                                           #
#                                                                            #
#  History Change Log:                                                       #
#                                                                            #
#    1.0  [JGC]  2018/06/26    first version                                 #
#                                                                            #
#  Objective:                                                                #
#                                                                            #
#    Supporting module for pygnmi.py                                         #
#    Some ported from previous version of gNMI_Subscribe.py                  #
#                                                                            #
#  Features supported:                                                       #
#                                                                            #
#    - create_channel (secure and insecure)                                  #
#    - logging                                                               #
#    - path manipulation                                                     #
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
gNMI Supporting Modules in Python Version 1.0
Copyright (C) 2017 Nokia. All Rights Reserved.
"""

__title__   = "grpc_support"
__version__ = "1.0"
__status__  = "dev"
__author__  = "James Cumming"
__date__    = "2018 June 26th"

##############################################################################

import argparse
import re
import sys
import os
import logging
import time
import gnmi_pb2

##############################################################################

def create_channel(options,log):
    try:
        import grpc
    except ImportError as err:
        log.error(str(err))
        quit()

    if options.tls or options.cert:
        log.debug("Create SSL Channel")
        if options.cert:
            cred = grpc.ssl_channel_credentials(root_certificates=open(options.cert).read())
            opts = []
            if options.altName:
                opts.append(('grpc.ssl_target_name_override', options.altName,))
            if options.noHostCheck:
                log.error('Disable server name verification against TLS cert is not yet supported!')
                # TODO: Clarify how to setup gRPC with SSLContext using check_hostname:=False

            channel = grpc.secure_channel(options.server, cred, opts)
            return channel
        else:
            log.error('Disable cert validation against root certificate (InsecureSkipVerify) is not yet supported!')
            # TODO: Clarify how to setup gRPC with SSLContext using verify_mode:=CERT_NONE

            cred = grpc.ssl_channel_credentials(root_certificates=None, private_key=None, certificate_chain=None)
            channel = grpc.secure_channel(options.server, cred)
            return channel

    else:
        log.info("Create insecure Channel... Username: "+options.username+" Password: "+options.password)
        channel = grpc.insecure_channel(options.server)
        return channel

def list_from_path(path='/'):
    if path:
        if path[0]=='/':
            if path[-1]=='/':
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:-1]
            else:
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[1:]
        else:
            if path[-1]=='/':
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)[:-1]
            else:
                return re.split('''/(?=(?:[^\[\]]|\[[^\[\]]+\])*$)''', path)
    return []


def path_from_string(path='/'):
    mypath = []

    for e in list_from_path(path):
        eName = e.split("[", 1)[0]
        eKeys = re.findall('\[(.*?)\]', e)
        dKeys = dict(x.split('=', 1) for x in eKeys)
        mypath.append(gnmi_pb2.PathElem(name=eName, key=dKeys))

    return gnmi_pb2.Path(elem=mypath)


def gen_request( opt,log ):
    mysubs = []
    for path in opt.xpaths:
        mypath = path_from_string(path)
        mysub = gnmi_pb2.Subscription(path=mypath, mode=opt.submode, suppress_redundant=opt.suppress, sample_interval=opt.interval*1000000000, heartbeat_interval=opt.heartbeat)
        mysubs.append(mysub)

    if opt.prefix:
        myprefix = path_from_string(opt.prefix)
    else:
        myprefix = None

    if opt.qos:
        myqos = gnmi_pb2.QOSMarking(marking=opt.qos)
    else:
        myqos = None

    mysblist = gnmi_pb2.SubscriptionList(prefix=myprefix, mode=opt.mode, allow_aggregation=opt.aggregate, encoding=opt.encoding, subscription=mysubs, use_aliases=opt.use_alias, qos=myqos)
    mysubreq = gnmi_pb2.SubscribeRequest( subscribe=mysblist )

    log.info('Sending SubscribeRequest\n'+str(mysubreq))
    yield mysubreq

##############################################################################

def setup_log(options,prog):
    #  setup logging

    if options.quiet:
        loghandler = logging.NullHandler()
        loglevel = logging.NOTSET
    else:
        if options.verbose==None:
            logformat = '%(asctime)s,%(msecs)-3d %(message)s'
        else:
            logformat = '%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(message)s'

        if options.verbose==None or options.verbose==1:
            loglevel = logging.INFO
        else:
            loglevel = logging.DEBUG

        # For supported GRPC trace options check:
        #   https://github.com/grpc/grpc/blob/master/doc/environment_variables.md

        if options.verbose==3:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "ERROR"

        if options.verbose==4:
          os.environ["GRPC_TRACE"] = "api,call_error,channel,connectivity_state,op_failure"
          os.environ["GRPC_VERBOSITY"] = "INFO"

        if options.verbose==5:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "INFO"

        if options.verbose==6:
          os.environ["GRPC_TRACE"] = "all"
          os.environ["GRPC_VERBOSITY"] = "DEBUG"

        timeformat = '%y/%m/%d %H:%M:%S'
        loghandler = logging.StreamHandler(options.logfile)
        loghandler.setFormatter(logging.Formatter(logformat, timeformat))

    log = logging.getLogger(prog)
    log.setLevel(loglevel)
    log.addHandler(loghandler)
    return log

# EOF

