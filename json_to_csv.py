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
    headers = ["ID [IGNORE]", "Turn Number [IGNORE]", "English With Annotations [IGNORE]", "English",
               "Generated Maltese", "Maltese", "Maltese With Annotations [IGNORE]"]
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

                    writer.writerow({"ID [IGNORE]": conv, "Turn Number [IGNORE]": i,
                                     "English With Annotations [IGNORE]": modify_string_to_have_entities_annotated(
                                         turn["text"], sublist),
                                     "English": turn["text"], "Generated Maltese": "",
                                     "Maltese": "", "Maltese With Annotations [IGNORE]": ""})
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


# TODO - change this to Maltese With Annotations [IGNORE] when working with dev, Maltese otherwise
def convert_csv_to_multiwoz():
    with open("./totranslate.csv", "r", newline='', errors="ignore", encoding="utf-8") as translated:
        translated_data = []
        reader = csv.DictReader(translated, delimiter=',')  # Read the headers
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
                        test_mt_data[conv]["log"][i]["text"] = restore_string(
                            translated_data[current_translation_index]["Maltese With Annotations [IGNORE]"])

                        # Update the list of entities (span_info)
                        last_four_elements = extract_entity_name_positions(
                            restore_string(translated_data[current_translation_index]["Maltese With Annotations [IGNORE]"]),
                            translated_data[current_translation_index]["Maltese With Annotations [IGNORE]"])
                        # print(last_four_elements)
                        if restore_string(translated_data[current_translation_index][
                                              "Maltese With Annotations [IGNORE]"]) == 'Hemm 14 lukandi fiż-żona li jaqblu mal-kriterji tiegħek, inti interessat fl-Arbury Lodge Guesthouse?':
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
                    current_translation_index += 1  # There is an empty line between each conversation

                json.dump(test_mt_data, test_mt)


def pass_to_fast_align():
    with open("./totranslate.csv", "r", newline='', errors="ignore", encoding="utf-8") as translated:
        translated_data = []
        reader = csv.DictReader(translated, delimiter=',')  # Read the headers
        for row in reader:
            translated_data.append(row)
    with open("./tmp.txt", "w+", encoding="utf-8") as tmp:
        for i, row in enumerate(translated_data):
            if not re.findall(r"[\w:']+|[.,!?;]", translated_data[i]["English"]):
                continue
            tmp.write(" ".join(re.findall(r"[\w:']+|[.,!?;]", translated_data[i]["English"])) + " ||| " + " ".join(
                re.findall(r"[\w:']+|[.,!?;]", translated_data[i]["Maltese"])))
            tmp.write("\n")

def to_add_to_line(dict_in, index, to_add_string):
    if index in dict_in:
        if "entity" in to_add_string:
            dict_in[index] = to_add_string + dict_in[index]
        else:
            dict_in[index] += to_add_string
    else:
        dict_in[index] = to_add_string
    return dict_in


def search_substrings_with_positions(row, entities_that_need_to_be_added):
    """
    Function to search for substrings within a string and return their positions.

    Args:
        row (list): A list containing elements, where row[3] is the string to search within.
        entities_that_need_to_be_added (list): A list of substrings to search for.

    Returns:
        list: A list where each element is a list containing the indices of all occurrences
              of the corresponding substring in the string. If a substring is not found,
              its value is an empty list.
    """
    results = []  # List to store results

    # Split the string into words
    words = row[3].split()

    for substring in entities_that_need_to_be_added:
        found_positions = []
        # Iterate over all possible substrings in the string
        for i in range(len(words)):
            if substring in words[i]:
                found_positions.extend([i])  # Append all indices in the substring
                continue
            for j in range(i + 1, len(words) + 1):
                current_substring = ' '.join(words[i:j])
                # Check if the current substring matches the target substring
                if substring == current_substring:
                    found_positions.extend(range(i, j))  # Append all indices in the substring
                    break  # Exit the inner loop after finding all occurrences

        if found_positions:
            results.append(found_positions)  # Append the list of indices
        else:
            results.append([])  # Append empty list if not found

    return results

