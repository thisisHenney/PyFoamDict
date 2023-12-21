#!/usr/bin/env python3
# -*-coding:utf8-*-
# !/bin/bash

# For converting
def get_type(state=True, opt=0):
    if state:  # true, 1, on 모두 같은 값임
        if opt == 'truefalse' or opt == 0:
            value = 'true'
        elif opt == 'onoff' or opt == 1:
            value = 'on'
        elif opt == 'yesno' or opt == 2:
            value = 'yes'
        elif opt == '1' or opt == 3:
            value = '1'
        else:
            value = 1
    else:
        if opt == 'truefalse' or opt == 0:
            value = 'false'
        elif opt == 'onoff' or opt == 1:
            value = 'off'
        elif opt == 'yesno' or opt == 2:
            value = 'no'
        elif opt == 0 or opt == 3:
            value = '0'
        else:
            value = 0
    return value
