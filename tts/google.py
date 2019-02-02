import os
import extended_command
import logging
log = logging.getLogger('LR.tts.google')

# When using Google as TTS, you can specify a language. This makes the voice
# speak that languange more accuately, but also gives an interesting accent
# Refer to https://ctrlq.org/code/19899-google-translate-languages#languages
# for language choices.
# This is also configuable via '.lang es' in chat. 2-letter locale codes only.
google_language = 'it'

# Set a maximum queue length of stacked messages before blocking
# set this to False to disable
max_queue = False

playing = False

hw_num = None

_message_queue = []


def googleSay(message):
    global playing
    if not max_queue and len(_message_queue) <= max_queue:  # Queue length control
        _message_queue.append(message)
    if playing:  # If playing, add to queue and exit
        return
    playing = True
    while len(_message_queue) > 0:  # Keep playing until queue is exhausted
        message = _message_queue.pop(0).lstrip().replace(" ", "%20")
        cmdLine = ('wget --header "Referer: http://translate.google.com/" --header "User-Agent: stagefright/1.2 (Linux;Android 5.0)" -qO- "https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl={lang}&client=tw-ob" | aplay -D plughw:{hw_num},0').format(msg=message, lang=google_language, hw_num=hw_num)
        os.devnull = os.system(cmdLine)
    playing = False


def setLang(command, args):
    print("lang command triggered: %s" % (command))
    global google_language
    if extended_command.is_authed(args['name']) >= 1: # Moderator or owner
        if len(command) == 2:
            if len(command[1]) == 2:
                google_language = command[1]
            


def setup(robot_config):
    global hw_num
    hw_num = robot_config.getint('tts', 'hw_num')
    if robot_config.getboolean('tts', 'ext_chat'):
        import extended_command
        extended_command.add_command('.lang', setLang)
    return


def say(*args):
    message = args[0]
    googleSay(message)
