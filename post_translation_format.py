# OLD. SEE README.md for the updated overview

import re

import yaml
import csv

import codecs

responses_beginning = """
version: "3.1"

intents:
- greet
- nlu_fallback
- regist-docs.accepted
- regist-docs.error-generic
- regist-docs.expired
- regist-docs.formats
- regist-docs.residence-proof
- regist-docs.upload-modify
- regist-docs.why
- regist-docs.check
- regist-docs.residence-list
- regist-docs.residence-verify
- regist-docs.error-change
- regist-docs.exclamation-mark
- regist-docs.residence-no
- regist-docs.upload-multiple-docs
- regist-docs.upload-deletion
- regist-docs.upload-replacement
- registration.verification-code
- registration.telephone.error
- registration.no-want
- registration.present
- registration.password.error
- registration.problem-otp
- access.mail-not-present
- access.guest
- registration.minor
- form-fill.grey-fields
- form-fill.address
- form-fill.no_land_line
- form-fill.occupation_why
- form-fill.occupation_mandatory
- form-fill.occupation_list
- form-fill.other
- form-fill.other-not-editable
- form-fill.problem-spouse
- form-fill.missing-field
- form-fill.spouse-why
- form-fill.dependent-children-why
- form-fill.family-status-why
- form-fill.beneficiary.no
- form-fill.beneficiary
- form-fill.children_why
- form-fill.separated
- form-fill.other-request
- onboarding.fourth-bank
- onboarding.broker-definition
- onboarding.currency
- onboarding.imports
- onboarding.engagement
- onboarding.engagement-amount
- onboarding.pep_advantages
- onboarding.pep_definition
- onboarding.pep_why
- onboarding.American_taxes_definition
- onboarding.American_taxes_why
- onboarding.fiscal_residency_def
- onboarding.fiscal_residency_multi
- onboarding.fiscal_residency_why
- onboarding.TIN_definition
- onboarding.TIN_where
- onboarding.TIN_why
- onboarding.payment-method
- onboarding.account-type
- onboarding.account-why
- onboarding.account-open
- onboarding.activity-enter
- onboarding.activity-mandatory
- onboarding.job-not-present
- onboarding.job-years
- onboarding.job-years-why
- onboarding.job-years-zero
- onboarding.job-years-less-than-one
- onboarding.source-definition
- onboarding.source-multiple
- onboarding.source-active
- onboarding.asset-details
- onboarding.source-other
- onboarding.second-residency-why
- onboarding.privacy
- onboarding.privacy-why
- onboarding.activity-countries
- onboarding.activity-number
- onboarding.activity-delete
- onboarding.activity-country-delete
- mifid.update-info
- mifid.omit-info
- mifid.help-fill
- mifid.professional-client
- mifid.update-name-surname
- mifid.why-education-level
- mifid.education-level
- mifid.finance-professionist
- mifid.tool-knowledge-no
- mifid.investment-not-listed
- mifid.ethical-exclusion
- mifid.tax-exclusion
- mifid.time-horizon-advantages
- mifid.time-horizon-different
- mifid.heritage-percentage-for-expenses
- mifid.investor-strategy
- mifid.heritage-notification-no
- mifid.heritage-value-precision
- mifid.heritage-binding
- mifid.self-assessment
- mifid.variable-annual-saving
- mifid.privacy-health-information
- mifid.questionnaire-modification
- mifid.disinvestment-costs
- mifid.example-swing-investment
- mifid.different-returns-investimento
- general.mifid-certified-user
- general.messagges
- videocall-description
- videocall-avoid
- videocall-impossible
- sign.how
- sign.where
- sign.error-spec-characters
- sign.OTP-code
- sign.error-OTP-code
- sign.signed-documents
- sign.coupon
- sign.order-payment

entities:
- identity_document_entity
- accepted_formats_entity
- proof_of_residence_entity
- contacts_entity

slots:
  identity_document_slot:
    type: text
    mappings:
    - type: from_entity
      entity: identity_document_entity
  accepted_formats_slot:
    type: categorical
    mappings:
    - type: from_entity
      entity: accepted_formats_entity
  proof_of_residence_slot:
    type: categorical
    mappings:
    - type: from_entity
      entity: proof_of_residence_entity
  contacts_slot:
    type: categorical
    mappings:
    - type: from_entity
      entity: contacts_entity
responses:
"""

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
        nlu_list.append(
            ["intent (DONT TRANSLATE): " + intent["intent"], "intent (DONT TRANSLATE): " + intent["intent"]])
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


