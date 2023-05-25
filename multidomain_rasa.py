# -*- coding: utf-8 -*-
"""
MultiWOZ to Rasa
"""

import json
import random
import string
import nltk
import codecs


def loadDomainStories(readFile):
    with open(readFile, 'r') as f_in:
        data = json.load(f_in)

    domainStories = []
    for story in data:
        domainStories.append(data[story])

    return domainStories


def generateRasaDomain(domainStories, writeFile):
    print('  Domain generation: getting entities...\n')
    entities = getAllEntities(domainStories)
    print('  Domain generation: getting intents...\n')
    intents = getAllIntents(domainStories)
    print('  Domain generation: getting actions...\n')
    actions, messages = getAllActions(domainStories)
    # to-do: figure out response generation.

    print('  Domain generation: writing to file...\n')
    buildRasaDomain(entities, intents, actions, messages, writeFile)


def buildRasaDomain(entities, intents, actions, messages, writeFile):
    with codecs.open(writeFile, 'w', 'utf-8') as f_out:
        f_out.write('version: "3.1"\n')
        # for entity in entities:
        #     f_out.write('  ' + entity + ':\n')
        #     f_out.write('    type: text\n')
        f_out.write('\n' + 'entities:\n')
        for entity in entities:
            f_out.write('- ' + entity + '\n')
        f_out.write('\n' + 'intents:\n')
        for intent in intents:
            f_out.write(' - ' + intent + '\n')
        f_out.write('\n' + 'actions:\n')
        for i, action in enumerate(actions):
            if "inform" in action or "recommend" in action or "select" in action:
                f_out.write('- action_' + action + '\n')
        f_out.write('\n' + 'responses:\n')
        for i, action in enumerate(actions):
            if "inform" not in action and "recommend" not in action and "select" not in action:
                f_out.write('  utter_' + action + ':\n')
                for message in messages[action]:
                    f_out.write('  - text: "' + message + '"\n')
        f_out.write('  utter_default_fallback:\n  - text: "Fallback"')
        f_out.write('\n' + 'session_config:\n  session_expiration_time: 60\n  carry_over_slots_to_new_session: true')


def extract(lst):
    return [item[0] for item in lst]


def getAllActions(domainStories):
    actionsList = []
    messageList = {}
    print(len(domainStories))
    for i, story in enumerate(domainStories):
        if i % 1000 == 0:
            print(i)
        for turn in story['log']:
            if turn['metadata']:
                actionsList = actionsList + intentsFromTurn(turn)
                message_to_add = annotate_utterance_domain(turn['text'], turn['span_info'])
                for action in intentsFromTurn(turn):
                    skip = False
                    if action not in messageList:
                        messageList[action] = []
                        messageList[action].append(message_to_add)
                        skip = True

                    # Todo remove this -
                    if random.random() < 0.2 and not skip:
                        messageList[action].append(message_to_add)
                    # break

        # break

    for key in messageList:
        messageList[key] = [*set(messageList[key])]
    return list(dict.fromkeys(actionsList)), messageList


def getAllEntities(domainStories):
    entitiesList = []
    for story in domainStories:
        for turn in story['log']:
            if not turn['metadata']:
                entitiesList = entitiesList + entitiesFromTurn(turn)

    return list(dict.fromkeys(entitiesList))


def entitiesFromTurn(turn):
    entities = []
    try:
        for slot in turn['span_info']:
            entities.append(slot[1].lower())
    except:
        pass
    return entities


def getAllIntents(domainStories):
    intentsList = []
    for story in domainStories:
        for turn in story['log']:
            if not turn['metadata']:
                intentsList = intentsList + intentsFromTurn(turn)

    return list(dict.fromkeys(intentsList))


def intentsFromTurn(turn):
    intents = []
    try:
        for intent in list(turn['dialog_act'].keys()):
            if 'Request' in intent:
                requestList = constructRequestList(turn['dialog_act'][intent])
                for request in requestList:
                    intents.append(intent.lower() + '-' + request)
            else:
                intents.append(intent.lower())
    except:
        pass
    return intents


def generateRasaStories(domainStories, writeFile):
    print(writeFile)
    with codecs.open(writeFile, 'w+', 'utf-8') as f_out:
        for i, story in enumerate(domainStories):
            f_out.write('## path nr %s\n' % i)
            intents = constructRasaStory(story)
            try:
                for intent in intents:
                    f_out.write(intent + '\n')
            except:
                pass
            f_out.write('\n')


def constructRasaStory(story):
    intents = []
    for turn in story['log']:
        try:
            for intent in list(turn['dialog_act'].keys()):
                core = intent.lower()
                info = ""

                if not turn['metadata']:
                    prefix = " * "
                    if 'Inform' in intent:
                        info = constructInformList(turn['dialog_act'][intent])
                else:
                    if "inform" in intent.lower() or "recommend" in intent.lower() or "select" in intent.lower():
                        prefix = "  - action_"
                    else:
                        prefix = "  - utter_"

                if 'Request' in intent:
                    reqlist = constructRequestList(turn['dialog_act'][intent])
                    for req in reqlist:
                        fullTurn = prefix + core + '-' + req
                        intents.append(fullTurn)
                        continue
                else:
                    fullTurn = prefix + core + info
                    intents.append(fullTurn)
        except:
            pass
    return intents


def constructRequestList(intent):
    requests = []
    for request in intent:
        requests.append(request[0].lower())
    return requests


