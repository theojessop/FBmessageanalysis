import json
import string
import os
import fnmatch


content_key = 'content'
sender_key = 'sender_name'


def get_file_names():
    for filename in os.listdir('.'):
        if fnmatch.fnmatch(filename, '*.json'):
            yield filename


def scrub_empties(in_dict):
    for k in [k for k in in_dict if in_dict[k] == 0]:
        del in_dict[k]

files = [open(filename) for filename in get_file_names()]

json_objects = [json.load(file) for file in files]

for file in files:
    file.close()

participants = [o['name'] for o in json_objects[0]['participants']]


def get_messages():
    for json_object in json_objects:
        for message in json_object['messages']:
            if content_key not in message.keys():
                # Skip messages that lack text content (photos, gifs, etc)
                continue
            yield message[content_key]


def write_text_messages_to_file(filename="messages.txt"):
    printable = set(string.printable)
    with open(filename, 'w') as f:
        for item in get_messages():
            try:
                f.write("%s\n" % ''.join(filter(lambda x: x in printable, item)).lower())
            except UnicodeEncodeError:
                print(f'Failed on:\t{item}')

def is_invalid_message(message):
    return content_key not in message.keys() or message[sender_key] not in participants

def rank_senders_by_message_count():
    counts = {k: 0 for k in participants}
    for json_object in json_objects:
        for message in json_object['messages']:
            if is_invalid_message(message):
                continue
            counts[message[sender_key]] += 1
    scrub_empties(counts)
    return counts


def rank_senders_by_word_count():
    wordcounts = {k: 0 for k in participants}
    for json_object in json_objects:
        for message in json_object['messages']:
            if is_invalid_message(message):
                continue
            wordcounts[message[sender_key]] += len(message[content_key].split())
    scrub_empties(wordcounts)
    return wordcounts


message_counts = rank_senders_by_message_count()
word_counts = rank_senders_by_word_count()
assert word_counts.keys() == message_counts.keys()

print(json_objects[0]['title'])

print("\nTotal messages:")
for k in message_counts:
    print(f'{k}:\t{message_counts[k]}')

print("\nWordcounts:")
for k in word_counts:
    print(f'{k}:\t{word_counts[k]}')

print("\nWords per message:")
for k in word_counts:
    print(f'{k}:\t{word_counts[k] / message_counts[k]}')