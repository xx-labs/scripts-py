# This file is taken from Sequential Phragmen reference
# implementation by WEB3 Foundation
# https://github.com/w3f/consensus/blob/master/NPoS/npos.py
# Small modifications were made

import logging as log

#################################
# Class definitions
#################################
class edge:
    def __init__(self, nominator_id, validator_id):
        self.nominator_id = nominator_id
        self.validator_id = validator_id
        self.load = 0
        self.weight = 0
        self.candidate = None

    def __str__(self):
        return "Edge({}, weight = {:,})".format(
            self.validator_id,
            self.weight,
        )


class nominator:
    def __init__(self, nominator_id, budget, targets):
        self.nominator_id = nominator_id
        self.budget = budget
        self.edges = [edge(self.nominator_id, validator_id) for validator_id in targets]
        self.load = 0

    def __str__(self):
        return "Nominator({}, budget = {:,}, load = {}, edges = {})".format(
            self.nominator_id,
            self.budget,
            self.load,
            [str(e) for e in self.edges]
        )


class candidate:
    def __init__(self, validator_id, index):
        self.validator_id = validator_id
        self.valindex = index
        self.approval_stake = 0
        self.backed_stake = 0
        self.elected = False
        self.score = 0
        self.backers = 0

    def __str__(self):
        return "Candidate({}, approval = {:,}, backed_stake = {:,})".format(
            self.validator_id,
            self.approval_stake,
            int(self.backed_stake),
        )

#################################
# Helper methods
#################################
def calculate_approval(nomlist):
    for nom in nomlist:
        for edge in nom.edges:
            edge.candidate.approval_stake += nom.budget
            edge.candidate.backers += 1


def setuplists(votelist):
    '''
    Basically populates edge.candidate, and returns nomlist and candidate array. The former is a
    flat list of nominators and the latter is a flat list of validator candidates.

    Instead of Python's dict here, you can use anything with O(log n) addition and lookup. We can
    also use a hashmap like dict, by generating a random constant r and useing H(canid+r) since the
    naive thing is obviously attackable.
    '''
    nomlist = [nominator(votetuple[0], votetuple[1], votetuple[2]) for votetuple in votelist]
    # Basically used as a cache.
    candidate_dict = dict()
    candidate_array = list()
    num_candidates = 0
    # Get an array of candidates.# We could reference these by index rather than pointer
    for nom in nomlist:
        for edge in nom.edges:
            validator_id = edge.validator_id
            if validator_id in candidate_dict:
                index = candidate_dict[validator_id]
                edge.candidate = candidate_array[index]
            else:
                candidate_dict[validator_id] = num_candidates
                newcandidate = candidate(validator_id, num_candidates)
                candidate_array.append(newcandidate)

                edge.candidate = newcandidate
                num_candidates += 1
    return nomlist, candidate_array


def printresult(nomlist, candidates):
    for candidate in candidates:
        if candidate.elected:
            log.info(f"{candidate.validator_id} is elected with stake {candidate.backed_stake / 1e9}, and score {candidate.score}")
        else:
            log.info(f"{candidate.validator_id} is NOT elected, with stake of {candidate.backed_stake / 1e9}")
    for nom in nomlist:
        log.debug(f"{nom.nominator_id} has load {nom.load} and supported ")
        for edge in nom.edges:
            log.debug(f"{edge.validator_id} with stake {edge.weight / 1e9}, ")
        log.debug("")
    log.debug("")


