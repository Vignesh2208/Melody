home_dir=$(HOME)
melody_dir=${home_dir}/Melody
core_dir=${melody_dir}/src/core
utils_dir=${melody_dir}/src/utils


clean_libs:
	@cd ${core_dir}/libs && $(MAKE) clean;
	@rm -f ${core_dir}/shared_buf.so
	@rm -f ${core_dir}/gettimepid.so

build_libs:
    @echo "#############################################################################"
	@echo "Setting up Melody"
	@echo "#############################################################################"
	@cd ${core_dir}/libs && $(MAKE) build_ext;


clean : clean_libs

build:	build_libs

install_deps: @cd ${melody_dir} && ./install_deps.sh;

install: clean build
		
