from queue import LifoQueue as Stack
from queue import PriorityQueue
from math import sqrt
from random import random

import arcade
import game_core
import game_data
import threading
import time
import os
import pygame
import numpy

class Agent(threading.Thread):

    def __init__(self, threadID, name, counter, show_grid_info=True):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.show_grid_info = show_grid_info

        self.game = []
        self.move_grid = []         # 2D list containing the environment
        self.kill_grid = []         # 2D list containing enemy locations, constantly updates
        self.isGameClear = False
        self.isGameOver = False
        self.current_stage = 0
        self.time_limit = 0
        self.total_score = 0
        self.total_time = 0
        self.total_life = 0
        self.tanuki_r = 0
        self.tanuki_c = 0
        self.last_move = 0; # Last move the agent did
    #############################################################
    #      YOUR SUPER COOL ARTIFICIAL INTELLIGENCE HERE!!!      #
    #############################################################
    def ai_function(self):
        # To send a key stroke to the game, use self.game.on_key_press() method

        # Get current state of goals
        environment = self.move_grid
        cur_r = self.tanuki_r
        cur_c = self.tanuki_c
        target_list = []

        # Get a list of the coordinates of all the goals we want through a basic search
        for row in range(0, len(environment) - 1):
            for col in range(0, len(environment[0]) - 1):
                if environment[row][col] == 8:
                    target_list.append((row, col))
        print(target_list)
        # Inefficient way of checking if our path to one fruit crossed another fruit
        # We remove it from the environment grid then
        for i in range (0, len(target_list) - 1):
            if (cur_r == target_list[i][0] and cur_c == target_list[i][1]):
                self.move_grid[cur_r][cur_c] = 1
        """
        The idea for moving the agent is to find the path to the goal first, move the agent ONE square only and repeat

        Combining this with pathfinding for the enemies, the agent should be able to successfully 
        dodge enemies whos state changes often by continuously finding the path to the goal
        """
        try:
            fruit_path = self.dfs_search_starter(move_grid=environment, cur_r=cur_r, cur_c=cur_c, target=target_list[0])
            if fruit_path is None:
                print("No goal found")
            else:
                print(fruit_path)
                # Move the agent one square
                # If we are already on the target square, remove it from the environment because this isnt done automatically when the fruit is collected
                if (cur_r == target_list[0][0] and cur_c == target_list[0][1]):
                    self.move_grid[cur_r][cur_c] = 1
                else:
                    self.last_move = self.move_agent(cur_r=cur_r, cur_c=cur_c, path_grid=fruit_path, last_move=self.last_move)
        except RecursionError:
            print("Could not find a path: Recursion error")


    #lastMove: 0 left, 1 left jump, 2 right, 3 right jump, 4 up, 5 down
    def move_agent(self, cur_r, cur_c, path_grid, last_move):
        '''
        Moves the agent one square, following the path given by path_grid
        '''
        lastMove = last_move
        # Move left    
        if (cur_c != 0) and (path_grid[cur_r][cur_c-1] == 1 or path_grid[cur_r][cur_c-1] == 9): #left
            if lastMove == 2 or lastMove == 3 or lastMove == 4 or lastMove == 5:
                self.game.on_key_press(key = arcade.key.LEFT, key_modifiers = False)
            self.game.on_key_press(key = arcade.key.LEFT, key_modifiers = False)
            
            path_grid[cur_r][cur_c] = 0
            cur_c = cur_c-1
            lastMove = 0
            print("left")
        # Jump left
        elif (cur_c != 0) and (path_grid[cur_r][cur_c - 1] == 2): #jump
            print(f"Last Move: {lastMove}")
            if lastMove in [1, 2, 3, 4, 5]:
                print("Turn left")
                self.game.on_key_press(key = arcade.key.LEFT, key_modifiers = False)
            self.game.on_key_press(key = arcade.key.SPACE, key_modifiers = False)
            
            path_grid[cur_r][cur_c] = 0
            cur_c = cur_c-2
            lastMove = 1
            print("jump Left")
        # Move right
        elif (cur_c != len(path_grid[cur_r]) - 1) and (path_grid[cur_r][cur_c + 1] == 1 or path_grid[cur_r][cur_c + 1] == 9): #right
            if lastMove == 0 or lastMove == 1 or lastMove == 4 or lastMove == 5:
                self.game.on_key_press(key = arcade.key.RIGHT, key_modifiers = False)
            self.game.on_key_press(key = arcade.key.RIGHT, key_modifiers = False)
            
            path_grid[cur_r][cur_c] = 0
            cur_c = cur_c+1
            lastMove = 2
            print("right")
        # Jump right
        elif (cur_c != len(path_grid[cur_r]) - 1) and (path_grid[cur_r][cur_c + 1] == 2): #jump
            if lastMove == 0 or lastMove == 1 or lastMove == 4 or lastMove == 5:
                self.game.on_key_press(key = arcade.key.RIGHT, key_modifiers = False)
            self.game.on_key_press(key = arcade.key.SPACE, key_modifiers = False)
                
            path_grid[cur_r][cur_c] = 0
            cur_c = cur_c+2
            lastMove = 3
            print("jump Right")
        # Move up
        elif (cur_r != 0) and (path_grid[cur_r - 1][cur_c] == 1 or path_grid[cur_r - 1][cur_c] == 9): #up
            if lastMove == 0 or lastMove == 1 or lastMove == 2 or lastMove == 3:
                self.game.on_key_press(key = arcade.key.UP, key_modifiers = False)
            self.game.on_key_press(key = arcade.key.UP, key_modifiers = False)
            
            path_grid[cur_r][cur_c] = 0
            cur_r = cur_r-1
            lastMove = 4
            print("up")
        # Move down
        elif (cur_r != len(path_grid) - 1) and (path_grid[cur_r + 1][cur_c] == 1 or path_grid[cur_r + 1][cur_c] == 9): #down
            if lastMove == 0 or lastMove == 1 or lastMove == 2 or lastMove == 3:
                self.game.on_key_press(key = arcade.key.DOWN, key_modifiers = False)
            self.game.on_key_press(key = arcade.key.DOWN, key_modifiers = False)

            path_grid[cur_r][cur_c] = 0
            cur_r = cur_r+1
            lastMove = 5
            print("down")

        time.sleep(0.05)
         
        return lastMove
        

    def dfs_search_starter(self, move_grid, cur_r, cur_c, target):
        '''
        Starter function that prepares the recursive function.
        Handles the very first iteration by loading the queue with the initial nodes agent can travel to.

        move_grid -> the move grid with only one of the targets
        cur_r, cur_c -> current Row/column coordinates
        visited_grid -> 2-d numpy array containing the path so far
        target -> (row, column) tuple

        '''

        # Create the priority queue for the A* search
        search_queue = PriorityQueue(maxsize=1000)

        # Initialize path grid
        path_grid = numpy.zeros_like(move_grid)
        visited_grid = numpy.zeros_like(move_grid)

        # Get surrounding nodes
        neighbor_nodes = self.__get_surrounding_nodes(cur_r, cur_c, move_grid, visited_grid)
        # Find valid nodes and add to the stack
        self.__get_valid_moves(cur_r, cur_c, target, neighbor_nodes, move_grid, path_grid, search_queue, visited_grid, 0)

        # Start the helper function after initialization given the queue has some nodes
        if (search_queue.empty()):
            return None
        else:
            # print(f"Nodes in stack: {search_stack.qsize()}")
            return self.dfs_search_helper(move_grid=move_grid, queue=search_queue, target=target, visited=visited_grid)


    def dfs_search_helper(self, move_grid, queue, target, visited):
        '''
        Find the path to the specified goal via A* search

        Each tile on the playing grid is its own node with any valid moves being potential branches
        Prioritize minimizing the cost
        Use a priority queue that contains the value of the function f = total_cost_paid + distance_to_goal
        everytime a node is expanded, calculate the cost for that node (IE expanding 3 nodes like it normally does does not increment the total cost by 3 but keeps and instance of the cost where each one is only incremented once)
        The priority queue will automatically sort by the lowest cost and we expand those nodes until the goal is found.

        The algorithm takes the following directions in order: left, up, right, down

        The visited grid is used so the agent doesnt try to push valid nodes to the queue if they had already been visited

        1. Pop the queue (if any) => gets current coordinates and the path so far
        2. Check if current node is target node
        3. get all the valid next nodes and add their coords to the stack.
        4. Add the action to the path grid for each valid node 
        5. Repeat until target reached or stack is completely empty

        Use a starter function for the first iteration that leads into the recursive function

        Integer values for move_grid:
        0 -> invalid space
        1 -> empty space
        2, 3, 4 -> platforms agent can STAND on
        5 -> Island agent can JUMP to and STAND on
        6 -> ladder
        7 -> spike

        9, 10, 11 -> bonus items
        The path grid contains 1 for valid move, 2 for spike
        '''

        # First check if there are any items in the stack, if empty then the target was not found
        if queue.empty():
            return None
        else:
            # Pop the queue and get the current coordinate and path
            (cost, cur_r, cur_c, path) = queue.get()
            # Set the current node as visited
            visited[cur_r][cur_c] = 1
            (target_row, target_column) = target
            #print(visited)
            # Check if we are already on the target: return the path if so
            if cur_r == target_row and cur_c == target_column:
                print("TARGET REACHED!")
                path[cur_r][cur_c] = 9
                return path
            else:
                # Get surrounding nodes
                neighbor_nodes = self.__get_surrounding_nodes(cur_r, cur_c, move_grid, visited)
                # Find valid nodes and add to the stack
                self.__get_valid_moves(cur_r, cur_c, target, neighbor_nodes, move_grid, path, queue, visited, cost)

                #print(f"Nodes in stack: {stack.qsize()}")
                return self.dfs_search_helper(move_grid=move_grid, queue=queue, target=target, visited=visited)


    def __get_surrounding_nodes(self, cur_r, cur_c, move_grid, visited):
        '''
        Gets all surrounding nodes in the environment
        takes the agents current coordinates and the corresponding environment and any visited nodes as the input

        outputs a tuple of (left, right, up, down) nodes
        any visited spaces or out-of-boundries are always -1

        returns a 4-tuple containing what thing (integer) is in the surrounding nodes
        '''
        node_left = move_grid[cur_r][cur_c - 1] if (cur_c != 0) and (visited[cur_r][cur_c-1] != 1) else -1
        node_right = move_grid[cur_r][cur_c + 1] if (cur_c != len(move_grid[cur_r]) - 1) and (visited[cur_r][cur_c + 1] != 1) else -1
        node_up = move_grid[cur_r - 1][cur_c] if (cur_r != 0) and (visited[cur_r - 1][cur_c] != 1) else -1
        node_down = move_grid[cur_r + 1][cur_c] if (cur_r != len(move_grid) - 1) and (visited[cur_r + 1][cur_c] != 1) else -1  

        return (node_left, node_right, node_up, node_down)


    def __get_valid_moves(self, cur_r, cur_c, target, neighbor_nodes, move_grid, path, queue, visited, total_cost):
        '''
        Takes the surrounding nodes of the current coordinates and determines wheteher they are valid nodes that the agent can travel to
        When a node is valid, it copies the current path, sets the current coords of the agent on the copie path to visited and pushes the new coordinates and copied path to a global stack
        If theres any jump at all, it sets the obsticals coordinates as visited on the visited grid.

        cur_r, cur_c -> current row/column coordinates of the agent (TODO: Change to tuple?)
        target -> Target coordinates in tuple form (row, column)
        neighbor_nodes -> 4-tuple given by __get_surrounding_nodes()
        environment -> the environment grid the agent is in
        path -> the current path for the agent
        queue -> the global priority queue for the search. we want to append the total cost paid plus to the straight line heuristic to the goal for that node. in the form (cost, row, col, current_path)
        visited -> the global visited grid that tells the agent what nodes have been visited
        total_cost -> The total cost the agent has paid so far in the current search, this is for the heuristic

        this function does not return anything and only updates the search data-structure
        '''

        # Check if the surrounding nodes are valid spaces the agent can be in 
        # If the node is a spike, then 'jump' over it and add the subsequent node to the stack

        # The path grid is copied to a new variable and pushed to the queue for each condition
        # because this prevents the 'previous' iteration from being modified
        # Without this, the final path returned by the function may have unintended forks in it

        # We add an small random value, epsilon, to the heuristic to greaty decrease the chance of two having the same exact cost
        # This prevents an error with the priority queue module where when there is a tie for the cost, it will check the second type for priority
        # It will end up checking the path grid array for priority and because they can't be compared directly, the program crashes
        
        (node_left, node_right, node_up, node_down) = neighbor_nodes
        # Get the target for calculating the distance
        (target_row, target_col) = target

        # Left case
        if (node_left in [1, 6, 8, 9, 10, 11]) and (move_grid[cur_r + 1][cur_c - 1] in [2, 3, 4, 6]):
            path_grid = numpy.copy(path)
            path_grid[cur_r][cur_c] = 1
            epsilon = random() * 0.001
            queue.put( (total_cost + epsilon + self.__get_distance(cur_r, cur_c - 1, target_row, target_col) , cur_r, cur_c - 1, path_grid))  # Append 4-tuple of coordinates and the visited grid
        # Check if there is a spike to the left
        if (node_left == 7) and (move_grid[cur_r + 1][cur_c - 2] in [2, 3, 4, 6]):
            path_grid = numpy.copy(path)
            visited[cur_r][cur_c - 1] = 1   # Set that spike as visited

            path_grid[cur_r][cur_c] = 1
            path_grid[cur_r][cur_c - 1] = 2

            epsilon = random() * 0.001
            queue.put((total_cost + epsilon + self.__get_distance(cur_r, cur_c - 1, target_row, target_col), cur_r, cur_c - 2, path_grid))

        # Check if there is a gap to jump over
        if (node_left == 1 and move_grid[cur_r + 1][cur_c - 1] == 1) and (move_grid[cur_r + 1][cur_c - 2] in [2, 3, 4, 5, 6]):
            path_grid = numpy.copy(path)
            visited[cur_r][cur_c - 1] = 1

            # Set the current coordinates and the hazards coordinates as part of the path for that iteration
            path_grid[cur_r][cur_c] = 1
            path_grid[cur_r][cur_c - 1] = 2

            epsilon = random() * 0.001
            queue.put((total_cost + epsilon + self.__get_distance(cur_r, cur_c - 1, target_row, target_col), cur_r, cur_c - 2, path_grid))

        # Right case
        if (node_right in [1, 6, 8, 9, 10, 11]) and (move_grid[cur_r + 1][cur_c + 1] in [2, 3, 4, 6]):
            path_grid = numpy.copy(path)
            path_grid[cur_r][cur_c] = 1
            queue.put((total_cost + self.__get_distance(cur_r, cur_c - 1, target_row, target_col), cur_r, cur_c + 1, path_grid))  
        # Check for spike to the right
        if (node_right == 7) and (move_grid[cur_r + 1][cur_c + 2] in [2, 3, 4, 6]):
            path_grid = numpy.copy(path)
            visited[cur_r][cur_c + 1] = 1       # Set the spike as visited
            path_grid[cur_r][cur_c] = 1
            path_grid[cur_r][cur_c + 1] = 2

            epsilon = random() * 0.001
            queue.put((total_cost + epsilon + self.__get_distance(cur_r, cur_c - 1, target_row, target_col), cur_r, cur_c + 2, path_grid))

        # Check if there is a gap to the right to jump over
        if (node_right == 1 and move_grid[cur_r + 1][cur_c + 1] == 1) and (move_grid[cur_r + 1][cur_c + 2] in [2, 3, 4, 5, 6]):
            path_grid = numpy.copy(path)
            visited[cur_r][cur_c + 1] = 1
            path_grid[cur_r][cur_c] = 1
            path_grid[cur_r][cur_c + 1] = 2

            epsilon = random() * 0.001
            queue.put((total_cost + epsilon + self.__get_distance(cur_r, cur_c - 1, target_row, target_col), cur_r, cur_c + 2, path_grid))

        # Up case
        # We have to be on a ladder space to move up; we can move to an empty space provided the current space is a ladder
        if (node_up in [1, 6, 8, 9, 10, 11]) and (move_grid[cur_r][cur_c] == 6):
            path_grid = numpy.copy(path)
            path_grid[cur_r][cur_c] = 1

            epsilon = random() * 0.001
            queue.put( (total_cost + epsilon + self.__get_distance(cur_r - 1, cur_c, target_row, target_col), cur_r - 1, cur_c, path_grid) ) 

        # Down case
        # We can move down if the space below is a ladder and the current space is also a ladder or air (can stand on top of ladders)
        if (node_down == 6) and (move_grid[cur_r][cur_c] in [1, 6]):
            path_grid = numpy.copy(path)
            path_grid[cur_r][cur_c] = 1

            epsilon = random() * 0.001
            queue.put( ( total_cost + epsilon + self.__get_distance(cur_r + 1, cur_c, target_row, target_col), cur_r + 1, cur_c, path_grid) )

    def __get_distance(self, x, y, goalx, goaly):
        """
        Gets the immediate distance from a coordinate to some goal
        returns a double of the distance
        """
        return sqrt(pow(goalx - x, 2) + pow(goaly - y, 2))

    ####################################################################
    ####################################################################

    def run(self):
        print("Starting " + self.name)

        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50+320, 50)
