import argparse
import os

# TODO: this is also in main file
version = "0.6.7"

class Parser:
    parser = None
    args = None

    @classmethod
    def init(cls):
        cls.__init_parser()
        cls.__init_arguments()

    @classmethod
    def __init_parser(cls):
        cls.parser = argparse.ArgumentParser(
            description='RimTranslate.py v%s - Creating Gettext PO files and DefInjections for RimWorld translations.' % version,
            epilog='This is free software that licensed under GPL-3. See LICENSE for more info.',
            formatter_class=argparse.RawTextHelpFormatter
        )

        group_source = cls.parser.add_argument_group('Extracting options')
        group_source.add_argument(
            '--source-dir', '-s', type=str,
            help='''Root source dir where all Defs and Keyed files (ex. ~/.local/share/Steam/SteamApps/common/RimWorld/Mods/Core/)'''
        )

        group_generation = cls.parser.add_argument_group('Generation options')
        group_generation.add_argument(
            '--output-dir', '-o', type=str,
            help='Directory where will be placed InjDefs XML-files with actual translations'
        )

        cls.parser.add_argument(
            '--po-dir', '-p', type=str,
            help='Directory where will be placed generated or updated PO-files'
        )

        cls.parser.add_argument(
            '--compendium', '-c', type=str,
            help='Directory that conains already translated InjDefs XML files for generating compendium and using it as translation memory'
        )

        cls.parser.add_argument(
            '-v', type=str, default='WARNING',
            help='Enable verbose output (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
        )

    @classmethod
    def __init_arguments(cls):
        cls.args = cls.parser.parse_args()

        if not ((cls.args.output_dir or cls.args.source_dir) and cls.args.po_dir):
            cls.parser.error('''
                No action requested. The following arguments are required:
                "--source-dir <SOURCE_DIR> --po-dir <PO_DIR>"
                or
                "--output-dir <SOURCE_DIR> --po-dir <PO_DIR>"
            ''')

        # Add trailing slash for sure
        if cls.args.source_dir:
            cls.args.source_dir = os.path.join(cls.args.source_dir, '')
        if cls.args.po_dir:
            cls.args.po_dir = os.path.join(cls.args.po_dir, '')
        if cls.args.output_dir:
            cls.args.output_dir = os.path.join(cls.args.output_dir, '')

        return cls.args
