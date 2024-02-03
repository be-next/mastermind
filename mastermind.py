#!/usr/bin/env python3

import random
from enum import Enum
from tkinter import Button, Canvas, Frame, Label, Tk, messagebox

from PIL import Image, ImageTk

# Global parameters
__SIZE__ = 40
__RESOURCES_PATH__ = "./resources"
__NUMBER_OF_ATTEMPS__ = 10
# __CODE_PEG_LINE_SIZE__ ne fonctionne que pour la valeur 4
# cf. classe ResultCanvas qui ne sait gérer que 4 pegs
__CODE_PEG_LINE_SIZE__ = 4


class PegColor(Enum):
    no_color = -1
    blue = 0
    green = 1
    orange = 2
    pink = 3
    purple = 4
    red = 5

    @staticmethod
    def random():
        return PegColor(random.randint(0, 5))

    @staticmethod
    def get_number_of_colors() -> int:
        return 6


class PegColorFactory():
    _size = __SIZE__
    _resouces_path = __RESOURCES_PATH__
    _peg_color_file_names = {
        PegColor.blue: "blue.png",
        PegColor.green: "green.png",
        PegColor.orange: "orange.png",
        PegColor.pink: "pink.png",
        PegColor.purple: "purple.png",
        PegColor.red: "red.png"
    }

    def _create_image(self, color: PegColor):
        tmp_im = Image.open(
            f'{self._resouces_path}/{self._peg_color_file_names[color]}')
        tmp_im = tmp_im.resize((self._size, self._size),
                               Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(tmp_im)

    def __init__(self) -> None:
        self._button_colors = {color: self._create_image(
            color) for color in self._peg_color_file_names.keys()}
        self._init_no_color()

    def get_color(self, color: PegColor):
        return self._button_colors[color]

    def get_size(self) -> int:
        return self._size

    def _init_no_color(self):
        image = Image.new(mode='RGB', size=(
            self._size, self._size), color='grey')
        self._no_color = ImageTk.PhotoImage(image)

    @property
    def no_color(self):
        return self._no_color


class CodePeg(Button):
    _pcf: PegColorFactory

    def __init__(self, root, image=None):
        self._root = root
        self._pcf = PegColorFactory()
        self._color = PegColor.no_color

        img = image if image else self._pcf.no_color

        super().__init__(self._root, image=img, command=self._select_color)

    def set_color(self, color: PegColor):
        self._color = color
        self["image"] = self._pcf.get_color(color)

    @property
    def color(self):
        return self._color

    def _select_color(self):
        self._color = PegColor((self._color.value + 1) %
                               PegColor.get_number_of_colors())
        self.set_color(self._color)

    def disable(self):
        self.config(command="")

    def enable(self):
        self.config(command=self._select_color)

    def renew(self):
        self._color = PegColor.no_color
        self["image"] = self._pcf.no_color
        self.config(command="")


class ValidationButton(Button):
    _size = __SIZE__
    _resouces_path = __RESOURCES_PATH__
    _image_file = "validation_button_2.png"

    def __init__(self, root, state: bool = False):
        self._root = root
        self._init_disabled_image()
        self._init_enabled_image()
        super().__init__(self._root)
        self.set_state(new_state=state, new_command="")

    def _init_enabled_image(self):
        image = Image.open(
            f'{self._resouces_path}/{self._image_file}')
        image = image.resize(size=(self._size, self._size),
                             resample=Image.Resampling.LANCZOS)
        self._enabled_image = ImageTk.PhotoImage(image)

    def _init_disabled_image(self):
        image = Image.new(mode='RGB', size=(
            self._size, self._size), color='snow')
        self._disabled_image = ImageTk.PhotoImage(image)

    def set_state(self, new_state: bool, new_command):
        self._state = new_state
        self["image"] = self._enabled_image if self._state else self._disabled_image
        self.config(command=new_command)


class ResultCanvas(Canvas):
    _size = __SIZE__

    def __init__(self, root):
        self._root = root
        super().__init__(self._root, width=__SIZE__,
                         height=__SIZE__, bd=0, highlightthickness=0, bg='snow')
        self._init_coordonates()

    def _init_coordonates(self):
        radius = (__SIZE__ / 4) - 2
        step = __SIZE__ / 4

        self._coordonates = {
            0: [(step - radius), (step - radius), (step + radius), (step + radius)],
            1: [((step*3) - radius), (step - radius), ((step*3) + radius), (step + radius)],
            2: [(step - radius), ((step*3) - radius), (step + radius), ((step*3) + radius)],
            3: [((step*3) - radius), ((step*3) - radius), ((step*3) + radius), ((step*3) + radius)]
        }

    def _draw_kpeg(self, peg_id, peg_status):
        if peg_status == 1:  # misplaced
            self.create_oval(
                self._coordonates[peg_id][0],
                self._coordonates[peg_id][1],
                self._coordonates[peg_id][2],
                self._coordonates[peg_id][3],
                outline='black', width=2)
        elif peg_status == 2:
            self.create_oval(
                self._coordonates[peg_id][0],
                self._coordonates[peg_id][1],
                self._coordonates[peg_id][2],
                self._coordonates[peg_id][3],
                fill='black', width=2)

    def draw_result(self, well_placed_nb: int = 0, misplaced_nb: int = 0):
        for peg_id in range(__CODE_PEG_LINE_SIZE__):
            if well_placed_nb:
                well_placed_nb -= 1
                self._draw_kpeg(peg_id, 2)
            elif misplaced_nb:
                misplaced_nb -= 1
                self._draw_kpeg(peg_id, 1)
            else:
                break

        # pour forcer la mise à jour du canvas
        self.update()

    def renew(self):
        self.delete('all')


class CodePegLine(Frame):
    _size = __SIZE__
    _resouces_path = __RESOURCES_PATH__

    def __init__(self, nb, root, code):
        self._root = root
        self._code = code
        super().__init__(self._root)
        self._pack_number(nb)
        self._pack_code_pegs()
        self._pack_result_canvas()
        self._pack_validation_buton()

    def _pack_number(self, nb: int = 0):
        self._number = Label(self, text=str(
            nb), justify='center', width=2)  # largeur en nb de caractères
        self._number.pack(side='left')

    def _pack_code_pegs(self):
        self._code_pegs = [CodePeg(self)
                           for _ in range(__CODE_PEG_LINE_SIZE__)]

        for code_peg in self._code_pegs:
            code_peg.pack(side='left')

    def _pack_validation_buton(self):
        self._val_but = ValidationButton(self)
        self._val_but.pack(side='left')

    def _pack_result_canvas(self):
        self._result = ResultCanvas(self)
        self._result.pack(side='left')

    def check_code(self):
        ###
        current_code = [code_peg.color for code_peg in self._code_pegs]
        print(current_code)

        # Vérifie que toutes les couleurs ont bien été saisies
        if PegColor.no_color in current_code:
            messagebox.showwarning(
                "Attention", "Vous devez choisir une couleur pour chaque emplacement !")
            return

        well_placed = 0
        misplaced = 0

        current_code_copy = current_code[:]
        secret_code_copy = self._code[:]

        for i in range(len(self._code)):
            if current_code[i] == self._code[i]:
                well_placed += 1
                current_code_copy[i] = PegColor.no_color
                secret_code_copy[i] = PegColor.no_color

        for color in secret_code_copy:
            if color != PegColor.no_color and color in current_code_copy:
                misplaced += 1
                # supprime le 1er element 'color' de la liste
                current_code_copy.remove(color)

        self._result.draw_result(
            well_placed_nb=well_placed, misplaced_nb=misplaced)

        print(f'well_placed : {well_placed}, misplaced : {misplaced}')

        if well_placed == __CODE_PEG_LINE_SIZE__:
            # appelle la fonction MastermindBoard.win() pour indiquer la victoire !
            self._win_func_hook()
        else:
            # appelle la fonction MastermindBoard.next() pour changer la ligne active
            self._next_func_hook()

    def disable(self):
        self._val_but.set_state(new_state=False, new_command="")

        for code_peg in self._code_pegs:
            code_peg.disable()

    def enable(self):
        self._val_but.set_state(new_state=True, new_command=self.check_code)

        for code_peg in self._code_pegs:
            code_peg.enable()

    def renew(self, code):
        self._code = code
        self._val_but.set_state(new_state=False, new_command="")
        self._result.renew()

        for code_peg in self._code_pegs:
            code_peg.renew()

    def bind_win_func(self, win_func):
        self._win_func_hook = win_func

    def bind_next_func(self, next_func):
        self._next_func_hook = next_func


class MastermindBoard(Frame):
    _nb_of_attempts = __NUMBER_OF_ATTEMPS__

    def __init__(self, root):
        self._root = root
        self._init_code()
        self._current_line_index = 0
        super().__init__(self._root)
        self._init_board()

    def _init_board(self):
        self._lines = []
        for i in range(self._nb_of_attempts):
            self._lines.append(CodePegLine((i+1), self._root, self._code))
            self._lines[i].bind_next_func(self.next)
            self._lines[i].bind_win_func(self.win)
            self._lines[i].disable()
            self._lines[i].pack(side='top')

        self._lines[self._current_line_index].enable()

    def win(self):
        if messagebox.askyesno("Gagné !", "Bravo ! Vous avez gagné !\n Voulez-vous rejouer une nouvelle partie ?"):
            self.renew()
        else:
            self._quit_func()

    def next(self):
        # fonction appelée par chaque bouton de validation
        self._lines[self._current_line_index].disable()
        self._current_line_index += 1

        if self._current_line_index < self._nb_of_attempts:
            self._lines[self._current_line_index].enable()
        else:
            if messagebox.askyesno(
                    "Perdu !", "Vous avez perdu...\nVoulez-vous rejouer une nouvelle partie ?"):
                self.renew()
            else:
                # appel la fonction Mastermind.quit()
                self._quit_func()

    def renew(self):
        self._init_code()
        self._current_line_index = 0

        for line in self._lines:
            line.renew(self._code)

        self._lines[self._current_line_index].enable()

    def _init_code(self):
        self._code = [PegColor.random() for _ in range(__CODE_PEG_LINE_SIZE__)]
        # self._code = [PegColor.blue, PegColor.green,
        #               PegColor.blue, PegColor.orange]
        print(self._code)

    def bind_quit_func(self, quit_func):
        self._quit_func = quit_func


class Mastermind(Frame):
    def __init__(self) -> None:
        self._root = Tk()
        super().__init__(self._root)
        self._board = MastermindBoard(self)
        self._board.pack()
        self._board.bind_quit_func(self.quit)
        self.pack(padx=10, pady=10)
        self._root.mainloop()

    def quit(self):
        self._root.quit()


def main():
    Mastermind()


# entry point
if __name__ == '__main__':
    main()
