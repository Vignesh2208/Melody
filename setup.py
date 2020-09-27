from distutils.core import setup, Extension
from distutils.core import setup, Extension
setup(name='shared_buf', version='1.2',  \
      ext_modules=[
            Extension('shared_buf',
                  libraries=['rt','pthread'], 
                  library_dirs = ['/usr/local/lib','/usr/lib/i386-linux-gnu'],
                  sources = ['srcs/lib/libs/shared_buf.c',
                             'srcs/lib/libs/utils/linkedlist.c',
                             'srcs/lib/libs/utils/hashmap.c'])])