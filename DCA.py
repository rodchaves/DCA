# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 15:20:19 2022

@author: Rodrigo Chaves
"""

import pennylane as qml
from pennylane import numpy as np
import seaborn as sns 
import sys
import pandas as pd

"""
    Implemenatation of a simulation of a Dirac cellular automaton (DCA) using discrete-time quantum walks with 
different theta parameters for the coin. This algorithm is based on the work of Alderet et al. that can be found at
https://arxiv.org/pdf/2002.02537.pdf.

The idea behind is to implement a discrete-time quantum walk with two different coins and shift operators. The theta
values of the coins correspond to particles with different masses. The algorithm takes the value of two thetas as inputs 
and creates a pdf file with the probabilities of five steps of the quantum walk for a path graph with 15 vertices.

"""

"""
    Function that implemantes each step of the quantum walk. Notice that the gates used are dependent on how each vertex
is associated to each computational basis.
    
"""
def OddStep(theta1):
    qml.RX(2*theta1, wires = 0)
    qml.PauliX(wires = 0)
    qml.CNOT(wires = [0,3])
    qml.ctrl(qml.CNOT, control = [2,3])(wires = [0,1])
    qml.Toffoli(wires = [0,3,2])
    qml.PauliX(wires = 0)
    qml.PauliX(wires = 4)
    
def EvenStep(theta2):
    qml.RX(2*theta2, wires = 0)
    qml.Toffoli(wires = [0,3,2])
    qml.ctrl(qml.CNOT, control = [2,3])(wires = [0,1])
    qml.CNOT(wires = [0,3])
    qml.PauliX(wires = 4)
    
"""
   Function that creates the quantum circuit and measure the probabilities of each computational basis. It takes
the number of steps and the values of thetas in the coint and returns an array with each entry corresponding to the
probability of each computational basis. Therefore, the state |0000> is associated to the first entry of the array,
|0001> to the second entry, and so on. 

"""
dev = qml.device('default.qubit', wires = 5)

@qml.qnode(dev)
def Circuit(theta1, theta2, steps):
    
    qml.RX(-np.pi/2, wires = 0)
    
    if steps > 0:
       for step in range(steps):
            if (step+1)%2 == 0:
                EvenStep(theta2)
            else:
                OddStep(theta1)
    
    return qml.probs(wires=[1,2,3,4])        
    
"""
    Function that have as input the array with probabilities returned from the quantum circuit. It returns an array of
probabilities with each entry corresponding to the vertex of the path graph. Therefore, the first entry will be 
associated to find the walker on vertex -7, the second entry to the probability of finding the walker on vertex -6, and 
so on.

"""
def OrderStates(probs):
    ordered_probs = np.zeros(15)
    for i in range(len(probs)):
        if i < 4:
            ordered_probs[i+7] = probs[i]
        elif 4 <= i < 8 or 12 <= i < 15:
            ordered_probs[i-1] = probs[i]
        elif 8 < i < 12:
            ordered_probs[i-9] = probs[i]
    return ordered_probs

"""
    Function that have theta1 and theta2 as inputs and create a pdf with the heatmap corresponding to the probabilities
of fingind the walker on each vertex.

"""

def Output(theta1, theta2):
    result = {}
    for step in range(6):
        probs = Circuit(theta1, theta2, step)
        result[step] = OrderStates(probs)
    
    new_index = np.arange(-7,8)
    df = pd.DataFrame(data = result, index = new_index)
    df = df.transpose()
    
    ax = sns.heatmap(df)
    figure = ax.get_figure()
    figure.savefig('figure.pdf')
    
    return True

"""
    Function that recieve the inputs as entries as strings and return as flots.

"""
def CheckEntries(inputs):
    constants={'0': 0, 'pi/4': np.pi/4, 'pi/10': np.pi/10, 'pi/20': np.pi/20}
    for i in range(len(inputs)):
        if inputs[i] in constants.keys():
            inputs[i] = constants[inputs[i]]
    
    return inputs

if __name__ == '__main__':
    inputs = sys.stdin.read().split(",")
    inputs = CheckEntries(inputs)
    output = Output(inputs[0], inputs[1])
    print('Figure created')