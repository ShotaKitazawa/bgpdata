#!/usr/bin/env python3
# Author: Shota Kitazawa

import os
import sys

DIR = os.path.abspath(os.path.dirname(__file__))
files = os.listdir(DIR + "/network/")
f = open(DIR + "/hot-networks.yaml", "w")

# template
f.write("heat_template_version: pike\n")
f.write("\n")
f.write("resources:\n")
f.write("\n")

# create Monitor network
f.write("  monitor_network:\n")
f.write("    type: OS::Neutron::Net\n")
f.write("    properties:\n")
f.write("      name: monitor\n")
f.write("  monitor_subnet:\n")
f.write("    type: OS::Neutron::Subnet\n")
f.write("    properties:\n")
f.write("      name: monitor\n")
f.write("      network_id: { get_resource: monitor_network }\n")
f.write("      ip_version: 4\n")
f.write("      cidr: 172.16.0.0/16\n")
f.write("\n")

for netname in files:

    # create network
    f.write("  net_{}:\n".format(netname))
    f.write("    type: OS::Neutron::Net\n")
    f.write("    properties:\n")
    f.write("      name: {}\n".format(netname))

    # create subnet
    f.write("  subnet_{0}:\n".format(netname))
    f.write("    type: OS::Neutron::Subnet\n")
    f.write("    properties:\n")
    f.write("      name: {}\n".format(netname))
    f.write("      network_id: {{ get_resource: net_{} }}\n".format(netname))
    f.write("      ip_version: 4\n")
    with open(DIR + "/network/" + netname, "r") as g:
        f.write("      cidr: {}\n".format(g.readline()))
    f.write("      dns_nameservers:\n")
    f.write("        - 8.8.8.8\n")
    f.write("      enable_dhcp: false\n")
    f.write("\n")

f.close()