#
# def readd_annotations(all_slots, sentence_in):
#     to_insert = {}
#     for index_result, entity_res in enumerate(all_slots):
#         # get array of position indexs of result.group(1)
#
#         split_entity_res = re.findall(r"[\w:']+|[.,!?;]", entity_res)
#
#         pos_of_first_index = re.findall(r"[\w:']+|[.,!?;]", sentence_in).index(split_entity_res[0])
#         not_found = False
#         while True:
#             if not_found:
#                 not_found = False
#             for j, entity_word in enumerate(split_entity_res):
#                 if re.findall(r"[\w:']+|[.,!?;]", sentence_in)[pos_of_first_index + j] != split_entity_res[
#                     j]:
#                     not_found = True
#                     pos_of_first_index = re.findall(r"[\w:']+|[.,!?;]", sentence_in).index(
#                         split_entity_res[0], pos_of_first_index + 1)
#             if not not_found:
#                 break
#
#         # if len(re.findall(r"[\w']+|[.,!?;]", result.group(1))) > 1 and \
#         #         re.findall(r"[\w']+|[.,!?;]", en_no_annotations[i])[pos_of_first_index + 1] != \
#         #         re.findall(r"[\w']+|[.,!?;]", result.group(1))[1]:
#         #     print("ISSUE")
#         array_of_indexes = []
#         for j in range(pos_of_first_index,
#                        pos_of_first_index + len(re.findall(r"[\w']+|[.,!?;]", entity_res))):
#             array_of_indexes.append(j)
#         # print(array_of_indexes)
#
#         #  get translated words according to alignment
#         array_of_indexes_target = []
#         for alignment in alignments[i].split():
#             if int(alignment.split("-")[0]) in array_of_indexes:
#                 array_of_indexes_target.append(int(alignment.split("-")[-1]))
#         # array_of_indexes_target = array_of_indexes_target.sort()
#
#         # print(array_of_indexes_target)
#         if array_of_indexes_target == []:
#             # Error in alignment, so ignore
#             continue
#         # add [ ] before and after words in indexes array_of_indexes_target to mt[i]
#         mt_list = re.findall(r"[\w:']+|[.,!?;]", mt[i])
#
#         # get stuff that was in {} from "line"
#         entity_details_to_readd = re.findall('{[^}]+}', line)[index_result]
#         #  add stuff ^ after the last index in array_of_indexes_target to mt[i]
#         skip = False
#         for i_check_overlap in range(array_of_indexes_target[0], array_of_indexes_target[-1] + 2):
#             if i_check_overlap in indexes_to_avoid:
#                 skip = True
#                 break
#         if not skip:
#             to_insert = to_add_to_line(to_insert, array_of_indexes_target[0], "[")
#             to_insert = to_add_to_line(to_insert, array_of_indexes_target[-1] + 2, "]" + entity_details_to_readd)
#             for i_tmp in range(array_of_indexes_target[0], array_of_indexes_target[-1] + 2):
#                 indexes_to_avoid.append(i_tmp)
#
#     # Reverse order
#     to_insert = list(sorted(to_insert.items()))[::-1]
#     for val in to_insert:
#         mt_list.insert(val[0], val[1])
#     temp_copy_of_current_mt = " ".join(mt_list)
#
#     mt_out.write(temp_copy_of_current_mt.replace("\n", "") + "\n")

def add_annotations_to_chatgpt(file_in, file_out):
    with open(file_in, 'r', encoding='utf-8') as file_to_annotate:
        with open(file_out, "w+", newline='', encoding='utf-8') as file_to_write:
            csv_reader = csv.reader(file_to_annotate, delimiter=',')
            writer = csv.writer(file_to_write)

            for i, line in enumerate(csv_reader):
                try:
                    print(line)
                    copy_of_line = line
                    if i < 3:
                        pass
                    elif line[1] == "":
                        pass
                    # Original data
                    elif not line[1][0].isdigit():
                        last_original_line = line[1].replace("à", "a'").strip()  # get stuff between []
                        mt_list = re.findall(r'\[(.*?)\]', last_original_line)
                        for index_mt, mt in enumerate(mt_list):
                            mt_list[index_mt] = mt.replace("à", "a'").strip()

                        # get stuff between {}
                        entity_details_to_readd = re.findall('{[^}]+}', last_original_line)

                        if len(entity_details_to_readd) != len(mt_list):
                            print()
                    # ChatGPT data
                    else:
                        copy_of_line[0] = copy_of_line[0].lstrip('0123456789.- ')
                        copy_of_line[1] = copy_of_line[1].lstrip('0123456789.- ')

                        for slot_index, slot in enumerate(mt_list):
                            # print(line[1])
                            # print(slot)
                            copy_of_line[1] = copy_of_line[1].replace("à", "a'").replace(slot, "[" + slot + "]" + entity_details_to_readd[slot_index].replace("entità", "entity"))
                            # print(copy_of_line[1])
                    # write a row to the csv file
                    writer.writerow(copy_of_line)
                except:
                    print("ERROR")


