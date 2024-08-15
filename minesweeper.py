from tkinter import *
import ctypes
import random
import sys
from pygame import mixer
import emoji


class Utils:
    @staticmethod
    def height_prct(percentage):
        return (rheight / 100) * percentage

    @staticmethod
    def width_prct(percentage):
        return (rwidth / 100) * percentage

class Settings:
    DIFFICULTY = {
       'easy': {'mines': 8, 'flags': 8, 'grid_size': 8, 'cells': 64, 'cell_size':4},
        'medium': {'mines': 12, 'flags': 12, 'grid_size': 10, 'cells': 100, 'cell_size':3},
        'difficult': {'mines': 16, 'flags': 16, 'grid_size': 12, 'cells': 144, 'cell_size':2}
    }

    @classmethod
    def get_grid_size(Cell, difficulty):
        return Cell.DIFFICULTY[difficulty]['grid_size']

    @classmethod
    def get_cell_count(Cell, difficulty):
        return Cell.DIFFICULTY[difficulty]['cells']

    @classmethod
    def get_mines_count(Cell, difficulty):
        return Cell.DIFFICULTY[difficulty]['mines']

    @classmethod
    def get_flag_count(Cell, difficulty):
        return Cell.DIFFICULTY[difficulty]['flags']
    
    @classmethod
    def get_cell_size(Cell, difficulty):
        return Cell.DIFFICULTY[difficulty]['cell_size']
    
    

