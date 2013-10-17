import sys
from logilab.common.textutils import splitstrip
from prospector.tools.pylint.collector import Collector
from prospector.tools.pylint.linter import ProspectorLinter


class PylintTool():

    def _find_paths(self, rootpath):
        return ['prospector']
        pass

    def prepare(self, rootpath, args, profiles):
        linter = ProspectorLinter()
        linter.load_default_plugins()

        pylint_args = ['--max-line-length=160']  # TODO: move this into the 'common' profile

        paths = self._find_paths(rootpath)

        for profile in profiles:
            profile.apply_to_pylint(linter)

        pylint_args.append(' '.join(paths))

        # this rather cryptic invocation is lifted from the Pylint Run class
        linter.read_config_file()
        # is there some additional plugins in the file configuration, in
        config_parser = linter.cfgfile_parser
        if config_parser.has_option('MASTER', 'load-plugins'):
            plugins = splitstrip(config_parser.get('MASTER', 'load-plugins'))
            linter.load_plugin_modules(plugins)

        self._args = linter.load_command_line_configuration(pylint_args)

        if not self._args:
            print linter.help()
            sys.exit(2)

        # disable the warnings about disabling warnings...
        linter.disable('I0011')
        linter.disable('I0012')
        linter.disable('I0020')
        linter.disable('I0021')

        # insert current working directory to the python path to have a correct behaviour
        linter.prepare_import_path(self._args)

        # use the collector 'reporter' to simply gather the messages given by PyLint
        self._collector = Collector()
        linter.set_reporter(self._collector)

        self._linter = linter

    def run(self):
        # note: Pylint will exit with a status code indicating the health of the
        # code it was checking. Prospector will not mimic this behaviour, as it
        # interferes with scripts which depend on and expect the exit code of the
        # code checker to match whether the check itself was successful
        self._linter.check(self._args)
        return self._collector.get_messages()
