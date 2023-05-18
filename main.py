# This is a sample Python script.
import json


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def get_nlu(file_name):
    # Use a breakpoint in the code line below to debug your script.
    with open(file_name, "r", encoding="utf-8") as input_file:
        with open("nlu_output.yml", "w+", encoding="utf-8") as output_file:
            nlu_data = {}
            input_lines = input_file.read()
            input_lines = json.loads(input_lines)
            for line in input_lines:
                # print(line)
                for turn in line["turns"]:
                    if turn["speaker"] == "USER":
                        for frame in turn["frames"]:
                            if frame["state"]["active_intent"] != "NONE":
                                # TODO get slot values if any:
                                text_to_add = turn["utterance"]
                                if frame["state"]["slot_values"] != {}:
                                    # print("HAS SLOT")
                                    slotList = list(frame["state"]["slot_values"].keys())
                                    for slot in slotList:
                                        slot_values = frame["state"]["slot_values"].get(slot)
                                        for slot_value in slot_values:
                                            if slot_value:
                                                text_to_add = text_to_add.replace(" " + slot_value, f" [{slot_value}]{{\"entity\": \"{slot}\"}}")
                                                # text_to_add = f"Why are you asking me the {slot_values}{{\"entity\": \"{slot}\"}}"
                                                # print(text_to_add)
                                            else:
                                                print("No slot values found for the given entity.")


                                if frame["state"]["active_intent"] in nlu_data:
                                    nlu_data[frame["state"]["active_intent"]].append(text_to_add)
                                else:
                                    nlu_data[frame["state"]["active_intent"]] = [text_to_add]

            # print(nlu_data)
            output_file.write("version: '3.1'\n\nnlu:\n")
            for intent in nlu_data:
                output_file.write("- intent: " + intent + "\n")
                output_file.write("  examples: |\n")
                for example in nlu_data[intent]:
                    output_file.write("    - " + example +"\n")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_nlu('data/test.json')
