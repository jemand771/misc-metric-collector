class CollectorBase:
    ENV_PREFIX = ""

    def __init__(self, env):
        self.env = env

    def collect(self):
        pass

    def env_get_raise(self, name):
        if self.ENV_PREFIX:
            name = "_".join((self.ENV_PREFIX, name))
        if not (value := self.env.get(name)):
            raise NotConfigured
        return value


class NotConfigured(KeyError):
    pass