def reconstruct_nlu(file_in, nlu_out):
    with codecs.open(nlu_out, 'w+', 'utf-8') as f_out:
        with open(file_in, 'r', encoding='utf-8') as file_to_annotate:
            csv_reader = csv.reader(file_to_annotate, delimiter=',')
            f_out.write("version: '3.1'\n\nnlu:\n")
            for i, line in enumerate(csv_reader):
                print(line)
                try:
                    if i == 0:
                        pass
                    elif "DONT TRANSLATE" in line[0] :
                        # Create  - intent: + actual_intent + "\nexamples: |\n"
                        f_out.write('- intent: %s\n' % line[1].replace("intent (DONT TRANSLATE): ", "").replace("intenzjoni (DONT TRANSLATE): ", ""))
                        f_out.write('  examples: |\n')
                    elif line[1] == "":
                        pass
                    else:
                        # remove numbers and add the actual examples
                        toWrite = line[1].replace(']{"entità":', ']{"entity":' ).replace(']{"entita\'":', ']{"entity":' )
                        # Remove "- " at the beginning of some strings
                        if toWrite.startswith('- '):
                            toWrite = toWrite[2:]
                        if toWrite.endswith(':'):
                            toWrite = toWrite[:-1]
                        f_out.write('    - %s\n' % toWrite)
                        pass
                    # f_out.write('\n')

                except:
                    print("error")

def reconstruct_nlg(file_in, nlg_out):
    with codecs.open(nlg_out, 'w+', 'utf-8') as f_out:
        with open(file_in, 'r', encoding='utf-8') as file_to_annotate:
            csv_reader = csv.reader(file_to_annotate, delimiter=',')
            f_out.write(responses_beginning)
            data_list = list(csv_reader)
            skip_next_line = False
            for i, line in enumerate(data_list):
                print(line)
                if skip_next_line:
                    skip_next_line = False
                    continue

                try:
                    next_line = data_list[i+1]
                    j = 0

                    while next_line[1] == "":
                        j += 1
                        next_line = data_list[i+1 + j]
                except:
                    print("last line")
                    pass


                if i == 0:
                    continue

                elif "DONT TRANSLATE" in line[0]:
                    # Create  - intent: + actual_intent + "\nexamples: |\n"
                    f_out.write('  %s:\n' % line[1].replace("intent (DONT TRANSLATE): ", "").replace("intenzjoni (DONT TRANSLATE): ", "").replace("intenzjoni (M'għandekx tittraduċi): ", ""))
                    # f_out.write('  examples: |\n')
                    continue
                elif line[1] == "" or line[1] == ",":
                    continue

                try:
                    if data_list[i+1][1] != "" and data_list[i+1][1] != "," and "DONT TRANSLATE" not in data_list[i+1][0]:
                        line[0] += "\\n" + next_line[0]
                        line[1] += "\\n" + next_line[1]
                        skip_next_line = True
                except:
                    print("last line")
                if "{" in next_line[1]:
                    # get stuff between {}
                    slots = re.findall('{[^}]+}', next_line[1])
                    if len(slots) > 0:
                        for slot in slots:
                            f_out.write("  - condition:\n    - type: slot\n      name: ")
                            f_out.write(slot.replace("{", "").replace("}", ""))
                            f_out.write("\n      value: null")
                            f_out.write('\n    text: "%s"\n' % line[1].replace("\"", "").replace("\n", "\\n"))
                else:
                    f_out.write('  - text: "%s"\n' % line[1].replace("\"", "").replace("\n", "\\n"))
                    pass
                # f_out.write('\n')


            f_out.write("""
session_config:
  session_expiration_time: 60
  carry_over_slots_to_new_session: true
            """)
# create_csv("converted_files/data/nlu.yml", "converted_files/data/nlu_maltese_testversion.yml", "converted_files/data/domain.yml", "converted_files/data/nlg_maltese_testversion.yml")
# create_csv("converted_files/data/nlu.yml", "converted_files/data/nlu_maltese_testversion.yml", "converted_files/data/domain.yml", "domain.yml")
add_annotations_to_chatgpt("concat_nlu.csv", "updated_user_stories_to_translate.csv")
reconstruct_nlu("updated_user_stories_to_translate.csv", "nlu.yml")
reconstruct_nlg("responses.csv", "domain.yml")






