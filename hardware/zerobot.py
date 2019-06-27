#
# zerobot.py - by gcurtis79
# Modeled after l298n.py
# For a Pi Zero W with direct pin-to-motor-controller connection
#
# Make sure to set pins in letsrobot.conf [zerobot] section
#

import pigpio
# import pysftp
import requests
import os
import time
import extended_command
import logging
import schedule
import subprocess
import sys
import atexit
#import BlynkLib
from configparser import ConfigParser
import importlib
import _thread as thread
import tts.tts as tts

robot_config = ConfigParser()
robot_config.readfp(open('letsrobot.conf'))
pi = pigpio.pi()
log = logging.getLogger('LR.hardware.zerobot')

stopTheMotors = 0

startTime = time.time()

def cinc(n, smallest, largest, change):
    n += change
    return max(smallest, min(n, largest))


# Quickie clamp function cuz I'm lazy. (Or maybe not)
def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))


# Save config options
def config_save(section, param, value):
    robot_config.set(section, param, str(value))
    log.info('Setting %s/%s to %s', section, param, str(value))
    with open('letsrobot.conf', 'w') as configfile:
        robot_config.write(configfile)
        configfile.close()


# Function for setting turn delay
def set_turn_delay(command, args):
    global turnDelay
    if extended_command.is_authed(args['name']) == 2:
        if len(command) > 1:
            turnDelay = float(command[1])
            #blynk.virtual_write(1, turnDelay)
            config_save('zerobot', 'turnDelay', turnDelay)
            log.info("Rotate delay set to : %f", float(command[1]))


# Function for setting drive delay
def set_drive_delay(command, args):
    global driveDelay
    if extended_command.is_authed(args['name']) == 2:
        if len(command) > 1:
            driveDelay = float(command[1])
            #blynk.virtual_write(2, driveDelay)
            config_save('zerobot', 'driveDelay', driveDelay)
            log.info("Drive delay set to : %f", driveDelay)


# Function for setting drive speed
def set_drive_speed(command, args):
    global pwm_speed
    #global hud_url
    if extended_command.is_authed(args['name']) == 2:
        if len(command) > 1:
            pwm_speed = clamp(int(command[1]), 100, 180)
            #blynk.virtual_write(3, pwm_speed)
            #requests.post(hud_url, data={'maxspeed': pwm_speed})
            config_save('zerobot', 'pwm_speed', pwm_speed)
            log.info("Drive speed set to : %d", pwm_speed)


# Function for setting steering bias
def set_bias(command, args):
    global steeringBias
    if extended_command.is_authed(args['name']) == 2:
        if len(command) > 1:
            steeringBias = int(command[1])
            #blynk.virtual_write(4, steeringBias)
            steeringBias = int(command[1])
            #requests.post(hud_url, data={'steeringbias': steeringBias})
            config_save('zerobot', 'steeringbias', steeringBias)
            log.info("Steering bias set to : %d", steeringBias)


# Motor watchdog, stops motors in case of signal stall
def stopMotors(v1=0, v2=0):
    while (1):
        global driveDelay
        global stopTheMotors
        if stopTheMotors == 1:
            for i in range(0, 4):
                pi.write(motorPins[i], 0)
        if stopTheMotors == 0:
            stopTheMotors = 1
            time.sleep(driveDelay)

