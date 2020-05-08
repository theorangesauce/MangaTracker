""" config.py
Store and retrieve config variables from config.ini

Copyright 2019 by Nicholas Bishop
"""
import os
import configparser

class Singleton():
    """
    Singleton(object)

    Abstract class which ensures that only one instance of the
    class ever exists.
    """
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class Config(Singleton):
    """
    Config(Singleton)
    Container for a configparser object. Will be able retrieve config items
    for MangaTracker.
    """
    def __init__(self, filename="config.ini"):
        """
        __init__(self, filename)
        Create a configparser object and store config values in class variables
        for later retrieval

        Arguments:
        filename (String) -- Name of file for loading/saving config info,
        defaults to config.ini
        """
        if not os.path.isfile(filename):
            self.set_default_config(filename)

        self.config = configparser.ConfigParser()
        self.config.read(filename)

        self.filename = filename
        self.database_name = self.config.get('config',
                                             'database_name',
                                             fallback='manga.db')
        self.volume_limit = self.config.getint('config',
                                               'volume_limit',
                                               fallback=128)
        self.series_per_page = self.config.getint('config',
                                                  'series_per_page',
                                                  fallback=0)
        self.compact_list = self.config.getboolean('config',
                                                   'compact_list',
                                                   fallback=False)
        self.show_empty_series = self.config.getboolean('config',
                                                        'show_empty_series',
                                                        fallback=False)
        self.default_to_gui = self.config.getboolean('config',
                                                     'default_to_gui',
                                                     fallback=True)

    def set_property(self, prop_name, prop_value):
        """
        set_property(self, prop_name, prop_value)
        Set a config property to a new value. Checks to ensure that
        prop_name refers to a valid property, and prop_value is a valid
        value for that property
        """
        if prop_name == "database_name":
            if (prop_value and isinstance(prop_value, str)
                    and prop_value[-3:] == ".db"
               ):
                self.config["config"]["database_name"] = prop_value
        elif prop_name == "volume_limit":
            if isinstance(prop_value, int) and prop_value > 0:
                self.config["config"]["volume_limit"] = str(prop_value)
        elif prop_name == "series_per_page":
            if isinstance(prop_value, int) and prop_value >= 0:
                self.config["config"]["series_per_page"] = str(prop_value)
        elif prop_name == "compact_list":
            if ((isinstance(prop_value, int) and prop_value in [0, 1])
                    or isinstance(prop_value, bool)
               ):
                self.config["config"]["compact_list"] = str(prop_value)
        elif prop_name == "show_empty_series":
            if ((isinstance(prop_value, int) and prop_value in [0, 1])
                    or isinstance(prop_value, bool)
               ):
                self.config["config"]["show_empty_series"] = str(prop_value)
        elif prop_name == "default_to_gui":
            if ((isinstance(prop_value, int) and prop_value in [0, 1])
                    or isinstance(prop_value, bool)
               ):
                self.config["config"]["default_to_gui"] = str(prop_value)
        with open(self.filename, 'w') as config_ini:
            self.config.write(config_ini)

    def set_default_config(self, filename):
        """
        set_default_config()
        Saves default config to desired filename
        """
        if os.path.isfile(filename):
            os.remove(filename)

        config = configparser.ConfigParser()
        default_cfg = {'config': {'database_name' : 'manga.db',
                                  'volume_limit' : 128,
                                  'series_per_page' : 0,
                                  'compact_list' : 0,
                                  'show_empty_series' : False,
                                  'default_to_gui' : True}}

        config.read_dict(default_cfg)
        with open(filename, 'w') as config_ini:
            config.write(config_ini)

        # Reset class variables for config object as well
        self.config = config
        self.filename = filename
        self.database_name = 'manga.db'
        self.volume_limit = 128
        self.series_per_page = 0
        self.compact_list = False
        self.show_empty_series = False
        self.default_to_gui = True
