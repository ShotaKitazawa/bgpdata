#!/usr/bin/env python3
# Author: Takehiko Momma
# Author: Shota Kitazawa

import os
import sys

if len(sys.argv) < 1 and not os.path.isfile(sys.argv[1]):
    print("err: invalid command: python", sys.argv[0], "analyzed_file")
    sys.exit(1)

f = open(sys.argv[1], "r", encoding='utf-8')

DIR = os.path.abspath(os.path.dirname(__file__))
files = os.listdir(DIR + "/network")
filename = DIR + "/hot-instances.yaml"
g = open(filename, "w")

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

# create Monitoring network
g.write("  monitoring_network:\n")
g.write("    type: OS::Neutron::Net\n")
g.write("    properties:\n")
g.write("      name: monitoring\n")
g.write("  monitoring_subnet:\n")
g.write("    type: OS::Neutron::Subnet\n")
g.write("    properties:\n")
g.write("      name: monitoring\n")
g.write("      network_id: { get_resource: monitoring_network }\n")
g.write("      ip_version: 4\n")
g.write("      cidr: 172.16.0.0/16\n")
g.write("\n")

s = 0

for line in f:
    l = line[:-1].split(" ")
    if s == 0:
        AS = l[1]
        s = 1
    elif s == 1:
        s = 2
    elif s == 2:

        # create volume
        g.write("  as{}_cinder_volume:\n".format(AS))
        g.write("    type: OS::Cinder::Volume\n")
        g.write("    properties:\n")
        g.write("      name: as{}\n".format(AS))
        g.write("      image: Ubuntu-Router\n")
        g.write("      size: 10\n")
        g.write("      availability_zone: nova\n")

        # create instance
        g.write("  as{0}:\n".format(AS))
        g.write("    type: OS::Nova::Server\n")
        g.write("    properties:\n")
        g.write("      name: as{}\n".format(str(AS)))
        g.write("      key_name: default\n")
        g.write("      flavor: router\n")
        g.write("      block_device_mapping_v2:\n")
        g.write("        - volume_id: {{ get_resource: as{}_cinder_volume }}\n".format(AS))
        g.write("      networks:\n")
        g.write("        - network: { get_resource: monitoring_network }\n")
        for file in files:
            if "-" + AS in file or AS + "-" in file:
                g.write("        - network: {0}\n".format(str(file)))
        g.write("      security_groups:\n")
        g.write("        - { get_resource: security_group_allallow }\n")
        g.write("\n")

        s = 0
g.close()
f.close()
