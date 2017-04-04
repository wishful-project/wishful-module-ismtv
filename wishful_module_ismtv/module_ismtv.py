import logging
import random
import wishful_upis as upis
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions

from vesna import alh
from vesna.alh.spectrumsensor import SpectrumSensor

__author__ = "Matevz Vucnik"
__copyright__ = "Copyright (c) 2017, Jozef Stefan Instiute"
__version__ = "0.1.0"
__email__ = "matevz.vucnik@ijs.si"


@wishful_module.build_module
class IsmtvModule(wishful_module.AgentModule):
    node = alh.ALHWeb("http://localhost:9000/communicator", "/dev/ttyS1")
    sensor = SpectrumSensor(node)
    config_list = sensor.get_config_list()
    sweep_config = None
    
    def __init__(self):
        super(IsmtvModule, self).__init__()
        self.log = logging.getLogger('IsmtvModule')

    @wishful_module.bind_function(upis.radio.get_measurements)
    def get_measurements(self, params):
        self.log.debug("Get Measurements".format())
        if not self.sweep_config:
            self.sweep_config = self.config_list.get_sweep_config(params[0], params[1], params[2])
        sweep = self.sensor.sweep(self.sweep_config)
        f = list(self.sweep_config.get_hz_list())
        p = sweep.data
        return {'frequency':f, 'power':p}
