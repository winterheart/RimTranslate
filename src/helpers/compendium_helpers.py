import os
import polib

from .pot_helpers import create_pot_file
from ..logger import Logger

def build_compendium(compendium_path, source_dir_path):
    Logger.logger.info('Creating compendium from already exist DefInj XML files')

    if not os.path.isdir(compendium_path):
        Logger.logger.error('%s is not directory or does not exists!' % compendium_path)
        quit()

    compendium = polib.POFile()

    for root, dirs, files in os.walk(compendium_path):
        for file in files:
            if file.endswith('.xml'):
                full_filename = os.path.join(root, file)
                Logger.logger.debug('Processing %s for compendium' % full_filename)
                compendium += create_pot_file('Keyed', full_filename, source_dir_path, compendium_path, True)

    return compendium

def merge_compendium(compendium, po):
    # Fill current translation entries with translation memory from compendium
    for entry in po:
        if entry.msgstr == '':
            check_msg = compendium.find(entry.msgctxt, by='msgctxt', include_obsolete_entries=False)
            if check_msg and check_msg.msgstr:
                entry.msgstr = check_msg.msgstr
                if 'fuzzy' not in entry.flags:
                    entry.flags.append('fuzzy')

    return po
