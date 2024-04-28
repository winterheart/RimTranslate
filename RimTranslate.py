#!/usr/bin/python
from src.builders.source_dir_builder import SourceDirBuilder
from src.builders.output_dir_builder import OutputDirBuilder
from src.logger import Logger
from src.parser import Parser


Parser.init()
Logger.create_logger(Parser.args.v)

if Parser.args.source_dir:
    SourceDirBuilder().build_source_dir()
if Parser.args.output_dir:
    OutputDirBuilder().build_output_dir()
