#!/usr/bin/python
import sys

sys.path.append('src')

from logger import Logger
from parser_helpers import parse_arguments
from source_dir_builder import SourceDirBuilder
from output_dir_builder import OutputDirBuilder


args = parse_arguments()
Logger.create_logger(args.v)

if args.source_dir:
    SourceDirBuilder(args).build_source_dir()
if args.output_dir:
    OutputDirBuilder(args).build_output_dir()
