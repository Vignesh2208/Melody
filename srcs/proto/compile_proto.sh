#!/bin/sh

#cd to <Melody-Dir>/srcs/proto before running this script
protoc -I=. --python_out=. configuration.proto
protoc -I=. --python_out=. css.proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pss.proto
