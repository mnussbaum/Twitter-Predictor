#!/usr/bin/env python

# Network analysis on communities of twitter users!

import sys

class CommunityNet(object):
    '''A matrix of connections within a community of twitter users,
    and associated statistics.'''

    def __init__(self, source_pop, max_n=10, verbose=False, rho=.01):
        self.pop = source_pop._community_members
        self.max_n = max_n
        self.verbose = verbose
        # rho is the rate of remention: if someone you follow brings up a topic,
        # the probability that you'll bring it up, too.
        self.rho = rho
        self.uids = [member['uid'] for member in self.pop]
        self.size = len(self.uids)
        self.follower_dict = {}
        self.follower_matrix = {}
        # ith entry is follower matrix ^ i+1
        self.power_matrices = []
        # the summed power matrices, each multiplied by rho ^ i
        self.rho_matrix = {}

        self.build_follower_dict()
        self.build_follower_matrix()
        self.build_power_matrices()
        self.build_rho_matrix()

    def build_follower_dict(self):
        for member in self.pop:
            self.follower_dict[member['uid']] = member['follower_ids']

    def build_follower_matrix(self):
        '''matrix[i][j] is 1 if user j follows user i, otherwise 0.'''
        for i in self.uids:
            self.follower_matrix[i] = {}
            for j in self.uids:
                if j in self.follower_dict[i]:
                    self.follower_matrix[i][j] = 1
                else:
                    self.follower_matrix[i][j] = 0

    def matrix_product(self, left, right):
        '''multiplies square matrices of the same size represented as
        dictionaries of dictionaries, keys being the entries in self.uids'''
        new = {}
        for i in self.uids:
            new[i] = {}
            for j in self.uids:
                accum = 0
                for k in self.uids:
                    accum += left[i][k] * right[k][j]
                new[i][j] = accum
        return new

    def vm_product(self, v, m):
        '''multiplies a vector represented as a dictionary by a matrix
        represented as a dictionary of dictionaries to produce another vector;
        in all cases keys being the entries in self.uids'''
        exposures = {}
        for follower in self.uids:
            exposure = 0
            for poster in self.uids:
                posts = v[poster]
                weight = m[poster][follower]
                exposure += weight * posts
            exposures[follower] = exposure
        return exposures

    def build_power_matrices(self):
        if self.verbose == True:
            sys.stdout.write("building power matrices...")
            sys.stdout.flush()
        prev = self.follower_matrix
        for i in range(self.max_n):
            if self.verbose == True:
                sys.stdout.write(" %d" % i)
                sys.stdout.flush()
            self.power_matrices.append(prev)
            prev = self.matrix_product(prev, self.follower_matrix)
        if self.verbose == True:
            print ""

    def build_rho_matrix(self):
        if self.verbose == True:
            sys.stdout.write("building rho matrix...")
            sys.stdout.flush()
        for p in self.uids:
            self.rho_matrix[p] = {}
            for f in self.uids:
                self.rho_matrix[p][f] = 0
        for i in range(len(self.power_matrices)):
            if self.verbose == True:
                sys.stdout.write(" %d" % i)
                sys.stdout.flush()
            m = self.power_matrices[i]
            for p in self.uids:
                for f in self.uids:
                    self.rho_matrix[p][f] += m[p][f] * (self.rho ** i)
        if self.verbose == True:
            print ""
