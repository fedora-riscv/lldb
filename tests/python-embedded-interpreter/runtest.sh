#!/bin/bash

set -ex

g++ -gdwarf-4 -g test.cpp

test `lldb -b -o 'breakpoint set --file test.cpp --line 7' -o run -o 'p v' -- a.out \
  | grep \
    -e '(std::vector<int, std::allocator<int> >) $0 = size=1 {' \
    -e '\[0\] = 2' \
  | wc -l` -eq 2
