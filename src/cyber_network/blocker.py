import os
import sys
import time

print "Started Blocker ..."
sys.stdout.flush()
time.sleep(1)
os.system("taskset -cp " + str(os.getpid()))
os.nice(-20)
i = 1
factorial = 1
while True:

    if i < 1000000000:
        factorial = factorial*i
        i = i + 1
    else:
        i = 1
        factorial = 1
