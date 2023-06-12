import subprocess

import yaml
import re
def nlu(input_file):
    with open(input_file, 'r', encoding='utf-8') as nlu_in:
        nlu = yaml.safe_load(nlu_in)["nlu"]
        for intent in nlu:
            with open("converted_files/data/totranslate/nlu_" + intent["intent"] + ".txt", "w+", encoding='utf-8') as file_nlu_out:
                with open("converted_files/data/totranslate_withannotations/nlu_" + intent["intent"] + ".txt", "w+", encoding='utf-8') as file_nlu_out_with_annotations:

                    file_nlu_out_with_annotations.write(intent["examples"])
                    toWrite = intent["examples"].replace("- ", "").replace("[", "").replace("]", "")
                    toWrite = re.sub(r'\{([^{}]*)\}', '', toWrite)
                    file_nlu_out.write(toWrite)

        print(yaml.safe_load(nlu_in))

def nlg(input_file):
    with open(input_file, 'r', encoding='utf-8') as nlg_in:
        nlg = yaml.safe_load(nlg_in)["responses"]
        for intent in nlg:
            with open("converted_files/data/totranslate/nlg_" + intent + ".txt", "w+", encoding='utf-8') as file_nlg_out:
                with open("converted_files/data/totranslate_withannotations/nlg_" + intent + ".txt", "w+",
                          encoding='utf-8') as file_nlg_out_with_annotations:
                    for example in nlg[intent]:
                        file_nlg_out_with_annotations.write(example["text"]+ "\n")
                        toWrite = example["text"].replace("- ", "").replace("[", "").replace("]", "")
                        toWrite = re.sub(r'\{([^{}]*)\}', '', toWrite)
                        file_nlg_out.write(toWrite + "\n")

        print(yaml.safe_load(nlg_in))


import os


def merge_nlu(input_dir, original_nlu, original_domain):
    directory = os.fsencode(input_dir)

    def str_presenter(dumper, data):
        if len(data.splitlines()) > 1:  # check for multiline string
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, str_presenter)
    # to use with safe_dump:
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
    with open(original_nlu, 'r', encoding='utf-8') as nlu_in:
        nlu = yaml.safe_load(nlu_in)

    with open(original_domain, 'r', encoding='utf-8') as nlg_in:
        nlg = yaml.safe_load(nlg_in)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("final_translations_withannotationsnlu_"):
            for intent in nlu["nlu"]:
                if intent["intent"] in filename.replace("nlu_", "").replace(".txt", ""):
                    with open(input_dir  + "/" + filename, "r", encoding='utf-8') as file_in:
                        # print(file_in.read().splitlines())
                        examples_to_add = file_in.read().splitlines()
                        for i, example in enumerate(examples_to_add):
                            examples_to_add[i] = "- " + example
                        intent["examples"] = "\n".join(examples_to_add)
            # continue
        elif filename.startswith("final_translations_withannotationsnlg_"):
            with open(input_dir + "/" + filename, "r", encoding='utf-8') as file_in:
                responses = []
                for response in file_in.read().splitlines():
                    if response != "\n":
                        responses.append({"text": response})
                nlg["responses"][filename.replace("final_translations_withannotationsnlg_", "").replace(".txt", "")] = responses
            # continue

    with open("converted_files/data/nlu_maltese_testversion.yml", 'w', encoding='utf-8') as nlu_out:
        yaml.dump(nlu, nlu_out, default_flow_style=False, allow_unicode=True, sort_keys=False)

    with open("converted_files/data/nlg_maltese_testversion.yml", 'w', encoding='utf-8') as nlg_out:
        yaml.dump(nlg, nlg_out, default_flow_style=False, allow_unicode=True, sort_keys=False)





import re


def remove_annotationcs():
    with open("./tmp2nlg/totranslate_withannotations.en", "r", encoding="utf-8") as en_in:
        with open("./tmp2nlg/totranslate.txt", "w+", encoding="utf-8") as en_out:
            en = en_in.readlines()
            for line in en:
                # if "{" not in line:
                #     continue

                # Remove stuff between { }
                line = re.sub('{[^}]+}', '', line)
                print(line.replace("[", "").replace("]", ""))
                en_out.write(line.replace("[", "").replace("]", ""))
                # print(line)


def pass_to_fast_align(translate_dir, totranslate_dir):
    directory = os.fsencode(translate_dir)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.startswith("nlu_") or filename.startswith("nlg_"):

            with open(translate_dir + "/" + filename, "r", encoding='utf-8') as results_in:
                with open(totranslate_dir + "/" + filename, "r", encoding="utf-8") as en_in_no_annotations:
                    with open(totranslate_dir + "/" + filename + "_tmp.txt", "w+", encoding="utf-8") as tmp:
                        mt = results_in.readlines()
                        en_no_annotations = en_in_no_annotations.readlines()
                        for i, line in enumerate(en_no_annotations):
                            # if "{" not in line:
                            #     continue

                            # result = re.search('\[(.*)\]', line)
                            # print(line)
                            # print(en_no_annotations[i])
                            # print(mt[i])
                            # print(result.group(1))

                            if not re.findall(r"[\w:']+|[.,!?;]", en_no_annotations[i].replace("\n", "")):
                                continue

                            tmp.write(" ".join(
                                re.findall(r"[\w:']+|[.,!?;]", en_no_annotations[i].replace("\n", ""))) + " ||| " + " ".join(
                                re.findall(r"[\w:']+|[.,!?;]", mt[i])))
                            tmp.write("\n")
                            # os.system('wsl cd ~/../../mnt/c/University/PHD/rasa-test/Converting-MultiWoz-To-Rasa/totranslate/ \&\& ls -l > filelist.txt')
                            # print(subprocess.check_call(['wsl', 'ls -l totranslate']))
    # print(subprocess.check_call(['wsl',
    #                              '~/../../mnt/c/University/PHD/rasa-test/Converting-MultiWoz-To-Rasa/totranslate/fast_align.sh']))
                        # print(line)


