# AXOBOTL Python Code
# Team 4028X Extreme Axolotls
# 2023-25 VEX IQ Rapid Relay Challenge
from vex import *


# The Eye class is useful for us
# Represents a Distance sensor that broadcasts if it "sees" an object
class Eye:
    def __init__(self, portNumber: int, distanceThreshold: int, units: DistanceUnits.DistanceUnits = DistanceUnits.MM):
        self.sensor = Distance(portNumber)
        self.sensor.changed(self.look)
        self.distanceThreshold: int = distanceThreshold
        self.units = units
        self.seen: bool = False  # Variables keep us from broadcast()-ing repeatedly
        self.lost: bool = False
        self.eventSeen = None
        self.eventLost = None

    def setCallbacks(self, callbackSeen, callbackLost):
        self.eventSeen = Event(callbackSeen)
        self.eventLost = Event(callbackLost)

    def isInstalled(self) -> bool:
        return self.sensor.installed()

    def isObjectVisible(self) -> bool:
        return True if self.sensor.object_distance(self.units) <= self.distanceThreshold else False
    
    def look(self):
        if self.sensor.installed():
            if self.isObjectVisible():
                if not self.seen:
                    self.seen = True
                    self.lost = False
                    if self.eventSeen: self.eventSeen.broadcast()
            else:
                if not self.lost:
                    self.seen = False
                    self.lost = True
                    if self.eventLost: self.eventLost.broadcast()

# Setup
brain = Brain()
inertial = Inertial()
wheelLeft = Motor(Ports.PORT7, 2.0, True)  # Gear ratio: 2:1
wheelRight = Motor(Ports.PORT12, 2.0, False)
intakeEye = Eye(Ports.PORT6, 80, MM)
topEye = Eye(Ports.PORT5, 40, MM)
catEye = Eye(Ports.PORT2, 30, MM)
backEye = Eye(Ports.PORT8, 20, MM)
catBeltLeft = Motor(Ports.PORT3)
catBeltRight = Motor(Ports.PORT11,True)
intakeLeft = Motor(Ports.PORT4, True)
intakeRight = Motor(Ports.PORT1)
ledLeft = Touchled(Ports.PORT10)
ledRight = Touchled(Ports.PORT9)
ballHugger = Pneumatic(Ports.PORT10)
screenColor: Color.DefinedColor = Color.BLUE
penColor: Color.DefinedColor = Color.WHITE

catBeltRunning: bool = False
intakeRunning: bool = False

isContinuousCallback = None

wait(15, MSEC)  # Allow events and everything else to initialize

def setup():
    clearScreen()
    updateMotor(wheelLeft, 0.0, FORWARD)
    updateMotor(wheelRight, 0.0, FORWARD)
    wheelLeft.set_max_torque(100, PERCENT)
    wheelRight.set_max_torque(100, PERCENT)

    intakeLeft.set_velocity(100, PERCENT)
    intakeRight.set_velocity(100, PERCENT)
    intakeLeft.set_max_torque(100, PERCENT)
    intakeRight.set_max_torque(100, PERCENT)

    catBeltLeft.set_velocity(100, PERCENT)
    catBeltRight.set_velocity(100, PERCENT)
    catBeltLeft.set_max_torque(100, PERCENT)
    catBeltRight.set_max_torque(100, PERCENT)
    setupCatBelt()

def clearScreen(screenColorIn = None, penColorIn = None):
    global screenColor
    global penColor
    if screenColorIn is not None:
        screenColor = screenColorIn
    if penColorIn is not None:
        penColor = penColorIn
    brain.screen.clear_screen()
    brain.screen.set_fill_color(screenColor)
    brain.screen.set_pen_color(screenColor)
    brain.screen.draw_rectangle(0, 0, 170, 100, screenColor)
    brain.screen.set_pen_color(penColor)
    brain.screen.set_font(FontType.MONO20)
    brain.screen.set_cursor(1, 1)

def brainPrint(message, clear = False):
    if clear == True:
        brain.screen.clear_row()
    brain.screen.print(message)
    brain.screen.new_line()
    print(message)  # For connected console

def moveBallFromTopToBack():
    if topEye.isObjectVisible() and not backEye.isObjectVisible():
        startBelt(release=True)
        timeoutMs: int = 5000
        while (timeoutMs > 0 and not backEye.isObjectVisible()):
            wait(10, MSEC)
            timeoutMs -= 10
        if timeoutMs <= 0:
            print("Timed out moving the ball")
        stopCatAndBelt()

def onIntakeBallSeen(): 
    if topEye.isObjectVisible() and not backEye.isObjectVisible():
        releaseHug()
        moveBallFromTopToBack()
    else:
        if not isContinuousCallback or not isContinuousCallback():
            stopCatAndBelt()        
            releaseHug()

def onIntakeBallLost():
    pass

def onTopBallSeen():
    pass

def onTopBallLost():
    pass
    
def onBackBallSeen():
    pass

def onBackBallLost():
    pass

