# Author: Takehiko Momma

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
g.write("heat_template_version: pike\n")
g.write("\n")
g.write("resources:\n")


s = 0

for line in f:
    l = line[:-1].split(" ")
    if s == 0:
        AS = l[1]
        s = 1
    elif s == 1:
        s = 2
    elif s == 2:
        # if AS == "15169":
        #    s = 0
        #    continue
        g.write("  as{0}:\n".format(AS))
        g.write("    type: OS::Nova::Server\n")
        g.write("    properties:\n")
        g.write("      name: as{}\n".format(str(AS)))
        g.write("      image: Ubuntu-Router\n")
        g.write("      flavor: router\n")
        g.write("      networks:\n")
        for file in files:
            if "-" + AS in file or AS + "-" in file:
                g.write("        - network: {0}\n".format(str(file)))
        g.write("      security_groups:\n")
        g.write("        - AllAllow\n")
        g.write("      key_name: default\n")
        g.write("  as{}_cinder_volume:\n".format(AS))
        g.write("    type: OS::Cinder::Volume\n")
        g.write("    properties:\n")
        g.write("      size: 20\n")
        g.write("      availability_zone: nova\n")
        g.write("  as{}_volume_attachment:\n".format(AS))
        g.write("    type: OS::Cinder::VolumeAttachment\n")
        g.write("    properties:\n")
        g.write("      volume_id: {{ get_resource: as{}_cinder_volume }}\n".format(AS))
        g.write("      instance_uuid: {{ get_resource: as{} }}\n".format(AS))
        g.write("      mountpoint: /dev/vda\n")
        g.write("\n")

        s = 0
g.close()
f.close()
