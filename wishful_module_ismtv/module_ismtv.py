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
    sweep_config = config_list.get_sweep_config(868.3e6, 919.0e6, 400e3)
    
    def __init__(self):
        super(IsmtvModule, self).__init__()
        self.log = logging.getLogger('IsmtvModule')

    @wishful_module.bind_function(upis.radio.get_noise)
    def get_noise(self):
        self.log.debug("Get noise".format())
        return self._calculate_noise()
        
    def _calculate_noise(self):
        sweep = self.sensor.sweep(self.sweep_config)
        noise = sweep.data
        return sum(noise) / len(noise)
