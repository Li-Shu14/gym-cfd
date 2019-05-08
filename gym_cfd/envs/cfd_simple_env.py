import gym
import numpy as np

from gym import error, spaces, utils
from gym.utils import seeding
from .cfd_objects import *

class CfdSimpleEnv(gym.Env):
	metadata = {'render.modes': ['human']}

	def __init__(self):
		"""
		问题定义：控制为连续域，状态也为连续域。
		状态包括：温度传感器温度，房间内IT设备负载，上一个step的空调温度设定点
		动作空间：空调温度设定点
		"""
		self.initial_temperature = 24 # 房间初始温度场中某传感器温度（基于稳态计算结果）
		self.initial_load = 2 # 房间初始的机柜负载
		self.initial_setpoint = 22 # 空调初始的温度设定值
		
		self.min_temperature = 13 # 房间最低温度设置为冷冻水进口温度————13摄氏度。
		self.max_temperature = 40 # 房间最高温度暂定为40摄氏度。
		self.min_load = 2 # 机柜最低负载，kw
		self.max_load = 3 # 机柜最高负载，kw
		self.min_temperature_setpoint = 15 # 空调温度设定点最低值
		self.max_temperature_setpoint = 25 # 空调温度设定点最高值
		self.alarm_temperature = 25 # 房间关键温度测点不应该超过的值，一旦超过，视为该次模拟失败。重新开始。
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

		self.seed()
		self.reset()

	def seed(self, seed=None):
		self.np_random, seed = seeding.np_random(seed)
		return [seed]
		
	def step(self, action):
		# assert self.action_space.contains(action), "%r (%s) invalid"%(action,type(action))
		state = self.state
		temperature, load, temperature_setpoint = state

		# 随机得到反馈结果，最终这里需要链接到matlab的接口
		temperature_new = self.np_random.uniform(low=temperature-1, high=temperature+1, size=(1,))
		load_new = load # 设备负载应该是按照某种规律变化，需要了解当前进展的时间步。这一点是否需要体现在step函数里？目前认为暂时不用。那么将负载归入state里是否还需要？当然。
		temperature_setpoint = action
		
		done = bool(temperature_new > self.alarm_temperature) # 结束标志
		# 奖赏函数
		if not done:
			reward = 1.0 + (temperature_new - self.alarm_temperature) # 暂未体现出PUE
		else:
			reward = 0.0
			
		self.state =(temperature_new, load_new, temperature_setpoint)
		return self.state, reward, done, {}



	def reset(self):
		self.state = np.array([self.initial_temperature,self.initial_load,self.initial_setpoint])
		return np.array(self.state)

	# def render(self, mode='human'):
	#   ...

	def close(self):
		if self.viewer:
			self.viewer.close()
			self.viewer = None
		