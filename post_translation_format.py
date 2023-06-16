import yaml
import csv

def str_presenter(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

# Go from domain.yml and nlu.yml to nlu.csv and nlg.csv
def create_csv(nlu_en_file, nlu_mt_file, nlg_en_file, nlg_mt_file):
    nlu_list = []
    nlg_list = []
    yaml.add_representer(str, str_presenter)
    # to use with safe_dump:
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter)
    with open(nlu_en_file, 'r', encoding='utf-8') as nlu_in:
        nlu_en = yaml.safe_load(nlu_in)

    with open(nlu_mt_file, 'r', encoding='utf-8') as nlu_in:
        nlu_mt = yaml.safe_load(nlu_in)

    with open(nlg_en_file, 'r', encoding='utf-8') as nlg_in:
        nlg_en = yaml.safe_load(nlg_in)

    with open(nlg_mt_file, 'r', encoding='utf-8') as nlg_in:
        nlg_mt = yaml.safe_load(nlg_in)

    # starting with NLU
    for i, intent in enumerate(nlu_en["nlu"]):
        # print(intent)
        en_examples = intent["examples"].splitlines()
        mt_examples = nlu_mt["nlu"][i]["examples"].splitlines()
        nlu_list.append(["\n", "\n"])
        nlu_list.append(["intent (DONT TRANSLATE): " + intent["intent"], "intent (DONT TRANSLATE): " + intent["intent"]])
        for j, example in enumerate(en_examples):
            nlu_list.append([example, mt_examples[j]])
        print("")
        # examples_to_add = file_in.read().splitlines()
        # for i, example in enumerate(examples_to_add):
        #     examples_to_add[i] = "- " + example
        # intent["examples"] = "\n".join(examples_to_add)

    for i, intent in enumerate(nlg_en["responses"]):
        en_examples = nlg_en["responses"][intent]
        mt_examples = nlg_mt["responses"][intent]
        nlg_list.append(["\n", "\n"])
        nlg_list.append(["intent (DONT TRANSLATE): " + intent, "intent (DONT TRANSLATE): " + intent])
        for j, _ in enumerate(en_examples):
            nlg_list.append([en_examples[j]["text"], mt_examples[j]["text"]])
        print("")
    #
    # with open(input_dir + "/" + filename, "r", encoding='utf-8') as file_in:
    #     responses = []
    #     for response in file_in.read().splitlines():
    #         if response != "\n":
    #             responses.append({"text": response})
    #     nlg["responses"][filename.replace("final_translations_withannotationsnlg_", "").replace(".txt", "")] = responses
    #
    #
    with open("nlu.csv", 'w', encoding='utf-8', newline='') as nlu_out:
        writer = csv.writer(nlu_out)
        for row in nlu_list:
            writer.writerow(row)
    with open("nlg.csv", 'w', encoding='utf-8') as nlg_out:
        writer = csv.writer(nlg_out)
        for row in nlg_list:
            writer.writerow(row)


create_csv("converted_files/data/nlu.yml", "converted_files/data/nlu_maltese_testversion.yml", "converted_files/data/domain.yml", "converted_files/data/nlg_maltese_testversion.yml")