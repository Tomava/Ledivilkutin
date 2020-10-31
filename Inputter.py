import Ledivilkutin
import os
import json


def main():
    path = os.getcwd()
    while True:
        list_of_files = os.listdir("code")
        list_of_input_files = []
        for file in list_of_files:
            if file.count("input") > 0:
                list_of_input_files.append(f"{path}{os.sep}code{os.sep}{file}")
        for i, file in enumerate(list_of_input_files):
            print(f"{i} : {path}{os.sep}code{os.sep}{file}")
        print()
        file_index = int(input("Give input file index from the list: "))
        if 0 <= file_index < len(list_of_input_files):
            print(f"Inputting file {path}{os.sep}code{os.sep}{file}")
            print()
            break
        else:
            print("Incorrect index")
            print()
            print()
    file_path = list_of_input_files[file_index]
    with open(file_path, "r", encoding="utf-8") as file:
        data = dict(json.load(file))
        try:
            list_of_screens = data["Screens"]
            wait_time = int(data["Wait_time"])
        except KeyError:
            list_of_screens = data
            wait_time = -1
    Ledivilkutin.main(list_of_screens, wait_time)


if __name__ == "__main__":
    main()
