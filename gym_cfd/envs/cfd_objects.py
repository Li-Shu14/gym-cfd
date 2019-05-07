class Controller():
    def __init__(self):
        self.Output = None # read only, the current signal output from the controller. %
        self.Setpoint = None
        self.DeadBand = None
        self.InputSignal = None

class Sensor():
    def __init__(self):
        self.Value = None

class Vents():
    def __init__(self):
        self.FlowRate = None # The volume flow rate of the airflow(or fluid). Measured in m3/s
        self.Temperature = None

class ACU():
    def __init__(self):
        self.FanSpeed = None # Measured in %
        self.CoolantFlowRate = None # Measured in m3/s
        self.CoolantTemperatureIn = None 
        self.CoolantTemperatureOut = None 

class ITEquipment():
    def __init__(self):
        self.HeatPowerFactor = None # The scaling factor taht determines the fraction of the name plate power that is actually drawn. Measured in %.

class HeatExchanger():
    def __init__(self):
        self.CoolantTemperatureIn = None
        self.CoolantTemperatureOut = None
        self.CoolantFlowRate = None

