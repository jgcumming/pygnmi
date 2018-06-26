def get_capabilities(channel, options, log):
  try:
    import grpc
    import gnmi_pb2
  except ImportError as err:
    log.error(str(err))
    quit()
  stub = gnmi_pb2.gNMIStub(channel)
  metadata = [('username',options.username), ('password',options.password)]
  responses = gnmi_pb2.CapabilityResponse()
  responses = stub.Capabilities(gnmi_pb2.CapabilityRequest(),5,metadata=metadata)
  print responses

