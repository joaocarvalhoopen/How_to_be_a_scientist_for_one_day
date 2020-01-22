# File name:    arctan_v002.py
#
# Project name: How to be a scientist for one day.
#
# Author: Joao Nuno Carvalho (Heavily modified the example file of DEAP)
#
# Objective of this project: Is to find a better approximation solution
#                            to the ArcTan(x/y) that was given by Prof.
#                            Richard G. Lyons in a DSP article. This
#                            approximation is routinely used in DSP
#                            systems as a building block, because ArcTan(x/y)
#                            is a computationally heavy function to calculate,
#                            using the Taylor series expantion. And the fact
#                            in DSP normally there is a need to perform a hugh
#                            number os this calculation in each instant,
#                            normally in real time.
#                            For details, see the full description of the
#                            project at the project page in github:
#                            https://github.com/joaocarvalhoopen/How_to_be_a_scientist_for_one_day   
#                            
# The code is based on: The starting point of this code was the the example
#                       of symbolic regression of the Genetic Programming
#                       framework DEAP. (https://deap.readthedocs.io/en/master/) 
#
# Modification to the code: I modified heaveally the code to adapt it to solve
#                           my problem and with it I have found some interesting
#                           results. With it I have rediscovered Prof. Richard 
#                           G. Lyons approximation formula, proving that the
#                           code works correctly. Note this code isn't the most
#                           clean code that it could be, because it was the 
#                           the playground to make all the experiments for this
#                           project and I wanted to let that pass through the
#                           code in this file. 
#
# License: GNU Lesser General Public License along with EAP.
#
# Note: The following the code file original License. 
#
#    This file is part of EAP.
#
#    EAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    EAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with EAP. If not, see <http://www.gnu.org/licenses/>.

import operator
import math
import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

# matplotlib
import matplotlib.pyplot as plt


# Define new functions
def protectedDiv(left, right):
    with numpy.errstate(divide='ignore',invalid='ignore'):
        x = numpy.divide(left, right)
        if isinstance(x, numpy.ndarray):
            x[numpy.isinf(x)] = 1
            x[numpy.isnan(x)] = 1
        elif numpy.isinf(x) or numpy.isnan(x):
            x = 1
    return x

# This are binary shift constants
bin_shift_array = numpy.zeros(25)
bin_shift_array[0]  = 1
bin_shift_array[1]  = 2
bin_shift_array[2]  = 4
bin_shift_array[3]  = 8
bin_shift_array[4]  = 16
bin_shift_array[5]  = 32
bin_shift_array[6]  = 64
bin_shift_array[7]  = 128
bin_shift_array[8]  = 256
bin_shift_array[9]  = 512
bin_shift_array[10] = 1024
bin_shift_array[11] = 2048
bin_shift_array[12] = 4096
bin_shift_array[13] = 1/2
bin_shift_array[14] = 1/4
bin_shift_array[15] = 1/8
bin_shift_array[16] = 1/16
bin_shift_array[17] = 1/32
bin_shift_array[18] = 1/64
bin_shift_array[19] = 1/128
bin_shift_array[20] = 1/256
bin_shift_array[21] = 1/512
bin_shift_array[22] = 1/1024
bin_shift_array[23] = 1/2048
bin_shift_array[24] = 1/4096



def ephemeral_shift_constant():
    index = random.randint(0,24)
    return bin_shift_array[index]

pset = gp.PrimitiveSet("MAIN", 2)  # 1
pset.addPrimitive(numpy.add, 2, name="vadd")
pset.addPrimitive(numpy.subtract, 2, name="vsub")
pset.addPrimitive(numpy.multiply, 2, name="vmul")
#pset.addPrimitive(protectedDiv, 2)

pset.addPrimitive(numpy.divide, 2)
pset.addPrimitive(numpy.negative, 1, name="vneg")
#pset.addPrimitive(numpy.cos, 1, name="vcos")
#pset.addPrimitive(numpy.sin, 1, name="vsin")

# pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))
pset.addEphemeralConstant("rand101", ephemeral_shift_constant)

pset.renameArguments(ARG0='x')
pset.renameArguments(ARG1='z')

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)


#samples_x = numpy.linspace(-1, 1, 10000)  # Numerator
#samples_z = numpy.linspace(-1, 1, 10000)  # Denominator

number_of_samples = 20000   # 10000

samples_x = numpy.linspace(-1000, 1000, number_of_samples)  # Numerator
samples_z = numpy.linspace(-1000, 1000, number_of_samples)  # Denominator


numpy.random.shuffle(samples_x)
numpy.random.shuffle(samples_z)

