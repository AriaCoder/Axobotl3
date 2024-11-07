# AXOBOTL Python Code
# Team 4028X Extreme Axolotls
# 2023-25 VEX IQ Rapid Relay Challenge
from vex import * 
import time


# Bot is a "base class" inherited (shared) by both DriveBot and AutoBot. All
# the common stuff goes in the Bot class. Our mentor showed us how inheritance
# can help keep our code organized. Because VEX doesn't let us create our
# own python modules to share, we just have to copy 
class Bot:
    def __init__(self,
                 screenColor: Color.DefinedColor = Color.BLUE,
                 penColor: Color.DefinedColor = Color.WHITE):
        self.isRunningNow = False
        self.screenColor = screenColor
        self.penColor = penColor

    def isRunning(self) -> bool:
        return self.isRunningNow

    def isContinuous(self) -> bool:
        return False

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
        if self.isBallOnCatapult() or not self.isCatapultDown():
            self.stopIntake()

    def onIntakeBallLost(self):
        pass

    def onCatapultBallFound(self):
        if self.isBallAtIntake() and not self.isContinuous():
            self.stopIntake()
        elif not self.isContinuous():
            self.releaseHug()

    def onCatapultBallLost(self):
        if self.isBallAtIntake():
            if not self.isCatapultDown():
                self.stopIntake()
                self.windCatapult()
            if not self.isBallOnCatapult() and self.isBallAtIntake():
                self.spinIntake(REVERSE)

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
        self.touchLedLeft = Touchled(Ports. PORT10)
        self.touchLedRight = Touchled(Ports. PORT9)
        self.backBumper = Bumper(Ports.PORT8)
        self.ballHugger = Pneumatic(Ports.PORT10)

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

    def updateMotor(self,
                    motor: Motor,
                    velocityPercent: float,
                    direction: DirectionType.DirectionType = FORWARD,
                    brakeType: BrakeType.BrakeType = COAST,
                    timeoutSecs: float = 0.0,
                    spinNow: bool = True,
                    resetPosition: bool = False):
        motor.set_velocity(velocityPercent, PERCENT)
        motor.set_max_torque(100, PERCENT)
        motor.set_stopping(brakeType)
        if timeoutSecs > 0.0:
            motor.set_timeout(timeoutSecs, SECONDS)
        if spinNow:
            motor.spin(direction)
        if resetPosition:
            motor.set_position(0, RotationUnits.REV)

    def updateDriveTrain(self,
                      velocityPercent: float,
                      direction: DirectionType.DirectionType = FORWARD,
                      brakeType: BrakeType.BrakeType = COAST,
                      timeoutSecs: float = 0.0,
                      spinNow: bool = True,
                      resetPosition: bool = False):
        self.updateMotor(self.wheelLeft, velocityPercent, direction, brakeType, timeoutSecs, spinNow, resetPosition)
        self.updateMotor(self.wheelRight, velocityPercent, direction, brakeType, timeoutSecs, spinNow, resetPosition)

    def stopDriveTrain(self,brakeType: BrakeType.BrakeType = COAST):
        self.wheelLeft.stop(brakeType)
        self.wheelRight.stop(brakeType)

    def setupCatapult(self, velocity: int = 100):
        self.updateMotor(self.catapultLeft, velocity, brakeType=HOLD, spinNow=False)
        self.updateMotor(self.catapultRight, velocity, brakeType=HOLD, spinNow=False)
        self.backBumper.pressed(self.onBumperPressed)
        self.backBumper.released(self.onBumperReleased)
        self.ballHugger.pump_on()

    def setupIntake(self, velocity: int = 100):
        self.intakeLeft.set_velocity(velocity, PERCENT)
        self.intakeRight.set_velocity(velocity, PERCENT)

    def spinIntake(self, direction: DirectionType.DirectionType):
        self.intakeLeft.set_velocity(100, PERCENT)
        self.intakeRight.set_velocity(100, PERCENT)
        self.intakeLeft.spin(direction)
        self.intakeRight.spin(direction) # Motor is configured reverse

    def stopIntake(self, mode = HOLD):
        self.intakeLeft.set_velocity(0)
        self.intakeRight.set_velocity(0)
        self.intakeLeft.stop(mode)
        self.intakeRight.stop(mode)
    
    def runIntake(self):
        if not self.isCatapultDown(): # Catapult is up... somehow
            self.windCatapult() # Lower catapult
        if self.isContinuous():
            self.hugBall()
        else:
            self.releaseHug(stop=True)  # Open up for the next ball
        self.spinIntake(REVERSE)

    def intakeReverse(self):
        self.spinIntake(FORWARD)

    def runBelt(self):
        self.hugBall()
        self.catapultLeft.set_velocity(100, PERCENT)
        self.catapultRight.set_velocity(100, PERCENT)
        self.catapultLeft.spin(REVERSE)
        self.catapultRight.spin(REVERSE)

    def stopCatAndBelt(self):
        self.catapultLeft.set_velocity(0, PERCENT)
        self.catapultRight.set_velocity(0, PERCENT)
        self.catapultLeft.stop(HOLD)
        self.catapultRight.stop(HOLD)

    def isCatapultDown(self):
        self.print(self.catapultSensor.installed())
        return self.catapultSensor.object_distance(MM) < 80

    def isBallAtIntake(self):
        return self.intakeSensor.object_distance(MM) < 80

    def isBallOnCatapult(self):
        return self.topSensor.object_distance(MM) < 50 and self.isCatapultDown()

    def onBumperPressed(self):
        self.brain.play_sound(SoundType.TADA)
        self.touchLedLeft.set_color(Color.GREEN)
        self.eventBackBumperPressed.broadcast()

    def onBumperReleased(self):
        self.touchLedLeft.off()
        self.eventBackBumperReleased.broadcast()

    def releaseCatapult(self, cancelRewind = None): # Down Button
        self.releaseHug()
        self.catapultLeft.set_velocity(100, PERCENT)
        self.catapultRight.set_velocity(100, PERCENT)
        self.catapultRight.spin_for(FORWARD, 180, DEGREES, wait=False)
        self.catapultLeft.spin_for(FORWARD, 180, DEGREES)
        # cancelWinding lets the caller of releaseCatapult() know
        # if winding should be cancelled (keeps tension off rubber bands)
        if (cancelRewind is None or not cancelRewind()):
            self.windCatapult()

    def windCatapult(self):  # Up Button
        self.releaseHug()
        self.catapultLeft.set_velocity(100, PERCENT)
        self.catapultRight.set_velocity(100, PERCENT)
        while not self.isCatapultDown():
            self.catapultRight.spin(FORWARD)
            self.catapultLeft.spin(FORWARD)
            wait(100, MSEC)
        # Spinning the catapult a little more because sensor placement can't go lower
        self.catapultRight.spin_for(FORWARD, 10, DEGREES, wait = False)
        self.catapultLeft.spin_for(FORWARD, 10, DEGREES)
        self.stopCatAndBelt()

    def setupDriveTrain(self):
        self.updateMotor(self.wheelLeft, 0.0, FORWARD)
        self.updateMotor(self.wheelRight, 0.0, FORWARD)

    def releaseHug(self, stop: bool = True):
        if stop:
            self.stopCatAndBelt()
        self.ballHugger.pump_on()
        self.ballHugger.extend(CylinderType.CYLINDER1)
        self.ballHugger.extend(CylinderType.CYLINDER2)

    def hugBall(self):
        self.ballHugger.pump_on()
        self.ballHugger.retract(CylinderType.CYLINDER1)
        self.ballHugger.retract(CylinderType.CYLINDER2)

    def stopAll(self):
        self.stopCatAndBelt()
        self.releaseHug(stop=True)
        if self.intakeLeft.velocity() == 0.0:
            self.ballHugger.pump_off()  # Stop TWICE to shut off the pump
        self.stopIntake(HOLD)
        
    def setupSensors(self):
        self.foundIntakeBall: bool = False
        self.lostIntakeBall: bool = True
        self.foundCatapultBall: bool = False
        self.lostCatapultBall: bool = True
        self.sensorThread = Thread(self.checkSensors)

    def checkSensors(self):
        # Loop forever in a separate thread ("when started" in Vex Blocks)
        while self.isRunning():
            if  self.intakeSensor.installed():
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
            if self.topSensor.installed():
                if self.isBallOnCatapult():
                    if not self.foundCatapultBall:
                        self.foundCatapultBall = True
                        self.lostCatapultBall = False
                        self.eventCatapultBallFound.broadcast()
                else:
                    if not self.lostCatapultBall:
                        self.foundCatapultBall = False
                        self.lostCatapultBall = True
                        self.eventCatapultBallLost.broadcast()
            wait(20, MSEC)

    def run(self):
        self.isRunningNow = True
        self.setup()
        self.clearScreen()

