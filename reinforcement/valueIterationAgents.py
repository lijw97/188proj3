# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        counter = 0
        while counter < self.iterations:
            tempcount = util.Counter()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue
                else:
                    q_values = []
                    #print("here!")
                    for action in self.mdp.getPossibleActions(state):
                        x = self.computeQValueFromValues(state, action)
                        #print(x)
                        q_values.append(x)
                    tempcount[state] = max(q_values)
            self.values = tempcount
            counter += 1




    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return 0
        transitions = self.mdp.getTransitionStatesAndProbs(state, action)
        value = 0
        for transition in transitions:
            value = value + (transition[1]) * (self.mdp.getReward(state, action, transition[0]) + (self.discount * self.values[transition[0]]))

        return value
        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"

        if self.mdp.isTerminal(state):
            return None
        else:
            actions = self.mdp.getPossibleActions(state)
            q_values = []
            for action in actions:
                q_values.append(self.computeQValueFromValues(state, action))
            return actions[q_values.index(max(q_values))]
        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        counter = 0
        index = 0
        num_states = len(self.mdp.getStates())
        states = self.mdp.getStates()
        while counter < self.iterations:
            if index == num_states:
                index = 0
            state = states[index]
            if self.mdp.isTerminal(state):
                index += 1
                counter += 1
                continue
            else:
                index += 1
                q_values = []
                #print("here!")
                for action in self.mdp.getPossibleActions(state):
                    x = self.computeQValueFromValues(state, action)
                    #print(x)
                    q_values.append(x)
                self.values[state] = max(q_values)
                counter += 1


class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"

        predecessors = {}
        queue = util.PriorityQueue()
        for state in self.mdp.getStates():
            predecessors[state] = set()
        for state in self.mdp.getStates():
            for action in self.mdp.getPossibleActions(state):
                transitions = self.mdp.getTransitionStatesAndProbs(state, action)
                for transition in transitions:
                    successorstate = transition[0]
                    predecessors[successorstate].add(state)
        for state in self.mdp.getStates():
            if not (self.mdp.isTerminal(state)):
                q_values = []
                for action in self.mdp.getPossibleActions(state):
                    q_values.append(self.computeQValueFromValues(state, action))
                max_q = max(q_values)
                queue.push(state, -1*abs(max_q - self.values[state]))

        for i in range(0, self.iterations):
            if len(queue.heap) == 0:
                return None
            curr_state = queue.pop()

            q_values = []
            #print(queue.count)
            for action in self.mdp.getPossibleActions(curr_state):
                q_values.append(self.computeQValueFromValues(curr_state, action))
            max_q = max(q_values)
            if not self.mdp.isTerminal(curr_state):
                self.values[curr_state] = max_q
            for predecessor_state in predecessors[curr_state]:
                q_values = []
                for action in self.mdp.getPossibleActions(predecessor_state):
                    q_values.append(self.computeQValueFromValues(predecessor_state, action))
                max_q = max(q_values)
                diff = abs(max_q - self.values[predecessor_state])
                if diff > self.theta:
                    queue.update(predecessor_state, -1*diff)