# Invalid substitution method (out of range in the division).
tmp = samples_x / samples_z
tmp_arcTan_angle = numpy.zeros(number_of_samples)
numpy.arctan2( samples_x, samples_z, tmp_arcTan_angle)

#for i in range(10):
#    tmp_arcTan_angle_val = math.atan2(samples_x[i], samples_z[i])
#    print(tmp_arcTan_angle[i], '    ', tmp_arcTan_angle_val)


pi_div_4 = math.pi / 4.0
for i in range(len(samples_x)):
    if ((tmp_arcTan_angle[i] < -pi_div_4 ) or (tmp_arcTan_angle[i] > pi_div_4 ) or (tmp[i] == numpy.nan) or (tmp[i] < -10) or (tmp[i] >= 10) or (samples_z[i] == 0)):

        val_x = random.randint(-10000,10000)
        val_z = random.randint(-10000,10000)
        if val_z != 0:
            res = (val_x / val_z)
        tmp_arcTan_angle_val = math.atan2(val_x, val_z)
        while( (tmp_arcTan_angle_val < -pi_div_4 ) or (tmp_arcTan_angle_val > pi_div_4 ) or (res == math.nan) or (res < -10) or (res >= 10) or (val_x == 0) or (val_z == 0) ):
            val_x = random.randint(-10000,10000)
            val_z = random.randint(-10000,10000)
            if val_z != 0:
                res = (val_x / val_z)
            tmp_arcTan_angle_val = math.atan2(val_x, val_z)
        samples_x[i] = val_x
        samples_z[i] = val_z

values = numpy.zeros(number_of_samples)
numpy.arctan2( samples_x, samples_z, values )

lyons_res = (samples_x / samples_z ) / ( 1 + 0.28125*((samples_x / samples_z )**2))

def lyons_fitness():
    return numpy.sum((lyons_res - values)**2)

def evalSymbReg(individual):
    # Transform the tree expression in a callable function
    func = toolbox.compile(expr=individual)
    # Evaluate the sum of squared difference between the expression
    # and the real function values : x**4 + x**3 + x**2 + x
    diff = numpy.sum((func(samples_x, samples_z) - values)**2)

    nodes, edges, labels = gp.graph(individual)
    if len(nodes) > 16:  # 18
        diff += 100000000000000.0
    return diff,

toolbox.register("evaluate", evalSymbReg)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register('mutate', gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

def main(num_individuals):
    #random.seed(322)

    pop = toolbox.population(n=num_individuals)  # 100000  #1000  # 300
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 40, stats, halloffame=hof)

    bests = tools.selBest(pop, k=1)
    print(bests[0])
    best_fit = bests[0].fitness
    print('Best fitness:', best_fit)

    lyons_fit = lyons_fitness()
    print('Lyons fitness: ', lyons_fit)
    str_best_fit = str(best_fit).replace('(', '').replace(')', '').replace(',', '')

    nodes, edges, labels = gp.graph(bests[0])
    print(len(nodes))

    # DEBUG
    #str_best_fit = 0.0

    if (lyons_fit >= ( float( str_best_fit ) - 0.001 ) ):
        print('We have found a candidate equation! ########################################')
        # Write to file (append):
        with open("Output_better_then_lyons.txt", "a") as text_file:
            text_file.write("\r\n\r\n%s \r\n Best fitness: %s \r\nLyons fitness: %s\r\nnodes: %s\r\n" % (str(bests[0]), str(best_fit), str(lyons_fit), str(len(nodes)) ))

    return pop, stats, hof


