import PySimpleGUI as sg
import os
import json

# List of raw commands by screen
list_of_screens = {}
# List of LEDs to light by screen
list_of_coordinate_screens = {}
# Undo list with screen indexes as keys and list of selected buttons after each button press as values
undo_list = {}


def turn_on():
    """
    Turn on command
    :return:
    """
    command = '"e0f"'
    comment = "// Select max brightness"
    return f"{command:<6}\t\t\t{comment}"


def turn_off():
    """
    Turn off command
    :return:
    """
    command = '"e00"'
    comment = "// Select min brightness"
    return f"{command:<6}\t\t\t{comment}"


def choose_led(x=0, y=0, choose_all=False):
    """
    Gives command to select specifies LED or all LEDs
    :param x: int, x-coordinate
    :param y: int, y-coordinate
    :param choose_all: bool
    :return: str, Command to select specifies LED or all LEDs
    """
    if choose_all:
        command = '"a"'
        return f'{command:<6}\t\t\t// Select all'
    comment = f"// Select LED on row {y + 1} on column {x + 1}"
    x = f"{x:01x}"
    y = f"{y:01x}"
    command = f'"s{y}{x}"'
    return f'{command:<6}\t\t\t{comment}'


def next_screen(wait_time=-1, last_screen=False):
    """
    Next screen command
    :param wait_time: int, If it's an animation how long to wait between frames
    :param last_screen: bool, Don't add "x" if it's the last screen
    :return: str, Change command
    """

    change = ""
    if not last_screen:
        command = '"x"'
        change = f'{command:<6}\t\t\t// Next screen'
    if wait_time == -1:
        command = '"wffff"'
        wait = f'{command:<6}\t\t\t// Stop here'
        return f'{wait}\n{change}'
    else:
        # Make sure it doesn't print "wffff" or more
        if wait_time > 983024:
            wait_time = 983024
        elif wait_time < 0:
            wait_time = 0
        command = f'"w{int(wait_time / 15):04x}"'
        comment = f"// Wait for about {wait_time} milliseconds"
        return f"{command:<6}\t\t\t{comment}"


def get_button_coordinates(button):
    """
    Gets button's coordinates from button's name
    :param button: str
    :return: int, int
    """
    x = button[16:18]
    y = button[-2:]
    return x, y


def make_dictionary(i):
    """
    Makes an empty dictionary with i amount of x and y coordinates
    :param i: int
    :return: dict
    """
    temp_dict = {}
    for x in range(i):
        temp_dict[f"{x:02d}"] = []
    return temp_dict


def print_commands(wait_time=-1):
    """
    Prints all of machine code
    :param wait_time: int, How much to wait between frames if it's an animation (if -1, not an animation)
    :return:
    """
    delete_extra_screens()
    if len(list_of_coordinate_screens) <= 0:
        return
    for i in range(max(list_of_coordinate_screens.keys()) + 1):
        for command in get_screen_commands(i, wait_time):
            print(command)
    print()


def save_commands(wait_time=-1):
    """
    Saves all of machine code
    :param wait_time: int, How much to wait between frames if it's an animation (if -1, not an animation)
    :return:
    """
    delete_extra_screens()
    raw_code = []
    descriptive_code = []
    if len(list_of_coordinate_screens) <= 0:
        return
    for i in range(max(list_of_coordinate_screens.keys()) + 1):
        if i > 0:
            descriptive_code.append("\n")
        if wait_time == -1:
            descriptive_code.append(f"// Screen #{i + 1}:")
        else:
            descriptive_code.append(f"// Frame #{i + 1}:")
        for command in get_screen_commands(i, wait_time):
            raw_code.append(command)
            descriptive_code.append(command)
    if not os.path.exists("code"):
        os.mkdir("code")
    i = 1
    while True:
        if not os.path.isfile("code" + os.sep + f"code{i}.txt"):
            with open("code" + os.sep + f"code{i}.txt", "w", encoding="utf-8") as file:
                for line in raw_code:
                    file.write(str(line) + "\n")
            break
        i += 1
    with open("code" + os.sep + f"code_with_descriptions{i}.txt", "w", encoding="utf-8") as file:
        for line in descriptive_code:
            file.write(str(line) + "\n")
    input_code = {"Screens": list_of_coordinate_screens, "Wait_time": wait_time}
    with open("code" + os.sep + f"input_code{i}.json", "w", encoding="utf-8") as file:
        json.dump(input_code, file, indent=2, ensure_ascii=False)
    print("Saved raw code to \"" + os.getcwd() + os.sep + "code" + os.sep + f"code{i}.txt\"")
    print("and informative code to \"" + os.getcwd() + os.sep + "code" + os.sep + "code_with_descriptions.txt\"")
    print("and input code to \"" + os.getcwd() + os.sep + "code" + os.sep + f"input_code{i}.json")


