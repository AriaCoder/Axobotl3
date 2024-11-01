# AXOBOTL Python Code
# Team 4028X Extreme Axolotls
# 2023-25 VEX IQ Rapid Relay Challenge
from vex import * 

# Bot is a "base class" inherited (shared) by both DriveBot and AutoBot. All
# the common stuff goes in the Bot class. Our mentor showed us how inheritance
# can help keep our code organized. Because VEX doesn't let us create our
# own python modules to share, we just have to copy 
class Bot:
    def __init__(self):
        self.isRunningNow = False
        self.screenColor = Color.BLUE
        self.penColor = Color.WHITE

    def isRunning(self) -> bool:
        return self.isRunningNow

    def setup(self):
        self.brain = Brain()
        self.inertial = Inertial()
        self.setupScreen()
        self.setupPortMappings()
        self.setupDriveTrain()
        self.setupEvents()
        self.setupCatapult()
        self.setupIntake()
        self.setupSensors()
        wait(15, MSEC)  # Just make sure events have time to get setup

    def setupEvents(self):  # Custom events
        self.eventBackBumperPressed: Event = Event(self.onBackBumperPressed)
        self.eventBackBumperReleased: Event = Event(self.onBackBumperReleased)
        self.eventIntakeBallFound: Event = Event(self.onIntakeBallFound)
        self.eventIntakeBallLost: Event = Event(self.onIntakeBallLost)
        self.eventCatapultBallFound: Event = Event(self.onCatapultBallFound)
        self.eventCatapultBallLost: Event = Event(self.onCatapultBallLost)

    def onBackBumperPressed(self):
        pass

    def onBackBumperReleased(self):
        pass

    def onIntakeBallFound(self):
        if self.isBallOnCatapult():
            self.stopIntake()

    def onIntakeBallLost(self):
        pass

    def onCatapultBallFound(self):
        if self.isBallAtIntake():
            self.stopIntake()

    def onCatapultBallLost(self):
        pass

    def setupPortMappings(self):    
        # Drive train gear ratio is 2:1
        self.wheelLeft = Motor(Ports.PORT7, 2.0, True)
        self.wheelRight = Motor(Ports.PORT12, 2.0, False)
        self.intakeSensor = Distance(Ports.PORT6)
        self.catapultRight = Motor(Ports.PORT11,True)
        self.catapultLeft = Motor(Ports.PORT3)
        self.topSensor = Distance(Ports.PORT5)
        self.intakeRight = Motor(Ports.PORT1)
        self.intakeLeft = Motor(Ports.PORT4, True)
        self.catapultSensor = Distance(Ports.PORT2)
        self.LEDLeft = Touchled(Ports. PORT10)
        self.LEDRight = Touchled(Ports. PORT9)
        self.backBumper = Bumper(Ports.PORT8)

    def setupScreen(self):
        self.brain.screen.clear_screen()
        self.brain.screen.set_font(FontType.MONO20)
        self.brain.screen.set_pen_color(self.penColor)
        self.brain.screen.set_fill_color(self.screenColor)
        self.brain.screen.set_cursor(1, 1)
        self.clearScreen()

    def clearScreen(self, screenColor = None, penColor = None):
        self.screenColor = self.screenColor if screenColor is None else screenColor
        self.penColor = self.penColor if penColor is None else penColor
        self.brain.screen.clear_screen()
        self.brain.screen.set_fill_color(self.screenColor)
        self.brain.screen.set_pen_color(self.screenColor)
        self.brain.screen.draw_rectangle(0, 0, 170, 100, self.screenColor)
        self.brain.screen.set_pen_color(self.penColor)
        self.brain.screen.set_font(FontType.MONO20)
        self.brain.screen.set_cursor(1, 1)

    def print(self, message):
        self.brain.screen.print(message)
        self.brain.screen.new_line()
        print(message)  # For connected console

    def setupDriveMotor(self, motor: Motor):
        motor.set_velocity(0, PERCENT)
        motor.set_max_torque(100, PERCENT)
        motor.spin(FORWARD)

    def setupCatapult(self, velocity: int = 100):
        self.catapultRight.set_velocity(velocity)
        self.catapultLeft.set_velocity(velocity)
        self.catapultRight.set_stopping(HOLD)
        self.catapultLeft.set_stopping(HOLD)
        self.backBumper.pressed(self.onBumperPressed)
        self.backBumper.released(self.onBumperReleased)

    def setupIntake(self, velocity: int = 100):
        self.intakeRight.set_velocity(velocity)
        self.intakeLeft.set_velocity(velocity)

    def spinIntake(self, direction: DirectionType.DirectionType):
        self.intakeRight.spin(direction) 
        self.intakeLeft.spin(direction)

    def stopIntake(self, mode = HOLD):
        self.intakeRight.stop(mode)
        self.intakeLeft.stop(mode)
    
    def runIntake(self):    
        if not self.isCatapultDown(): # Catapult is up... somehow
            self.windCatapult() # Lower catapult
        self.spinIntake(REVERSE)

    def intakeReverse(self):
        self.spinIntake(FORWARD)

    def runBelt(self):
        self.catapultLeft.spin(REVERSE)
        self.catapultRight.spin(REVERSE)

    def isCatapultDown(self):
        return self.catapultSensor.object_distance(MM) < 80

    def isBallAtIntake(self):
        return self.intakeSensor.object_distance(MM) < 100

    def isBallOnCatapult(self):
        return self.topSensor.object_distance(MM) < 50

    def onBumperPressed(self):
        self.brain.play_sound(SoundType.TADA)
        self.LEDLeft.set_color(Color.GREEN)
        self.eventBackBumperPressed.broadcast()

    def onBumperReleased(self):
        self.LEDLeft.off()
        self.eventBackBumperReleased.broadcast()

    def releaseCatapult(self, cancelRewind = None): # Down Button
        if self.isCatapultDown():
            self.catapultRight.spin_for(FORWARD, 180, DEGREES, wait=False)
            self.catapultLeft.spin_for(FORWARD, 180, DEGREES)
            # cancelWinding lets the caller of releaseCatapult() know
            # if winding should be cancelled (keeps tension off rubber bands)
            if (cancelRewind is None or not cancelRewind()):
                self.windCatapult()

    def windCatapult(self):  # Up Button
        while not self.isCatapultDown():
            self.catapultRight.spin(FORWARD)
            self.catapultLeft.spin(FORWARD)
            wait(100, MSEC)
        # Spinning the catapult a little more because sensor placement can't go lower
        self.catapultRight.spin_for(FORWARD, 60, DEGREES, wait = False)
        self.catapultLeft.spin_for(FORWARD, 60, DEGREES)
        self.catapultRight.stop(HOLD)
        self.catapultLeft.stop(HOLD)

    def setupDriveTrain(self):
        self.setupDriveMotor(self.wheelLeft)
        self.setupDriveMotor(self.wheelRight)

    def stopAll(self):
        self.catapultRight.stop(HOLD)    
        self.catapultLeft.stop(HOLD) 
        self.stopIntake(HOLD)

    def setupSensors(self):
        self.foundIntakeBall: bool = False
        self.lostIntakeBall: bool = False
        self.foundCatapultBall: bool = False
        self.lostCatapultBall: bool = False
        self.sensorThread = Thread(self.checkSensors)

    def checkSensors(self):
        # Loop forever in a separate thread ("when started" in Vex Blocks)
        while self.isRunning():
            if self.isBallAtIntake():
                if not self.foundIntakeBall:
                    self.foundIntakeBall = True  # These variables keep us from raising
                    self.lostIntakeBall = False  # the broadcast over and over again
                    self.eventIntakeBallFound.broadcast()
            else:
                if not self.lostIntakeBall:
                    self.lostIntakeBall = True
                    self.foundIntakeBall = False
                    self.eventIntakeBallLost.broadcast()
            if self.isBallOnCatapult():
                if not self.foundCatapultBall:
                    self.foundCatapultBall = True
                    self.lostCatapultBall = False
                    self.eventCatapultBallFound.broadcast()
                else:
                    self.foundCatapultBall = False
                    self.lostCatapultBall = True
                    self.eventCatapultBallLost.broadcast()
            wait(20, MSEC)

    def run(self):
        self.isRunningNow = True
        self.setup()

