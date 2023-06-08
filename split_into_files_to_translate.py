import yaml
import re
def nlu(input_file):
    with open(input_file, 'r', encoding='utf-8') as nlu_in:
        nlu = yaml.safe_load(nlu_in)["nlu"]
        for intent in nlu:
            with open("converted_files/data/totranslate/nlu_" + intent["intent"] + ".txt", "w+", encoding='utf-8') as file_nlu_out:
                toWrite = intent["examples"].replace("- ", "").replace("[", "").replace("]", "")
                toWrite = re.sub(r'\{(.*)}', '', toWrite)
                file_nlu_out.write(toWrite)

        print(yaml.safe_load(nlu_in))

def nlg(input_file):
    with open(input_file, 'r', encoding='utf-8') as nlg_in:
        nlg = yaml.safe_load(nlg_in)["responses"]
        for intent in nlg:
            with open("converted_files/data/totranslate/nlg_" + intent + ".txt", "w+", encoding='utf-8') as file_nlg_out:
                for example in nlg[intent]:
                    toWrite = example["text"].replace("- ", "").replace("[", "").replace("]", "")
                    toWrite = re.sub(r'\{(.*)}', '', toWrite)
                    file_nlg_out.write(toWrite + "\n")

        print(yaml.safe_load(nlg_in))


# nlu("converted_files/data/nlu.yml")
nlg("totranslate/domain.yml")
