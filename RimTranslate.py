#!/usr/bin/python
import os
import polib
import sys

sys.path.append('src')

from helpers import create_pot_file_from_keyed, create_logger
from parser_helpers import parse_arguments
from source_dir_builder import SourceDirBuilder
from output_dir_builder import OutputDirBuilder

class Translator:
    def __init__(self):
        self.args = parse_arguments()
        self.logger = create_logger(self.args.v)
        self.compendium = None

        if self.args.compendium:
            self.compendium = self.build_compendium()

        # TODO: move log into a new log/ folder
        if os.path.exists('RimTranslate.log'):
            os.remove('RimTranslate.log')

    def start(self):
        if self.args.source_dir:
            SourceDirBuilder(self.args, self.compendium, self.logger).build_source_dir()
        if self.args.output_dir:
            OutputDirBuilder(self.args, self.logger).build_output_dir()

    def build_compendium(self):
        if self.compendium is not None:
            self.logger.warn('Compendium already built; skipping.')
            return self.compendium

        self.logger.info('Creating compendium from already exist DefInj XML files')

        if not os.path.isdir(self.args.compendium):
            self.logger.error('%s is not directory or does not exists!' % self.args.compendium)
            quit()

        compendium = polib.POFile()

        for root, dirs, files in os.walk(self.args.compendium):
            for file in files:
                if file.endswith('.xml'):
                    full_filename = os.path.join(root, file)
                    self.logger.debug('Processing %s for compendium' % full_filename)
                    compendium += create_pot_file_from_keyed(full_filename, self.args.source_dir, self.args.compendium, True)

        return compendium

Translator().start()
