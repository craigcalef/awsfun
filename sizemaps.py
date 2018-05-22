# Simple script to format /proc/<pid>/maps memory region format to make it easy sortable
# Ex:
# $ cat /proc/8553/maps | python sizemaps.py | sort -n
import sys

for l in sys.stdin.readlines():
  e = l.split(' ')
  x,y = e[0].split('-')
  print int(y, 16) - int(x, 16), l.strip()
