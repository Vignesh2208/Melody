from distutils.core import setup, Extension
setup(name='shared_buf', version='1.0',  \
      ext_modules=[Extension('shared_buf', include_dirs=['/usr/local/include'], libraries=['pthread'], library_dirs = ['/usr/local/lib'], sources = ['shared_buf.c','utils/linkedlist.c','utils/hashmap.c'])])
