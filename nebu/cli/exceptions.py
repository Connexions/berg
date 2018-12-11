import click


__all__ = (
    'ExistingOutputDir',
    'MissingContent',
    'MissingBakedContent',
    'OldContent',
    'UnknownEnvironment',
)


class ExistingOutputDir(click.ClickException):
    exit_code = 3

    def __init__(self, output_dir):
        message = "directory already exists:  {}".format(output_dir)
        super(ExistingOutputDir, self).__init__(message)


class MissingContent(click.ClickException):
    exit_code = 4

    def __init__(self, target):
        message = "content unavailable for '{}'".format(target)
        super(MissingContent, self).__init__(message)


class MissingBakedContent(click.ClickException):
    exit_code = 7

    def __init__(self, target):
        message = "baked content unavailable for '{}'".format(target)
        super(MissingBakedContent, self).__init__(message)


class OldContent(click.ClickException):
    exit_code = 6

    def __init__(self):
        message = "Non-latest version requested"
        super(OldContent, self).__init__(message)


class UnknownEnvironment(click.ClickException):
    exit_code = 5

    def __init__(self, environ_name):
        message = "unknown environment '{}'".format(environ_name)
        super(UnknownEnvironment, self).__init__(message)
