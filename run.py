import sys
from random import randrange

class Block:
    def __init__(self, _type="S"):
        self.pos_x = 1
        self.pos_y = 1
        self.size_x = 3
        self.size_y = 3
        self.center_x = 1
        self.center_y = 1
        self.type = _type
        self.mask = self.createMask()
        

    def setPosition(self, _x, _y):
        self.pos_x = _x
        self.pos_y = _y

    def createMask(self):
        if(self.type == "T"):
            mask = [["T" for y in range(0, self.size_x)] for x in range(0, self.size_y)]
            mask[0] = ["O" for y in range(0, self.size_x)]
            mask[2][0] = "O"
            mask[2][2] = "O"
            return mask

        if(self.type == "L"):
            mask = [["L" for y in range(0, self.size_x)] for x in range(0, self.size_y)]
            mask[0] = ["O" for y in range(0, self.size_x)]
            mask[1][0] = "O"
            mask[1][1] = "O"
            return mask

        if(self.type == "I"):
            mask = [["I" for y in range(0, self.size_x)] for x in range(0, self.size_y)]
            mask[0] = ["O" for y in range(0, self.size_x)]
            mask[2] = ["O" for y in range(0, self.size_x)]
            return mask  

        # by default a square
        return [["S" for y in range(0, self.size_x)] for x in range(0, self.size_y)]

    def rotateLeft(self):
        
        self.mask = list(zip(*self.mask ))[::-1]
        for i, m in enumerate(self.mask):
            self.mask[i] = list(m)
        return True

class Tetris:
    def __init__(self, _size_x=15, _size_y=15):
        self.size_x = _size_x
        self.size_y = _size_y
        self.raw_frame = self.getEmptyFrame()
        self.blocks = []
        self.active_block_index = -1
        self.rotate_input = False
        self.move_side_input = 0

    def getEmptyFrame(self):
        return [["O" for y in range(0, self.size_y)] for x in range(0, self.size_x)]

    def addBlock(self, _block):
        self.blocks.append(_block)
        return True

    def getDisplayStr(self):
        out_str = ""
        for r, row in enumerate(self.raw_frame):
            if(r == 0 or r == 1):   # skip first 2 row where the blocks start
                continue

            for elem in row:
                out_str += str(elem) + " "
            out_str += "\n"
        return out_str

    def draw(self, skip_active_block=False):
        # clean frame
        self.raw_frame = self.getEmptyFrame()

        # draw all objects onto the frame
        for b, block in enumerate(self.blocks):
            if(skip_active_block and b == self.active_block_index):
                continue
            for x in range(0, block.size_x):
                for y in range(0, block.size_y):
                    if(block.mask[x][y] == "O"):
                        continue
                    frame_x = block.pos_x + (x - block.center_x)
                    frame_y = block.pos_y + (y - block.center_y)
                    if(frame_y >= self.size_y or frame_y < 0 or frame_x >= self.size_x or frame_x < 0):
                        continue
                    self.raw_frame[frame_x][frame_y] = block.mask[x][y]
        return True

    def checkIfBlockCanMove(self, _block, _move_x=1, _move_y=0, _rotate=False):
        move_x = _move_x
        move_y = _move_y
        rotate = _rotate

        # ensure maximum of 1 move
        if(move_x > 1):
            move_x = 1
        if(move_x < -1):
            move_x = -1
        if(move_y > 1):
            move_y = 1
        if(move_y < -1):
            move_y = -1

        # redo if cant move in y axis or cant rotate
        redo = True
        while(redo):
            redo = False

            # copy and possibly rotate block
            block = Block(_block.type)
            block.setPosition(_block.pos_x,_block.pos_y)
            if(rotate):
                block.rotateLeft()

            # check is mask of block doesnt collide
            for x in range(0, block.size_x):
                for y in range(0, block.size_y):
                    # calculate new position
                    frame_x = block.pos_x + move_x + (x - block.center_x)
                    frame_y = block.pos_y + move_y + (y - block.center_y)

                    # no point in checking for nothing
                    if(block.mask[x][y] == "O"):
                        continue

                    # fix if out bounds in y axis
                    if(frame_y >= self.size_y or frame_y < 0):
                        if(move_y != 0):
                            move_y = 0
                            redo = True
                            break
                        if(rotate):
                            rotate = False
                            redo = True
                            move_y = _move_y # set initial move_y aswell
                            break

                    # check if out bounds in x axis
                    if(frame_x >= self.size_x or frame_x < 0):
                        if(rotate):
                            rotate = False
                            redo = True
                            move_y = _move_y # set initial move_y aswell
                            break
                        return [False, move_x, move_y, rotate]

                    # check if collides with other blocks
                    if(self.raw_frame[frame_x][frame_y] != "O"):
                        if(move_y != 0):
                            redo = True
                            move_y = 0
                            break
                        if(rotate):
                            rotate = False
                            redo = True
                            move_y = _move_y # set initial move_y aswell
                            break
                        return [False, move_x, move_y, rotate]
                if redo:
                    break
        
        # return the new move values if succesful (in particular the y value)
        return [True, move_x, move_y, rotate]

    def createNewRandomBlock(self):
        # create random block
        new_block = None
        random_num = randrange(4)
        if random_num == 0:
            new_block = Block("L")
        if random_num == 1:
            new_block = Block("T")
        if random_num == 2:
            new_block = Block("I")
        if random_num == 3:
            new_block = Block("S")

        new_block.setPosition(1, int(self.size_x/2) - 1)

        # check if can add new block
        if self.checkIfBlockCanMove(new_block, _move_x=0, _move_y=0)[0]:
            self.addBlock(new_block)
            self.active_block_index = self.active_block_index + 1
        else:
            print("could not create new block")
            return False
        print("created new block")
        return True

    def applyInput(self, move_side=0, rotate=False):
        self.move_side_input = move_side
        self.rotate_input = rotate

    def update(self):
        # draw frame without current block
        self.draw(skip_active_block=True)

        # start
        if self.active_block_index == -1:
            self.blocks.clear()
            if not (self.createNewRandomBlock()):
                return False

        # update     
        else:
            # check for collision if moves
            result = self.checkIfBlockCanMove(self.blocks[self.active_block_index], 1, self.move_side_input, self.rotate_input)
            if result[0]:
                # move if doesnt collide
                self.blocks[self.active_block_index].pos_x += result[1]
                self.blocks[self.active_block_index].pos_y += result[2]
                if result[3]:
                    self.blocks[self.active_block_index].rotateLeft()
            else:
                # if collides, add new block, exit if new block collides
                if not (self.createNewRandomBlock()):
                    return False

        # draw complete frame
        self.draw()
        self.move_side_input = 0
        self.rotate_input = False
        return True

if __name__ == "__main__":
    game = Tetris(15,20)
    for i in range(0, 100): # show 200 moves
        game.applyInput(1, True) #  apply input to move left and rotate aswell
        game.update()   # update routine
        print(game.getDisplayStr()) # get display as str

sys.exit(0)