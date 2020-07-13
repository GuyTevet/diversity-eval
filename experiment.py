from abc import ABC, abstractmethod


class Experiment(ABC):

    def __init__(self):
        super().__init__()

    def __call__(self, config):
        self.check_config(config)
        data = self.collect_data(config)
        results = self.run(config, data)
        self.visualize(config, data, results)
        self.export(config, data, results)

    @abstractmethod
    def check_config(self, config):
        pass

    @abstractmethod
    def collect_data(self, config):
        pass

    @abstractmethod
    def run(self, config, data):
        pass

    @abstractmethod
    def visualize(self, config, data, results):
        pass

    @abstractmethod
    def export(self, config, data, results):
        pass