class DriveBot(Bot):
    def __init__(self):
        super().__init__()

    def setupController(self):
        self.controller = Controller()
        # Left buttons
        self.controller.buttonLUp.pressed(self.runIntake)
        self.controller.buttonLDown.pressed(self.intakeReverse)
        # Right buttons
        self.controller.buttonRUp.pressed(self.releaseDriveCatapult)
        self.controller.buttonRDown.pressed(self.windCatapult)
        # Special buttons
        self.controller.buttonEUp.pressed(self.runBelt)
        self.controller.buttonFUp.pressed(self.stopAll)
        # Delay a tiny bit to make sure events get setup
        wait(15, MSEC)

    def cancelCatapultRewind(self):
        # Special trick: hold down EUp to cancel re-wind of catapult
        return self.controller.buttonEUp.pressing()

    def releaseDriveCatapult(self):
        # This is passing a function, not a function call return value!
        self.releaseCatapult(self.cancelCatapultRewind)

    def updateDriveMotor(self, drive: Motor, velocity: float, joystickTolerance: int):
        print("i am driving")
        # Cubic function helps improve drive responsiveness?
        velocity = velocity**3
        velocity = velocity/10000
        if math.fabs(velocity) <= joystickTolerance:
            velocity = 0
        drive.set_velocity(velocity, PERCENT)

    def run(self):
        super().run()
        self.print("Extreme Axolotls!")
        self.print("Ready")
        self.setupController()
        while self.isRunning():
            self.updateDriveMotor(self.wheelRight, self.controller.axisD.position(), 5)
            self.updateDriveMotor(self.wheelLeft, self.controller.axisA.position(), 5)
            sleep(20)


# TODO: Separate class for doing all the autonomous stuff
class AutoBot(Bot):
    def __init__(self):
        super().__init__()
        self.cancelCalibration = False

    def run(self):
        super().run()


# Where it all begins.
bot = DriveBot()
bot.run()

