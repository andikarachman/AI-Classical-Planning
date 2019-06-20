
from itertools import chain, combinations
from aimacode.planning import Action
from aimacode.utils import expr

from layers import BaseActionLayer, BaseLiteralLayer, makeNoOp, make_node


class ActionLayer(BaseActionLayer):

    def _inconsistent_effects(self, actionA, actionB):
        """ Return True if an effect of one action negates an effect of the other

        See Also
        --------
        layers.ActionNode
        """
    
        actionA_eff = actionA.effects
        actionB_eff = actionB.effects
        for effA in actionA_eff:
            if effA.__invert__() in actionB_eff:
                return True
        return False


    def _interference(self, actionA, actionB):
        """ Return True if the effects of either action negate the preconditions of the other 
        
        See Also
        --------
        layers.ActionNode
        """
    
        actionA_eff = actionA.effects
        actionB_eff = actionB.effects
        actionA_precond = actionA.preconditions
        actionB_precond = actionB.preconditions
        for effA in actionA_eff:
            if effA.__invert__() in actionB_precond:
                return True
        for effB in actionB_eff:
            if effB.__invert__() in actionA_precond:
                return True        
        return False

    def _competing_needs(self, actionA, actionB):
        """ Return True if the preconditions of the actions are all pairwise mutex in the parent layer 
        
        See Also
        --------
        layers.ActionNode
        layers.BaseLayer.parent_layer
        """
        
        actionA_precond = actionA.preconditions
        actionB_precond = actionB.preconditions
        for precondA in actionA_precond:
            for precondB in actionB_precond:
                if (self.parent_layer.is_mutex(precondA, precondB)) or (self.parent_layer.is_mutex(precondB, precondA)):
                    return True
        return False
 
        #python test_my_planning_graph.py


class LiteralLayer(BaseLiteralLayer):

    def _inconsistent_support(self, literalA, literalB):
        """ Return True if all ways to achieve both literals are pairwise mutex in the parent layer

        See Also
        --------
        layers.BaseLayer.parent_layer
        """
        actionsLitA = self.parents[literalA]
        actionsLitB = self.parents[literalB]
        for actA in actionsLitA:
            for actB in actionsLitB:
                if (not self.parent_layer.is_mutex(actA, actB)) or (not self.parent_layer.is_mutex(actB, actA)):
                    return False
        return True

    def _negation(self, literalA, literalB):
        """ Return True if two literals are negations of each other """
        # TODO: implement this function
        if literalA.__invert__() == literalB:
            return True
        return False


