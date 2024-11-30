# AXOBOTL Python Code
# Team 4028X Extreme Axolotls
# 2023-25 VEX IQ Rapid Relay Challenge
from vex import *


# The Eye class is useful for us
# Represents a Distance sensor that broadcasts if it "sees" an object
class Eye:
    def __init__(self, portNumber: int, distanceThreshold: int, units: DistanceUnits.DistanceUnits = DistanceUnits.MM):
        self.sensor = Distance(portNumber)
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
    
    def look(self) -> bool:
        if self.sensor.installed():
            if self.isObjectVisible():
                if not self.seen:
                    self.seen = True
                    self.lost = False
                    if self.eventSeen: self.eventSeen.broadcast()
                    return True
            else:
                if not self.lost:
                    self.seen = False
                    self.lost = True
                    if self.eventLost: self.eventLost.broadcast()
        return False

# Setup
brain = Brain()
inertial = Inertial()

wheelLeft = Motor(Ports.PORT7, 2.0, True)  # Gear ratio: 2:1
wheelRight = Motor(Ports.PORT12, 2.0, False)
intakeEye = Eye(Ports.PORT6, 80, MM)
topEye = Eye(Ports.PORT5, 50, MM)
catEye = Eye(Ports.PORT2, 30, MM)
backEye = Eye(Ports.PORT8, 30, MM)
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

def clearScreen(screenColor = None, penColor = None):
    screenColor = screenColor if screenColor is None else screenColor
    penColor = penColor if penColor is None else penColor
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

def onIntakeBallSeen(): 
    if topEye.isObjectVisible():
        print("starting")
        startBelt()
    else:
        stopCatAndBelt()
        if not isContinuousCallback or not isContinuousCallback():
            releaseHug()

def onIntakeBallLost():
    pass

def onTopBallSeen():
    if backEye.isObjectVisible():
        stopCatAndBelt()
    if not isContinuousCallback or not isContinuousCallback():
        if intakeEye.isObjectVisible(): stopIntake()
        releaseHug()

def onTopBallLost():
    if not topEye.isObjectVisible():
        if not catEye.isObjectVisible():
            stopIntake()
            windCat()
        if not topEye.isObjectVisible() and intakeEye.isObjectVisible(): spinIntake(REVERSE)
    
def onBackBallSeen():
    if not isContinuousCallback or not isContinuousCallback():
        stopIntake()

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
    if not catEye.isObjectVisible(): windCat()
    if isContinuousCallback and isContinuousCallback(): hugBall()
    else: releaseHug(stop=True)  # Open up for the next ball
    spinIntake(REVERSE)

def reverseIntake():
    spinIntake(FORWARD)

def startBelt(release=False):
    global catBeltRunning
    if release == False:
        hugBall()
    else:
        releaseHug()
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
    if not backEye.isInstalled() or backEye.isObjectVisible():
        startBelt(release=True)
        wait(500, MSEC)
    catBeltRight.spin_for(FORWARD, 180, DEGREES, wait=False)
    catBeltLeft.spin_for(FORWARD, 180, DEGREES)
    # cancelWinding lets the caller of releaseCatapult() know
    # if winding should be cancelled (keeps tension off rubber bands)
    stopCatAndBelt()
    if (cancelRewind is None or not cancelRewind()): windCat()

def windCat():  # Up Button
    releaseHug()
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

def releaseHug(stop: bool = True):
    if stop: stopCatAndBelt()
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
    releaseHug(stop=True)
    if not intakeRunning: ballHugger.pump_off()  # Stop TWICE to shut off the pump
    stopIntake(HOLD)

def onCatSeen():
    pass

def onCatLost():
    pass

# Broadcasters

def checkEyes():
    intakeEye.setCallbacks(onIntakeBallSeen, onIntakeBallLost)
    topEye.setCallbacks(onTopBallSeen, onTopBallLost)
    catEye.setCallbacks(onCatSeen, onCatLost)
    backEye.setCallbacks(onBackBallSeen, onBackBallLost)
    while True: # Loop forever in a thread (like "when started" in Vex Blocks)
        intakeEye.look()
        topEye.look()
        catEye.look()
        wait(10, MSEC)

sensorThread = Thread(checkEyes)

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