# ============================================================================
# ============================================================================
# ============================================================================

class DriveBot(Bot):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.setupController()
        super().setup()

    def setupController(self):
        self.controller = Controller()
        # Left buttons
        self.controller.buttonLUp.pressed(self.runIntake)  
        self.controller.buttonLDown.pressed(self.onLDown)
        # Right buttons
        self.controller.buttonRUp.pressed(self.releaseDriveCatapult)
        self.controller.buttonRDown.pressed(self.windCatapult)
        # Special buttons
        self.controller.buttonEUp.pressed(self.runBelt)
        self.controller.buttonEDown.pressed(self.intakeReverse)
        self.controller.buttonFUp.pressed(self.stopAll)
        # Delay a tiny bit to make sure events get setup
        wait(15, MSEC)

    def onLDown(self):
        if abs(self.catapultLeft.velocity()) > 0:
            self.stopCatAndBelt()
        else:
            self.runBelt()

    def isContinuous(self) -> bool:
        return self.controller.buttonLDown.pressing()

    def cancelCatapultRewind(self):
        # Special trick: hold down EUp to cancel re-wind of catapult
        return self.controller.buttonEUp.pressing()

    def releaseDriveCatapult(self):
        # This is passing a function, not a function call return value!
        self.releaseCatapult(self.cancelCatapultRewind)

    def updateDriveMotor(self, drive: Motor, velocity: float, joystickTolerance: int):
        # Cubic function helps improve drive responsiveness?
        velocity = velocity**3
        velocity = velocity/10000
        if math.fabs(velocity) <= joystickTolerance:
            velocity = 0
        drive.set_velocity(velocity, PERCENT)

    def run(self):
        super().run()
        self.clearScreen()
        self.print("Extreme Axolotls!")
        self.print("Ready")
        while self.isRunning():
            self.updateDriveMotor(self.wheelRight, self.controller.axisD.position(), 5)
            self.updateDriveMotor(self.wheelLeft, self.controller.axisA.position(), 5)
            sleep(20)


# Where it all begins.
bot = DriveBot()
bot.run()
