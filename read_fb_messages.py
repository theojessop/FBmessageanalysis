import json
import string
import os
import fnmatch


content_key = 'content'
sender_key = 'sender_name'
title_key = 'title'


def get_file_names():
    """Identify all .json files in the working directory"""
    for filename in os.listdir('.'):
        if fnmatch.fnmatch(filename, '*.json'):
            yield filename


def scrub_empties(in_dict):
    """Kill entries in a dictionary that have zero value. F's in chat."""
    for k in [k for k in in_dict if in_dict[k] == 0]:
        del in_dict[k]


files = [open(filename) for filename in get_file_names()]

message_stacks = [json.load(file) for file in files]

for file in files:
    file.close()

participants = [o['name'] for o in message_stacks[0]['participants']]


def get_messages():
    for message_stack in message_stacks:
        for message in message_stack['messages']:
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
    """Return false if the message has an unanticipated sender or no text content."""
    return content_key not in message.keys() or message[sender_key] not in participants


def rank_senders_by_message_count():
    counts = {k: 0 for k in participants}
    for json_object in message_stacks:
        for message in json_object['messages']:
            if is_invalid_message(message):
                continue
            counts[message[sender_key]] += 1
    scrub_empties(counts)
    return counts


def rank_senders_by_word_count():
    wordcounts = {k: 0 for k in participants}
    for json_object in message_stacks:
        for message in json_object['messages']:
            if is_invalid_message(message):
                continue
            wordcounts[message[sender_key]] += len(message[content_key].split())
    scrub_empties(wordcounts)
    return wordcounts


message_counts = rank_senders_by_message_count()
word_counts = rank_senders_by_word_count()

# Check that the participants and message titles came out ok
assert word_counts.keys() == message_counts.keys(), "Participants of "
assert all([message_stack[title_key] == message_stacks[0][title_key] for message_stack in message_stacks]), "Titles do not match. Do you have multiple chat logs in the working directory?"

write_text_messages_to_file()

print(message_stacks[0]['title'])

print("\nTotal messages:")
for k in message_counts:
    print(f'{k}:\t{message_counts[k]}')

print("\nWordcounts:")
for k in word_counts:
    print(f'{k}:\t{word_counts[k]}')

print("\nWords per message:")
for k in word_counts:
    print(f'{k}:\t{word_counts[k] / message_counts[k]}')
