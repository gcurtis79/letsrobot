import os
import tempfile
import uuid
import logging

log = logging.getLogger('LR.tts.espeak')

male = None
voice_number = None
hw_num = None
custom_voice = None

max_queue = False
playing = False
_message_queue = []

def setup(robot_config):
    global male
    global voice_number
    global hw_num
    global custom_voice

    male = robot_config.getboolean('espeak', 'male')
    voice_number = robot_config.getint('espeak', 'voice_number')
    hw_num = robot_config.getint('tts', 'hw_num')
    custom_voice = robot_config.get('espeak', 'custom_voice')


def say(*args):
    message = args[0]
<<<<<<< HEAD
    global playing
    if not max_queue and len(_message_queue) <= max_queue:  # Queue length control
        _message_queue.append(message)
    if playing:  # If playing, add to queue and exit
        return
    playing = True
    while len(_message_queue) > 0:  # Keep playing until queue is exhausted
        saythis = _message_queue.pop(0).lstrip()
        #cmdLine = ('wget --header "Referer: http://translate.google.com/" --header "User-Agent: stagefright/1.2 (Linux;Android 5.0)" -qO- "https://translate.google.com/translate_tts?ie=UTF-8&q={msg}&tl={lang}&client=tw-ob" | ffplay -loglevel quiet -nodisp -autoexit -').format(msg=message, lang=google_language)
        if male:
            voice = ('en-us+m%d' % (voice_number))
        if not male:
            voice = ('en-us+f%d -s170' % (voice_number))
        if custom_voice:
            voice = ('%s' % (custom_voice))
        cmdLine = ('espeak -v%s -s170 --stdout "%s" 2>/dev/null | aplay -q -D plughw:%d,0' % (voice, str(saythis), hw_num))
        os.devnull = os.system(cmdLine)
    playing = False
=======
    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()

    if male:
        os.system('cat ' + tempFilePath + ' | espeak -v en-us+m%d -s 170 --stdout | aplay -D plughw:%d,0' %(voice_number, hw_num) )
    else:
        os.system('cat ' + tempFilePath + ' | espeak -v en-us+f%d -s 170 --stdout | aplay -D plughw:%d,0' % (voice_number, hw_num) )
    os.remove(tempFilePath)    
>>>>>>> 0111c17a2f88e8b94faaf3629302034dd5b387d7
