#!/bin/sh -eux

lldb -b -o 'b main' -o run -o c -- true 2>&1 | tee lldb.log

# lldb should report unsupported dwarf data, yet shouldn't crash
grep "unsupported DW_FORM values" lldb.log
grep "stop reason = breakpoint" lldb.log
# Ensure the process ends successfully (no crashes)
grep -E "Process [0-9]+ exited with status = 0" lldb.log
