from distutils.core import setup, Extension
from distutils.core import setup, Extension
setup(name='shared_buf', version='1.2',  \
      ext_modules=[
            Extension('shared_buf',
                  libraries=['rt','pthread'], 
                  library_dirs = ['/usr/local/lib','/usr/lib/i386-linux-gnu'],
                  sources = ['src/core/libs/shared_buf.c',
                             'src/core/libs/utils/linkedlist.c',
                             'src/core/libs/utils/hashmap.c'])])