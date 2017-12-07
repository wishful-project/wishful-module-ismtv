import logging
import random
import wishful_upis as upis
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions

import time
import serial
from vesna import alh
from vesna.alh.spectrumsensor import SpectrumSensor
from vesna.alh.signalgenerator import SignalGenerator, SignalGeneratorProgram

__author__ = "Matevz Vucnik"
__copyright__ = "Copyright (c) 2017, Jozef Stefan Instiute"
__version__ = "0.1.0"
__email__ = "matevz.vucnik@ijs.si"


@wishful_module.build_module
class IsmtvModule(wishful_module.AgentModule):
    node = None
    sensor = None
    sweep_config = None
    generator = None
    tx_config = None
    
    def __init__(self, dev):
        super(IsmtvModule, self).__init__()
        self.log = logging.getLogger('IsmtvModule')
        ser = serial.Serial(dev, 115200)
        self.node = alh.ALHTerminal(ser)

    @wishful_module.bind_function(upis.radio.get_measurements)
    def get_measurements(self, params):
        if not self.sensor:
            self.sensor = SpectrumSensor(self.node)
            config_list = self.sensor.get_config_list()
            self.sweep_config = config_list.get_sweep_config(params[0], params[1], params[2])
            if self.sweep_config is None:
                self.sensor = None
                raise Exception("Node can not scan specified frequency range.")
        sweep = self.sensor.sweep(self.sweep_config)
        f = list(self.sweep_config.get_hz_list())
        p = sweep.data
        return {'frequency':f, 'power':p}


    @wishful_module.bind_function(upis.radio.play_waveform)
    def play_waveform(self, iface, freq, power_lvl, kwargs):
        if not self.generator:
            self.generator = SignalGenerator(self.node)
            config_list = self.generator.get_config_list()
            self.tx_config = config_list.get_tx_config(freq, power_lvl)
            if self.tx_config is None:
                self.generator = None
                return 2

        now = time.time()
        program = SignalGeneratorProgram(self.tx_config, now + 5, kwargs['play_time'])
        self.generator.program(program)

        return 0

    @wishful_module.bind_function(upis.radio.get_radio_info)
    def get_radio_info(self, platform_id):
        if platform_id == "sensor":
            sensor = SpectrumSensor(self.node)
            config_list = sensor.get_config_list()
        elif platform_id == "generator":
            generator = SignalGenerator(self.node)
            config_list = generator.get_config_list()
        else:
            config_list = str(platform_id) + ": Not supported! Try: sensor or generator"

        return config_list
