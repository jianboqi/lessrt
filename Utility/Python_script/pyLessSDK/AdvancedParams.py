# coding: utf-8


class AdvancedParams(object):
    def __init__(self):
        self.number_of_cores = 12
        self.minimum_iteration = 5
        self.network_sim = False

    def init_advanced_params_from_json(self, json_object):
        self.number_of_cores = json_object["Advanced"]["number_of_cores"]
        self.minimum_iteration = json_object["Advanced"]["minimum_iteration"]
        self.network_sim = json_object["Advanced"]["network_sim"]
        return self

    def to_json_object(self):
        json_object = {"number_of_cores": self.number_of_cores,
                       "minimum_iteration": self.minimum_iteration,
                       "network_sim": self.network_sim}
        return json_object