def test_run():
    x = samples_x
    z = samples_z



    # result = ( 4.0 + x ) / ( z  + (x / 4.0))

    #true_divide(vadd(4.0, x), vadd(z, true_divide(x, 4.0)))
    #Best fitness: (1.4595810721607618,)
    #Lyons fitness:  0.0769056541189


    result = ( x ) / ( (x / (4.0 + 0.25) ) + z )
    # true_divide(x, vadd(true_divide(x, vadd(4.0, 0.25)), z))
    # Best fitness: (1.2801246595251405,)
    # Lyons fitness:  0.0754782247326


    # Run with just 1000 test cases, the other have 10000 test cases, so the error is smaller.
    #vadd(0.0078125, true_divide(x, vadd(vmul(0.25, x), z)))
    #Best fitness:  (0.076155992679634049,)
    #Lyons fitness:  0.00802796769858

    result = ( x / ( z + ( x / 4.0) ))  - ( - 0.0078125)
    # Run com 250.000 individuals 10.000 cases 10 nodes in the tree
    #vsub(true_divide(x, vadd(z, true_divide(x, 4.0))), vneg(0.0078125))
    #Best fitness: (0.77890987941412915,)
    #Lyons fitness:  0.0756549044525


    # Run 10.000 individuals 10.000 cases 14 nodes in the tree
    #true_divide(x, vadd(true_divide(x, vmul(true_divide(2.0, x), vadd(z, x))), z))
    #Best fitness: (0.20510689925496772,)
    #Lyons fitness:  0.0763884847339

    # Run 100.000 individuals 10.000 cases 14 nodes in the tree
    #true_divide(x, vadd(z, true_divide(x, true_divide(vadd(z, x), vmul(0.5, x)))))
    #Best fitness: (0.21019978704468312,)
    #Lyons fitness:  0.0770276610918
    #13 nos


    result =  x / ( (  ( ( 0.03125 + 0.25 ) * x) /  (z / x)   )  +  z )
    result =  x / ( (  ( 0.28125 * x) /  (z / x)   )  +  z )

    # Fantastic I rediscovered the Prof. Lyons approximation formula.
    # Run 100.000 individuals 10.000 cases 14 nodes in the tree (    random.seed(320) )
    #true_divide(x, vadd(true_divide(vmul(vadd(0.03125, 0.25), x), true_divide(z, x)), z))
    #Best fitness: (0.077318096009023896,)
    #Lyons fitness:  0.077318096009
    #13

    result = (4*x* z) / (x*x + 0.125*x*z + 4*z*z)

    # More precise then the approximation of Prof. Lyons but a little bit more complex.
    # x / ( ( (0.25 * x) / (z / ( x + 0.125*z)) ) + z)

    # true_divide(x, vadd(true_divide(vmul(x, 0.25), true_divide(z, vadd(x, vmul(0.125, z)))), z))
    # Best fitness: (0.013625947480946707,)    (erro)
    # Lyons fitness: 0.0744682331229                (erro)

    result_2 = x / ( (x *x) / ( (z + z) + z) + z)


    result = x / (  ( (x*x) / ( ( z - (z * 0.125) ) * 4.0) )  + z )

    #true_divide(x, vadd(true_divide(vmul(x, x), vmul(vsub(z, vmul(z, 0.125)), 4.0)), z))
    #Best fitness: (0.12785344960848949,)
    #Lyons fitness:  0.149809677989
    #15

    result_fit = numpy.sum((result - values)**2)

    lyons_res = (samples_x / samples_z ) / ( 1 + 0.28125*((samples_x / samples_z )**2))
    lyons_fitness_calc =  numpy.sum((lyons_res - values)**2)

    print('result_fit: ', result_fit)
    print('lyons_fit: ', lyons_fitness_calc)

    list = []
    for i in range(len(samples_x)):
        angle = values[i]
        val_x = samples_x[i]
        val_y = samples_z[i]
        res = result[i]
        diff = math.fabs(angle - res)
        res_lyons  = lyons_res[i]
        diff_lyons = math.fabs(angle - res_lyons)
        list.append( (angle, res, diff, res_lyons, diff_lyons, val_x, val_y ) )

    def getKey(item):
        return item[0]
    sorted(list, key=getKey)

    print(list[0])
    print(list[79])

    list_tmp = []
    list_tmp_lyons = []
    for i in list:
        list_tmp.append(i[2])
        list_tmp_lyons.append(i[4])

    plt.plot(list_tmp)
    plt.show()

    plt.plot(list_tmp_lyons)
    plt.show()

    # ArcTan graphic plot.
    #x = numpy.linspace(0, 5, 100)  # Numerator
    x = numpy.linspace(-5, 5, 100)  # Numerator
    z = 2
    result_real_arctan = numpy.zeros(100)

    #result = ( 4.0 + x ) / ( z  + (x / 4.0))
    #result = ( x ) / ( (x / (4.0 + 0.25) ) + z )
    #result = ( x / ( z + ( x / 4.0) ))  - ( - 0.0078125)

    # This was a very good model but only is good  from 0 to 45 degrees not very good from -45 to 0.
    #result = (4*x*z) / (x*x + 0.125*x*z + 4*z*z)

    #result = x / ( (x *x) / ( (z + z) + z) + z)

    result = x / (  ( (x*x) / ( ( z - (z * 0.125) ) * 4.0) )  + z )

    plt.plot(result)

    numpy.arctan2(x, z, result_real_arctan)
    plt.plot(result_real_arctan)

    lyons_res = (x / z ) / ( 1 + 0.28125*((x / z )**2))
    plt.plot(lyons_res)


    plt.legend(['Under_testy', 'y = arctan2(x/z)', 'y = Lyons(x/z)'], loc='upper left')
    plt.show()



if __name__ == "__main__":
    #main()

    num_individuals = 100000 # 100000
    seed = 526
    while(True):
        random.seed(seed)
        seed += 1
        main(num_individuals)


    #test_run()
