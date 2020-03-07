# gym-cfd
Trying to integrate the CFD simulation of 6sigmaRoom into gym in order to realize reinforcement learning algoritms.
# Installation
First Install *gym* with `pip install gym`. Then enter the directory where you put 'gym-cfd' file. Installed your package with `pip install -e gym-cfd`, you can create an instance of the environment with 
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
This project is far from completed. Welcome further discussion. Embarrassing is that my software has already expired...

# Citation
If you find this package really helpful and are interested in citing it here's how you do it:
@Misc{,
    author = {Shu Li},
    title = {{Gym-CFD}: An implement of combining reinforcement learning and CFD simulation with 6SigmaRoom based on libraries from OpenAI},
    year = {2018--},
    url = " https://github.com/Li-Shu14/gym-cfd/"
}
