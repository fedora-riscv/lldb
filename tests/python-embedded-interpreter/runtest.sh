#!/bin/bash

set -ex

g++ -g test.cpp

lldb -b -o 'breakpoint set --file test.cpp --line 7' -o run -o 'p v' -- a.out | tee lldb.log

test `grep \
    -e '(std::vector<int, std::allocator<int> >) $0 = size=1 {' \
    -e '\[0\] = 2' \
    lldb.log \
  | wc -l` -eq 2