#################################
# Sequential Phragmen Core
#################################
def seq_phragmen_core(votelist, num_to_elect):
    nomlist, candidates = setuplists(votelist)
    calculate_approval(nomlist)

    # main election loop
    for _ in range(num_to_elect):
        # loop 1: initialize score
        for candidate in candidates:
            if not candidate.elected:
                if candidate.approval_stake > 0:
                    candidate.score = 1 / candidate.approval_stake
                else:
                    candidate.score = 1000
        # loop 2: increment score
        for nom in nomlist:
            for edge in nom.edges:
                if not edge.candidate.elected and edge.candidate.approval_stake > 0:
                    edge.candidate.score += nom.budget * nom.load / edge.candidate.approval_stake
        best_candidate = 0
        best_score = 1000  # should be infinite but I'm lazy
        # loop 3: find winner
        for candidate in candidates:
            if not candidate.elected and candidate.score < best_score:
                best_score = candidate.score
                best_candidate = candidate.valindex
        candidates[best_candidate].elected = True
        # loop 3: update voter and edge load
        for nom in nomlist:
            for edge in nom.edges:
                if edge.candidate.valindex == best_candidate:
                    edge.load = candidates[best_candidate].score - nom.load
                    nom.load = candidates[best_candidate].score

    # update backing stake of candidates and voters
    for nom in nomlist:
        for edge in nom.edges:
            if edge.candidate.elected:
                edge.weight = nom.budget * edge.load/nom.load
            else:
                edge.weight = 0
            edge.candidate.backed_stake += edge.weight
        nom.edges = list(filter(lambda edge: edge.weight > 0, nom.edges))
    
    # populate backing stake of non elected
    for candidate in candidates:
        if not candidate.elected:
            candidate.backed_stake = 1 / candidate.score
    return (nomlist, candidates)


#################################
# Equalisation of elected stake
#################################
def equalise(nom, tolerance):
    # Attempts to redistribute the nominators budget between elected validators. Assumes that all
    # elected validators have backed_stake set correctly. Returns the max difference in stakes
    # between sup.

    elected_edges = [edge for edge in nom.edges if edge.candidate.elected]

    if len(elected_edges) < 2:
        return 0.0

    stake_used = sum([edge.weight for edge in elected_edges])
    backed_stakes = [edge.candidate.backed_stake for edge in elected_edges]
    backingbacked_stakes = [
        edge.candidate.backed_stake for edge in elected_edges if edge.weight > 0.0
    ]

    if len(backingbacked_stakes) > 0:
        difference = max(backingbacked_stakes)-min(backed_stakes)
        difference += nom.budget - stake_used
        if difference < tolerance:
            return difference
    else:
        difference = nom.budget

    # remove all backing
    for edge in nom.edges:
        edge.candidate.backed_stake -= edge.weight
        edge.weight = 0

    elected_edges.sort(key=lambda x: x.candidate.backed_stake)
    cumulative_backed_stake = 0
    last_index = len(elected_edges) - 1

    for i in range(len(elected_edges)):
        backed_stake = elected_edges[i].candidate.backed_stake
        if backed_stake * i - cumulative_backed_stake > nom.budget:
            last_index = i-1
            break
        cumulative_backed_stake += backed_stake

    last_stake = elected_edges[last_index].candidate.backed_stake
    ways_to_split = last_index+1
    excess = nom.budget + cumulative_backed_stake - last_stake*ways_to_split

    for edge in elected_edges[0:ways_to_split]:
        edge.weight = excess / ways_to_split + last_stake - edge.candidate.backed_stake
        edge.candidate.backed_stake += edge.weight

    return difference


def equalise_all(nomlist, maxiterations, tolerance):
    for _ in range(maxiterations):
        maxdifference = 0
        for nom in nomlist:
            difference = equalise(nom, tolerance)
            maxdifference = max(difference, maxdifference)
        if maxdifference < tolerance:
            return


#################################
# Sequential Phragmen Algorithm
#################################
def seq_phragmen(votelist, num_to_elect):
    nomlist, candidates = seq_phragmen_core(votelist, num_to_elect)
    equalise_all(nomlist, 10, 0)
    return nomlist, sorted(candidates, key=lambda item: item.backed_stake, reverse=True)


def compute_score(candidates):
    min_support = min([c.backed_stake if c.elected else 1e18 for c in candidates])
    sum_support = sum([c.backed_stake if c.elected else 0 for c in candidates])
    sum_squared = sum([c.backed_stake*c.backed_stake if c.elected else 0 for c in candidates])
    return [int(min_support), int(sum_support), int(sum_squared)]
