import os
import polib

from Helpers import create_pot_file, create_pot_file_from_keyed, create_languagedata_xml_file, create_logger, merge_compendium
from Parser import parse_arguments

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
            self.build_source_dir()
        if self.args.output_dir:
            self.build_output_dir()


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


    def build_source_dir_defs(self):
        self.build_source_dir_generic(
            'DefInjected',
            os.path.join(self.args.source_dir, 'Defs', '')
        )


    def build_source_dir_keyed(self):
        self.build_source_dir_generic(
            'Keyed',
            os.path.join(self.args.source_dir, 'Languages/English/Keyed', '')
        )

    def build_source_dir(self):
        self.logger.info('Beginning to generate PO-files')
        self.build_source_dir_defs()
        self.build_source_dir_keyed()



    def build_source_dir_generic(self, category_name, source_dir, compendium_mode=False):
        self.logger.info('Generating PO-files from %s' % category_name)

        if not os.path.isdir(source_dir):
            self.logger.error('%s is not a directory' % source_dir)
            quit()

        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.xml'):
                    full_filename = os.path.join(root, file)
                    self.logger.info("Processing " + full_filename)
                    file_dir = full_filename.split(source_dir, 1)[1]

                    if category_name == 'DefInjected':
                        # Replace Defs to Def (https://github.com/winterheart/RimTranslate/issues/1)
                        file_dir = file_dir.replace("Defs", "Def")

                    pot = create_pot_file(category_name, full_filename, self.args.source_dir, self.args.compendium, compendium_mode)
                    pofilename = os.path.join(self.args.po_dir, category_name, file_dir)
                    pofilename += '.po'

                    if os.path.exists(pofilename):
                        self.logger.info("Updating PO file " + pofilename)
                        po = polib.pofile(pofilename)
                        po.merge(pot)
                    else:
                        # Is there some useful info?
                        if len(pot) > 0:
                            directory = os.path.dirname(pofilename)
                            if not (os.path.exists(directory)):
                                self.logger.info("Creating directory " + directory)
                                os.makedirs(directory)
                            self.logger.info("Creating PO file " + pofilename)
                        po = pot

                    if self.args.compendium:
                        po = merge_compendium(self.compendium, po)

                    if len(po):
                        po.save(pofilename)


    def build_output_dir(self):
        self.logger.info('Beginning to generate DefInjected files')
        fuzzy = 0
        total = 0
        translated = 0
        untranslated = 0

        for root, dirs, files in os.walk(self.args.po_dir):
            for file in files:
                if file.endswith('.po'):
                    full_filename = os.path.join(root, file)
                    self.logger.info("Processing " + full_filename)
                    xml_filename = full_filename.split(self.args.po_dir, 1)[1]
                    xml_filename = xml_filename.strip('.po')
                    xml_filename = os.path.join(self.args.output_dir, xml_filename)
                    directory = os.path.dirname(xml_filename)

                    po = polib.pofile(full_filename)
                    translated_po_entries = len(po.translated_entries())
                    fuzzy_po_entries = len(po.fuzzy_entries())
                    untranslated_po_entries = len(po.untranslated_entries())

                    translated = translated + translated_po_entries
                    fuzzy = fuzzy + fuzzy_po_entries
                    untranslated = untranslated + untranslated_po_entries

                    # Do we have translated entries?
                    if translated_po_entries > 0:
                        if not (os.path.exists(directory)):
                            self.logger.info("Creating directory " + directory)
                            os.makedirs(directory)
                        xml_content = create_languagedata_xml_file(full_filename)
                        target = open(xml_filename, "w", encoding="utf8")
                        target.write(xml_content)
                        target.close()
                    total_po_entries = len([e for e in po if  not e.obsolete])
                    total = total + total_po_entries

        print("Statistics (untranslated/fuzzy/translated/total): %d/%d/%d/%d" % (untranslated, fuzzy, translated, total))

