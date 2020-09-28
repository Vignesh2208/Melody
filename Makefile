home_dir=$(HOME)
melody_dir=${home_dir}/Melody
core_dir=${melody_dir}/srcs/lib
utils_dir=${melody_dir}/srcs/utils

clean:
    @cd srcs/lib/libs && make clean;
	@rm -f srcs/lib/libs/shared_buf.so
	@rm -f srcs/lib/libs/gettimepid.so

build:
    @echo "#############################################################################"
	@echo "Setting up Melody"
	@echo "#############################################################################"
	@cd ${core_dir}/libs && $(MAKE) build_ext;

install_deps: @cd ${melody_dir} && ./install_deps.sh;

install: clean build
		
