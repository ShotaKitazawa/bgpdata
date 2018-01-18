# Author: ShotaKitazawa

import sys
from multiprocessing import Pool
from multiprocessing import Process

import tqdm

DEBUG = False

files = []
as_neighbors = [set() for i in range(pow(2, 16))]
as_extention_neighbors = {}
as_addresses = [set() for i in range(pow(2, 16))]
as_extention_addresses = {}


def mapped_as_numbers(line):
    return_array = []
    return_extention_array = []
    return_array_all = []
    array = line.split(" ")[1:]
    for word in array:
        if not "{" in word and not "}" in word:
            if int(word) < pow(2, 16):
                return_array.append(int(word))
            else:
                return_extention_array.append(int(word))
            return_array_all.append(int(word))
    return return_array, return_extention_array, return_array_all


def calculate(files):
    global as_neighbors, as_extention_neighbors, as_addresses, as_extention_addresses
    for idx_file, file in enumerate(files):
        pbar = tqdm.tqdm(file)
        pbar.set_description("Caluculate %s" % sys.argv[idx_file + 1])
        for idx, line in enumerate(pbar):
            if (line.startswith("TIME: ")):
                pass
            elif (line.startswith("TYPE: ")):
                if "IPV4" in line:
                    flag_ipv4 = True
                else:
                    flag_ipv4 = False
            elif (line.startswith("PREFIX: ")):
                if (flag_ipv4):
                    tmp_as_address = line.split(" ")[1].replace("\n", "")
            elif (line.startswith("SEQUENCE: ")):
                pass
            elif (line.startswith("FROM: ")):
                pass
            elif (line.startswith("ORIGINATED: ")):
                pass
            elif (line.startswith("ORIGIN: ")):
                pass
            elif (line.startswith("ASPATH: ")):
                if (flag_ipv4):
                    if (DEBUG):
                        print(idx)
                    as_numbers, as_extention_numbers, as_numbers_all = mapped_as_numbers(line)
                    if (as_numbers_all[-1] < pow(2, 16)):
                        as_addresses[as_numbers[-1]].add(tmp_as_address)
                    else:
                        if as_numbers_all[-1] not in as_extention_addresses:
                            as_extention_addresses[as_numbers_all[-1]] = set()
                        as_extention_addresses[as_numbers_all[-1]].add(tmp_as_address)
                    for i in as_numbers:
                        as_number_index = as_numbers_all.index(i)
                        # Add one left
                        if (as_number_index > 0) and (as_numbers_all[as_number_index] != as_numbers_all[as_number_index - 1]):
                            as_neighbors[i].add(as_numbers_all[as_number_index - 1])
                        # Add one right
                        if (as_number_index < len(as_numbers_all) - 1) and (as_numbers_all[as_number_index] != as_numbers_all[as_number_index + 1]):
                            as_neighbors[i].add(as_numbers_all[as_number_index + 1])
                    for i in as_extention_numbers:
                        as_number_index = as_numbers_all.index(i)
                        # Add one left
                        if (as_number_index > 0) and (as_numbers_all[as_number_index] != as_numbers_all[as_number_index - 1]):
                            if i not in as_extention_neighbors:
                                as_extention_neighbors[i] = set()
                            as_extention_neighbors[i].add(as_numbers_all[as_number_index - 1])
                        # Add one right
                        if (as_number_index < len(as_numbers_all) - 1) and (as_numbers_all[as_number_index] != as_numbers_all[as_number_index + 1]):
                            if i not in as_extention_neighbors:
                                as_extention_neighbors[i] = set()
                            as_extention_neighbors[i].add(as_numbers_all[as_number_index + 1])
            elif (line.startswith("NEXT_HOP: ")):
                pass
        file.close()


def sort_addresses(as_address):
    as_addresses_result = [i for i in as_address]
    for idx_i in range(len(as_addresses_result)):
        for idx_j in range(idx_i + 1, len(as_addresses_result)):
            if ((int(as_addresses_result[idx_i].split(".")[0]) > int(as_addresses_result[idx_j].split(".")[0])) or
                (int(as_addresses_result[idx_i].split(".")[0]) == int(as_addresses_result[idx_j].split(".")[0]) and int(as_addresses_result[idx_i].split(".")[1]) > int(as_addresses_result[idx_j].split(".")[1])) or
                (int(as_addresses_result[idx_i].split(".")[0]) == int(as_addresses_result[idx_j].split(".")[0]) and int(as_addresses_result[idx_i].split(".")[1]) == int(as_addresses_result[idx_j].split(".")[1]) and int(as_addresses_result[idx_i].split(".")[2]) > int(as_addresses_result[idx_j].split(".")[2])) or
                (int(as_addresses_result[idx_i].split(".")[0]) == int(as_addresses_result[idx_j].split(".")[0]) and int(as_addresses_result[idx_i].split(".")[1]) == int(as_addresses_result[idx_j].split(".")[1]) and int(as_addresses_result[idx_i].split(".")[2]) == int(as_addresses_result[idx_j].split(".")[2]) and int(as_addresses_result[idx_i].split(".")[3].split("/")[0]) > int(as_addresses_result[idx_j].split(".")[3].split("/")[0])) or
                    (int(as_addresses_result[idx_i].split(".")[0]) == int(as_addresses_result[idx_j].split(".")[0]) and int(as_addresses_result[idx_i].split(".")[1]) == int(as_addresses_result[idx_j].split(".")[1]) and int(as_addresses_result[idx_i].split(".")[2]) == int(as_addresses_result[idx_j].split(".")[2]) and int(as_addresses_result[idx_i].split(".")[3].split("/")[0]) == int(as_addresses_result[idx_j].split(".")[3].split("/")[0]) and int(as_addresses_result[idx_i].split(".")[3].split("/")[1]) > int(as_addresses_result[idx_j].split(".")[3].split("/")[1]))):
                as_addresses_result[idx_i], as_addresses_result[idx_j] = as_addresses_result[idx_j], as_addresses_result[idx_i]
    return as_addresses_result


def print_result():
    for idx, val in enumerate(as_neighbors):
        if (len(val) != 0):
            print("AS:", idx)
            print("  ADDRESSES:", end=" ")
            for address in sort_addresses(as_addresses[idx]):
                print(address, end=" ")
            print()
            print("  NEIGHBOR:", end=" ")
            for neighbor in sorted(val):
                print(neighbor, end=" ")
            print()

    for idx in sorted(as_extention_neighbors):
        print("AS:", idx)
        print("  ADDRESSES:", end=" ")
        if idx in as_extention_addresses:
            for address in sort_addresses(as_extention_addresses[idx]):
                print(address, end=" ")
        print()
        print("  NEIGHBOR:", end=" ")
        for neighbor in sorted(as_extention_neighbors[idx]):
            print(neighbor, end=" ")
        print()


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("Error:", "command invalid:", __file__, "FILENAME")
        sys.exit(1)

    for i in sys.argv[1:]:
        files.append(open(i, "r"))

    calculate(files)
    print_result()
