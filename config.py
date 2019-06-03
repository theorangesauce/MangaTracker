# Config
# Store and retrieve config variables from config.ini

import os
import configparser

class Config(object):
    """
    Config(object)
    Container for a configparser object. Will be able retrieve config items
    for MangaTracker
    """
    def __init__(self, filename="config.ini"):
        """
        __init__(self, filename)
        Create a configparser object and store config values in class variables
        for later retrieval

        Arguments:
        filename (String) -- Name of file for loading/saving config info 
        """
        if !os.path.isfile(filename):
            set_default_config(filename)

        self.config = configparser.ConfigParser()
        self.config.read(filename)

        self.database_name = config.get('config', 'database_name', fallback='manga.db')
        self.volume_limit = config.getint('config', 'volume_limit', fallback=128)
        self.paginated = config.getboolean('config', 'paginated', fallback=False)
        self.series_per_page = config.getint('config', 'series_per_page', fallback=5)
        self.compact_list = config.getboolean('config', 'compact_list', fallback=False)


def set_default_config(filename):
    """
    set_default_config()
    Saves default config to desired filename
    """
    if os.path.isfile(filename):
        os.remove(filename)

    config = configparser.ConfigParser()
    default_cfg = {'config': {'database_name' : 'manga.db',
                              'volume_limit' : 128,
                              'paginated' : 0,
                              'series_per_page' : 5,
                              'compact_list': 0}}

    config.read_dict(default_cfg)
    with open('config.ini', 'w') as config_ini:
        config.write(config_ini)
        
config = Config();
