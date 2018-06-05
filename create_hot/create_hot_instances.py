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
g.write("        - network: monitor\n")
g.write("      security_groups:\n")
g.write("        - { get_resource: security_group_allallow }\n")
g.write("\n")


s = 0

for line in f:
    l = line[:-1].split(" ")
    if s == 0:
        asn = l[1]
        s = 1
    elif s == 1:
        s = 2
    elif s == 2:

        # exclude google (google is Catalyst 4500)
        if asn == "15169":
            s = 0
            continue

        # create instance
        g.write("  asn{0}:\n".format(asn))
        g.write("    type: OS::Nova::Server\n")
        g.write("    properties:\n")
        g.write("      name: asn{}\n".format(asn))
        g.write("      key_name: default\n")
        g.write("      flavor: router\n")
        g.write("      block_device_mapping_v2:\n")
        g.write("        - image: Ubuntu-Router\n")
        g.write("          volume_size: 10\n")
        g.write("      networks:\n")
        g.write("        - network: monitor\n")
        for filename in files:
            if "-" + asn in filename or asn + "-" in filename:
                # connect to google
                if "-15169" in filename or "15169-" in filename:
                    g.write("        - network: to_catalyst\n")
                # other
                else:
                    g.write("        - network: {0}\n".format(filename))
        g.write("      security_groups:\n")
        g.write("        - { get_resource: security_group_allallow }\n")
        g.write("\n")

        s = 0
g.close()
f.close()
