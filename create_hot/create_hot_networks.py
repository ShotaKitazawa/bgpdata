#!/usr/bin/env python3
# Author: Shota Kitazawa

import os
import sys
import ipaddress

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
f.write("  monitor_port:\n")
f.write("    type: OS::Neutron::Port\n")
f.write("    properties:\n")
f.write("      network: { get_resource: monitor_network }\n")
f.write("      fixed_ips:\n")
f.write("        - subnet: { get_resource: monitor_subnet }\n")
f.write("          ip_address: 172.16.0.254\n")
f.write("\n")

vlan_id = 101
vlan_dict = {}

for netname in files:

    # connect to google
    if "15169-" in netname[:len("15169-")] or "-15169" in netname[-1 * len("-15169"):]:

        # create network
        f.write("  net_{}:\n".format(netname))
        f.write("    type: OS::Neutron::ProviderNet\n")
        f.write("    properties:\n")
        f.write("      name: {}\n".format(netname))
        f.write("      physical_network: provider\n")
        f.write("      network_type: vlan\n")
        f.write("      segmentation_id: {}\n".format(vlan_id))
        f.write("      router_external: true\n")

        # create subnet
        f.write("  subnet_{0}:\n".format(netname))
        f.write("    type: OS::Neutron::Subnet\n")
        f.write("    properties:\n")
        f.write("      name: {}\n".format(netname))
        f.write("      network_id: {{ get_resource: net_{} }}\n".format(netname))
        f.write("      ip_version: 4\n")
        with open(DIR + "/network/" + netname, "r") as g:
            f.write("      cidr: {}\n".format(g.readline()))
        f.write("      enable_dhcp: false\n")
        f.write("\n")

        # append address to dict
        vlan_dict[vlan_id] = netname

        vlan_id += 1

    # other
    else:
        g = open(DIR + "/network/" + netname, "r")
        netaddr = g.readline()
        hosts = [str(list(ipaddress.ip_network(netaddr).hosts())[0]), str(list(ipaddress.ip_network(netaddr).hosts())[1])]
        g.close()

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
        f.write("      cidr: {}\n".format(netaddr))
        f.write("      enable_dhcp: false\n")

#        # create port
#        f.write("  port_{}_1:\n".format(netname))
#        f.write("    type: OS::Neutron::Port\n")
#        f.write("    properties:\n")
#        f.write("      fixed_ips:\n")
#        f.write("        - subnet: {{ get_resource: subnet_{} }}\n".format(netname))
#        f.write("          ip_address: {}\n".format(hosts[0]))
#        f.write("  port_{}_2:\n".format(netname))
#        f.write("    type: OS::Neutron::Port\n")
#        f.write("    properties:\n")
#        f.write("      fixed_ips:\n")
#        f.write("        - subnet: {{ get_resource: subnet_{} }}\n".format(netname))
#        f.write("          ip_address: {}\n".format(hosts[1]))

        f.write("\n")

f.close()

with open(DIR + "/catalyst.conf", "w") as f:
    for vlan_id, netname in vlan_dict.items():

        with open(DIR + "/network/" + netname, "r") as g:
            if "15169-" in netname[:len("15169-")]:
                address = str(list(ipaddress.ip_network(g.readline()).hosts())[0])
            elif "-15169" in netname[-1 * len("-15169"):]:
                address = str(list(ipaddress.ip_network(g.readline()).hosts())[1])
            else:
                raise("Error")

        # write conf
        f.write("vlan {}\n".format(vlan_id))
        f.write(" name vlan{}\n".format(vlan_id))
        f.write("!\n")
        f.write("interface Vlan{}\n".format(vlan_id))
        f.write(" ip address {} 255.255.255.248\n".format(address))
        f.write(" no shutdown\n")
        f.write("!\n")

    f.write("router bgp 15169\n")

    for vlan_id, netname in vlan_dict.items():
        with open(DIR + "/network/" + netname, "r") as g:
            if "15169-" in netname[:len("15169-")]:
                neighbor_address = str(list(ipaddress.ip_network(g.readline()).hosts())[1])
                neighbor_as = netname[len("15169-"):]
            elif "-15169" in netname[-1 * len("-15169"):]:
                neighbor_address = str(list(ipaddress.ip_network(g.readline()).hosts())[0])
                neighbor_as = netname[:-1 * len("-15169")]
            else:
                raise("Error")

        f.write(" neighbor {0} remote-as {1}\n".format(neighbor_address, neighbor_as))

    f.write("!\n")

    # TODO: RouteAdvertize: (config-router)# network network mask mask