class Cell:
    game_started = False
    game_finished = False
    all = []
    cell_count = 0
    flag_count = 0
 

    def __init__(self, x, y, is_mine=False):
        self.is_mine = is_mine
        self.is_opened = False
        self.is_mine_candidate = False
        self.cell_btn_object = None
        self.x = x
        self.y = y

        # Append the object to the Cell.all list
        Cell.all.append(self)

    def create_btn_object(self, location):
        btn = Button(
            location,
            width=3 * Settings.get_cell_size(selected_difficulty.get()),
            height=Settings.get_cell_size(selected_difficulty.get()),
            bg='#5F9EA0'
        )
        btn.bind('<Button-1>', self.left_click_actions)  # Left Click
        btn.bind('<Button-3>', self.right_click_actions)  # Right Click
        self.cell_btn_object = btn

    @staticmethod
    def create_cell_count_label(location):
        cell_lbl = Label(
            location,
            bg='black',
            fg='white',
            text=f"Cells Left:{Cell.cell_count}",
            font=("", 30)
        )
        Cell.cell_count_label_object = cell_lbl
        Cell.cell_count_label_object.grid(row=0, column=0)

    @staticmethod
    def create_flag_count_label(location):
        flag_lbl = Label(
            location,
            bg='black',
            fg='white',
            text=f"Remaining Flags:{Cell.flag_count}",
            font=("", 30)
        )
        Cell.cell_flag_label_object = flag_lbl
        Cell.cell_flag_label_object.grid(row=2, column=0)


    def left_click_actions(self, event):
        result = 0
        if self.is_mine:
            self.show_mine()
        else:
            if self.surrounded_cells_mines_length == 0:
                for cell_obj in self.surrounded_cells:
                    cell_obj.show_cell()
            self.show_cell()
            # If Mines count is equal to the cells left count, the player won
            if Cell.cell_count == Settings.get_mines_count(selected_difficulty.get()):
                Cell.playsound("victory.mp3",False)
                self.game_finished = True
                result = ctypes.windll.user32.MessageBoxW(0, 'Congratulations! You won the game!\nEnter Yes to restart.',
                                                        'Game Finished', 4)
                # Ask Do you Want To Continue
                if result == 6:  # 6 corresponds to "Yes" button
                    # Reset the game or continue playing
                    Cell.reset_game()
                else:
                    sys.exit()
        # Cancel Left and Right click events if the cell is already opened:
        self.cell_btn_object.unbind('<Button-1>')
        self.cell_btn_object.unbind('<Button-3>')

    def get_cell_by_axis(self, x, y):
        # Return a cell object based on the value of x, y
        for cell in Cell.all:
            if cell.x == x and cell.y == y:
                return cell

    @property
    def surrounded_cells(self):
        cells = [
            self.get_cell_by_axis(self.x - 1, self.y - 1),
            self.get_cell_by_axis(self.x - 1, self.y),
            self.get_cell_by_axis(self.x - 1, self.y + 1),
            self.get_cell_by_axis(self.x, self.y - 1),
            self.get_cell_by_axis(self.x + 1, self.y - 1),
            self.get_cell_by_axis(self.x + 1, self.y),
            self.get_cell_by_axis(self.x + 1, self.y + 1),
            self.get_cell_by_axis(self.x, self.y + 1)
        ]

        cells = [cell for cell in cells if cell is not None]
        return cells

    @property
    def surrounded_cells_mines_length(self):
        counter = 0
        for cell in self.surrounded_cells:
            if cell.is_mine:
                counter += 1

        return counter

    def show_cell(self):
        if not self.is_opened:
            Cell.cell_count -= 1
            self.cell_btn_object.configure(text=self.surrounded_cells_mines_length)
            # Replace the text of the cell count label with the newer count
            if Cell.cell_count_label_object:
                Cell.cell_count_label_object.configure(
                    text=f"Cells Left:{Cell.cell_count}"
                )
            # If this was a mine candidate, then for safety, we should
            # configure the background color to SystemButtonFace
            self.cell_btn_object.configure(
                bg='SystemButtonFace'
            )

        # Mark the cell as opened (Use it as the last line of this method)
        self.is_opened = True

    def show_mine(self):
        result = 0
        self.cell_btn_object.configure(bg='red')
        Cell.playsound("defeat.mp3",False)
        self.game_finished = True
        result = ctypes.windll.user32.MessageBoxW(0, 'You clicked on a mine\nEnter Yes to restart.', 'Game Over', 4)
        # Ask Do you Want To Continue
        if result == 6:  # 6 corresponds to "Yes" button
            # Reset the game or continue playing
            Cell.reset_game()
        else:
            sys.exit()

    def right_click_actions(self, event):
        if not self.is_mine_candidate and not self.is_opened:
            self.cell_btn_object.configure(
                bg='yellow',
                fg="red",
                text=f'{emoji.emojize(":triangular_flag:")}'
            )
            Cell.flag_count -= 1
            Cell.cell_flag_label_object.configure(
                text=f"Remaining Flags:{Cell.flag_count}"
            )
            self.is_mine_candidate = True
            self.cell_btn_object.unbind('<Button-1>')
        else:
            self.cell_btn_object.configure(
                # Change to murky blue
                bg='#5F9EA0',
                fg="black",
                text=""
            )
            Cell.flag_count += 1
            Cell.cell_flag_label_object.configure(
                text=f"Remaining Flags:{Cell.flag_count}"
            )
            self.is_mine_candidate = False
            self.cell_btn_object.bind('<Button-1>',self.left_click_actions)

    @staticmethod
    def randomize_mines(difficulty):
        mines_to_place = Settings.get_mines_count(difficulty)
        available_cells = Cell.all.copy()
        for _ in range(mines_to_place):
            cell = random.choice(available_cells)
            cell.is_mine = True
            available_cells.remove(cell)
            
    def __repr__(self):
        return f"Cell({self.x},{self.y})"
    
    def playsound(soundeffect, is_Looping):
        mixer.init()
        mixer.music.load(soundeffect)
        if is_Looping:
            mixer.music.play(-1)
        else:
            mixer.music.play()
    
    @classmethod
    def reset_game(Cell):
    # Clear existing cells and recreate them
        for cell in Cell.all:
            cell.cell_btn_object.grid_forget()
        Cell.all.clear()

    # Get the selected difficulty from the class variable
        difficulty = selected_difficulty.get()

    # Reset all necessary variables and UI elements
        grid_size = Settings.get_grid_size(difficulty)  # Get the grid size
        Cell.cell_count = grid_size * grid_size  # Update cell count based on grid size
        Cell.flag_count = Settings.get_flag_count(difficulty)  # Set the flag count
        Cell.game_finished = False
      
    #BACKGROUND SOUND
        Cell.playsound("bg_Toofpick.mp3",True)

    # Create cells with the new difficulty
        Cell.create_cells(difficulty)

    # Update the flag count label
        if Cell.cell_flag_label_object:
            Cell.cell_flag_label_object.configure(text=f"Remaining Flags:{Cell.flag_count}")

    # Update the cell count label
        if Cell.cell_count_label_object:
            Cell.cell_count_label_object.configure(text=f"Cells Left:{Cell.cell_count}")


    @classmethod
    def create_cells(Cell, difficulty):
        grid_size = Settings.get_grid_size(difficulty)
        Cell.cell_count = grid_size * grid_size  # Set the cell count based on grid size
        Cell.flag_count = Settings.get_flag_count(difficulty)
        Cell.game_finished = False

        for x in range(grid_size):
            for y in range(grid_size):
                c = Cell(x, y)
                c.create_btn_object(center_frame)
                c.cell_btn_object.grid(column=x, row=y)

        # Call randomize_mines after creating all cells
        Cell.randomize_mines(difficulty)