def setup(robot_config):

    global motorPins
    motorPins = [int(robot_config.get('zerobot', 'zerobot1A')),
                 int(robot_config.get('zerobot', 'zerobot1B')),
                 int(robot_config.get('zerobot', 'zerobot2A')),
                 int(robot_config.get('zerobot', 'zerobot2B'))]

    global driveDelay
    driveDelay = float(robot_config.getfloat('zerobot', 'driveDelay'))
    global turnDelay
    turnDelay = float(robot_config.getfloat('zerobot', 'turnDelay'))
    global steeringBias
    steeringBias = int(robot_config.getfloat('zerobot', 'steeringBias'))
    global pwm_freq
    pwm_freq = int(robot_config.getfloat('zerobot', 'pwm_freq'))
    global pwm_range
    pwm_range = int(robot_config.getfloat('zerobot', 'pwm_range'))
    global pwm_speed
    pwm_speed = int(robot_config.getfloat('zerobot', 'pwm_speed'))
    #global hud_url
    #os.devnull = requests.post(hud_url,
    #                           data={'steeringbias': steeringBias,
    #                                 'maxspeed': pwm_speed})

    # Activate chat commands for motor settings
    if robot_config.getboolean('tts', 'ext_chat'):
        extended_command.add_command('.set_turn_delay', set_turn_delay)
        extended_command.add_command('.set_drive_delay', set_drive_delay)
        extended_command.add_command('.set_speed', set_drive_speed)
        extended_command.add_command('.set_bias', set_bias)

    # Init the pins into the array and configure them
    for i in range(0, 4):
        pi.set_mode(motorPins[i], pigpio.OUTPUT)
        pi.write(motorPins[i], 0)
        pi.set_PWM_range(motorPins[i], pwm_range)
        pi.set_PWM_frequency(motorPins[i], pwm_freq)

    # Play some tones at startup
    for i in range(0, 3):
        pi.set_PWM_frequency(motorPins[i], 800)
        pi.set_PWM_dutycycle(motorPins[i], 30)
        time.sleep(0.2)
        pi.write(motorPins[i], 0)
        time.sleep(0.5)
    pi.set_PWM_frequency(motorPins[3], 1600)
    pi.set_PWM_dutycycle(motorPins[3], 30)
    time.sleep(0.5)
    pi.write(motorPins[3], 0)
    pi.set_PWM_frequency(motorPins[i], pwm_freq)

    # Motor watchdog, stops motors in case of signal stall
    # global direction
    # direction = 'stop'
    # thread.start_new_thread(driveFunc, ())
    # thread.start_new_thread(stopMotors, (0,0))

def move(args):
    global motorPins
    global driveDelay
    global turnDelay
    global steeringBias
    global pwm_speed
    global pwm_freq
    global pwm_range
    global stopTheMotors

    # Not drive commands
    if (len(args['command'].split(" ")) > 1):
        if extended_command.is_authed(args['name']): # Moderator
            cmd_split = args['command'].split(" ")
            if cmd_split[0] == "set_drive_speed":
                if cmd_split[1] == "up":
                    pwm_speed = cinc(pwm_speed, 100, 180, 10)
                if cmd_split[1] == "dn":
                    pwm_speed = cinc(pwm_speed, 100, 180, -10)
                #blynk.virtual_write(3, pwm_speed)
                #requests.post(hud_url, data={'maxspeed': pwm_speed})
                config_save('zerobot', 'pwm_speed', pwm_speed)
            if cmd_split[0] == "set_bias":
                if cmd_split[1] == "up":
                    steeringBias = cinc(steeringBias, -20, 20, 1)
                if cmd_split[1] == "dn":
                    steeringBias = cinc(steeringBias, -20, 20, -1)
                #blynk.virtual_write(4, steeringBias)
                #requests.post(hud_url, data={'steeringbias': steeringBias})
                config_save('zerobot', 'steeringbias', steeringBias)
            #if cmd_split[0] == "battery":
            #    checkBatt(1)

    direction = args['command']
    if direction == 'F':
        pi.set_PWM_dutycycle(motorPins[0], pwm_speed-steeringBias)
        pi.set_PWM_dutycycle(motorPins[2], pwm_speed+steeringBias)
        time.sleep(driveDelay)
        for i in range(0, 4):
            pi.write(motorPins[i], 0)
    if direction == 'B':
        pi.set_PWM_dutycycle(motorPins[1], pwm_speed-steeringBias)
        pi.set_PWM_dutycycle(motorPins[3], pwm_speed+steeringBias)
        time.sleep(driveDelay)
        for i in range(0, 4):
            pi.write(motorPins[i], 0)
    if direction == 'L':
        pi.set_PWM_dutycycle(motorPins[0], (pwm_speed-steeringBias)*1.5)
        #pi.set_PWM_dutycycle(motorPins[3], (pwm_speed+steeringBias)*1.5)
        time.sleep(turnDelay)
        for i in range(0, 4):
            pi.write(motorPins[i], 0)
    if direction == 'R':
        #pi.set_PWM_dutycycle(motorPins[1], (pwm_speed-steeringBias)*1.5)
        pi.set_PWM_dutycycle(motorPins[2], (pwm_speed-steeringBias)*1.5)
        time.sleep(turnDelay)
        for i in range(0, 4):
            pi.write(motorPins[i], 0)
    if direction == 'stop':
        for i in range(0, 4):
            pi.write(motorPins[i], 0)


@atexit.register
def zeroExit():
    for i in range(0, 4):
        pi.write(motorPins[i], 0)
    tts.say("Shutting down")
    #subprocess.call(['rsh', 'gcurtis79@%s' % hud_host, 'bin/87156782.kill'])
