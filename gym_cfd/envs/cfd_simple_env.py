import os,sys,io,time
import subprocess
import numpy as np
import logging
import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym_cfd.envs.cfd_objects import *
from gym_cfd.envs.matlab_util import *
class CfdSimpleEnv(gym.Env):
	metadata = {'render.modes': ['human']}
	def __init__(self):
		"""
		问题定义：控制为连续域，状态也为连续域。
		状态包括：温度传感器温度，房间内IT设备负载，上一个step的空调温度设定点
		动作空间：空调温度设定点
		关于CfdSimpleEnv的仿真环境描述请见CfdSimpleEnv.txt
		"""
		# ----matlab交互----
		# matlab_mode = 0: 创建一个新的matlab会话; 1 连接到一个已经打开的matlab共享会话（窗口）,matlab.engine.shareEngine。
		# 关于更加系统地对python通过matlab与6SigmaRoom CFD交互过程的说明请见unit_test，其中的代码（script_originV1_embed.py）带有大量注释
		self.eng = None
		self.out = None
		self.err = None
		self.eng = new_matlab_engine(matlab_mode = 1) 
		# ----仿真房间的部分常数设置----
		self.LAMBDA_temp = 0.002 					# reward函数中温度罚项前的系数
		self.LAMBDA_energy = 0.002 					# reward函数中能耗项前的系数
		self.time_interval = 1						# 控制实施的时间间隔,min
		self.current_time = 0						# 当前时间
		self.SixSigma = None						# 每个迭代步从Matlab接收的原数据
		self.SixSigmaHistroy = [] 					# 原数据历史记录
		self.ParametersHistroy = []					# 参数历史
		self.rated_power = 3 						# 空调额定功率，kW
		self.energy_efficiency = 3	 				# 空调能效比,每kW电能可以制造的冷量kW，数据机房空调通常是2.5-3.5
		self.initial_temperature = 24.0 			# 房间初始温度场中某传感器温度（基于稳态计算结果）
		self.initial_load = 0.5 					# 房间初始的机柜负载,百分比
		self.initial_setpoint = 18.0 				# 空调初始的温度设定值
		self.min_temperature = 13.0 				# 房间最低温度设置为冷冻水进口温度————13摄氏度。
		self.max_temperature = 40.0 				# 房间最高温度暂定为40摄氏度。
		self.min_load = 0.0 						# 机柜最低负载，%
		self.max_load = 1.0 						# 机柜最高负载，%
		self.min_temperature_setpoint = 15.0 		# 空调温度设定点最低值
		self.max_temperature_setpoint = 25.0 		# 空调温度设定点最高值
		self.alarm_temperature = 40.0 				# 房间关键温度测点不应该超过的值，一旦超过，视为该次模拟失败。重新开始。
		self.low_state = np.array([self.min_temperature, self.min_load, self.min_temperature_setpoint])
		self.high_state = np.array([self.max_temperature, self.max_load, self.max_temperature_setpoint])

		self.viewer = None

		self.action_space = spaces.Box(low=self.min_temperature_setpoint,
									   high=self.max_temperature_setpoint, 
                                       shape=(1,),
									   dtype=np.float32)

		self.observation_space = spaces.Box(low=self.low_state,
											high=self.high_state, 
											dtype=np.float32)  # 这里的观测量和状态量完全一致
		self.CFDdata_init()
		self.change_matlab_directory()
		self.seed()
		print('init_fun_finised!')
		
		self.p = None # 初始化一个在命令行里运行仿真环境脚本的工作进程 subprocess
		self.reset()

	def CFDdata_init(self):
		self.room = Room()
		self.room.sensor03 = Sensor()
		self.room.acu01 = ACU()
		self.room.itequipment = ITEquipment()
		self.room.controller = Controller()

	def seed(self, seed=None):
		self.np_random, seed = seeding.np_random(seed)
		return [seed]
		
	def step(self, action):
		# assert self.action_space.contains(action), "%r (%s) invalid"%(action,type(action))
		temperature, load, temperature_setpoint = self.state
		old_action = temperature_setpoint
		while(1):
			if len(self.SixSigmaHistroy) < 3 :
				break
			elif self.SixSigmaHistroy[-1]['SolutionControl']['Time']['Value'] >= (self.SixSigmaHistroy[-2]['SolutionControl']['Time']['Value']+self.time_interval):
				break
			else: 
				self.write_cfd_file(float(old_action))
				self.read_cfd_file() # self.state updated!
		self.write_cfd_file(float(action))
		self.read_cfd_file() # self.state updated!
		print(self.SixSigma)
		self.state = np.array([self.room.sensor03.value,self.room.itequipment.HeatPowerFactor,action])
		
		done = bool(self.room.sensor03.value > self.alarm_temperature) or self.SixSigmaHistroy[-1]['SolutionControl']['Time']['Value'] >55 # 结束标志
		# 奖赏函数
		if not done:
			reward = self.LAMBDA_temp * np.log(1 + np.exp(self.room.sensor03.value - self.alarm_temperature)) + \
				     self.LAMBDA_energy * (self.room.acu01.FanSpeed * self.rated_power + self.room.acu01.RefrigeratingCapacity / self.energy_efficiency)
		# reward = λt*ln(1+exp(T-25)) + λe*(E_fan+E_CoolingStation)		 
		else:
			reward = 0.0
		return self.state, reward, done, {}

	def reset(self):
		# if eng.eval('exist("SixSigma")',nargout=1):
		print('reset!')
		self.eng.eval('clear global SixSigma',nargout=0)
		self.eng.fclose('all',nargout=0)
		self.eng.clear('all',nargout=0) 
		self.eng.close('all',nargout=0)
		self.out,self.err = io.StringIO(), io.StringIO()
		self.stdout, self.stderr = None, None
		self.eng.SixSigma_initialize(False,nargout=0,stdout=self.out,stderr=self.err)
		self.eng.eval('global SixSigma',nargout=0)
		while self.eng.eval("exist('in.csv', 'file')"):
			self.eng.eval("delete 'in.csv'",nargout=0)
		while self.eng.eval("exist('out.csv', 'file')"):
			self.eng.eval("delete 'out.csv'",nargout=0)
		print('Initialization finished!')

		self.writer_count = 0
		self.reader_count = 0
		no_file_time = 0
		no_update_file_time = 0
		# time_out_threshold = 3000 if matlab_mode else 12000 # matlab_mode=1时等待3秒即可。matlab_mode=0时等待12秒，等待超出时长则结束程序
		
		self.end_cfd_subproc() # 先结束上一项进程，再开始新的进程
		self.p = subprocess.Popen("cmd /k" + " D:\\reinforcement_learning\\sfd_simulation\\run_embed_simulation.bat",stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		time.sleep(5)
		print('open cmd!')
		self.read_cfd_file()
		print('read initial output.csv!')
		# self.state = np.array([self.initial_temperature,self.initial_load,self.initial_setpoint])
		return np.array(self.state)

	# def render(self, mode='human'):
	#   ...

	def close(self):
		self.eng = None # 释放self.eng占用内存，从而将matlab进程杀掉。
		self.end_cfd_subproc()
		if self.viewer:
			self.viewer.close()
			self.viewer = None
		print('environment closed!')

	def end_cfd_subproc(self):
		if self.p != None :
			p_end = subprocess.Popen('taskkill /pid '+str(self.p.pid)+' -t -f', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	def read_cfd_file(self):
		while 1:
			if self.eng.exist('out.csv', 'file'):
				self.eng.fclose('all',nargout=0)
				no_file_time = 0
				if self.eng.SixSigma_readCFDOutFile('out.csv') > 0:
					self.reader_count += 1
					print ('SixSigma_readCFDOutFile ',self.reader_count,' times')
					self.SixSigma = self.eng.workspace['SixSigma']
					# print(self.SixSigma)
					self.SixSigmaHistroy.append(self.SixSigma)
					no_update_file_time = 0
					temperature_new = self.eng.SixSigma_getCFDOutData('Sensor','Sensor03','Value')
					self.get_room_info_from_matlab()
					self.state = np.array([self.room.sensor03.value, self.room.itequipment.HeatPowerFactor, self.room.controller.SetPoint])
					break
				else:
					time.sleep(0.01)
			else:
				time.sleep(0.01)
	
	def write_cfd_file(self,action):
		self.eng.SixSigma_setCFDInData('Controller','Air Temperature Controller','SetPoint',action,'C',nargout=0)
		self.eng.SixSigma_writeCFDInFile('in.csv',nargout=0)
		self.writer_count += 1
		print ('SixSigma_writeCFDOutFile ',self.writer_count,' times')

	def change_matlab_directory(self):
		local_path = 'D:\\reinforcement_learning\\sfd_simulation\\SimpleTestCase_cloud_transient\\SimpleTestCase\\SolverExchange'
		ret = self.eng.cd(local_path,nargout=0,stdout=self.out,stderr=self.err)

	def get_room_info_from_matlab(self):
			self.room.controller.SetPoint = self.eng.SixSigma_getCFDOutData('Controller','Air Temperature Controller','SetPoint')
			self.room.sensor03.value = self.eng.SixSigma_getCFDOutData('Sensor','Sensor03','Value')
			self.room.acu01.CoolantFlowRate = self.eng.SixSigma_getCFDOutData('ACU','ACU01','CoolantFlowRate')
			self.room.acu01.CoolantTemperatureIn = self.eng.SixSigma_getCFDOutData('ACU','ACU01','CoolantTemperatureIn')
			self.room.acu01.CoolantTemperatureOut = self.eng.SixSigma_getCFDOutData('ACU','ACU01','CoolantTemperatureOut')
			self.room.acu01.FanSpeed = self.eng.SixSigma_getCFDOutData('ACU','ACU01','FanSpeed')
			self.room.acu01.cal_RefrigeratingCapacity()
			self.room.itequipment.HeatPowerFactor = self.eng.SixSigma_getCFDOutData('ITEquipment','C5:Slot 1','HeatPowerFactor')


if __name__ == '__main__':

	env = CfdSimpleEnv()
	start = 20
	for i in range(5):
		print(env.state)
		env.step(start+1)
	# time.sleep(5)
	# env.reset()
	env.close()

