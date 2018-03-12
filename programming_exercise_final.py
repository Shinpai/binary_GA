# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import random as rng
import os
import math
from matplotlib import pyplot as plt
import matplotlib.animation as animation

# @author Harri Juutilainen 02/2018
# Memetic particle swarm optimization

# PARAMETERS, McCormick function
FILE_NAME = 'MPSO_result.dat'
POPULATION_SIZE = 200
ACC_CONST = 2
VMAX = 3
DIM = 2
R_NEIGHBORS = 4
BOUNDS = [(-1.5, 4), (-3, 4)]

fig, ax = plt.subplots()
ln, = plt.plot([], [], 'ro')

frames = []
anis = []

'''
FUNC_ : (x - 2) ** 2 + (y - 1) ** 2
EQ_1 : 2 * y - 1 = x
INEQ_1 : x ** 2 / 4 + y - 1 <= 0
'''


class Particle:
    def __init__(self, index):
        self.index = index
        self.position = [rng.uniform(BOUNDS[i][0],
                                     BOUNDS[i][1]) for i in range(DIM)]
        self.velocity = [rng.uniform(-VMAX, VMAX) for i in range(DIM)]

        self.fitness = 0.0
        self.pbest = self
        self.lbest = self

    def evaluate(self, x, y):
        '''
        Function to optimize (minimize),
        particles fitness set as function value,
        compares particle to its personal best after eval
        '''
        return math.sin(x + y) + (x - y) ** 2 - 1.5 * x + 2.5 * y + 1

    def compare_pbest(self):
        '''
        Checks if particle is at pbest fitness.
        Sets new pbest accordingly.
        '''
        if self.fitness < self.pbest.fitness:
            self.pbest = self

    def update_velocity(self, v_kohde):
        '''
        Updates the velocity of a particle with weighted factors
        '''
        for i in range(DIM):
            p_1 = self.velocity[i]
            # accelerate towards personal best
            p_2 = ACC_CONST * rng.random() * (self.pbest.position[i] - self.position[i])
            # accelerate towards local or global best
            p_3 = ACC_CONST * rng.random() * (v_kohde.position[i] - self.position[i])
            self.velocity[i] = p_1 + p_2 + p_3

    def move(self):
        '''
        Update the position of a particle.
        Subjects particle to positional constraints (torque).
        '''
        vanha = [self.position[0], self.position[1]]

        # calculate new position
        for i in range(DIM):
            self.position[i] += self.velocity[i]
            max_l = abs(BOUNDS[i][0] - BOUNDS[i][1])
        # torque constraints
            if self.position[i] > BOUNDS[i][0]:
                self.position[i] = BOUNDS[i][0] + (self.position[i] % max_l)
            elif self.position[i] < BOUNDS[i][1]:
                self.position[i] = BOUNDS[i][1] - (self.position[i] % max_l)

        uusi = [self.position[0], self.position[1]]

        vanha_f = self.evaluate(vanha[0], vanha[1])
        uusi_f = self.evaluate(uusi[0], uusi[1])
        # check if old pos is better than new
        if vanha_f < uusi_f:
            self.position = vanha
        else:
            self.position = uusi

    def print_par(self):
        ''' Print info of a particle '''
        with open(FILE_NAME, 'a') as f:
            print("#{}\nPOS ({},{})\nvalue: {}\n".format(
                self.index, round(self.position[0], 3),
                round(self.position[1], 3), round(self.fitness, 3)),
                file=f)


