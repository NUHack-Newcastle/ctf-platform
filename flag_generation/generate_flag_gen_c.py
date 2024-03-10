#!/usr/bin/python3

import os
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Generate flag_gen.c from template')
parser.add_argument('--seed', type=int, help='Specify the seed value')
parser.add_argument('--out', type=str, help='Specify the output file name')
args = parser.parse_args()

# Use specified seed or generate random bytes
seed = args.seed if args.seed is not None else int.from_bytes(os.urandom(4), 'little')

key = []

lfsr = seed
for _ in range(22):
    for _ in range(32):
        lfsr_newbit = (((lfsr >> 0) & 1) ^ ((lfsr >> 1) & 1) ^ ((lfsr >> 3) & 1) ^ ((lfsr >> 5) & 1) ^ ((lfsr >> 8) & 1) ^ ((lfsr >> 13) & 1) ^ ((lfsr >> 21) & 1))
        lfsr = (lfsr >> 1) | ((lfsr_newbit & 1) << 31)
    key.append((lfsr >> 19) & 0xff)

# Read template from the script's folder
script_folder = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(script_folder, 'flag_gen.template.c')
template = open(template_path).read().replace("_LFSR_SEED", hex(seed))

for i in range(22):
    template = template.replace("_KEY_BYTE%02d" % (i+1), hex(key[i]))

# Use specified output file or default to flag_gen.c
output_file = args.out if args.out is not None else 'flag_gen.c'

# Write to the specified output file
with open(output_file, 'w') as f:
    f.write(template)