def constructInformList(intent):
    slots = []
    for slot in intent:
        slots.append("\"" + slot[0].lower() + "\": \"" + slot[1].lower() + "\"")
        # print(slots)
    joinedString = '{' + ', '.join(slot for slot in slots) + '}'
    return joinedString


def generateUtterances(domainStories, writeFile):
    utterancesByIntent = getAllUtterances(domainStories)

    with codecs.open(writeFile, 'w', 'utf-8') as f_out:
        for intent in utterancesByIntent:
            f_out.write('## intent:%s\n' % intent.lower())
            for utter in utterancesByIntent[intent]:
                f_out.write('- %s\n' % utter)
            f_out.write('\n')


def getAllUtterances(domainStories):
    utterancesByIntent = {}

    for story in domainStories:
        for turn in story['log']:
            if not turn['metadata']:
                try:
                    intents = list(turn['dialog_act'].keys())
                    for intent in intents:
                        if intent not in utterancesByIntent:
                            utterancesByIntent[intent] = []
                        utterancesByIntent[intent].append(annotate_utterance(turn['text'], turn['span_info']))
                except:
                    pass

    return utterancesByIntent


# Python code to convert string to list character-wise

def convert(string):
    list1 = []
    list1[:0] = string
    return list1


def annotate_utterance_domain(utter, spans):
    utter = ' '.join(nltk.word_tokenize(utter.lower()))

    for span in spans:
        normalized_token = span[2].lower()

        if ' %s ' % (normalized_token) not in utter \
                and not utter.endswith(' %s' % (normalized_token)) \
                and not utter.startswith('%s ' % (normalized_token)):
            # tokens = nltk.word_tokenize(utter)
            utter = convert(utter)
            # utter[span[-2]] = '[%s' % (utter[span[-2]])
            # utter[span[-1]] = '%s](%s:%s)' % (utter[span[-1]], span[1].lower(), normalized_token)
            utter[span[-1] - 1] = '{%s}' % (span[1].lower())
            utter = ''.join(utter)

    for span in spans:
        normalized_token = span[2].lower()
        annotation = '{%s}' % (span[1].lower())

        token_match = ' %s ' % (normalized_token)
        if token_match in utter:
            utter = utter.replace(token_match, annotation)

        token_match = ' %s' % (normalized_token)
        if utter.endswith(token_match):
            utter = utter.replace(token_match, annotation)

        token_match = '%s ' % (normalized_token)
        if utter.startswith(token_match):
            utter = utter.replace(token_match, annotation)

    tokens = nltk.word_tokenize(utter)
    detokenized = nltk.tokenize.treebank.TreebankWordDetokenizer().detokenize(tokens)
    fixed_markers = detokenized.replace('] (', '](').replace('] {', ']{').replace('[ ', '[').replace(': ', ':').replace(
        '"', '\'')
    fixed_punctuation = string.punctuation.translate(str.maketrans('', '', ':()[]{}'))
    toReturn = fixed_markers.translate(str.maketrans('', '', fixed_punctuation)).replace(' ]', ']').replace('  ', ' ')
    return toReturn


def annotate_utterance(utter, spans):
    utter = ' '.join(nltk.word_tokenize(utter.lower()))

    for span in spans:
        normalized_token = span[2].lower()

        if ' %s ' % (normalized_token) not in utter \
                and not utter.endswith(' %s' % (normalized_token)) \
                and not utter.startswith('%s ' % (normalized_token)):
            tokens = nltk.word_tokenize(utter)
            tokens[span[-2]] = '[%s' % (tokens[span[-2]])
            tokens[span[-1]] = '%s]{"entity": "%s"}' % (tokens[span[-1]], span[1].lower())
            utter = ''.join(tokens)

    for span in spans:
        normalized_token = span[2].lower()
        annotation = ' [%s]{"entity": "%s"}) ' % (normalized_token, span[1].lower())

        token_match = ' %s ' % (normalized_token)
        if token_match in utter:
            utter = utter.replace(token_match, annotation)

        token_match = ' %s' % (normalized_token)
        if utter.endswith(token_match):
            utter = utter.replace(token_match, annotation)

        token_match = '%s ' % (normalized_token)
        if utter.startswith(token_match):
            utter = utter.replace(token_match, annotation)

    tokens = nltk.word_tokenize(utter)
    detokenized = nltk.tokenize.treebank.TreebankWordDetokenizer().detokenize(tokens)
    fixed_markers = detokenized.replace('] {', ']{').replace('{ ', '{').replace('[ ', '[')
    fixed_punctuation = string.punctuation.translate(str.maketrans('', '', ':{}[]""'))
    return fixed_markers.translate(str.maketrans('', '', fixed_punctuation)).replace(' ]', ']').replace('  ', ' ')


def main():
    readFile = 'data/test_full.json'
    rasaStoriesFile = 'converted_files/data/stories.md'
    rasaUtterancesFile = 'converted_files/data/nlu.md'
    rasaDomainFile = '../../domain.yml'

    nltk.download('punkt')
    print('Reading file...\n')
    domainStories = loadDomainStories(readFile)
    print('Generating stories file...\n')
    generateRasaStories(domainStories, rasaStoriesFile)
    print('Generating domain file...\n')
    generateRasaDomain(domainStories, rasaDomainFile)
    print('Generating utterances file...\n')
    generateUtterances(domainStories, rasaUtterancesFile)
    print('Done (:\n')


if __name__ == "__main__":
    main()
