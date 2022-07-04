#!/bin/sh -eux

# Verify the formal side of things, lldb should really depend on its Python bits.
rpm -q --requires "$LLDB_PACKAGE" | grep python3-lldb

# Sanity test
g++ -g test.cpp

lldb -b -o 'breakpoint set --file test.cpp --line 9' \
  -o run -o 'p i' -o 'p f'\
  -- a.out | tee lldb.log

test `grep \
    -e '(int) $0 = 1' \
    -e '(float) $1 = 1' \
    lldb.log \
  | wc -l` -eq 2

rm lldb.log
