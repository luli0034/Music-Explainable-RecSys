from pyhocon import ConfigParser, ConfigTree


class Configger(object):

    __config_path = ''
    __conf = None

    @classmethod
    def path(cls, path):
        cls.__config_path = path
        cls.__conf = ConfigParser.parse_file(path)

    @classmethod
    def get_config(cls):
        return cls.__conf

    @staticmethod
    def merge_configs(confs):
        configs = ConfigTree()
        for conf in confs:
            configs = ConfigTree.merge_configs(configs, conf)

        return configs