#        if self.show_grid_info:
        pygame.init()
#        else:
#            pygame = []

        # Prepare grid information display (can be turned off if performance issue exists)
        if self.show_grid_info:
            screen_size = [200, 120]
            backscreen_size = [40, 12]

            screen = pygame.display.set_mode(screen_size)
            backscreen = pygame.Surface(backscreen_size)
            arr = pygame.PixelArray(backscreen)
        else:
            time.sleep(0.5)  # wait briefly so that main game can get ready

        # roughly every 50 milliseconds, retrieve game state (average human response time for visual stimuli = 25 ms)
        go = True
        while go and (self.game is not []):
            # Dispatch events from pygame window event queue
            if self.show_grid_info:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        go = False
                        break

            # RETRIEVE CURRENT GAME STATE
            self.move_grid, self.kill_grid, \
                self.isGameClear, self.isGameOver, self.current_stage, self.time_limit, \
                self.total_score, self.total_time, self.total_life, self.tanuki_r, self.tanuki_c \
                = self.game.get_game_state()
            self.ai_function()

            # Display grid information (can be turned off if performance issue exists)
            
            if self.show_grid_info:
                for row in range(12):
                    for col in range(20):
                        c = self.move_grid[row][col] * 255 / 12
                        arr[col, row] = (c, c, c)
                    for col in range(20, 40):
                        if self.kill_grid[row][col-20]:
                            arr[col, row] = (255, 0, 0)
                        else:
                            arr[col, row] = (255, 255, 255)

                pygame.transform.scale(backscreen, screen_size, screen)
                pygame.display.flip()
            
            # We must allow enough CPU time for the main game application
            # Polling interval can be reduced if you don't display the grid information
            time.sleep(0.05)

        print("Exiting " + self.name)


def main():
    ag = Agent(1, "My Agent", 1, True)

    ag.game = game_core.GameMain()
    ag.game.set_location(50, 50)

    ag.start()


    # Uncomment below for recording
    # ag.game.isRecording = True
    # ag.game.replay('replay.rpy')  # You can specify replay file name or it will be generated using timestamp

    # Uncomment below to replay recorded play
    # ag.game.isReplaying = True
    # ag.game.replay('replay.rpy')

    ag.game.reset()
    arcade.run()


if __name__ == "__main__":
    main()