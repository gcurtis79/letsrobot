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
    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()

    if male:
        os.system('cat ' + tempFilePath + ' | espeak -v en-us+m%d -s 170 --stdout | aplay -D plughw:%d,0' %(voice_number, hw_num) )
    else:
        os.system('cat ' + tempFilePath + ' | espeak -v en-us+f%d -s 170 --stdout | aplay -D plughw:%d,0' % (voice_number, hw_num) )
    os.remove(tempFilePath)    
