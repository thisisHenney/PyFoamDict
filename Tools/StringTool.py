#!/usr/bin/env python3
# -*-coding:utf8-*-
# !/bin/bash

def find_string(buffer='', string='', start=0, end=-1, chars=[], reverse=False):
    found_pos = -1
    searching_pos = -1

    buffer_size = len(buffer)
    string_size = len(string)

    while searching_pos < buffer_size and found_pos < 0:
        if reverse:
            searching_pos = buffer.rfind(string, start, end)
        else:
            searching_pos = buffer.find(string, start, end)

        if searching_pos == -1:
            return -1
        if not chars:
            check_word = True
            found_pos = searching_pos
        else:
            check_pos = searching_pos + string_size
            if check_pos >= buffer_size:
                check_word = True
                found_pos = searching_pos
            else:
                check_word = False
                for dd in chars:
                    if dd == buffer[check_pos]:
                        check_word = True
                        found_pos = searching_pos
                        break
        if not check_word:
            start = searching_pos + 1

    # print("find_string: %d" % found_pos)
    return found_pos


def find_near_by_string(buffer='', string='', start=0, end=-1, reverse=False):
    buffer_size = len(buffer)

    start = max(0, start)
    if end < 0:
        end = buffer_size
    else:
        if end >= buffer_size:
            end = buffer_size
    buffer_size = len(buffer[start:end])

    if not reverse:
        found_pos = buffer[start:end].find(string, 0)
    else:
        found_pos = buffer[start:end].rfind(string, 0)
        if found_pos == -1:
            found_pos = False
        elif found_pos >= 0:
            found_pos = -(buffer_size - found_pos)

    # print("find_near_by_string: %d (%d:%d)[%d]" % (
    #                                       found_pos, start, end, buffer_size))
    return found_pos


def find_braces_set(buffer='', start=0, char_type=None):
    if char_type is None:
        char_type = ['{', '}']

    first = start
    last = start
    searching_pos = start

    check = False
    count = 0

    if len(buffer) < 2:
        return -1, -1
    if searching_pos == -1 or searching_pos >= len(buffer):
        return -1, -1

    while not check:
        if count == 0 and buffer[searching_pos] == ";":
            return -1, -1

        if buffer[searching_pos] == char_type[0]:
            if count == 0:
                first = searching_pos
            count += 1

        elif buffer[searching_pos] == char_type[1]:
            count -= 1
            if count == 0:
                last = searching_pos + 1
                check = True
        searching_pos += 1

    if first >= last:
        last = first

    # The last number refers to what comes after '}'
    return first, last


def find_indent(buffer='', current=0):
    found_pos = find_near_by_string(buffer, '\n', 0, current, True)
    if not found_pos:
        found_pos = current
    else:
        found_pos = -(found_pos+1)
    return found_pos


def remove_comment(buffer, delete_type=0, keep_line=False):
    if not buffer:
        return buffer

    buffer_size = len(buffer)

    if delete_type == 0 or (delete_type & 1) == 1:  # remove '/* ... */'
        start = buffer.find('/*')
        while start != -1:
            end = buffer.find('*/', start + 1)
            if end == -1:
                end = buffer_size
            buffer = replace_string_by_index(buffer, start, end + 2, '', keep_line)
            start = buffer.find('/*', start)

    if delete_type == 0 or (delete_type & 2) == 2:  # remove '// ...'
        start = buffer.find('//')
        while start != -1:
            end = buffer.find('\n', start + 1)
            if end == -1:
                end = buffer_size
            buffer = replace_string_by_index(buffer, start, end, '', keep_line)
            start = buffer.find('//', start)

    if delete_type == 0 or (delete_type & 4) == 4:  # remove '# ...'
        start = buffer.find('#')
        while start != -1:
            end = buffer.find('\n', start + 1)
            if end == -1:
                end = buffer_size
            buffer = replace_string_by_index(buffer, start, end, '', keep_line)
            start = buffer.find('#', start)
    return buffer


# Change all space(' ') and tabs('\t') to single space
# desired_char: Can be added with desired characters
# remove_all: remove whitespace completely
def remove_empty(buffer, desired_char='', remove_all=False):
    if not buffer:
        return buffer

    total_data = buffer
    changed_data = ''

    pos = 0
    last = len(total_data)
    dd_prev = ' '
    while pos < last:
        dd = total_data[pos]

        if dd == ' ' or dd == '\t' or dd == desired_char:
            if dd_prev != ' ' and dd_prev != '\t' and dd_prev != desired_char:
                if not remove_all:
                    changed_data += ' '
        else:
            changed_data += dd

        dd_prev = dd
        pos += 1
    return changed_data


def insert_string_by_index(buffer, start=0, insert_data=''):
    buffer_size = len(buffer)

    change_string = buffer[0:start]
    for e in insert_data:
        change_string += e

    change_string += buffer[start:buffer_size]
    return change_string


def replace_string(buffer, org_string='', new_string='', count=0):
    # count: 0 is All, 1~ is times(1 is once)
    if not buffer:
        return buffer

    buffer_size = len(buffer)
    org_string_size = len(org_string)

    pos = 0
    replace_data = ''
    pos_start = buffer.find(org_string)
    while pos < buffer_size:
        if pos == pos_start:
            for ee in new_string:
                replace_data += ee
            pos += org_string_size

            count -= 1
            if count == 0:
                pos_start = -1
            else:
                pos_start = buffer.find(org_string, pos)
        else:
            replace_data += buffer[pos]
            pos += 1
    return replace_data


def replace_string_by_index(buffer, start=0, end=0, string='', keep_line=False):
    if not buffer:
        return buffer

    buffer_size = len(buffer)

    changed_buffer = buffer[0:start]
    for ee in string:
        changed_buffer += ee
        start += 1
    if keep_line:   # Delete deleted line position
        for ii in range(start, end):
            changed_buffer += ' '
    changed_buffer += buffer[end:buffer_size]
    return changed_buffer
