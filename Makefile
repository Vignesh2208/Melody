home_dir=$(HOME)
melody_dir=${home_dir}/NetPower_TestBed
core_dir=${melody_dir}/src/core
utils_dir=${melody_dir}/src/utils



clean_bin: 
	@cd ${core_dir}/bin && $(MAKE) clean;

clean_libs:
	@cd ${core_dir}/libs && $(MAKE) clean;
	@cd ${core_dir}/libs/utils && $(MAKE) clean;

clean_utils:
	@cd ${utils_dir} && $(MAKE) clean;

build_bin:
	@echo "#############################################################################"
	@echo "Setting up NetPower"
	@echo "#############################################################################"
	@cd ${core_dir}/bin && $(MAKE) build;

build_libs:
	@cd ${core_dir}/libs && $(MAKE) build;

build_utils:
	@cd ${utils_dir} && $(MAKE) build;

clean : clean_bin clean_libs clean_utils

build:	build_bin build_libs build_utils

install_deps: @cd ${melody_dir} && ./setup.sh;

install: clean build
		
