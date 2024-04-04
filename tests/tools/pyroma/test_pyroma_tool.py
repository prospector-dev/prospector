from pathlib import Path

from prospector.config import ProspectorConfig
from prospector.finder import FileFinder
from prospector.tools.pyroma import PyromaTool

from ...utils import patch_cli, patch_cwd


def test_forced_include():
    """
    The built-in default profiles for prospector will ignore `setup.py` by default, but this needs
    to be explicitly overridden for pyroma *only*

    However, other ignore files should still not be returned. Only a setup.py in the root of the
    working directory should be explicitly force-included.

    see https://github.com/PyCQA/prospector/pull/106
    """
    test_data = Path(__file__).parent / "testdata"

    with patch_cwd(test_data):
        # can't use the patch_execution shortcut due to pyroma playing with things itself too
        with patch_cli("prospector", "--profile", "test-pyroma-profile.yml"):
            config = ProspectorConfig()
            files = FileFinder(*config.paths, exclusion_filters=[config.make_exclusion_filter()])
            # this should not return the root setup.py by default (using the strictness profile)
            # but will return others (they might just be called setup.py by coincidence)
            assert len(files.python_modules) == 3
            tool = PyromaTool()
            tool.configure(config, files)

        # must do this outside of the CLI patch because pyroma does its own sys.argv patching...
        print(files.files)
        messages = tool.run(files)
        print(messages)

        # this should still find errors in the setup.py, but not any of the others
        assert len(messages) == 10
        allowed = (test_data / "setup.py", test_data / "pkg1/this_one_is_fine/setup.py")
        for message in messages:
            assert message.location.path in allowed
