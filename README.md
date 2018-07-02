# pygnmi
Python tools for gNMI

## Installation
Python tools for gNMI can be used with Python 2.7 and Python3.
Please follow gRPC Installation Guide from:
https://grpc.io/docs/quickstart/python

```
$ pip install --upgrade pip
$ pip install grpcio
$ pip install grpcio-tools googleapis-common-protos
$ curl -O https://raw.githubusercontent.com/openconfig/gnmi/master/proto/gnmi/gnmi_pb2.py
$ python pygnmi.py --help
```

## The default service is 'capabilities'

## Usage Example (CAPABILITIES):

```
$ pygnmi.py --service capabilities --username grpc --password nokia123 \
            --server 192.168.5.10:57400

18/07/02 08:21:51,712 Create insecure channel to 192.168.5.10:57400 Username: grpc Password: nokia123
18/07/02 08:21:51,714 Obtaining capabilities from 192.168.5.10:57400
supported_models {
  name: "nokia-conf"
  organization: "Nokia"
  version: "16.0.R1"
}
supported_models {
  name: "nokia-state"
  organization: "Nokia"
  version: "16.0.R1"
}
supported_encodings: JSON
gNMI_version: "0.4.0"

```

## Usage Example (SUBSCRIBE):

```
$ python pygnmi.py  --server 192.168.33.2:57400 --username grpc --password Nokia4gnmi \
                    --service subscribe --cert CAcert.pem \
                    --ciphers AES128 /state/port[port-id=1/1/1]/ethernet/statistics/out-utilization

17/12/04 16:02:43,160 Sending SubscribeRequest
subscribe {
  subscription {
    path {
      elem {
        name: "state"
      }
      elem {
        name: "port"
        key {
          key: "port-id"
          value: "1/1/1"
        }
      }
      elem {
        name: "ethernet"
      }
      elem {
        name: "statistics"
      }
      elem {
        name: "out-utilization"
      }
    }
    mode: SAMPLE
    sample_interval: 10000000000
  }
}

17/12/04 16:02:54,532 Update received
update {
  timestamp: 1512399461394858020
  prefix {
    elem {
      name: "state"
    }
    elem {
      name: "port"
      key {
        key: "port-id"
        value: "1/1/1"
      }
    }
    elem {
      name: "ethernet"
    }
    elem {
      name: "statistics"
    }
  }
  update {
    path {
      elem {
        name: "out-utilization"
      }
    }
    val {
      json_val: "0"
    }
  }
}


^C
17/12/04 16:03:04,511 pygnmi stopped by user
```
