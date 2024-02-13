import copy
import csv
import json
import re


def modify_string_to_have_entities_annotated(original_string, sublist):
    modified_string = original_string
    for item in sublist:
        start_pos, end_pos = item[3], item[4]
        entity = item[1]
        word_to_replace = original_string[start_pos:end_pos]
        replacement = f"[{word_to_replace}]{{\"entity\": \"{entity}\"}}"
        modified_string = modified_string[:start_pos] + replacement + modified_string[end_pos:]
    return modified_string


def convert_multiwoz_to_csv():
    headers = ["ID", "Turn Number", "English", "Maltese"]
    with open("./totranslate.csv", "w+", newline='', encoding="utf-8") as totranslate:
        writer = csv.DictWriter(totranslate, fieldnames=headers)
        # Write headers
        writer.writeheader()
        with open("./data/test.json", "r+", encoding="utf-8") as test:
            test_data = json.load(test)
            for conv in test_data.keys():
                for i, turn in enumerate(test_data[conv]["log"]):
                    sublist = copy.deepcopy(turn["span_info"])
                    sublist.sort(key=lambda x: x[3],
                                 reverse=True)  # Sort sublist based on start position in descending order

                    writer.writerow({"ID": conv, "Turn Number": i,
                                     "English": modify_string_to_have_entities_annotated(turn["text"], sublist),
                                     "Maltese": ""})
                totranslate.write("\n")



def restore_string(modified_string):
    restored_string = re.sub(r'\[(.*?)\]\{"entity": "(.*?)"\}', r'\1', modified_string)
    return restored_string

def extract_entity_name_positions(clean_string, modified_string):
    pattern = r'\[(.*?)\]\{"entity": "(.*?)"\}'
    matches = re.finditer(pattern, modified_string)
    extracted_data = []
    offset = 0
    for match in matches:
        name, entity_type = match.groups()
        start_pos = clean_string.find(name, offset)
        end_pos = start_pos + len(name)
        offset = end_pos + 1
        extracted_data.append({"entity": entity_type, "name": name, "start_pos": start_pos, "end_pos": end_pos})
    return extracted_data

def convert_csv_to_multiwoz():
    with open("./totranslate.csv", "r", newline='', errors="ignore", encoding="utf-8") as translated:
        translated_data = []
        reader = csv.DictReader(translated, delimiter=',') # Read the headers
        for row in reader:
            translated_data.append(row)
        with open("./data/test.json", "r", encoding="utf-8") as test:
            with open("./data/test_mt.json", "w+", encoding="utf-8") as test_mt:

                test_data = json.load(test)
                test_mt_data = copy.deepcopy(test_data)
                current_translation_index = 0
                for conv_id, conv in enumerate(test_mt_data.keys()):
                    for i, turn in enumerate(test_mt_data[conv]["log"]):

                        # print(test_mt_data[conv]["log"][i]["text"])
                        # print(translated_data[i]["Maltese"])
                        # Remove the entities and place it in "text"
                        test_mt_data[conv]["log"][i]["text"] = restore_string(translated_data[current_translation_index]["Maltese"])

                        # Update the list of entities (span_info)
                        last_four_elements = extract_entity_name_positions( restore_string(translated_data[current_translation_index]["Maltese"]), translated_data[current_translation_index]["Maltese"])
                        #print(last_four_elements)
                        if restore_string(translated_data[current_translation_index]["Maltese"]) == 'Hemm 14 lukandi fiż-żona li jaqblu mal-kriterji tiegħek, inti interessat fl-Arbury Lodge Guesthouse?':
                            print("")
                        last_four_elements_seen = []
                        for ind, span in enumerate(test_mt_data[conv]["log"][i]["span_info"]):

                            for ind_entity, entity in enumerate(last_four_elements):
                                if ind_entity not in last_four_elements_seen and span[1] == entity["entity"]:
                                    test_mt_data[conv]["log"][i]["span_info"][ind][2] = entity["name"]
                                    test_mt_data[conv]["log"][i]["span_info"][ind][3] = entity["start_pos"]
                                    test_mt_data[conv]["log"][i]["span_info"][ind][4] = entity["end_pos"]
                                    last_four_elements_seen.append(ind_entity)
                                    break
                        current_translation_index += 1
                    current_translation_index += 1 # There is an empty line between each conversation

                json.dump(test_mt_data, test_mt)
if __name__ == '__main__':
    # convert_multiwoz_to_csv()
    # (Translate) and then convert back to multiwoz format
    convert_csv_to_multiwoz()