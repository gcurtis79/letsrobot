#
# zerobot.py - by gcurtis79
# Modeled after l298n.py
# For a Pi Zero W with direct pin-to-motor-controller connection
#
# Make sure to set pins in letsrobot.conf [zerobot] section
#

#import pigpio
#pi=pigpio.pi()
import os
import time
import extended_command
import logging
log = logging.getLogger('LR.hardware.zerobot')
import thread
import BlynkLib
blynk = BlynkLib.Blynk('86ed838111d84fb4aa4b2b51a4019cd9', '127.0.0.1', 8888)
thread.start_new_thread(blynk.run, ())

from configparser import ConfigParser
robot_config = ConfigParser()
robot_config.readfp(open('letsrobot.conf'))

driveDelay=None
turnDelay=None
steeringBias=None

motorPins=None
pwm_freq=None
pwm_range=None
pwm_speed=None

def config_save(section, param, value):
    robot_config.set(section, param, str(value))
    #log.info('In %s, saving %s into %s.', os.getcwd(), str(value), param)
    with open('letsrobot.conf', 'w') as configfile:
        robot_config.write(configfile)
        configfile.close()

# Function for setting turn delay
def set_turn_delay(command, args):
    global turnDelay
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            turnDelay=float(command[1])
            blynk.virtual_write(1, turnDelay)
            config_save('zerobot', 'turnDelay', turnDelay)
            log.info("Rotate delay set to : %d", float(command[1]))

# Function for setting drive delay
def set_drive_delay(command, args):
    global driveDelay
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            driveDelay=float(command[1])
            blynk.virtual_write(2, driveDelay)
            config_save('zerobot', 'driveDelay', driveDelay)
            log.info("Drive delay set to : %d", float(command[1]))

# Function for setting drive speed
def set_drive_speed(command, args):
    global pwm_speed
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            pwm_speed=int(command[1])
            blynk.virtual_write(3, pwm_speed)
            config_save('zerobot', 'pwm_speed', pwm_speed)
            log.info("Drive speed set to : %d", int(command[1]))

# Function for setting steering bias
def set_bias(command, args):
    global steeringBias
    if extended_command.is_authed(args['name']) == 2: # Owner
        if len(command) > 1:
            steeringBias=int(command[1])
            blynk.virtual_write(4, steeringBias)
            steeringBias=int(command[1])
            config_save('zerobot', 'steeringBias', steeringBias)
            log.info("Steering bias set to : %d", int(command[1]))

def setup(robot_config):
    global motorPins
    global driveDelay
    global turnDelay
    global steeringBias
    global pwm_freq
    global pwm_range
    global pwm_speed

    driveDelay = float(robot_config.getfloat('zerobot', 'driveDelay'))
    turnDelay = float(robot_config.getfloat('zerobot', 'turnDelay'))
    steeringBias = int(robot_config.getfloat('zerobot', 'steeringBias'))
    pwm_freq = int(robot_config.getfloat('zerobot', 'pwm_freq'))
    pwm_range = int(robot_config.getfloat('zerobot', 'pwm_range'))
    pwm_speed = int(robot_config.getfloat('zerobot', 'pwm_speed'))

    blynk.virtual_write(1, turnDelay)
    blynk.virtual_write(2, driveDelay)
    blynk.virtual_write(3, pwm_speed)
    blynk.virtual_write(4, steeringBias)

    # Activate chat commands for motor settings
    if robot_config.getboolean('tts', 'ext_chat'): #ext_chat enabled, add motor commands
        extended_command.add_command('.set_turn_delay', set_turn_delay)
        extended_command.add_command('.set_drive_delay', set_drive_delay)
        extended_command.add_command('.set_drive_speed', set_drive_speed)
        extended_command.add_command('.set_bias', set_bias)

#    # Init the pins into the array and configure them
    motorPins = [int(robot_config.get('zerobot', 'zerobot1A')), int(robot_config.get('zerobot', 'zerobot1B')), int(robot_config.get('zerobot', 'zerobot2A')), int(robot_config.get('zerobot', 'zerobot2B'))]
#    for i in range(0,4):
#        pi.set_mode(motorPins[i], pigpio.OUTPUT)
#        pi.write(motorPins[i], 0)
#        pi.set_PWM_range(motorPins[i], pwm_range)
#        pi.set_PWM_frequency(motorPins[i], pwm_freq)

#    # Play some tones at startup
#    for i in range(0,3):
#        pi.set_PWM_frequency(motorPins[i], 800)
#        pi.set_PWM_dutycycle(motorPins[i], 30)
#        time.sleep(0.2)
#        pi.write(motorPins[i], 0)
#        time.sleep(0.5)
#    pi.set_PWM_frequency(motorPins[3], 1600)
#    pi.set_PWM_dutycycle(motorPins[3], 30)
#    time.sleep(0.5)
#    pi.write(motorPins[3], 0)

@blynk.VIRTUAL_WRITE(1)
def v1_write_handler(value):
    turnDelay=float(value)
    config_save('zerobot', 'turnDelay', turnDelay)

@blynk.VIRTUAL_WRITE(2)
def v2_write_handler(value):
    driveDelay=float(value)
    config_save('zerobot', 'driveDelay', driveDelay)

@blynk.VIRTUAL_WRITE(3)
def v3_write_handler(value):
    pwm_speed=int(value)
    config_save('zerobot', 'pwm_speed', pwm_speed)

@blynk.VIRTUAL_WRITE(4)
def v4_write_handler(value):
    steeringBias=int(value)
    config_save('zerobot', 'steeringBias', steeringBias)

def move(args):
    direction = args['command']
    if direction == 'F':
#        pi.set_PWM_dutycycle(motorPins[0], pwm_speed-steeringBias)
#        pi.set_PWM_dutycycle(motorPins[2], pwm_speed+steeringBias)
        log.debug('Drove forward at: %d', pwm_speed+steeringBias)
        time.sleep(driveDelay)
#        for i in range(0,4):
#            pi.write(motorPins[i], 0)
    if direction == 'B':
#        pi.set_PWM_dutycycle(motorPins[1], pwm_speed-steeringBias)
#        pi.set_PWM_dutycycle(motorPins[3], pwm_speed+steeringBias)
        time.sleep(driveDelay)
#        for i in range(0,4):
#            pi.write(motorPins[i], 0)
    if direction == 'L':
#        pi.set_PWM_dutycycle(motorPins[0], pwm_speed-steeringBias)
#        pi.set_PWM_dutycycle(motorPins[3], pwm_speed+steeringBias)
        time.sleep(turnDelay)
#        for i in range(0,4):
#            pi.write(motorPins[i], 0)
    if direction == 'R':
#        pi.set_PWM_dutycycle(motorPins[1], pwm_speed-steeringBias)
#        pi.set_PWM_dutycycle(motorPins[2], pwm_speed+steeringBias)
        time.sleep(turnDelay)
#        for i in range(0,4):
#            pi.write(motorPins[i], 0)


