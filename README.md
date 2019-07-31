# gym-cfd
Trying to integrate the CFD simulation of 6sigmaRoom into gym in order to realize reinforcement learning algoritms.
# Installation
First Install *gym* with `pip install gym`. Then enter the directory where you put 'gym-cfd' file .installed your package with `pip install -e gym-cfd`, you can create an instance of the environment with 
`gym.make('gym_cfd:cfd_simple-v0')` or `gym.make('gym_cfd:cfd_complex-v0')`
# Test
Once you finished installment, you can use codes below to see whether it works:
```Python
import gym
env = gym.make('gym_cfd:cfd_simple-v0')
env.reset()

for i in range(1000):
    action = env.action_space.sample() # take a random action
    state, reward, done, info = env.step(action) 
    # def : state = (temperature_new, load_new, temperature_setpoint)
    print(state, reward, done, info)
env.close()
```

# Development
This project is still in build...