def extract_fast_align_results(translate_dir, totranslate_dir):

    directory = os.fsencode(totranslate_dir)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".txt_forward.align"):
            original_filename = filename.replace("_tmp.txt_forward.align", "")
            with open(totranslate_dir + filename, "r", encoding="utf-8") as alignment:
                print(translate_dir + original_filename)
                with open(translate_dir + original_filename, "r", encoding="utf-8") as results_in:
                    print("converted_files/data/totranslate_withannotations/" + original_filename)
                    with open("converted_files/data/totranslate_withannotations/" + original_filename, "r", encoding="utf-8") as en_in:

                        print(totranslate_dir + original_filename)
                        with open(totranslate_dir + original_filename, "r", encoding="utf-8") as en_in_no_annotations:
                            print(translate_dir + "final_translations_withannotations" + original_filename)
                            with open(translate_dir + "final_translations_withannotations" + original_filename, "w", encoding="utf-8") as mt_out:
                                en = en_in.readlines()
                                mt = results_in.readlines()
                                en_no_annotations = en_in_no_annotations.readlines()
                                alignments = alignment.readlines()
                                for i, line in enumerate(en):

                                    if "{" not in line:
                                        mt_out.write(mt[i])
                                        continue

                                    # get all stuff in []
                                    result = re.findall('\[(.*?)\]', line)
                                    # print(line)
                                    # print(en_no_annotations[i])
                                    # print(mt[i])
                                    # print(result.group(1))
                                    # print(alignments[i])
                                    try:
                                        for entity_res in result:
                                        #get array of position indexs of result.group(1)

                                            split_entity_res = re.findall(r"[\w:']+|[.,!?;]", entity_res)

                                            pos_of_first_index = re.findall(r"[\w:']+|[.,!?;]", en_no_annotations[i]).index(split_entity_res[0])
                                            not_found = False
                                            temp_copy_of_current_mt = mt[i]
                                            while True:
                                                if not_found:
                                                    not_found = False
                                                for j, entity_word in enumerate(split_entity_res):
                                                    if re.findall(r"[\w:']+|[.,!?;]", en_no_annotations[i])[pos_of_first_index + j] != split_entity_res[j]:
                                                        not_found = True
                                                        pos_of_first_index = re.findall(r"[\w:']+|[.,!?;]", en_no_annotations[i]).index(split_entity_res[0], pos_of_first_index+1)
                                                if not not_found :
                                                    break

                                            # if len(re.findall(r"[\w']+|[.,!?;]", result.group(1))) > 1 and \
                                            #         re.findall(r"[\w']+|[.,!?;]", en_no_annotations[i])[pos_of_first_index + 1] != \
                                            #         re.findall(r"[\w']+|[.,!?;]", result.group(1))[1]:
                                            #     print("ISSUE")
                                            array_of_indexes = []
                                            for j in range(pos_of_first_index,
                                                           pos_of_first_index + len(re.findall(r"[\w']+|[.,!?;]", entity_res))):
                                                array_of_indexes.append(j)
                                            # print(array_of_indexes)

                                            #  get translated words according to alignment
                                            array_of_indexes_target = []
                                            for alignment in alignments[i].split():
                                                if int(alignment.split("-")[0]) in array_of_indexes:
                                                    array_of_indexes_target.append(int(alignment[-1]))
                                            # array_of_indexes_target = array_of_indexes_target.sort()

                                            # print(array_of_indexes_target)
                                            if array_of_indexes_target == []:
                                                # Error in alignment, so ignore
                                                continue
                                            #                       add [ ] before and after words in indexes array_of_indexes_target to mt[i]
                                            mt_list = re.findall(r"[\w:']+|[.,!?;]", mt[i])
                                            mt_list.insert(array_of_indexes_target[0], "[")
                                            mt_list.insert(array_of_indexes_target[-1] + 2, "]")

                                            # get stuff that was in {} from "line"
                                            entity_details_to_readd = re.findall('{[^}]+}', line)[0]
                                            # print(entity_details_to_readd)

                                            #  add stuff ^ after the last index in array_of_indexes_target to mt[i]

                                            mt_list.insert(array_of_indexes_target[-1] + 3, entity_details_to_readd)
                                            temp_copy_of_current_mt = " ".join(mt_list)

                                        mt_out.write(temp_copy_of_current_mt.replace("\n", "") + "\n")
                                    except:
                                        print("error")
                                        mt_out.write(mt[i].replace("\n", "") + "\n")
                                        continue


# nlu("converted_files/data/nlu.yml")
# nlg("totranslate/domain.yml")
# #
# # Translate and put back in ./translated
pass_to_fast_align("./translated", "./totranslate")


# open wsl and do:
# cd ../../University/PHD/rasa-test/Converting-MultiWoz-To-Rasa/totranslate/
# ./fast_align.sh


extract_fast_align_results("./translated/", "./totranslate/")
#
merge_nlu("./translated", "converted_files/data/nlu.yml","totranslate/domain.yml")