class Swarm:
    ''' Set of Particles '''
    def __init__(self):
        self.particles = []
        self.gbest = None

    def initialize_swarm(self):
        ''' Initializes a swarm with random particles '''
        for i in range(POPULATION_SIZE):
            self.particles.append(Particle(i))

    def compare_gbest(self, particle):
        ''' Compare particle value to best value of swarm '''
        if particle.fitness < self.gbest.fitness:
            self.gbest = particle

    def compare_lbest(self, particle, p, n):
        ''' Compare particle value to neighboring particles '''
        best_fit = min([particle.fitness, p.fitness, n.fitness])
        lbest = [x for x in [particle, p, n] if x.fitness == best_fit]
        return lbest.pop()

    def print_gen(self, index, mode, file):
        ''' prints out the necessary info for a generation '''
        print("ITERS: {}, {}\ngbest fit: {}\npos: ({},{})\n".format(
            index, mode, round(self.gbest.fitness, 3),
            round(self.gbest.position[0], 3), round(self.gbest.position[1], 3)
        ), file=file)

    def get_neighbors(self, par):
        neighs = []
        indeksi = self.particles.index(par)
        for r in range(R_NEIGHBORS):
            ind_l = (indeksi + r) % len(self.particles)
            ind_k = (indeksi - r) % len(self.particles)
            neighs.append(self.particles[ind_l])
            neighs.append(self.particles[ind_k])
        return neighs

    def local_search(self, schema):
        if schema == 'scheme_1':
            # local search in the position of gbest
            neighbors = self.get_neighbors(self.gbest)
            new_solution = max(neighbors, key=lambda x: x.fitness)
            return new_solution
        elif schema == 'scheme_2':
            # search threshold with rng for each position
            pass
        elif schema == 'scheme_3a':
            # search on best position and randomly selected positions
            results = []
            # best (same as scheme 1)
            best_neighbors = self.get_neighbors(self.gbest)
            results.append(max(best_neighbors, key=lambda x: x.fitness))
            # some random particles selected
            sample = rng.sample(self.particles, 4)
            for n in sample:
                rng_neighbors = self.get_neighbors(n)
                results.append(max(rng_neighbors, key=lambda x: x.fitness))
            return max(results, key=lambda x: x.fitness)
        elif schema == 'scheme_3b':
            # search on best position and randomly selected positions
            # search space is defined by parameter SS
            results = []
            # best (same as scheme 1)
            best_neighbors = self.get_neighbors(self.gbest)
            results.append(max(best_neighbors, key=lambda x: x.fitness))
            # some random particles selected
            sample = rng.sample(self.particles, 4)
            for n in sample:
                rng_neighbors = self.get_neighbors(n)
                results.append(max(rng_neighbors, key=lambda x: x.fitness))
            return max(results, key=lambda x: x.fitness)


def MPSO(ITERS, mode):
    '''
    Main MPSO loop.
    '''
    t = 0
    # Initialize swarm
    swarm = Swarm()
    swarm.initialize_swarm()
    swarm.gbest = swarm.particles[0]

    # Evaluate
    for p in swarm.particles:
        p.evaluate(p.position[0], p.position[1])

    while t < ITERS:
        for par in swarm.particles:
            # Evaluate particle and check personal best
            par.fitness = par.evaluate(par.position[0], par.position[1])
            par.compare_pbest()
            # Check global best for velocity calculation
            swarm.compare_gbest(par)

            vanha = par
            # Update velocity of particle
            par.update_velocity(swarm.gbest)
            # Move particle according to velocity
            par.move()
            uusi = par
            # Compare particle before and after moving and choose optimal
            par = vanha if vanha.fitness < uusi.fitness else uusi

            # LOCAL SEARCH
            if t % 20 == 0:
                y = swarm.local_search(mode)
                # Compare to previous particle and choose optimal
                par = par if par.fitness < y.fitness else y                

        # PRINTING AND VISUALS
        if t % 200 == 0 or t == ITERS:
            with open(FILE_NAME, 'a') as f:
                swarm.print_gen(t, mode, f)
        if t % 20 == 0:
            make_frame(swarm, mode)

        t += 1


def clear():
    # *-* EXTRA *-* #
    ''' Clears the console '''
    name = os.name
    if name == 'posix':
        os.system('clear')
    elif name == 'nt' or name == 'dos':
        os.system('cls')
    else:
        print("\n" * 30)


def make_frame(swarm, mode):
    # *-* EXTRA *-* #
    ''' Create a snapshot of swarm particle positions '''
    x = [par.position[0] for par in swarm.particles]
    y = [par.position[1] for par in swarm.particles]
    frame = [x, y, mode]
    frames.append(frame)


def init():
    ax.set_xlim(-2, 3)
    ax.set_ylim(-2, 2)
    return ln,


def update(counter):
    x = frames[counter][0]
    y = frames[counter][1]
    plt.title(frames[counter][2])
    ln.set_data(x, y)
    return ln,


def scaffold(iters, mode):
    '''
    Scaffold printing file and animations. Runs the main MPSO loop.
    '''
    with open(FILE_NAME, 'a') as f:
        print('\n############### ' + mode.upper() + ' ###############\n', file=f)
    MPSO(iters, mode)
    exit(0)

    # TODO
    anis.append((mode, animation.FuncAnimation(fig, update, init_func=init,
                                               interval=60, repeat=False)))
    frames = []


def main():
    clear()
    # clear result file
    open('MPSO_result.dat', 'w').close()
    modes = ['scheme_1', 'scheme_3a']

    for mode in modes:
        scaffold(2000, mode)
    exit(0)

    # TODO
    # save animations for all schemes
    for ani in anis:
        ani[1].save('MPSO_' + ani[0] + '.mp4')

##############################################################################

if __name__ == "__main__":
    main()
