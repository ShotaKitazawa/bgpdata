#!/usr/bin/env python3
# Author: Takehiko Momma
# Author: Shota Kitazawa

import os
import sys
import ipaddress
from collections import OrderedDict

import tqdm

if len(sys.argv) < 1 and not os.path.isfile(sys.argv[1]):
    print("err: invalid command: python", sys.argv[0], "analyzed_file")
    sys.exit(1)

f = open(sys.argv[1], "r", encoding='utf-8')

DIR = os.path.abspath(os.path.dirname(__file__))
files = os.listdir(DIR + "/network")
g = open(DIR + "/hot-instances.yaml", "w")

# template
g.write("heat_template_version: pike\n")
g.write("\n")
g.write("resources:\n")
g.write("\n")

# create AllAllow security group
g.write("  security_group_allallow:\n")
g.write("    type: OS::Neutron::SecurityGroup\n")
g.write("    properties:\n")
g.write("      name: AllAllow\n")
g.write("      rules:\n")
g.write("        - direction: ingress\n")
g.write("          ethertype: IPv4\n")
g.write("          remote_ip_prefix: 0.0.0.0/0\n")
g.write("          protocol: tcp\n")
g.write("        - direction: ingress\n")
g.write("          ethertype: IPv4\n")
g.write("          remote_ip_prefix: 0.0.0.0/0\n")
g.write("          protocol: udp\n")
g.write("        - direction: ingress\n")
g.write("          ethertype: IPv4\n")
g.write("          remote_ip_prefix: 0.0.0.0/0\n")
g.write("          protocol: icmp\n")
g.write("\n")

# create monitor instance
g.write("  monitor_volume:\n")
g.write("    type: OS::Cinder::Volume\n")
g.write("    properties:\n")
g.write("      name: monitor\n")
g.write("      image: Ubuntu-Monitor\n")
g.write("      size: 10\n")
g.write("      availability_zone: nova\n")
g.write("  monitor_server:\n")
g.write("    type: OS::Nova::Server\n")
g.write("    properties:\n")
g.write("      name: monitor\n")
g.write("      key_name: default\n")
g.write("      flavor: monitor\n")
g.write("      block_device_mapping_v2:\n")
g.write("        - volume_id: { get_resource: monitor_volume }\n")
g.write("      networks:\n")
g.write("        - port: monitor\n")
g.write("        - network: external\n")
#g.write("      security_groups:\n")
#g.write("        - { get_resource: security_group_allallow }\n")
g.write("\n")