def delete_extra_screens():
    """
    Deletes empty extra screens
    :return: nothing
    """
    to_be_deleted = []
    for screen in list_of_coordinate_screens.keys():
        empty = True
        for value_list in list_of_coordinate_screens.get(screen).values():
            if value_list:
                empty = False
                break
        if empty:
            to_be_deleted.append(screen)
    for screen in to_be_deleted:
        del list_of_coordinate_screens[screen]


def get_screen_commands(screen_index, wait_time=-1):
    """
    Get's a specified screen's commands from LIST_OF_COORDINATE_SCREENS
    :param wait_time: int, How much to wait between frames if it's an animation (if -1, not an animation)
    :param screen_index: int, Screen's/frame's index
    :return: list, List containing all that screen's/frame's commands
    """
    selected_buttons = list_of_coordinate_screens.get(screen_index)
    # If screen doesn't exist
    if selected_buttons is None:
        if wait_time == -1:
            return [next_screen()]
        else:
            return [next_screen(wait_time)]
    list_of_commands = [turn_off(), choose_led(choose_all=True), turn_on()]
    # Get commands to select all LEDs from selected buttons
    for x in selected_buttons:
        for y in selected_buttons.get(x):
            list_of_commands.append(choose_led(int(x), int(y)))
            # print(choose_led(int(x), int(y)))
    if screen_index != max(list_of_coordinate_screens.keys()):
        list_of_commands.append(next_screen(wait_time))
    else:
        list_of_commands.append(next_screen(wait_time, True))
    return list_of_commands


def current_screen_commands(selected_buttons, screen_index):
    """
    Saves screen's buttons with a given screen index
    :param selected_buttons: dict, Contains x-coordinates as keys and y-coordinates as values
    :param screen_index: int, Wanted screen index
    :return: nothing
    """
    list_of_coordinate_screens[screen_index] = selected_buttons.copy()