root = Tk()
# Override the settings of the window
root.configure(bg="black")
rwidth, rheight = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry('%dx%d+0+0' % (rwidth, rheight))
root.title("Minesweeper Game")
root.resizable(False, False)

#BACKGROUND SOUND
Cell.playsound("bg_Toofpick.mp3",True) 

# Create a Tkinter StringVar to store the selected difficulty
selected_difficulty = StringVar()
# Set the default difficulty
selected_difficulty.set('easy')
difficulty = 'easy'

top_frame = Frame(
    root,
    bg='black',
    width=rwidth,
    height=Utils.height_prct(25)
)
top_frame.place(x=0, y=0)

# Restart button
restart_button = Button(
    top_frame,
    bg="#000000",
    fg="#FFFFFF",
    text="Restart",
    relief="ridge",
    font=("", 20),
    command=Cell.reset_game  # Bind the reset_game class method
)
restart_button.place(x=0, y=0)

game_title = Label(
    top_frame,
    bg='black',
    fg='white',
    text='Minesweeper Game',
    font=('', 48)
)
game_title.pack()

game_title.place(
    x=Utils.width_prct(25),
    y=0
)
      
left_frame = Frame(
    root,
    bg='black',
    width=Utils.width_prct(25),
    height=Utils.height_prct(75)
)
left_frame.place(x=0, y=Utils.height_prct(25))

center_frame = Frame(
    root,
    bg='black',
    width=Utils.width_prct(75),
    height=Utils.height_prct(75)
)
center_frame.place(
    x=Utils.width_prct(25),
    y=Utils.height_prct(25)
)

# Difficulty level selection menu
difficulty_menu = OptionMenu(top_frame, selected_difficulty, 'easy', 'medium', 'difficult')
difficulty_menu.configure(bg='black', fg='white', font=('', 24))
difficulty_menu.place(x=Utils.width_prct(75), y=0)

# Bind the difficulty change to the reset_game class method
difficulty_menu.bind("<Configure>", lambda event, difficulty=selected_difficulty: Cell.reset_game())

# Call the label creation methods from the Cell class
Cell.create_cell_count_label(left_frame)
Cell.create_flag_count_label(left_frame)
rules_lbl = Label(
           left_frame,
            bg='black',
            fg='white',
            text="Rules:",
            font=("", 30)
        )
rules_lbl.grid(row=8, column=0)
rules1_lbl = Label(
           left_frame,
            bg='black',
            fg='white',
            text="Beware of Mines",
            font=("", 30)
        )
rules1_lbl.grid(row=14, column=0)
rules2_lbl = Label(
           left_frame,
            bg='black',
            fg='white',
            text="Flag Mine Candidates",
            font=("", 30)
        )
rules2_lbl.grid(row=16, column=0)
rules3_lbl = Label(
           left_frame,
            bg='black',
            fg='white',
            text="Always Have Fun!",
            font=("", 30)
        )
rules3_lbl.grid(row=18, column=0)
   

Cell.create_cells(selected_difficulty.get())  # Pass the selected difficulty to the create_cells method

# Run the window
root.mainloop()
