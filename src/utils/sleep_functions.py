import time

from ctypes import *
libc = CDLL("libc.so.6")


def sleep(duration):

    # Check if the provided input value is integer by using float().is_integer()
    if float(duration).is_integer():
        libc.sleep(int(duration))
    else:
        start_time = time.time()
        while time.time() - start_time < duration:
            pass


def sleep_vt(duration):
    #TODO: Replace with get_virtual_time and sleep in virtual time
    time.sleep(duration)


def main():
    print "sleeping for 5.2"
    sleep(5.2)
    print "sleeping for 5.0"
    sleep(5.0)


if __name__ == "__main__":
    main()

