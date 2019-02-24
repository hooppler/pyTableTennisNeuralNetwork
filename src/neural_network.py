"""
Copyright 2019, Aleksandar Stojimirovic <stojimirovic@yahoo.com>

Licence: MIT
Source: https://github.com/hooppler/pyTableTennisNeuralNetwork
"""

from math import *
import random


class NeuralNetwork(object):
    def __init__(self):
        self.N = 3
        self.n = [3, 150, 1]
        
        self.y = []
        sum = 0
        for s in range(0, self.N):
            sum += self.n[s] + 1
        for i in range(0, sum):
            self.y.append(1.0)
            
        self.delta = []
        for i in range(0, sum):
            self.delta.append(0.0)
        
        self.w = []
        sum = 0
        for s in range(1, self.N):
            sum += (self.n[s-1]+1)*(self.n[s]+1)
        for i in range(0, sum):
            self.w.append(0.0)
        self.etha = 0.2;


    def _iNtok(self, i, N):
        sum = 0
        for s in range(0, N):
            sum += self.n[s] + 1
        k = sum + i
        return k
        
    def _ijNtok(self,i,j,N):
        sum = 0
        for s in range(1,N):
            sum += (self.n[s-1]+1)*(self.n[s]+1)
        k = sum + j * (self.n[N-1]+1) + i
        return k
        
    def get_input(self):
        input = []
        for i in range(1, self.n[0]+1):
            input.append(self.y[self._iNtok(i,0)])
        return input
        
    def set_input(self, input):
        for i in range(1, self.n[0]+1):
            self.y[self._iNtok(i,0)] = input[i-1]
            
    def get_output(self):
        output = []
        for i in range(1, self.n[self.N-1]+1):
            output.append(self.y[self._iNtok(i,self.N-1)])
        return output
        
    def get_t_input(self, k):
        t_input = []
        for i in range(0, self.n[0]):
            t_input.append(self.t[ k*(self.n[0]+self.n[self.N-1]) + i])
        return t_input
        
    def get_t_output(self, k):
        t_output = []
        for i in range(0, self.n[self.N-1]):
            t_output.append(self.t[self.n[0] + k * (self.n[0]+self.n[self.N-1]) + i])
        return t_output
        
    def sigmoid(self, x):
        return 1/(1+exp(-x))

        
    def dsigmoid(self, x):
        return self.sigmoid(x) * (1-self.sigmoid(x))
        
    def net(self, j, N):
        sum = 0
        for i in range(0, self.n[N-1]+1):
            sum += self.w[self._ijNtok(i,j,N)] * self.y[self._iNtok(i,N-1)]
        return sum
        
    def net_delta(self, i, N):
        sum = 0
        for j in range(1, self.n[N+1]+1):
            sum += self.w[self._ijNtok(i,j,N+1)] * self.delta[self._iNtok(j,N+1)]
        return sum
        
    def feed_forward(self):
        for s in range(1, self.N):
            for j in range(1, self.n[s]+1):
                self.y[self._iNtok(j,s)] = self.sigmoid(self.net(j,s))
                
    def set_delta_output(self, t_output):
        for i in range(1, self.n[self.N-1]+1):
            self.delta[self._iNtok(i,self.N-1)] = self.dsigmoid(self.net(i,self.N-1)) * (self.y[self._iNtok(i,self.N-1)] - t_output[i-1])
            
    def back_propagation(self):
        for s in range(self.N-2, 0, -1):
            for i in range(1, self.n[s]+1):
                self.delta[self._iNtok(i,s)] = self.dsigmoid(self.net(i,s)) * self.net_delta(i,s)
            
    def set_random_w(self):
        for s in range(1, self.N):
            for j in range(1, self.n[s]+1):
                for i in range(0, self.n[s-1]+1):
                    self.w[self._ijNtok(i,j,s)] = random.uniform(-1, 1)
                    #print(self.w[self._ijNtok(i,j,s)])
                    
    def adjust_w(self):
        for s in range(1, self.N):
            for j in range(1, self.n[s]+1):
                for i in range(0, self.n[s-1]+1):
                    self.w[self._ijNtok(i,j,s)] += - self.etha * self.delta[self._iNtok(j,s)] * self.y[self._iNtok(i,s-1)]
                    #print(self.w[self._ijNtok(i,j,s)])
    
    def train(self, epochs):
        for s in range(0, epochs):
            for k in range(0, self.t_n):
                t_input = self.get_t_input(k)
                t_output = self.get_t_output(k)
                
                self.set_input(t_input)
                self.feed_forward()
                self.set_delta_output(t_output)
                self.back_propagation()
                self.adjust_w()