class GUI:

    def __init__(self, wait_time=-1):
        if wait_time == -1:
            checkbox_value = False
        else:
            checkbox_value = True
        layout = []
        row_layout = []
        layout.append([sg.Text("Screen", key="Screen Text Text", font="Any 18", text_color="white"),
                       sg.Text(f'{1}', key="Screen Text", size=(10, 1), font="Any 18", text_color="white")])
        for y in range(16):
            row_layout.clear()
            for x in range(16):
                row_layout.append(sg.Button(f"{x:02d},{y:02d}", key=f"CoordinateButton{x:02d},{y:02d}", size=(4, 2),
                                            button_color=('pink', 'black')))
            if y == 6:
                row_layout.append(sg.Checkbox('This is an animation', default=checkbox_value, key='is_animation',
                                              change_submits=True,
                                              tooltip="Makes this an animation with frames instead of separate screens"))
            elif y == 7:
                row_layout.append(sg.Text("Milliseconds per animation frame:", key=f"Milliseconds_text"))
            elif y == 8:
                row_layout.append(sg.Spin([i for i in range(0, 10000, 15)], change_submits=True, key="Milliseconds",
                                          size=(5, 0), disabled=not checkbox_value, initial_value=wait_time,
                                          tooltip="Defines how many milliseconds there are per frame (-1 if this "
                                                  "is not an animation)"))
            elif y == 9:
                row_layout.append(sg.Button("Save", key=f"Save",
                                            tooltip="Save all commands of all screens/frames to a file"))
            elif y == 10:
                row_layout.append(sg.Button("Print", key=f"Print", tooltip="Print all commands of all screens/frames"))
            elif y == 11:
                row_layout.append(sg.Button("Clear", key=f"Clear", tooltip="Turn all LEDs on this screen/frame off"))
            elif y == 12:
                row_layout.append(sg.Button("Undo", key=f"Undo", tooltip="Undo last action"))
            elif y == 13:
                row_layout.append(sg.Button("Copy selected screen", key=f"Paste",
                                            tooltip="Copy selected screen/frame to current screen"))
                row_layout.append(sg.Spin([i for i in range(1, 10000)], key="CopyScreen", size=(5, 0),
                                          change_submits=True, tooltip="Choose which screen/frame gets copied"))
            elif y == 14:
                row_layout.append(sg.Button("Previous screen", key=f"Previous screen",
                                            tooltip="Change to previous screen/frame"))
            elif y == 15:
                row_layout.append(sg.Button("Next screen", key=f"Next screen", tooltip="Change to next screen/frame"))
            layout.append(row_layout.copy())
        self.__window = sg.Window('Ledivilkutin', layout)

    def activate_screen(self, screen_index, change_screen_number=True):
        """
        Activates a screen with given screen_index. If screen doesn't exist yet, creates and empty screen
        :param screen_index: int, Wanted screen index
        :param change_screen_number: bool, If true changes the screen text
        :return: dict, Selected buttons from wanted screen (empty if screen doesn't exist yet)
        """
        if screen_index in list_of_coordinate_screens.keys():
            selected_buttons = list_of_coordinate_screens[screen_index]
            # Make all buttons unactivated
            for y in range(16):
                for x in range(16):
                    self.__window[f"CoordinateButton{x:02d},{y:02d}"].Update(button_color=('pink', 'black'))
            # Activate buttons that were activated in wanted screen
            for x in selected_buttons:
                for y in selected_buttons.get(x):
                    self.__window[f"CoordinateButton{x},{y}"].Update(button_color=('black', 'pink'))
        else:
            # Make new empty window
            selected_buttons = self.clear_screen()
        if change_screen_number:
            self.__window["Screen Text"].Update(f"{screen_index + 1}")
        return selected_buttons

    def clear_screen(self):
        """
        Deactivates all buttons and leds from current screen
        :param window: sg.Window, Needed to deactivate and activate buttons
        :return: dict, Empty selected buttons dictionary
        """
        for y in range(16):
            for x in range(16):
                self.__window[f"CoordinateButton{x:02d},{y:02d}"].Update(button_color=('pink', 'black'))
        return make_dictionary(16)

    def start(self):
        """
        Gui stuff
        :return:
        """
        # Event Loop to process "events" and get the "values" of the inputs
        current_screen = 0
        last_screen = 0
        self.__window.Finalize()
        selected_buttons = self.activate_screen(0)
        while True:
            event, values = self.__window.read()
            # self.__window["Spinner"].Update(int(values["Spinner"]))
            if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
                break
            elif event == "is_animation":
                self.__window["Milliseconds"].Update(value=-1)
                self.__window["Milliseconds"].Update(disabled=not values["is_animation"])
            elif event == "Next screen":
                current_screen_commands(selected_buttons, current_screen)
                selected_buttons = self.activate_screen((current_screen + 1)).copy()
                last_screen = current_screen
                current_screen += 1
                self.__window["CopyScreen"].Update(value=last_screen + 1)
            elif event == "Previous screen":
                if current_screen != 0:
                    current_screen_commands(selected_buttons, current_screen)
                    selected_buttons = self.activate_screen((current_screen - 1)).copy()
                    last_screen = current_screen
                    current_screen -= 1
                    self.__window["CopyScreen"].Update(value=last_screen + 1)
            elif event == "Print":
                current_screen_commands(selected_buttons, current_screen)
                print_commands(wait_time=int(values["Milliseconds"]))
            elif event == "Save":
                current_screen_commands(selected_buttons, current_screen)
                save_commands(wait_time=int(values["Milliseconds"]))
            elif event == "Undo":
                # Check if there is something to undo
                if len(undo_list.get(current_screen, [])) > 0:
                    # Get the previous saved list of activated buttons
                    current_screen_commands(undo_list.get(current_screen, [])[-1], current_screen)
                    # Set these buttons to be currently activated buttons
                    selected_buttons = self.activate_screen(current_screen).copy()
                    # Remove latest item from undo list
                    temp_list = undo_list.get(current_screen, [])
                    temp_list.pop(-1)
                    undo_list[current_screen] = temp_list
            else:
                temp_list = undo_list.get(current_screen, [])
                temp_list.append(selected_buttons.copy())
                undo_list[current_screen] = temp_list
                if event.startswith("CoordinateButton"):
                    x, y = get_button_coordinates(event)
                    if y not in selected_buttons.get(x):
                        self.__window[event].Update(button_color=('black', 'pink'))
                        temp_list = selected_buttons.get(x).copy()
                        temp_list.append(y)
                        selected_buttons[x] = temp_list
                    else:
                        self.__window[event].Update(button_color=('pink', 'black'))
                        temp_list = selected_buttons.get(x).copy()
                        temp_list.remove(y)
                        selected_buttons[x] = temp_list
                elif event == "Clear":
                    selected_buttons = self.clear_screen()
                elif event == "Paste":
                    selected_buttons = self.activate_screen(values["CopyScreen"] - 1, change_screen_number=False).copy()
                    current_screen_commands(selected_buttons, values["CopyScreen"] - 1)


def main(input_list=list_of_coordinate_screens, wait_time=-1):
    global list_of_coordinate_screens
    for key in input_list:
        list_of_coordinate_screens[int(key)] = input_list.get(key)
    gui = GUI(wait_time)
    gui.start()


if __name__ == "__main__":
    main()
