#!/usr/bin/python
from src.builders.source_dir_builder import SourceDirBuilder
from src.builders.output_dir_builder import OutputDirBuilder
from src.helpers.parser_helpers import parse_arguments
from src.logger import Logger


args = parse_arguments()
Logger.create_logger(args.v)

if args.source_dir:
    SourceDirBuilder(args).build_source_dir()
if args.output_dir:
    OutputDirBuilder(args).build_output_dir()
