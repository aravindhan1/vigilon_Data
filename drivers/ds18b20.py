# drivers/ds18b20.py

import glob

class DS18B20:
    def __init__(self):
        base_dir = '/sys/bus/w1/devices/'
        self.device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'

    def read_temp(self):
        with open(self.device_file, 'r') as f:
            lines = f.readlines()

        while lines[0].strip()[-3:] != 'YES':
            with open(self.device_file, 'r') as f:
                lines = f.readlines()

        temp_line = lines[1]
        temp = float(temp_line.split('t=')[-1]) / 1000.0
        return temp