def extract_fast_align_results():

    with open("./totranslate.csv", "r", newline='', encoding="utf-8-sig") as original_csv:
        with open("./final_translated_csv.csv", "w+", newline='',  encoding="utf-8-sig") as final_csv:
            with open("./after_forward_align.txt", "r", encoding="utf-8") as fast_align_results:
                alignments = fast_align_results.readlines()
                for i, alignment in enumerate(alignments):
                    alignments[i] = alignment.replace("\n", "")
                reader = csv.reader(original_csv)
                writer = csv.writer(final_csv)

                # Write header as is
                header = next(reader)
                writer.writerow(header)

                skipped_lines = 0
                for i, row in enumerate(reader):
                    if row == ["", "", "", "", "", "", ""]:
                        skipped_lines += 1
                        writer.writerow(row)
                        continue
                    en_with_annotations = row[2]

                    # if we have to fix the entity annotations
                    if "{" in en_with_annotations:
                        entities_that_need_to_be_added = re.findall('\[(.*?)\]', en_with_annotations)

                        indexes_to_avoid = []
                        to_insert = {}
                        for index_result, entity_to_annotate in enumerate(entities_that_need_to_be_added):
                            # get array of position indexs of result.group(1)
                            array_of_indexes = search_substrings_with_positions(row, entities_that_need_to_be_added)
                            # split_entity_res = re.findall(r"\S+", entity_to_annotate)
                            #
                            # pos_of_first_index = re.findall(r"\S+",
                            #                                 row[3]).index(
                            #     split_entity_res[0])
                            #not_found = False
                            # while True:
                            #     if not_found:
                            #         not_found = False
                            #     for j, entity_word in enumerate(split_entity_res):
                            #         if re.findall(r"[\w:']+|[.,!?;]",row[3] )[
                            #             pos_of_first_index + j] != split_entity_res[j]:
                            #             not_found = True
                            #             pos_of_first_index = re.findall(r"\S+",
                            #                                             row[3]).index(
                            #                 split_entity_res[0], pos_of_first_index + 1)
                            #     if not not_found:
                            #         break
                            #
                            # array_of_indexes = []
                            # for j in range(pos_of_first_index,
                            #                pos_of_first_index + len(
                            #                    re.findall(r"[\w']+|[.,!?;]", entity_to_annotate))):
                            #     array_of_indexes.append(j)
                            # # print(array_of_indexes)

                            #  get translated words according to alignment
                            array_of_indexes_target = []
                            for alignment in alignments[i-skipped_lines].split():
                                if int(alignment.split("-")[0]) in array_of_indexes[index_result]:
                                    array_of_indexes_target.append(int(alignment.split("-")[-1]))
                            # array_of_indexes_target = array_of_indexes_target.sort()

                            # print(array_of_indexes_target)
                            if array_of_indexes_target == []:
                                # Error in alignment, so ignore
                                continue
                            # add [ ] before and after words in indexes array_of_indexes_target to mt[i]
                            mt_list = re.findall(r"[\w:']+|[.,!?;]", row[-2])

                            # get stuff that was in {} from "en_with_annotations"
                            entity_details_to_readd = re.findall('{[^}]+}', en_with_annotations)[index_result]
                            #  add stuff ^ after the last index in array_of_indexes_target to mt[i]
                            skip = False
                            for i_check_overlap in range(array_of_indexes_target[0],
                                                         array_of_indexes_target[-1] + 1):
                                if i_check_overlap in indexes_to_avoid:
                                    skip = True
                                    break
                            if not skip:
                                to_insert = to_add_to_line(to_insert, array_of_indexes_target[0] + index_result, "[")
                                to_insert = to_add_to_line(to_insert, array_of_indexes_target[-1] + index_result+ 2,
                                                           "]" + entity_details_to_readd)
                                for i_tmp in range(array_of_indexes_target[0],
                                                   array_of_indexes_target[-1] + 1):
                                    indexes_to_avoid.append(i_tmp)

                        # Reverse order
                        to_insert = list(sorted(to_insert.items()))
                        for val in to_insert:
                            mt_list.insert(val[0], val[1])

                        temp_copy_of_current_mt = " ".join(mt_list)

                        row[-1] = temp_copy_of_current_mt.replace("\n", "") + "\n"

                    writer.writerow(row)

if __name__ == '__main__':
    # convert_multiwoz_to_csv()
    # (Translate)
    # pass_to_fast_align()

    # open wsl and do (at least on laptop):
    # cd /mnt/c/University/RasaPlayground/ConvertingMultiWozToRasa/fast_align-master/fast_align-master/build
    # ./fast_align -i ../../../Converting-MultiWoz-To-Rasa/tmp.txt -d -o -v > ../../../Converting-MultiWoz-To-Rasa/after_forward_align.txt

    # extract_fast_align_results()
    #
    convert_csv_to_multiwoz()
