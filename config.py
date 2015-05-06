import ConfigParser

class Config(object):
    
    def __init__(self):
        self.section = []
    
    def ConfigSectionMap(self, section):
        config = ConfigParser.ConfigParser()
        config.read('properties')
        dict = {}
        options = config.options(section)
        for option in options:
            try:
                dict[option] = config.get(section, option)
                if dict[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict[option] = None
        return dict