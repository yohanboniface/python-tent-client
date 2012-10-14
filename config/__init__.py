# -*- coding: utf-8 -*-

import os

import ConfigParser

USER_DIR = os.path.expanduser('~')


class Config(object):

    CONFIG_DIR = os.path.join(
        USER_DIR,
        ".tentapp/"
    )
    CONFIG_FILE = os.path.join(
        CONFIG_DIR,
        "config.cfg"
    )
    DEFAULT_CONFIG_FILE = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        "default.cfg"
    )
    NoOptionError = ConfigParser.NoOptionError  # Convenient to use them outside
    NoSectionError = ConfigParser.NoSectionError

    def __init__(self, *args, **kwargs):
        if not os.path.exists(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
        # Make parsers case sensitive
        self.parser = ConfigParser.SafeConfigParser()
        self.default = ConfigParser.SafeConfigParser()
        self.parser.optionxform = str
        self.default.optionxform = str
        self.parser.read(self.CONFIG_FILE)
        self.default.read(self.DEFAULT_CONFIG_FILE)
        self.check_configuration()

    def get(self, *args):
        """
        parser.get shortcut, cachting errors if requested option does not exists.
        So use parser.get directly for a better control.
        """
        try:
            output = self.parser.get(*args)
        except (self.NoOptionError, self.NoSectionError):
            output = None
        return output

    def items(self, section):
        return self.parser.items(section)

    def save(self):
        with open(self.CONFIG_FILE, 'wb') as configfile:
            self.parser.write(configfile)

    def prompt(self, section, option):
        default = self.get(section, option)
        if not default:
            default = self.default.get(section, option)
        print u"Please enter a value for %s=>%s:" % (section, option)
        print u"(Type «Enter» to get default value: %s" % default
        value = raw_input("=> ? ")
        if not value:
            value = default
        return value

    def check_configuration(self):
        """
        Check that mandatory configuration is ok to make the tentcli app working.
        """
        for section in self.default.sections():
            options = self.default.options(section)
            if not self.parser.has_section(section):
                self.parser.add_section(section)
            for option in options:
                if not self.parser.has_option(section, option):
                    value = self.prompt(section, option)
                    self.parser.set(section, option, value)
        self.save()
