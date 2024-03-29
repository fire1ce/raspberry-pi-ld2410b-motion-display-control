#!/usr/bin/python3

import logging
from threading import Timer
from subprocess import getoutput, run, DEVNULL
from gpiozero import MotionSensor
from signal import pause


class Display:
    @staticmethod
    def isTurnedOn():
        status = getoutput("vcgencmd display_power")
        isTurnedOn = status == "display_power=1"
        logging.debug(f"[Display]: Is turned on: {isTurnedOn}")
        return isTurnedOn

    @staticmethod
    def turnOn():
        logging.debug("[Display]: Turning ON the display..")
        run(["vcgencmd", "display_power", "1"], stdout=DEVNULL)

    @staticmethod
    def turnOff():
        logging.debug("[Display]: Turning OFF the display..")
        run(["vcgencmd", "display_power", "0"], stdout=DEVNULL)


class Motion:
    timer = None

    def __init__(self, gpio_pin, display_delay, verbose):
        if verbose == True:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        logging.info(
            f"[Motion]: Initializing - GPIO_PIN: {gpio_pin}, DISPLAY_DELAY: {display_delay}, VERBOSE: {verbose}"
        )

        if verbose == True:
            logging.basicConfig(level=logging.DEBUG)

        self.display_delay = display_delay
        self.pir = MotionSensor(gpio_pin)
        self.pir.when_motion = self.onMotion
        self.pir.when_no_motion = self.noMotion
        self.resetTimer()
        pause()

    def resetTimer(self):
        logging.debug("[Motion]: Resetting timer..")

        if self.timer:
            logging.debug("[Motion]: Old timer found! Destroying it!")
            self.timer.cancel()

        logging.debug(f"[Motion]: Setting timer for {self.display_delay}")
        self.timer = Timer(self.display_delay, Display.turnOff)
        self.timer.start()

    def onMotion(self):
        logging.debug("[Motion]: Motion detected!")

        if Display.isTurnedOn() == False:
            logging.debug("[Motion]: Display is off, turning it on!")
            Display.turnOn()

        if self.timer:
            logging.debug("[Motion]: Existing timer found! Destroying it!")
            self.timer.cancel()

    def noMotion(self):
        logging.debug(f"[Motion]: No Motion detected waiting {self.display_delay} seconds to turn off the display!")
        self.resetTimer()


motion = Motion(gpio_pin=4, display_delay=30, verbose=False)
