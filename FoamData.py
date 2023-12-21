#!/usr/bin/env python3
# -*-coding:utf8-*-
# !/bin/bash

# Name Definition
# Dict    : All formats such as 'Name' and 'Keyword' except entry
# Name    : dict with sub dict
# Keyword : dict without sub dict
# Entry   : value of 'Keyword'

# Hierarchy of foam file
# Name
# {
#     keyword     entry;
#     Name
#     {
#         keyword     entry;
#     }
# }

from NextLibs.File import read_file, write_file
from NextLibs.OpenFOAM.PyFoamDict.Tools.StringTool import *


class FoamData:
    def __init__(self):
        super().__init__()

        self._org_data = ''     # Original data
        self._pure_data = ''    # Data without annotations
        self._token_data = []   # token data (Minimum unit of data)

        self.file_name = ''     # full path and name
        self.foam_data = []     # extracted data

    def set_file(self, file_name):
        self.file_name = file_name
        self.load()

    def load(self, load_header=True):
        self._org_data = read_file('%s' % self.file_name)
        self._token_data = self._extract_data(self._org_data)
        self.foam_data = self._get_foam_data(self._token_data)

        if not load_header and len(self.foam_data) > 0:
            if len(self.foam_data[0]) and self.foam_data[0][0] == 'FoamFile':
                del self.foam_data[0]
        self._pure_data = remove_comment(self._org_data, 0, True)

    def save(self):
        self._org_data = replace_string(self._org_data, '\n\n\n', '\n\n')
        self._org_data = replace_string(self._org_data, '\n\n\n', '\n')
        write_file(self.file_name, self._org_data)
        self.load()

    def is_foam_file(self):
        if not self.file_name or not self.foam_data:
            return False
        return True

    def is_dict(self, route=[]):
        total_pos = len(route)

        if total_pos == 0:
            return False

        for d in self.foam_data:
            if d[0] == route[0]:
                if total_pos == 1:
                    return True
                else:
                    return self._is_dict_sub(route[1:], d[1:])
        return False

    def _is_dict_sub(self, sub_route, sub_foam_data):
        # If the error does not appear in the future, delete code below.
        # if len(sub_route) == 0 or len(sub_foam_data) == 0:
        #     return False

        total_sub_pos = len(sub_route)

        for d in sub_foam_data:
            if len(d) == 0:    # If it is empty, return False
                return False
            elif d[0] == sub_route[0]:
                if total_sub_pos == 1:
                    return True
                else:
                    return self._is_dict_sub(sub_route[1:], d[1:])
        return False

    def is_name(self, route=[]):
        if not self.is_dict(route):
            return False

        pure_data = self._pure_data

        end = self._get_dict_title_pos(route)[1]
        if end == -1:
            return False

        brace_pos = find_braces_set(pure_data, end)
        if brace_pos == (-1, -1):
            return False

        return True

    def is_keyword(self, route=[]):
        if not self.is_dict(route):
            return False

        pure_data = self._pure_data

        end = self._get_dict_title_pos(route)[1]
        if end == -1:
            return False

        if route[-1].find('#') == 0:
            return True

        brace_pos = find_braces_set(pure_data, end)
        if brace_pos == (-1, -1):
            return True

        return False

    def get(self, route=[], pos=-1, duple=False, combined=True):    # ([],0,F,F)
        # pos(number of values to output): -1 is total, n is nth value)

        if not self.is_dict(route):
            result = self.get_dict_list(route)
            if not result:
                return []
            else:
                return result

        # FunctionObject
        if duple:
            return self.get_entry(route, duple=duple)

        if self.is_keyword(route):
            get_data = self.get_entry(route, pos)
            if len(get_data) == 1 and isinstance(get_data[0], list):
                get_data = get_data[0]      # [[0,0,0]] -> [0,0,0]
            if combined and isinstance(get_data, list):
                get_data = ' '.join(get_data)
            return get_data

        total_pos = len(route)

        for dd in self.foam_data:
            if len(dd) > 0:
                if dd[0] == route[0]:
                    if (total_pos-1) == 0:
                        if pos >= 0:
                            return dd[pos + 1]  # first pos is name of keyword
                        else:
                            return dd[1:]   # 222
                    else:
                        return self._get_sub(dd, route[1:], pos)
        return []

    def _get_sub(self, sub_foam_data, route, pos=-1):   # ([], [], 0)
        total_pos = len(route)

        for ee in sub_foam_data:
            if ee[0] == route[0]:
                if (total_pos - 1) == 0:
                    if pos >= 0:
                        return ee[pos + 1]  # 0th value is name of keyword
                    else:
                        return ee[1:]
                else:
                    return self._get_sub(ee, route[1:], pos)
        return []

    def get_dict_list(self, route=[], load_header=False):
        results = []
        sub_pos = len(route)

        if not self.foam_data:
            return results

        for dd in self.foam_data:
            if sub_pos == 0:
                results.append(dd[0])
            else:
                if route[0] == '' or dd[0] == route[0]:
                    results = self._get_dict_list_sub(dd, route)

        if not load_header:
            if len(results) > 0 and isinstance(results, list):
                if results[0] == 'FoamFile':
                    del results[0]
                elif results[0][0] == 'FoamFile':
                    del results[0][0]
        return results

    def _get_dict_list_sub(self, data, route):    # ([], [])
        results = []

        sub_route = route[1:]
        sub_pos = len(sub_route)
        sub_data = data[1:]

        if len(sub_data) > 0 and not isinstance(sub_data[0], list):
            return results

        for dd in sub_data:
            if sub_pos == 0:
                results.append(dd[0])
            else:
                if sub_route[0] == '' or dd[0] == sub_route[0]:
                    results = self._get_dict_list_sub(dd, sub_route)
        return results

    def change_dict_title(self, route=[], title=''):
        if not self.is_dict(route):
            return False

        title_size = len(title)

        if title_size == 0:
            return False

        start, end = self._get_dict_title_pos(route)

        if self.is_name(route):
            last = end
        elif self.is_keyword(route):
            last = self._get_entry_pos(route)[0]
        else:
            return False

        gap = last - (start + title_size + 1)
        if gap > 0:
            self._change_string(start, last, title, True)
        else:
            title += ' '
            self._change_string(start, last, title, False)
        return True

    def set(self, route=[], value='', prev_name='-1', add_line=False):
        if isinstance(value, list) and len(value) > 0:
            tmp_data = '%s' % value[0]
            for ii in range(1, len(value)):
                tmp_data += ' %s' % value[ii]
            value = tmp_data

        value = str(value)

        if not self.is_dict(route):
            if value == '':
                return self.insert_name(route, prev_name=prev_name, add_line=add_line)
            else:
                return self.insert_keyword(route, value, prev_name=prev_name, add_line=add_line)

        if self.is_name(route):
            return self.change_dict_title(route, value)
        elif self.is_keyword(route):
            return self.set_entry(route, value)

        return False

    def set_entry(self, route=[], value=''):  # if no keyword, the keyword is added
        value = str(value)
        if not self.is_keyword(route):
            return False

        start, end = self._get_entry_pos(route)
        self._change_string(start, end, value)
        return True

    # def get_dict_name(self, route=[], pos=-1, duple=False, combined=True):  # ([],0,F,F)
    #     if not self.is_dict(route):
    #         result = self.get_dict_list(route)
    #         if not result:
    #             return []
    #         else:
    #             return result
    #
    #     total_pos = len(route)
    #
    #     for dd in self.foam_data:
    #         if len(dd) > 0:
    #             if dd[0] == route[0]:
    #                 if (total_pos - 1) == 0:
    #                     if pos >= 0:
    #                         return dd[pos + 1]  # first pos is name of keyword
    #                     else:
    #                         return dd[1:]
    #                 else:
    #                     return self._get_sub(dd, route[1:], pos)
    #     return []

    def get_entry(self, route=[], pos=-1, duple=False):  # pos : 몇 번째 값을 출력할 것인지 -1: 전체, 0: 1번째 값
        if not self.is_keyword(route):
            return []

        total_pos = len(route)
        total_data = []

        for dd in self.foam_data:
            if dd[0] == route[0]:
                if (total_pos - 1) == 0:
                    if pos >= 0:
                        if not duple:
                            return dd[pos + 1]  # '0'th is keyword name
                        else:
                            total_data.append(dd[pos + 1])
                    else:
                        if not duple:
                            return dd[1:]
                        else:
                            total_data.append(dd[pos + 1])
                else:
                    if not duple:
                        return self._get_entry_sub(dd, route[1:], pos)
                    else:
                        total_data.append(dd[pos + 1])
        return []

    def _get_entry_sub(self, sub_foam_data=[], route=[], pos=-1):
        total_pos = len(route)

        for ee in sub_foam_data:
            if ee[0] == route[0]:
                if (total_pos - 1) == 0:
                    if pos >= 0:
                        if len(ee) > pos + 1:
                            return ee[pos + 1]  # 0 is keyword, in some cases there is no
                        else:
                            return []
                    else:
                        return ee[1:]
                else:
                    return self._get_entry_sub(ee, route[1:], pos)
        return []

    def _get_entry_pos(self, route=[]):
        pure_data = self._pure_data

        # Check
        if not self.is_keyword(route):
            return []

        # Find
        find_start_pos = self._get_dict_title_pos(route)[1]
        find_last_pos = self._get_dict_pos(route)[1]
        result = self.get_entry(route)

        if len(result) == 0:
            start_pos = find_start_pos + find_near_by_string(pure_data, ';', find_start_pos, find_last_pos)
            end_pos = start_pos
        else:
            # '(', ')'
            braces_pos = find_braces_set(pure_data, find_start_pos, ['(', ')'])
            if braces_pos[0] != braces_pos[1]:
                start_pos = braces_pos[0]
                end_pos = braces_pos[1] + find_near_by_string(pure_data, ';', braces_pos[1])

            else:
                # '[', ']'
                braces_pos = find_braces_set(pure_data, find_start_pos, ['[', ']'])
                if braces_pos[0] != braces_pos[1]:
                    start_pos = braces_pos[0]
                    end_pos = braces_pos[1] + find_near_by_string(pure_data, ';', braces_pos[1])
                else:
                    entry_string = self.get_entry(route)[0]
                    start_pos = find_start_pos + find_near_by_string(pure_data, entry_string, find_start_pos,
                                                                     find_last_pos)
                    end_pos = start_pos + find_near_by_string(pure_data, ';', start_pos)

        return start_pos, end_pos

    def insert(self, route=[], entry='', prev_name='-1', add_line=False):
        # prev_name: 0 is Top, -1 is Bottom

        if len(route) >= 2 and self.is_keyword([route[0]]):
            return False
        if len(route) >= 2 and not self.is_name([route[0]]):   # root dict is necessary
            self.insert_name([route[0]], add_line=add_line)

        if self.is_dict(route):
            if entry:
                self.set_entry(route, entry)
            return False

        route_size = len(route[:-1])
        if route_size > 0:
            for ii in range(1, route_size):  # prev: route_size+1
                self.insert(route[:ii])
                # return    # 20211116 changed  >> ???

        if entry == '':
            self.insert_name(route, prev_name, add_line=add_line)
        else:
            self.insert_keyword(route, entry, prev_name, add_line=add_line)
        return True

    def insert_name(self, route=[], prev_name='', add_line=True):  # prev_name: 0 is top, others are bottom
        if not route or self.is_dict(route):
            return False    # pass if route is empty or exists

        org_data, pure_data = self._get_read_data()

        parent_route = route[:-1]

        if not self.is_name(parent_route):  # if no parent path, make path
            self.insert_name(parent_route)
            org_data, pure_data = self._get_read_data()  # update

        sub_dicts = self.get_dict_list(parent_route, load_header=True)

        insert_string = ''
        insert_tab = '    '     # openfoam file tab size is 4

        if len(sub_dicts) == 0:     # if empty file
            start_title, end_title = self._get_dict_title_pos(parent_route)
            start_brace, end_brace = find_braces_set(pure_data, end_title)

            if (start_brace, end_brace) == (-1, -1):
                insert_string += '%s\n{\n}\n' % route[-1]
                self._insert_string(len(org_data), insert_string)
            else:
                indent_size = find_indent(pure_data, start_title)
                insert_indent = ''
                for ee in range(indent_size):
                    insert_indent += ' '

                insert_string += '\n' + insert_indent + insert_tab + '%s' % route[-1]
                insert_string += '\n' + insert_indent + insert_tab + '{'
                insert_string += '\n' + insert_indent + insert_tab + '}'
                # insert_string += '\n' + insert_indent

                self._insert_string(start_brace + 1, insert_string)

        else:
            if prev_name == '0':    # insert first
                parent_route.append(sub_dicts[0])
                num_sub_dicts = len(sub_dicts)

                start_dict, end_dict = self._get_dict_pos(parent_route)

                indent_size = find_indent(pure_data, start_dict)
                insert_indent = ''
                for ee in range(indent_size):
                    insert_indent += ' '

                insert_string += '%s' % route[-1]
                insert_string += '\n' + insert_indent + '{'
                insert_string += '\n' + insert_indent + '}'
                # insert_string += '\n'

                if add_line and num_sub_dicts > 0:
                    insert_string += '\n'
                insert_string += insert_indent

                self._insert_string(start_dict, insert_string)

            else:
                if prev_name in sub_dicts:      # insert under prev_name
                    parent_route.append(prev_name)
                else:                           # insert last
                    parent_route.append(sub_dicts[-1])

                num_sub_dicts = len(sub_dicts)

                start_dict, end_dict = self._get_dict_pos(parent_route)
                last_pos = find_string(org_data, '\n', end_dict)
                end = max(end_dict, last_pos)

                indent_size = find_indent(pure_data, start_dict)
                insert_indent = ''
                for ee in range(indent_size):
                    insert_indent += ' '

                if add_line and num_sub_dicts > 0:
                    insert_string += '\n'
                insert_string += insert_indent

                insert_string += '\n' + insert_indent + '%s' % route[-1]
                insert_string += '\n' + insert_indent + '{'
                insert_string += '\n' + insert_indent + '}'
                # insert_string += '\n'

                self._insert_string(end, insert_string)

        return True

    def insert_keyword(self, route=[], entry='', prev_name='', add_line=False):  # prev_name: 0 is top, others are bottom
        if not route or self.is_name(route):
            return False  # pass if route is empty or name

        org_data, pure_data = self._get_read_data()

        if self.is_keyword(route):
            return self.set_entry(route, entry)    # if exists, change data

        parent_route = route[:-1]

        if not self.is_name(parent_route):  # if no parent path, make path
            self.insert_name(parent_route)
            org_data, pure_data = self._get_read_data()  # update
            # self.insert_keyword(route, entry, add_line=add_line)
            # return True

        sub_dicts = self.get_dict_list(parent_route, load_header=True)

        insert_string = ''
        insert_tab = '    '  # openfoam file tab size is 4

        if len(sub_dicts) == 0:  # if empty file
            start_title, end_title = self._get_dict_title_pos(parent_route)
            start_brace, end_brace = find_braces_set(pure_data, end_title)

            # if add_line:
            #     insert_string += '\n'

            if (start_brace, end_brace) == (-1, -1):
                insert_string += '%12s %s;\n' % (route[-1], entry)
                self._insert_string(len(org_data), insert_string)
            else:
                indent_size = find_indent(pure_data, start_title)    # start_brace
                insert_indent = ''
                for ee in range(indent_size):
                    insert_indent += ' '

                insert_string += '\n' + insert_indent + insert_tab + '%-15s %s;' % (route[-1], entry)

                self._insert_string(start_brace + 1, insert_string)
        else:
            if prev_name == '0':        # insert first
                parent_route.append(sub_dicts[0])

                start_dict, end_dict = self._get_dict_pos(parent_route)
                indent_size = find_indent(pure_data, start_dict)
                insert_indent = ''
                for ee in range(indent_size):
                    insert_indent += ' '

                insert_string += '%-15s %s;\n' % (route[-1], entry)

                if add_line:    # or len(route) == 0:
                    insert_string += '\n'

                insert_string += insert_indent

                self._insert_string(start_dict, insert_string)

            else:
                if prev_name in sub_dicts:      # insert under prev_name
                    parent_route.append(prev_name)
                else:                           # insert last
                    parent_route.append(sub_dicts[-1])

                num_sub_dicts = len(sub_dicts)

                start_dict, end_dict = self._get_dict_pos(parent_route)
                last_pos = find_string(org_data, '\n', end_dict)
                end = max(end_dict, last_pos)

                indent_size = find_indent(pure_data, start_dict)
                insert_indent = ''
                for ee in range(indent_size):
                    insert_indent += ' '

                if add_line and num_sub_dicts > 0:
                    insert_string += '\n'
                insert_string += insert_indent

                insert_string += '\n' + insert_indent + '%-15s %s;' % (route[-1], entry)

                self._insert_string(end, insert_string)
                # self._insert_string(pre_end + 1, insert_char)  # +1 is '\r\n'
        return True

    def _insert_string(self, start, insert_data=''):
        insert_data = str(insert_data)

        self._org_data = insert_string_by_index(self._org_data, start, insert_data)
        self._pure_data = insert_string_by_index(self._pure_data, start, insert_data)

        self._token_data = self._extract_data(self._org_data)
        self.foam_data = self._get_foam_data(self._token_data)

    def remove(self, route=[]):
        if self.is_name(route):
            return self._remove_name(route)
        elif self.is_keyword(route):
            return self._remove_keyword(route)

    def _remove_name(self, route=[]):
        start, end = self._get_dict_pos(route)
        if start == -1 or end == -1:
            return False

        start, end = self._adjust_indent(start, end, '\n')

        self._change_string(start, end)
        return True

    def _remove_keyword(self, route=[]):
        start_title, end_title = self._get_dict_title_pos(route)
        if start_title == -1 or end_title == -1:
            return False

        start, end = self._adjust_indent(start_title, end_title, ';')

        self._change_string(start, end)
        return True

    def _adjust_indent(self, start=-1, end=-1, chars='\n'):
        pure_data = self._pure_data
        changed_start_pos = start
        changed_end_pos = end

        remove_start_pos = find_near_by_string(pure_data, '\n', 0, changed_start_pos, True)
        if remove_start_pos is not False:
            changed_start_pos = start + remove_start_pos

        remove_end_pos = find_near_by_string(pure_data, chars, changed_end_pos)
        if remove_end_pos is not False:
            changed_end_pos = changed_end_pos + remove_end_pos
            if chars == ';':
                changed_end_pos += 1

        return changed_start_pos, changed_end_pos

    def clear(self):    # Remove all dict data except header
        get_dicts = self.get_dict_list()
        for dd in get_dicts:
            self.remove([dd])

        star_pos = 0
        end_pos = len(self._org_data)
        while star_pos < end_pos:
            find_pos = find_string(self._org_data, '\n\n', star_pos)
            if find_pos == -1:
                star_pos = end_pos
            else:
                self._org_data = replace_string_by_index(self._org_data, find_pos, find_pos + 2, '\n')
                self._pure_data = replace_string_by_index(self._pure_data, find_pos, find_pos + 2, '\n')
                star_pos = find_pos - 1

        self._token_data = self._extract_data(self._org_data)
        self.foam_data = self._get_foam_data(self._token_data)

    def reset_dict(self, route=[], value='', prev_name='-1'):
        org_data, pure_data = self._get_read_data()

        if self.is_name(route):
            pos_brace = self._get_brace_pos(route)

            insert_data = '{\n'
            insert_indent = find_indent(pure_data, pos_brace[0])
            for ee in range(insert_indent):
                insert_data += ' '
            insert_data += '}'

            self._change_string(pos_brace[0], pos_brace[1], insert_data, False)

        self.set(route=route, value=value, prev_name=prev_name)

    def _get_brace_pos(self, route=[]):  # ([])
        pure_data = self._pure_data

        start_title, end_title = self._get_dict_title_pos(route)
        if start_title < 0:
            return start_title, end_title

        result = find_braces_set(pure_data, end_title)
        return result

    def _get_read_data(self):
        return self._org_data, self._pure_data

    def _extract_data(self, src_data):
        if not src_data:
            return []

        total_data = src_data

        total_data = remove_comment(total_data)
        total_data = remove_empty(total_data, '\n')

        total_data = replace_string(total_data, ';', ' ; ')
        total_data = replace_string(total_data, '{', ' { ')
        total_data = replace_string(total_data, '}', ' } ')

        split_1_data = total_data.split(' ')
        split_2_data = []
        exist_dict_name = True  # first is always keyword

        for dd in split_1_data:
            if not dd:
                continue
            elif dd == ';' or dd == '{' or dd == '}' or \
                    dd == '(' or dd == ')' or dd == '[' or dd == ']':
                split_2_data.append(dd)
                exist_dict_name = True  # next Token is keyword
            else:
                if not exist_dict_name:  # replace 함수는 문자열 내 모둔 문자 변경
                    dd = replace_string(dd, '(', ' ( ')
                    dd = replace_string(dd, ')', ' ) ')
                    # dd = replaceString(dd, '[', ' [ ')
                    # dd = replaceString(dd, ']', ' ] ')

                    sub_split_data = dd.split(' ')
                    for ee in sub_split_data:
                        if ee:
                            split_2_data.append(ee)
                else:   # Exception handling
                    # Separate small/middle brackets
                    if (dd.find('(') == -1 and dd.find(')')) or (dd.find(')') == -1 and dd.find('(')):
                        dd = dd.replace(')', ' ) ')
                        sub_split_data = dd.split(' ')
                        for ee in sub_split_data:
                            if ee:
                                split_2_data.append(ee)
                    elif (dd.find('[') == -1 and dd.find(']')) or (dd.find(']') == -1 and dd.find('[')):
                        dd = dd.replace(']', ' ] ')
                        sub_split_data = dd.split(' ')
                        for ee in sub_split_data:
                            if ee:
                                split_2_data.append(ee)
                    else:
                        split_2_data.append(dd)
                exist_dict_name = False

        # Split '#include', '#remove'
        pos = -1
        split_3_data = []
        for ii, dd in enumerate(split_2_data):
            if not dd:
                continue
            if ii == pos:  # Do not change the code below.
                split_3_data.append(';')
            if dd.find('#include') == 0 or dd.find('#remove') == 0:
                pos = ii + 2
            split_3_data.append(dd)

        token_data = split_3_data
        return token_data

    def _get_foam_data(self, token_data):     # token_data is list
        pos = 0
        state = 0
        total_num = len(token_data)
        foam_data = []

        while pos < total_num:
            token = token_data[pos]
            if state == 0:
                state = 0
                if token == '{' or token == '(':
                    foam_data.append('@')
                elif token == '}' or token == ')' or token == ';':
                    pass
                else:
                    foam_data.append([token])
                    state += 1

            elif state == 1:
                pos, sub_data, exist_sub_data = self._get_foam_data_sub(pos, token_data)
                for ee in sub_data:
                    foam_data[-1].append(ee)
                # if not sub_data:      # 최상위 Dict가 empty Dict일 때 빈 칸이 생김
                #     foam_data[-1].append('')
                state -= 1
            pos += 1

        return foam_data

    def _get_foam_data_sub(self, pos, parent_data):
        state = 1
        total_num = len(parent_data)
        sub_foam_data = []
        exist_sub_data = False
        pre_token = ''

        #
        while state > 0 and pos < total_num:
            token = parent_data[pos]

            if state == 1:
                if token == ';' or token == '}' or token == ')':
                    state -= 1
                elif token == ']':
                    exist_sub_data = True  # may be data after the last square bracket
                    state -= 1
                elif token == '{' or token == '(' or token == '[':
                    state += 1
                else:
                    sub_foam_data.append(token)

            elif state == 2:
                if token == ';' or token == '}':
                    state -= 2

                elif token == ']':
                    state -= 1

                elif token == ')':
                    if pre_token == '(':  # pre_token == '{' (X)
                        sub_foam_data.append('')
                    #
                    state -= 1

                elif token == '(':
                    # state = 2  # 연속 소괄호는 현재 위치 유지하면서 연속으로 읽기
                    pass
                elif token == '(':  # or token == '{' or token == '[':
                    print('Cannot read file, %s' % pos)  # file error
                    return 0, [], exist_sub_data
                else:
                    if exist_sub_data:
                        sub_foam_data.append(token)
                        state = 2  # keep
                    else:
                        sub_foam_data.append([token])
                        state += 1

            elif state == 3:
                pos, sub_sub_data, exist_sub_data = self._get_foam_data_sub(pos, parent_data)
                for ee in sub_sub_data:
                    sub_foam_data[-1].append(ee)
                if not sub_foam_data:
                    sub_foam_data[-1].append('')
                state -= 1

            pos += 1
            pre_token = token

        pos -= 1
        return pos, sub_foam_data, exist_sub_data

    def _change_string(self, start, end, change_string='', keep_line=False):
        change_string = str(change_string)

        self._org_data = replace_string_by_index(self._org_data, start, end, change_string, keep_line)
        self._pure_data = replace_string_by_index(self._pure_data, start, end, change_string, keep_line)

        self._token_data = self._extract_data(self._org_data)
        self.foam_data = self._get_foam_data(self._token_data)

    def _get_dict_pos(self, route=[]):
        pure_data = self._pure_data

        start, end = self._get_dict_title_pos(route)
        if start < 0:
            return start, end

        dict_pos = find_braces_set(pure_data, start)

        if dict_pos[0] == -1 or dict_pos[1] == -1:     # if 'Keyword' format
            end = find_string(pure_data, ';', end) + 1
        else:                       # if 'Name' format
            end = dict_pos[1]

        return start, end

    def _get_dict_title_pos(self, route):     # ([])
        pure_data = self._pure_data
        start, end = -1, -1
        pos = 0

        for dd in self.foam_data:
            header = dd[0]
            sub_data = dd[1:]
            pos = find_string(pure_data, header, pos, chars=[' ', '\t', ';', ')', '\n', '{'])
            word_size = len(header)
            if header == route[0]:
                start = pos
                end = start + word_size
                pos = end
                if len(route) > 1:
                    start, end = self._get_dict_title_pos_sub(pure_data, sub_data, pos, route[1:])
                    break
            else:
                next_pos = self._jump_dict_title_pos_sub(pure_data, sub_data, pos)
                pos = next_pos
        return start, end

    def _get_dict_title_pos_sub(self, pure_data, sub_data, next_pos=0, route=[]):    # ([],[],0,[])
        pos = next_pos
        start = -1
        end = -1
        for dd in sub_data:
            header = dd[0]
            sub_data = dd[1:]
            pos = find_string(pure_data, header, pos, chars=[' ', '\t', ';', ')', '\n', '{'])
            if header == route[0]:
                if len(route) > 1:
                    start, end = self._get_dict_title_pos_sub(pure_data, sub_data, pos, route[1:])
                    break
                else:
                    start = pos
                    end = start + len(header)
            else:
                pos = self._jump_dict_title_pos_sub(pure_data, sub_data, pos)
        return start, end

    def _jump_dict_title_pos_sub(self, pure_data, sub_data, next_pos=0):    # ([],[],0)
        pos = next_pos
        for dd in sub_data:
            if isinstance(dd, list):
                header = dd[0]
                sub_data = dd[1:]
                pos = find_string(pure_data, header, pos,
                                  chars=[' ', '\t', ';', ')', '\n', '{'])
                pos = self._jump_dict_title_pos_sub(pure_data, sub_data, pos)
            else:
                pos = find_string(pure_data, dd, pos,
                                  chars=[' ', '\t', ';', ')', '\n', '{'])
                pos += len(dd)
        return pos