s = 0
for line in f:

    # networks["network_name"] = "network_address/mask"
    networks = OrderedDict()
    # my_addresses["interface"] = "my_address"
    my_addresses = OrderedDict()
    # neighbor_addresses["neighbor_as_number"] = "neighbor_address"
    neighbor_addresses = OrderedDict()

    l = line[:-1].split(" ")
    if s == 0:
        asn = l[1]
        s = 1
    elif s == 1:
        # print(str(list(ipaddress.ip_network(l[3:-1][0]).hosts())[0]))
        as_addresses = []
        for network_address in l[3:-1]:
            prefixlen = ipaddress.ip_network(network_address).prefixlen
            if (prefixlen != 32):
                as_addresses.append(str(list(ipaddress.ip_network(network_address).hosts())[0]) + "/" + str(prefixlen))
            else:
                as_addresses.append(network_address)
        s = 2
    elif s == 2:

        # exclude google (google is Catalyst 4500)
        if asn == "15169":
            s = 0
            continue

        # store own network
        # for monitor
        networks["monitor"] = "172.16.0.0/16"
        my_addresses["eth0"] = "dhcp"
        # for between-as
        cnt = 1
        for filename in files:
            if asn + "-" in filename[:len(asn + "-")]:
                with open(DIR + "/network/" + filename, "r") as h:
                    address = h.readline()
                    networks[filename] = str(address)
                    my_addresses["eth" + str(cnt)] = str(list(ipaddress.ip_network(address).hosts())[0])
                    cnt += 1
                    neighbor_addresses[filename[len(asn + "-"):]] = str(list(ipaddress.ip_network(address).hosts())[1])
            elif "-" + asn in filename[len(-1 * ("-" + asn)):]:
                with open(DIR + "/network/" + filename, "r") as h:
                    networks[filename] = str(address)
                    address = h.readline()
                    my_addresses["eth" + str(cnt)] = str(list(ipaddress.ip_network(address).hosts())[1])
                    cnt += 1
                    neighbor_addresses[filename[:-1 * len("-" + asn)]] = str(list(ipaddress.ip_network(address).hosts())[0])

        # create software config
        g.write("  script_asn{0}_1:\n".format(asn))
        g.write("    type: OS::Heat::SoftwareConfig\n")
        g.write("    properties:\n")
        g.write("      group: ungrouped\n")
        g.write("      config:\n")
        g.write("        str_replace:\n")
        g.write("          template:\n")
        g.write("            get_file: netconf.sh\n")
        g.write("          params:\n")
        g.write("            '$$interfaces': '{0}'\n".format(' '.join(my_addresses.keys())))
        g.write("            '$$addresses': '{0}'\n".format(' '.join(my_addresses.values())))
        g.write("            '$$networks': '{0}'\n".format(' '.join(networks.values())))
        g.write("            '$$asaddresses': '{0}'\n".format(' '.join(as_addresses)))
        g.write("  script_asn{0}_2:\n".format(asn))
        g.write("    type: OS::Heat::SoftwareConfig\n")
        g.write("    properties:\n")
        g.write("      group: ungrouped\n")
        g.write("      config:\n")
        g.write("        str_replace:\n")
        g.write("          template:\n")
        g.write("            get_file: gobgp.sh\n")
        g.write("          params:\n")
        g.write("            '$$my_as': '{0}'\n".format(asn))
        g.write("            '$$neighbor_ases': '{0}'\n".format(' '.join(neighbor_addresses.keys())))
        g.write("            '$$neighbor_addresses': '{0}'\n".format(' '.join(neighbor_addresses.values())))
        g.write("  scripts_asn{0}:\n".format(asn))
        g.write("    type: OS::Heat::MultipartMime\n")
        g.write("    properties:\n")
        g.write("      parts:\n")
        g.write("        - config: {{ get_resource: script_asn{0}_1 }}\n".format(asn))
        g.write("        - config: {{ get_resource: script_asn{0}_2 }}\n".format(asn))

        # create instance
        g.write("  volume_asn{0}:\n".format(asn))
        g.write("    type: OS::Cinder::Volume\n")
        g.write("    properties:\n")
        g.write("      name: asn{0}\n".format(asn))
        g.write("      image: Ubuntu-Router\n")
        g.write("      size: 10\n")
        g.write("      availability_zone: nova\n")
        g.write("  server_asn{0}:\n".format(asn))
        g.write("    type: OS::Nova::Server\n")
        g.write("    properties:\n")
        g.write("      name: asn{0}\n".format(asn))
        g.write("      key_name: default\n")
        g.write("      flavor: router\n")
        g.write("      block_device_mapping_v2:\n")
        g.write("        - volume_id: {{ get_resource: volume_asn{0} }}\n".format(asn))
        g.write("      networks:\n")
        for i, network in enumerate(networks.keys()):
            g.write("        - network: {0}\n".format(network))
            if my_addresses["eth" + str(i)] != "dhcp":
                g.write("          fixed_ip: {0}\n".format(my_addresses["eth" + str(i)]))
        g.write("      security_groups:\n")
        g.write("        - { get_resource: security_group_allallow }\n")
        g.write("      user_data_format: SOFTWARE_CONFIG\n")
        g.write("      user_data: {{ get_resource: scripts_asn{0} }}\n".format(asn))
        g.write("\n")

        s = 0
g.close()
f.close()