class PlanningGraph:
    def __init__(self, problem, state, serialize=True, ignore_mutexes=False):
        """
        Parameters
        ----------
        problem : PlanningProblem
            An instance of the PlanningProblem class

        state : tuple(bool)
            An ordered sequence of True/False values indicating the literal value
            of the corresponding fluent in problem.state_map

        serialize : bool
            Flag indicating whether to serialize non-persistence actions. Actions
            should NOT be serialized for regression search (e.g., GraphPlan), and
            _should_ be serialized if the planning graph is being used to estimate
            a heuristic
        """
        self._serialize = serialize
        self._is_leveled = False
        self._ignore_mutexes = ignore_mutexes
        self.goal = set(problem.goal)

        # make no-op actions that persist every literal to the next layer
        no_ops = [make_node(n, no_op=True) for n in chain(*(makeNoOp(s) for s in problem.state_map))]
        self._actionNodes = no_ops + [make_node(a) for a in problem.actions_list]
        
        # initialize the planning graph by finding the literals that are in the
        # first layer and finding the actions they they should be connected to
        literals = [s if f else ~s for f, s in zip(state, problem.state_map)]
        layer = LiteralLayer(literals, ActionLayer(), self._ignore_mutexes)
        layer.update_mutexes()
        self.literal_layers = [layer]
        self.action_layers = []

    def h_levelsum(self):
        """ Calculate the level sum heuristic for the planning graph

        The level sum is the sum of the level costs of all the goal literals
        combined. The "level cost" to achieve any single goal literal is the
        level at which the literal first appears in the planning graph. Note
        that the level cost is **NOT** the minimum number of actions to
        achieve a single goal literal.
        
        For example, if Goal1 first appears in level 0 of the graph (i.e.,
        it is satisfied at the root of the planning graph) and Goal2 first
        appears in level 3, then the levelsum is 0 + 3 = 3.

        Hint: expand the graph one level at a time and accumulate the level
        cost of each goal.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)
        """
        
        goal = self.goal
        level_sum = 0
        for x in goal:
            iteration = 1
            while iteration:
                self._extend()
                y = self.literal_layers[iteration-1].children[x]
                z = self.literal_layers[iteration-1].parents[x]
                if len(z) or len(y):
                    level_sum += iteration-1
                    iteration = 0
                else:
                    iteration += 1

        return level_sum
    

    def h_maxlevel(self):
        """ Calculate the max level heuristic for the planning graph

        The max level is the largest level cost of any single goal fluent.
        The "level cost" to achieve any single goal literal is the level at
        which the literal first appears in the planning graph. Note that
        the level cost is **NOT** the minimum number of actions to achieve
        a single goal literal.

        For example, if Goal1 first appears in level 1 of the graph and
        Goal2 first appears in level 3, then the levelsum is max(1, 3) = 3.

        Hint: expand the graph one level at a time until all goals are met.

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)

        Notes
        -----
        WARNING: you should expect long runtimes using this heuristic with A*
        """
        
        goal = self.goal
        level_sum = []
        for x in goal:
            iteration = 1
            while iteration:
                self._extend()
                y = self.literal_layers[iteration-1].children[x]
                z = self.literal_layers[iteration-1].parents[x]
                if len(z) or len(y):
                    level_sum.append(iteration-1)
                    iteration = 0
                else:
                    iteration += 1

        return max(level_sum)

    def h_setlevel(self):
        """ Calculate the set level heuristic for the planning graph

        The set level of a planning graph is the first level where all goals
        appear such that no pair of goal literals are mutex in the last
        layer of the planning graph.

        Hint: expand the graph one level at a time until you find the set level

        See Also
        --------
        Russell-Norvig 10.3.1 (3rd Edition)

        Notes
        -----
        WARNING: you should expect long runtimes using this heuristic on complex problems
        """
        
        goal = list(self.goal)
        set_level = []
        iteration = 1
        while iteration:
            self._extend()
            x = [True if ((self.literal_layers[iteration-1].children[g]) or (self.literal_layers[iteration-1].parents[g])) else False for g in goal]
            #goal1_children = self.literal_layers[iteration-1].children[goal[0]] #Check Goal1
            #goal1_parents = self.literal_layers[iteration-1].parents[goal[0]] #Check Goal1
            #goal2_children = self.literal_layers[iteration-1].children[goal[1]] #Check Goal2
            #goal2_parents = self.literal_layers[iteration-1].parents[goal[1]] #Check Goal2
            #if (len(goal1_children) or len(goal1_parents)) and (len(goal2_children) or len(goal2_parents)):
            if all(x):
                y = [True if ((not self.literal_layers[iteration-1].is_mutex(c1, c2)) and (not self.literal_layers[iteration-1].is_mutex(c2, c1))) else False for (c1, c2) in combinations(goal, 2)]

                #for c1, c2 in combinations(goal):
                #if (not self.literal_layers[iteration-1].is_mutex(c1, goal[1])) and (not self.literal_layers[iteration-1].is_mutex(goal[1], goal[0])):
                 #   set_level.append(iteration-1)
                  #  iteration = 0
                if all(y):
                    set_level.append(iteration-1)
                    iteration = 0
                else:
                    iteration += 1
            else:
                iteration += 1
        return set_level[0]

    ##############################################################################
    #                     DO NOT MODIFY CODE BELOW THIS LINE                     #
    ##############################################################################

    def fill(self, maxlevels=-1):
        """ Extend the planning graph until it is leveled, or until a specified number of
        levels have been added

        Parameters
        ----------
        maxlevels : int
            The maximum number of levels to extend before breaking the loop. (Starting with
            a negative value will never interrupt the loop.)

        Notes
        -----
        YOU SHOULD NOT THIS FUNCTION TO COMPLETE THE PROJECT, BUT IT MAY BE USEFUL FOR TESTING
        """
        while not self._is_leveled:
            if maxlevels == 0: break
            self._extend()
            maxlevels -= 1
        return self

    def _extend(self):
        """ Extend the planning graph by adding both a new action layer and a new literal layer

        The new action layer contains all actions that could be taken given the positive AND
        negative literals in the leaf nodes of the parent literal level.

        The new literal layer contains all literals that could result from taking each possible
        action in the NEW action layer. 
        """
        if self._is_leveled: return

        parent_literals = self.literal_layers[-1]
        parent_actions = parent_literals.parent_layer
        action_layer = ActionLayer(parent_actions, parent_literals, self._serialize, self._ignore_mutexes)
        literal_layer = LiteralLayer(parent_literals, action_layer, self._ignore_mutexes)

        for action in self._actionNodes:
            # actions in the parent layer are skipped because are added monotonically to planning graphs,
            # which is performed automatically in the ActionLayer and LiteralLayer constructors
            if action not in parent_actions and action.preconditions <= parent_literals:
                action_layer.add(action)
                literal_layer |= action.effects

                # add two-way edges in the graph connecting the parent layer with the new action
                parent_literals.add_outbound_edges(action, action.preconditions)
                action_layer.add_inbound_edges(action, action.preconditions)

                # # add two-way edges in the graph connecting the new literaly layer with the new action
                action_layer.add_outbound_edges(action, action.effects)
                literal_layer.add_inbound_edges(action, action.effects)

        action_layer.update_mutexes()
        literal_layer.update_mutexes()
        self.action_layers.append(action_layer)
        self.literal_layers.append(literal_layer)
        self._is_leveled = literal_layer == action_layer.parent_layer
