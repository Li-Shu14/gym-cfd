"""
这里定义的类是所有能通过matlab脚本与6sigmaroom交互的对象及其属性。其中主要关注：controller, sensor, acu, itequipment.
"""
class Room():
    def __init__(self):
        pass

class Controller():
    def __init__(self):
        self.Output = None # read only, the current signal output from the controller
        self.Setpoint = None
        self.DeadBand = None
        self.InputSignal = None # read only, value of the input signal from the associated sensor 

class Sensor():
    def __init__(self):
        self.Value = None # read only

class Vents():
    def __init__(self):
        self.FlowRate = None # The volume flow rate of the airflow(or fluid). Measured in m3/s
        self.Temperature = None

class ACU():
    def __init__(self):
        self.FanSpeed = None # Measured in %
        self.CoolantFlowRate = None # Measured in m3/s
        self.CoolantTemperatureIn = None 
        self.CoolantTemperatureOut = None # read only
        self.RefrigeratingCapacity = None # 总制冷量

    def cal_RefrigeratingCapacity(self): # 注意流量单位
        self.RefrigeratingCapacity = (self.CoolantTemperatureOut - self.CoolantTemperatureIn) * 4.2 * 1e3 * self.CoolantFlowRate
        return self.RefrigeratingCapacity
class ITEquipment():
    def __init__(self):
        self.HeatPowerFactor = None # The scaling factor that determines the fraction of the name plate power that is actually drawn. Measured in %.

class HeatExchanger():
    def __init__(self):
        self.CoolantTemperatureIn = None
        self.CoolantTemperatureOut = None
        self.CoolantFlowRate = None