def updateMotor(motor: Motor,
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

def updateDriveTrain(velocityPercent: float,
                     direction: DirectionType.DirectionType = FORWARD,
                     brakeType: BrakeType.BrakeType = COAST,
                     timeoutSecs: float = 0.0,
                     spinNow: bool = True,
                     resetPosition: bool = False):
    updateMotor(wheelLeft, velocityPercent, direction, brakeType, timeoutSecs, spinNow, resetPosition)
    updateMotor(wheelRight, velocityPercent, direction, brakeType, timeoutSecs, spinNow, resetPosition)

def stopDriveTrain(brakeType: BrakeType.BrakeType = COAST):
    wheelLeft.stop(brakeType)
    wheelRight.stop(brakeType)

def setupCatBelt(velocity: int = 100):
    updateMotor(catBeltLeft, velocity, brakeType=HOLD, spinNow=False)
    updateMotor(catBeltRight, velocity, brakeType=HOLD, spinNow=False)
    ballHugger.pump_on()

def spinIntake(direction: DirectionType.DirectionType):
    global intakeRunning
    intakeLeft.spin(direction)
    intakeRight.spin(direction) # Motor is configured reverse
    intakeRunning = True

def stopIntake(mode = HOLD):
    global intakeRunning
    intakeLeft.stop(mode)
    intakeRight.stop(mode)
    intakeRunning = False

def startIntake():
    windCat()
    if isContinuousCallback and isContinuousCallback():
        hugBall()
    else:
        releaseHug()  # Open up for the next ball
    spinIntake(REVERSE)

def reverseIntake():
    spinIntake(FORWARD)

def startBelt(release=False):
    global catBeltRunning
    releaseHug() if release else hugBall()
    catBeltLeft.spin(REVERSE)
    catBeltRight.spin(REVERSE)
    catBeltRunning = True

def stopCatAndBelt():
    global catBeltRunning
    catBeltLeft.stop(HOLD)
    catBeltRight.stop(HOLD)
    catBeltRunning = False

def releaseCat(cancelRewind = None): # Down Button
    releaseHug()
    startBelt(release=True)
    timeoutMs: int = 1000
    while (backEye.isObjectVisible() and timeoutMs > 0):
        wait(100, MSEC)
        timeoutMs -= 100

    catBeltRight.spin_for(FORWARD, 180, DEGREES, wait=False)
    catBeltLeft.spin_for(FORWARD, 180, DEGREES)
    # cancelWinding lets the caller of releaseCatapult() know
    # if winding should be cancelled (keeps tension off rubber bands)

    stopCatAndBelt()
    if (cancelRewind is None or not cancelRewind()): windCat()

def windCat():  # Up Button
    if (not isContinuousCallback or not isContinuousCallback()):
        releaseHug()
    if not catEye.isObjectVisible(): 
        catBeltLeft.spin(FORWARD)
        catBeltRight.spin(FORWARD)
        for _ in range(3 * 100):  # 3 seconds @ 10ms/loop
            if catEye.isObjectVisible(): break
            wait(10, MSEC)
        # TODO: Check if we still need/want this. Tune it to new Gen3 bot?
        # Spinning the catapult a little more because sensor placement can't go lower
        catBeltRight.spin_for(FORWARD, 10, DEGREES, wait = False)
        catBeltLeft.spin_for(FORWARD, 10, DEGREES)
        stopCatAndBelt()

def releaseHug(stop: bool = False):
  #  stopCatAndBelt()
  #  print("Stop1")
    ballHugger.pump_on()
    brainPrint("Releasing hug", True)
    ballHugger.retract(CylinderType.CYLINDER1)
    ballHugger.retract(CylinderType.CYLINDER2)

def hugBall():
    ballHugger.pump_on()
    brainPrint("Hugging", True)
    ballHugger.extend(CylinderType.CYLINDER1)
    ballHugger.extend(CylinderType.CYLINDER2)

def stopAll():
    stopCatAndBelt()
    windCat()
    releaseHug()
    if not intakeRunning: ballHugger.pump_off()  # Stop TWICE to shut off the pump
    stopIntake(HOLD)

def onCatSeen():
    pass

def onCatLost():
    pass

# Setup the callbacks
topEye.setCallbacks(onTopBallSeen, onTopBallLost)
catEye.setCallbacks(onCatSeen, onCatLost)
backEye.setCallbacks(onBackBallSeen, onBackBallLost)
intakeEye.setCallbacks(onIntakeBallSeen, onIntakeBallLost)

def run():
    setup()
    clearScreen()

# ============================================================================
# ============================================================================
# ============================================================================

controller: Controller = Controller()

def onLDown():
    stopCatAndBelt() if catBeltRunning else startBelt()

def cancelCatapultRewind():
    # Special trick: hold down EUp to cancel re-wind of catapult
    return controller.buttonEUp.pressing()

def releaseDriveCatapult():
    # This is passing a function, not a function call return value!
    releaseCat(cancelCatapultRewind)

def setupController():
    controller.buttonLUp.pressed(startIntake)  
    controller.buttonLDown.pressed(onLDown)
    controller.buttonRUp.pressed(releaseDriveCatapult)
    controller.buttonRDown.pressed(windCat)
    controller.buttonEDown.pressed(reverseIntake)
    controller.buttonFUp.pressed(stopAll)
    wait(15, MSEC)

def updateDriveMotor(drive: Motor, velocity: float, joystickTolerance: int):
    if math.fabs(velocity) <= joystickTolerance: velocity = 0
    drive.set_velocity(round(velocity), PERCENT)

def drive():
    global isContinuousCallback
    run()
    setupController()
    isContinuousCallback = lambda: controller.buttonLDown.pressing()
    clearScreen()
    brainPrint("Extreme Axolotls!")
    brainPrint("Ready")
    while True:
        updateDriveMotor(wheelRight, controller.axisD.position(), 5)
        updateDriveMotor(wheelLeft, controller.axisA.position(), 5)
        sleep(20, MSEC)


# Where it all begins.
drive()
