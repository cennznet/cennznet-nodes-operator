#!/usr/bin/env python3
import os
from kubernetes import client, config
from requests.sessions import session
from substrateinterface import SubstrateInterface
import yaml
from yaml.tokens import KeyToken

class NodeCluster(object):
    k8s_cluster = None
    pub_keytype_mapping = dict(
        gran = 'ed_pub_key',
        babe = 'sr_pub_key',
        imon = 'sr_pub_key',
        audi = 'sr_pub_key'
    )
    def __init__(self):
        self.loadKubeConfig()
        self.k8s_cluster = client.CoreV1Api()

    def loadKubeConfig(self):
        config_path = os.path.expanduser(config.KUBE_CONFIG_DEFAULT_LOCATION)
        if os.path.exists(config_path):
            config.load_kube_config()
        else:
            config.load_incluster_config()
            
    def getPodsIPsByNamespace(self, namespace=None):
        pods = self.getPodsByNamespace(namespace)
        return dict(list(map(lambda p: (p.metadata.name, p.status.pod_ip), pods.items)))

    def insertSessionKey(self, ip, keySet):
        interface = SubstrateInterface("http://%s:9933" % ip)
        ret = dict()
        ret['gran'] = interface.rpc_request("author_insertKey", ["gran", keySet["ed_secret_key"], keySet["ed_pub_key"]])
        ret['babe'] = interface.rpc_request("author_insertKey", ["babe", keySet["sr_secret_key"], keySet["sr_pub_key"]])
        ret['imon'] = interface.rpc_request("author_insertKey", ["imon", keySet["sr_secret_key"], keySet["sr_pub_key"]])
        ret['audi'] = interface.rpc_request("author_insertKey", ["audi", keySet["sr_secret_key"], keySet["sr_pub_key"]])
        if keySet["ec_secret_key"] and keySet["ec_pub_key"]:
            ret['eth-'] = interface.rpc_request("author_insertKey", ["eth-", keySet["ec_secret_key"], keySet["ec_pub_key"]])
        return ret

    def hasSessionKey(self, ip, keySets):
        interface = SubstrateInterface(
            url="http://%s:9933" % ip,
            type_registry_preset='default'
        )
        ret = dict()
        for keyType in ['gran', 'babe', 'imon', 'audi']:
            key = keySets.get(self.pub_keytype_mapping[keyType])
            rpc_ret = interface.rpc_request("author_hasKey", [key, keyType])
            ret[keyType] = rpc_ret.get('result', False)
        return ret

    def matchKeys(self, namespace, sessions):
        matched = dict()
        ips = dict(self.getPodsIPsByNamespace(namespace))
        for hostname, keySets in sessions.items():
            for nodename, ip in ips.items():
                ret = self.hasSessionKey(ip, keySets)
                if len(list(filter(lambda ret: ret, ret.values()))) == 4:
                    matched[nodename] = keySets
        return matched

    def rotateSessionKey(self, ip):
        interface = SubstrateInterface("http://%s:9933" % ip)
        ret = dict()
        ret = interface.rpc_request("author_rotateKeys", [])
        return ret

    def validatorKeys(self, namespace, sessions):
        ips = dict(self.getPodsIPsByNamespace(namespace))
        for nodename in sessions.keys():
            ip = ips[nodename]
            print(ip, sessions)
            ret = self.insertSessionKey(ip, sessions[nodename])
            print(ret)

    def validatorRotateKeys(self, namespace):
        ips = dict(self.getPodsIPsByNamespace(namespace))
        for nodename in sessions.keys():
            ip = ips[nodename]
            ret = self.rotateSessionKey(ip)
            print(ret)

if __name__ == '__main__':
    namespace = 'aws-us-cennznet-validators'
    with open('sessions.yaml', 'r') as session_mapping:
        sessions = yaml.safe_load(session_mapping)

    cluster = NodeCluster()
    #ret = cluster.matchKeys(namespace, sessions)
    cluster.validatorKeys(namespace, sessions)

    #for nodename, keySet in ret.items():
    #    print(nodename, keySet['sr_pub_key'])
