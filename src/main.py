# AXOBOTL Python Code
# Team 4028X Extreme Axolotls
# 2023-25 VEX IQ Rapid Relay Challenge
from vex import *


# Bot is a "base class" inherited (shared) by both DriveBot and AutoBot. All
# the common stuff goes in the Bot class. Our mentor showed us how inheritance
# can help keep our code organized. Because VEX doesn't let us create our
# own python modules to share, we just have to copy 
class Bot:
    def __init__(self,
                 screenColor: Color.DefinedColor = Color.BLUE,
                 penColor: Color.DefinedColor = Color.WHITE):
        self.screenColor = screenColor
        self.penColor = penColor

    def isContinuous(self) -> bool:
        return False

    def setup(self):
        self.brain = Brain()
        self.inertial = Inertial()
        self.clearScreen()
        self.setupPortMappings()
        self.updateMotor(self.wheelLeft, 0.0, FORWARD)
        self.updateMotor(self.wheelRight, 0.0, FORWARD)
        self.eventButtBumperPressed: Event = Event(self.onButtBumperPressed)
        self.eventButtBumperReleased: Event = Event(self.onButtBumperReleased)
        self.eventIntakeBallSeen: Event = Event(self.onIntakeBallSeen)
        self.eventIntakeBallLost: Event = Event(self.onIntakeBallLost)
        self.eventCatBallSeen: Event = Event(self.onTopBallSeen)
        self.eventCatBallLost: Event = Event(self.onTopBallLost)

        self.wheelLeft.set_max_torque(100, PERCENT)
        self.wheelRight.set_max_torque(100, PERCENT)

        self.intakeLeft.set_velocity(100, PERCENT)
        self.intakeRight.set_velocity(100, PERCENT)
        self.intakeLeft.set_max_torque(100, PERCENT)
        self.intakeRight.set_max_torque(100, PERCENT)

        self.catBeltLeft.set_velocity(100, PERCENT)
        self.catBeltRight.set_velocity(100, PERCENT)
        self.catBeltLeft.set_max_torque(100, PERCENT)
        self.catBeltRight.set_max_torque(100, PERCENT)

        self.catBeltRunning: bool = False
        self.intakeRunning: bool = False
        self.intakeBallSeen: bool = False
        self.intakeBallLost: bool = False
        self.topBallSeen: bool = False
        self.topBallLost: bool = False
        self.sensorThread = Thread(self.checkSensors)
        self.setupCatBelt()

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

    def setupPortMappings(self):    
        self.wheelLeft = Motor(Ports.PORT7, 2.0, True)  # Gear ratio: 2:1
        self.wheelRight = Motor(Ports.PORT12, 2.0, False)
        self.intakeEye = Distance(Ports.PORT6)
        self.topEye = Distance(Ports.PORT5)
        self.catEye = Distance(Ports.PORT2)
        self.catBeltLeft = Motor(Ports.PORT3)
        self.catBeltRight = Motor(Ports.PORT11,True)
        self.intakeLeft = Motor(Ports.PORT4, True)
        self.intakeRight = Motor(Ports.PORT1)
        self.ledLeft = Touchled(Ports.PORT10)
        self.ledRight = Touchled(Ports.PORT9)
        self.buttBumper = Bumper(Ports.PORT8)
        self.ballHugger = Pneumatic(Ports.PORT10)

    def print(self, message):
        self.brain.screen.print(message)
        self.brain.screen.new_line()
        print(message)  # For connected console

    def onButtBumperPressed(self):
        pass

    def onButtBumperReleased(self):
        pass

    def onIntakeBallSeen(self):
        if self.isBallOnTop(): self.stopIntake()

    def onIntakeBallLost(self):
        pass

    def onTopBallSeen(self):
        if not self.isContinuous():
            if self.isBallAtIntake(): self.stopIntake()
            self.releaseHug()

    def onTopBallLost(self):
        if self.isBallAtIntake():
            if not self.isCatDown():
                self.stopIntake()
                self.windCat()
            if not self.isBallOnTop() and self.isBallAtIntake(): self.spinIntake(REVERSE)

    def updateMotor(self,
                    motor: Motor,
                    velocityPercent: float,
                    direction: DirectionType.DirectionType = FORWARD,
                    brakeType: BrakeType.BrakeType = COAST,
                    timeoutSecs: float = 0.0,
                    spinNow: bool = True,
                    resetPosition: bool = False):
        motor.set_velocity(velocityPercent, PERCENT)
        motor.set_stopping(brakeType)
        if timeoutSecs > 0.0: motor.set_timeout(timeoutSecs, SECONDS)
        if spinNow: motor.spin(direction)
        if resetPosition: motor.set_position(0, RotationUnits.REV)
    
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

    def setupCatBelt(self, velocity: int = 100):
        self.updateMotor(self.catBeltLeft, velocity, brakeType=HOLD, spinNow=False)
        self.updateMotor(self.catBeltRight, velocity, brakeType=HOLD, spinNow=False)
        self.buttBumper.pressed(self.onBumperPressed)
        self.buttBumper.released(self.onBumperReleased)
        self.ballHugger.pump_on()

    def spinIntake(self, direction: DirectionType.DirectionType):
        self.intakeLeft.spin(direction)
        self.intakeRight.spin(direction) # Motor is configured reverse
        self.intakeRunning = True

    def stopIntake(self, mode = HOLD):
        self.intakeLeft.stop(mode)
        self.intakeRight.stop(mode)
        self.intakeRunning = False
    
    def startIntake(self):
        if not self.isCatDown(): self.windCat()
        if self.isContinuous(): self.hugBall()
        else: self.releaseHug(stop=True)  # Open up for the next ball
        self.spinIntake(REVERSE)

    def reverseIntake(self):
        self.spinIntake(FORWARD)

    def startBelt(self):
        self.hugBall()
        self.catBeltLeft.spin(REVERSE)
        self.catBeltRight.spin(REVERSE)
        self.catBeltRunning = True

    def stopCatAndBelt(self):
        self.catBeltLeft.stop(HOLD)
        self.catBeltRight.stop(HOLD)
        self.catBeltRunning = False

    def isCatDown(self):
        return self.catEye.object_distance(MM) < 80

    def isBallAtIntake(self):
        return self.intakeEye.object_distance(MM) < 80

    def isBallOnTop(self):
        return self.topEye.object_distance(MM) < 35

    def onBumperPressed(self):
        self.brain.play_sound(SoundType.TADA)
        self.ledLeft.set_color(Color.GREEN)
        self.eventButtBumperPressed.broadcast()

    def onBumperReleased(self):
        self.ledLeft.off()
        self.eventButtBumperReleased.broadcast()

    def releaseCat(self, cancelRewind = None): # Down Button
        self.releaseHug()
        self.catBeltRight.spin_for(FORWARD, 180, DEGREES, wait=False)
        self.catBeltLeft.spin_for(FORWARD, 180, DEGREES)
        # cancelWinding lets the caller of releaseCatapult() know
        # if winding should be cancelled (keeps tension off rubber bands)
        if (cancelRewind is None or not cancelRewind()): self.windCat()

    def windCat(self):  # Up Button
        self.releaseHug()
        self.catBeltLeft.spin(FORWARD)
        self.catBeltRight.spin(FORWARD)
        for _ in range(3 * 100):  # 3 seconds @ 10ms/loop
            if self.isCatDown(): break
            wait(10, MSEC)
        # TODO: Check if we still need/want this. Tune it to new Gen3 bot?
        # Spinning the catapult a little more because sensor placement can't go lower
        self.catBeltRight.spin_for(FORWARD, 10, DEGREES, wait = False)
        self.catBeltLeft.spin_for(FORWARD, 10, DEGREES)
        self.stopCatAndBelt()

    def releaseHug(self, stop: bool = True):
        if stop: self.stopCatAndBelt()
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
        if not self.intakeRunning: self.ballHugger.pump_off()  # Stop TWICE to shut off the pump
        self.stopIntake(HOLD)

    def checkIntakeEye(self):
        if self.intakeEye.installed():
            if self.isBallAtIntake():
                if not self.intakeBallSeen:
                    self.intakeBallSeen = True  # These variables keep us from raising
                    self.intakeBallLost = False  # the broadcast over and over again
                    self.eventIntakeBallSeen.broadcast()
            else:
                if not self.intakeBallLost:
                    self.intakeBallLost = True
                    self.intakeBallSeen = False
                    self.eventIntakeBallLost.broadcast()

    def checkTopEye(self):
        if self.topEye.installed():
            if self.isBallOnTop():
                if not self.topBallSeen:
                    self.topBallSeen = True
                    self.topBallLost = False
                    self.eventCatBallSeen.broadcast()
            else:
                if not self.topBallLost:
                    self.topBallSeen = False
                    self.topBallLost = True
                    self.eventCatBallLost.broadcast()

    def checkSensors(self):
        while True: # Loop forever in a thread (like "when started" in Vex Blocks)
            self.checkIntakeEye()
            self.checkTopEye()            
            wait(10, MSEC)

    def run(self):
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
        self.controller.buttonLUp.pressed(self.startIntake)  
        self.controller.buttonLDown.pressed(self.onLDown)
        self.controller.buttonRUp.pressed(self.releaseDriveCatapult)
        self.controller.buttonRDown.pressed(self.windCat)
        self.controller.buttonEUp.pressed(self.startBelt)
        self.controller.buttonEDown.pressed(self.reverseIntake)
        self.controller.buttonFUp.pressed(self.stopAll)
        wait(15, MSEC)

    def onLDown(self):
        self.stopCatAndBelt() if self.catBeltRunning else self.startBelt()

    def isContinuous(self) -> bool:
        return self.controller.buttonLDown.pressing()

    def cancelCatapultRewind(self):
        # Special trick: hold down EUp to cancel re-wind of catapult
        return self.controller.buttonEUp.pressing()

    def releaseDriveCatapult(self):
        # This is passing a function, not a function call return value!
        self.releaseCat(self.cancelCatapultRewind)

    def updateDriveMotor(self, drive: Motor, velocity: float, joystickTolerance: int):
        if math.fabs(velocity) <= joystickTolerance: velocity = 0
        drive.set_velocity(round(velocity), PERCENT)

    def run(self):
        super().run()
        self.clearScreen()
        self.print("Extreme Axolotls!")
        self.print("Ready")
        while True:
            self.updateDriveMotor(self.wheelRight, self.controller.axisD.position(), 5)
            self.updateDriveMotor(self.wheelLeft, self.controller.axisA.position(), 5)
            sleep(20, MSEC)


# Where it all begins.
bot = DriveBot()
bot.run()
