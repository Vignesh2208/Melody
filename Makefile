home_dir=$(HOME)
melody_dir=${home_dir}/Melody
core_dir=${melody_dir}/src/core
utils_dir=${melody_dir}/src/utils

clean:
    @cd src/core/libs && make clean;
	@rm -f src/core/libs/shared_buf.so
	@rm -f src/core/libs/gettimepid.so

build:
    @echo "#############################################################################"
	@echo "Setting up Melody"
	@echo "#############################################################################"
	@cd ${core_dir}/libs && $(MAKE) build_ext;

install_deps: @cd ${melody_dir} && ./install_deps.sh;

install: clean build
		
