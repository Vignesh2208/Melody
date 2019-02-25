from distutils.core import setup, Extension
setup(name='shared_buf', version='1.0',  \
      ext_modules=[Extension('shared_buf',include_dirs=['/usr/local/include','/usr/include'], libraries=['pthread','rt'], library_dirs = ['/usr/local/lib'], sources = ['src/core/libs/shared_buf.c','src/core/libs/utils/linkedlist.c','src/core/libs/utils/hashmap.c'])])
      
setup(name='gettimepid', version='1.0',  \
      ext_modules=[Extension('gettimepid', include_dirs=['/usr/local/include','/usr/include'], libraries=[], library_dirs = ['/usr/local/lib'], sources = ['src/core/libs/gettimepid.c'])])
