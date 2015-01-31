

class ToolBase(object):
    # This is an 'abstract' base class, used to provide an indication of
    # how to create a new tool class. Therefore, the arguments will be unused,
    # so that is suppressed here.
    # pylint: disable=unused-argument

    def configure(self, prospector_config, found_files):
        """
        Tools have their own way of being configured from configuration files
        on the current path - for example, a .pep8rc file. Prospector will use
        its own configuration settings unless this method discovers some
        tool-specific configuration that should be used instead.

        :return: A string indicating how or where this tool was configured from.
                 For example, this can be a path to the .pylintrc file used, if
                 used. Returning None means that prospector defaults were used.
        """
        # We don't want Pylint to tell us that this method should be a function,
        # it's an "abstract" class after all.
        # pylint: disable=no-self-use
        return None

    def run(self, found_files):
        """
        Actually run the tool and collect the various messages emitted by the tool.
        It is expected that this will convert whatever output of the tool into the
        standard prospector Message and Location objects.
        """
        raise NotImplementedError
