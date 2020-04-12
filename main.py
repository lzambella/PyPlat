from queue import LifoQueue as Stack

import arcade
import game_core
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
        # Iterate through each targets location and find the path to it
        for coord in target_list:
            try:
                fruit_path = self.dfs_search_starter(move_grid=environment, cur_r=cur_r, cur_c=cur_c, target=coord)
                if fruit_path is None:
                    print("No goal found")
                else:
                    print(fruit_path)
            except RecursionError:
                print("Could not find path, recursion error")
        return


    def dfs_search_starter(self, move_grid, cur_r, cur_c, target):
        '''
        Starter function that prepares the recursive function.
        Handles the very first iteration by loading the stack with the initial nodes agent can travel to.

        move_grid -> the move grid with only one of the targets
        cur_r, cur_c -> current Row/column coordinates
        visited_grid -> 2-d numpy array containing the path so far
        target -> (row, column) tuple

        '''

        # A search stack contains a 3-tuple in the form (column_coord, row_coord, current_path_grid)
        search_stack = Stack(maxsize = 1000)

        # Initialize path grid
        path_grid = numpy.zeros_like(move_grid)
        visited_grid = numpy.zeros_like(move_grid)

        # Get all surrounding nodes
        node_left = move_grid[cur_r][cur_c - 1] if (cur_c != 0) else -1
        node_right = move_grid[cur_r][cur_c + 1] if (cur_c != len(move_grid[cur_r]) - 1) else -1    # index OOB error
        node_up = move_grid[cur_r - 1][cur_c] if (cur_r != 0) else -1
        node_down = move_grid[cur_r + 1][cur_c] if (cur_r != len(move_grid) - 1) else -1

        
        # Check if the surrounding nodes are valid spaces the agent can be in 
        # If the node is a spike, then 'jump' over it and add the subsequent node to the stack
        
        # Left case, check if left node is empty space or ladder AND the space below it is a platform (or ladder)
        # TODO: This block can be condensed into its own function
        if (node_left in [1, 6]) and (move_grid[cur_r + 1][cur_c - 1] in [2, 3, 4, 6]):
            path_grid[cur_r][cur_c] = 1
            search_stack.put((cur_r, cur_c - 1, path_grid))  # Append 3-tuple of coordinates and the visited grid
        # If its a spike, do this instead but check if there is ground two spaces left and one space down
        elif (node_left == 7) and (move_grid[cur_r + 1][cur_c - 2] in [2, 3, 4, 5, 6]):
            path_grid[cur_r][cur_c] = 1
            path_grid[cur_r][cur_c - 1] = 2
            search_stack.put((cur_r, cur_c - 2, path_grid))
        # Check if there is a gap to jump to
        elif (node_left == 1 and move_grid[cur_r + 1][cur_c - 1] == 1) and (move_grid[cur_r + 1][cur_c - 2] in [2, 3, 4, 5, 6]):
            path_grid[cur_r][cur_c] = 1
            path_grid[cur_r][cur_c - 1] = 2
            search_stack.put((cur_r, cur_c - 2, path_grid))

        # Right case
        if (node_right in [1, 6]) and (move_grid[cur_r + 1][cur_c + 1] in [2, 3, 4, 6]):
            path_grid[cur_r][cur_c] = 1
            search_stack.put( (cur_r, cur_c + 1, path_grid) )  
        elif (node_right == 7) and (move_grid[cur_r + 1][cur_c + 2] in [2, 3, 4, 6]):
            path_grid[cur_r][cur_c] = 1
            path_grid[cur_r][cur_c + 1] = 2
            search_stack.put((cur_r, cur_c + 2, path_grid))
        # Check if there is a gap to jump to
        elif (node_right == 1 and move_grid[cur_r + 1][cur_c + 1] == 1) and (move_grid[cur_r + 1][cur_c + 2] in [2, 3, 4, 5, 6]):
            path_grid[cur_r][cur_c] = 1
            path_grid[cur_r][cur_c + 1] = 2
            search_stack.put((cur_r, cur_c + 2, path_grid))

        # Up case
        # We have to be on a ladder space to move up; we can move to an empty space provided the current space is a ladder
        if (node_up in {1, 6}) and (move_grid[cur_r][cur_c] == 6):
            path_grid[cur_r][cur_c] = 1
            search_stack.put((cur_r - 1, cur_c, path_grid)) 

        # Down case
        # We can move down if the space below is a ladder and the current space is also a ladder or air (can stand on top of ladders)
        if (node_down in {6}) and (move_grid[cur_r][cur_c] in [1, 6]):
            path_grid[cur_r][cur_c] = 1
            search_stack.put((cur_r + 1, cur_c, path_grid)) 

        # Start the helper function after initialization given the stack has some nodes
        if (search_stack.empty()):
            return None
        else:
            # print(f"Nodes in stack: {search_stack.qsize()}")
            return self.dfs_search_helper(move_grid=move_grid, stack=search_stack, target=target, visited=visited_grid)


    def dfs_search_helper(self, move_grid, stack, target, visited):
        '''
        Find the path to the specified goal via DFS (Later to be upgraded to A*)

        Each tile on the playing grid is its own node with any valid moves being potential branches
        Prioritize going as far deep as possible,
        storing each node in a stack and when there are no more moves to be made,
        pop the stack and take the next path that hasn't been visited.

        The algorithm takes the following directions in order: left, up, right, down

        The visited grid is used so the agent doesnt try to push valid nodes to the stack if they had already been visited

        We pop a node from the stack at the beginning.
        every possible 'next' node is stored before repeating the function

        1. Pop the stack (if any) => gets current coordinates and the path so far
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
        if stack.empty():
            return None
        else:
            # Pop the stack and get the current coordinate and path
            (cur_r, cur_c, path) = stack.get()        
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
            # Get all surrounding nodes, consider whether those surrounded nodes have already been visited
            node_left = move_grid[cur_r][cur_c - 1] if (cur_c != 0) and (visited[cur_r][cur_c-1] != 1) else -1
            node_right = move_grid[cur_r][cur_c + 1] if (cur_c != len(move_grid[cur_r]) - 1) and (visited[cur_r][cur_c + 1] != 1) else -1
            node_up = move_grid[cur_r - 1][cur_c] if (cur_r != 0) and (visited[cur_r - 1][cur_c] != 1) else -1
            node_down = move_grid[cur_r + 1][cur_c] if (cur_r != len(move_grid) - 1) and (visited[cur_r + 1][cur_c] != 1) else -1

            
            # Check if the surrounding nodes are valid spaces the agent can be in 
            # If the node is a spike, then 'jump' over it and add the subsequent node to the stack

            # The path grid is copied to a new variable and pushed to the stack for each condition
            # because this prevents the 'previous' iteration from being modified
            # Without this, the final path may have forks in it

            # Left case
            if (node_left in [1, 6, 8, 9, 10, 11]) and (move_grid[cur_r + 1][cur_c - 1] in [2, 3, 4, 6]):
                path_grid = numpy.copy(path)
                path_grid[cur_r][cur_c] = 1
                stack.put((cur_r, cur_c - 1, path_grid))  # Append 3-tuple of coordinates and the visited grid
            if (node_left == 7) and (move_grid[cur_r + 1][cur_c - 2] in [2, 3, 4, 6]):
                path_grid = numpy.copy(path)
                visited[cur_r][cur_c - 1] = 1   # Set that spike as visited
                path_grid[cur_r][cur_c] = 1
                path_grid[cur_r][cur_c - 1] = 2
                stack.put((cur_r, cur_c - 2, path_grid))
            # Check if there is a gap to jump to
            if (node_left == 1 and move_grid[cur_r + 1][cur_c - 1] == 1) and (move_grid[cur_r + 1][cur_c - 2] in [2, 3, 4, 5, 6]):
                path_grid = numpy.copy(path)
                visited[cur_r][cur_c - 1] = 1
                path_grid[cur_r][cur_c] = 1
                path_grid[cur_r][cur_c - 1] = 2
                stack.put((cur_r, cur_c - 2, path_grid))

            # Right case
            if (node_right in [1, 6, 8, 9, 10, 11]) and (move_grid[cur_r + 1][cur_c + 1] in [2, 3, 4, 6]):
                path_grid = numpy.copy(path)
                path_grid[cur_r][cur_c] = 1
                stack.put((cur_r, cur_c + 1, path_grid))  
            if (node_right == 7) and (move_grid[cur_r + 1][cur_c + 2] in [2, 3, 4, 6]):
                path_grid = numpy.copy(path)
                visited[cur_r][cur_c + 1] = 1       # Set the spike as visited
                path_grid[cur_r][cur_c] = 1
                path_grid[cur_r][cur_c + 1] = 2
                stack.put((cur_r, cur_c + 2, path_grid))
            # Check if there is a gap to jump to
            if (node_right == 1 and move_grid[cur_r + 1][cur_c + 1] == 1) and (move_grid[cur_r + 1][cur_c + 2] in [2, 3, 4, 5, 6]):
                path_grid = numpy.copy(path)
                visited[cur_r][cur_c + 1] = 1
                path_grid[cur_r][cur_c] = 1
                path_grid[cur_r][cur_c + 1] = 2
                stack.put((cur_r, cur_c + 2, path_grid))

            # Up case
            # We have to be on a ladder space to move up; we can move to an empty space provided the current space is a ladder
            if (node_up in [1, 6, 8, 9, 10, 11]) and (move_grid[cur_r][cur_c] == 6):
                path_grid = numpy.copy(path)
                path_grid[cur_r][cur_c] = 1
                stack.put((cur_r - 1, cur_c, path_grid)) 

            # Down case
            # We can move down if the space below is a ladder and the current space is also a ladder or air (can stand on top of ladders)
            if (node_down == 6) and (move_grid[cur_r][cur_c] in [1, 6]):
                path_grid = numpy.copy(path)
                path_grid[cur_r][cur_c] = 1
                stack.put((cur_r + 1, cur_c, path_grid))
            #print(f"Nodes in stack: {stack.qsize()}")
            return self.dfs_search_helper(move_grid=move_grid, stack=stack, target=target, visited=visited)

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