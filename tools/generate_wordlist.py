#!/usr/bin/env python3
# Generate wordlist for documentation from native_words.asm
# For Tali Forth 2
# Scot W. Stevenson <scot.stevenson@gmail.com>
# First version: 21. Nov 2017
# This version: 17. May 2018
"""Creates a markdown formated list of native words based on the header
comments in native_words.asm. It is called by the Makefile on the top level
"""

import sys

SOURCE = 'native_words.asm'
LABELS = 'docs/py65mon-labelmap.txt'
MARKER = '; ## '

labels = {}

# Counters for statistics. We just brutally use global variables for these
not_tested = 0


def get_sizes(label_dict):
    """Use the Ophis labelmap to calculate the length of the native words
    in bytes. Returns a dictionary that contains them based on the
    names. Assumes lines in label map are of the format

    "$0000 | cp                      | definitions.asm:90"

    """

    with open(LABELS) as f:
        raw_list = f.readlines()

    for line in raw_list:
        ws = line.split()
        
        if not ws[2].startswith('xt_') and not ws[2].startswith('z_'):
            continue

        addr_hex = ws[0].replace('$', '0x')
        addr = int(addr_hex, 16)

        label_dict[ws[2]] = addr

    return label_dict


def calc_size(word, raw_labels=labels):
    """Given the lowercase formal name of a Forth word, calculate the
    size of the code in bytes by subtracting the start address xt_word
    from the end address z_word.
    """
    start = 'xt_'+word
    end = 'z_'+word

    start_addr = raw_labels[start]
    end_addr = raw_labels[end]

    size = end_addr-start_addr

    return size


def print_intro():
    """Print a brief introduction to the information that follows
    in GitHub markdown
    """
    print('# Tali Forth 2 native words')
    print('This file is automatically generated by a script in `tools`.')
    print('Note these are not all the words in Tali Forth 2, the high-level')
    print('and user-defined words coded in Forth are in `forth_code`.')
    print('The size in bytes includes any underflow checks, but not the')
    print('RTS instruction at the end of each word.')
    print()


def print_footer(size):
    """Print statistical information at bottom of table"""
    global not_tested

    print()
    print('Found **{0}** native words in `native_words.asm`.'.format(size))
    print('Of those, **{0}** are not marked as "tested".'.format(not_tested))
    print()


def print_header():
    """Print the header of the table in markup"""
    print('| NAME | FORTH WORD | SOURCE | BYTES | STATUS |')
    print('| :--- | :--------- | :---   | ----: | :----  |')


def print_line(fl, sl):
    """Given the first and second line as strings, return a string with
    formatted information for WORDLIST.md. Note this is very brittle code
    because it all goes to hell if the format of the comment strings in
    the header changes. Currently, assumes

        ; ## COLD ( -- ) "Reset the Forth system"
        ; ## "cold"  coded  Tali Forth

    as line one and line two
    """
    global not_tested

    HAVE_TEST = 'tested'
    TEMPLATE = '| {0} | {1} | {2} | {3} | {4} |'

    l1 = fl[len(MARKER):].split()
    l2 = sl[len(MARKER):].split(maxsplit=2)

    name = l1[0]
    word = '`{0}`'.format(l2[0][1:-1]) # Include backticks

    # Size requires looking up the start and end addresses of the code. We can
    # safely assume that we have both xt_word and z_word or the code will not
    # compile at all
    size = calc_size(name.lower())

    status = l2[1]
    source = l2[2]

    # Statistics
    if status != HAVE_TEST:
        not_tested += 1

    # We want tested words to be bolded
    if status == HAVE_TEST:
        status = '**'+status+'**'

    print(TEMPLATE.format(name, word, source, size, status))


def main():

    with open(SOURCE) as f:
        raw_list = f.readlines()

    data_list = []

    for line in raw_list:

        if line.startswith(MARKER):
            data_list.append(line.strip())

    # Primitive internal testing: If we found an uneven number of lines,
    # something is wrong
    if len(data_list) % 2 != 0:
        print('Found odd number of lines, aborting')
        sys.exit(1)

    use_list = iter(data_list)
    number_of_words = int(len(data_list)/2)

    word_labels = get_sizes(labels)

    print_intro()
    print_header()

    while True:

        try:
            first_line = next(use_list)
            second_line = next(use_list)
        except StopIteration:
            break

        print_line(first_line, second_line)

    # At the moment, we only print the number of native words
    print_footer(number_of_words)


if __name__ == '__main__':
    main()
