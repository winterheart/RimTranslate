import os
import polib

from ..helpers.compendium_helpers import build_compendium, merge_compendium
from ..helpers.pot_helpers import create_pot_file
from ..logger import Logger
from ..parser import Parser

class SourceDirBuilder:
    def __init__(self):
        self.compendium = None
        if Parser.args.compendium:
            self.compendium = build_compendium(Parser.args.compendium, Parser.args.source_dir)

    def build_source_dir(self):
        Logger.logger.info('Beginning to generate PO-files')
        self.build_source_dir_defs()
        self.build_source_dir_keyed()

    # TODO: private
    def build_source_dir_defs(self):
        self.build_source_dir_files(
            'DefInjected',
            os.path.join(Parser.args.source_dir, 'Defs', '')
        )

    # TODO: private
    def build_source_dir_keyed(self):
        self.build_source_dir_files(
            'Keyed',
            os.path.join(Parser.args.source_dir, 'Languages/English/Keyed', '')
        )

    # TODO: private
    def build_source_dir_files(self, category_name, source_dir):
        Logger.logger.info('Generating PO-files from %s' % category_name)

        if not os.path.isdir(source_dir):
            Logger.logger.error('%s is not a directory' % source_dir)
            quit()

        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.xml'):
                    full_filename = os.path.join(root, file)
                    Logger.logger.info("Processing " + full_filename)
                    file_dir = full_filename.split(source_dir, 1)[1]

                    if category_name == 'DefInjected':
                        # Replace Defs to Def (https://github.com/winterheart/RimTranslate/issues/1)
                        file_dir = file_dir.replace("Defs", "Def")

                    pot = create_pot_file(category_name, full_filename, Parser.args.source_dir, Parser.args.compendium)
                    pofilename = os.path.join(Parser.args.po_dir, category_name, file_dir)
                    pofilename += '.po'

                    if os.path.exists(pofilename):
                        Logger.logger.info("Updating PO file " + pofilename)
                        po = polib.pofile(pofilename)
                        po.merge(pot)
                    else:
                        # Is there some useful info?
                        if len(pot) > 0:
                            directory = os.path.dirname(pofilename)
                            if not (os.path.exists(directory)):
                                Logger.logger.info("Creating directory " + directory)
                                os.makedirs(directory)
                            Logger.logger.info("Creating PO file " + pofilename)
                        po = pot

                    if Parser.args.compendium:
                        po = merge_compendium(self.compendium, po)

                    if len(po):
                        po.save(pofilename)
