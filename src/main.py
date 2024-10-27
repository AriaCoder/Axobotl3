# AXOBOTL Python Code
# Team 4028X Extreme Axolotls
# 2023-25 VEX IQ Rapid Relay Challenge
from vex import *


class Bot:
    def __init__(self):
        self.isRunning = False
        self.isScreenSetup = False
        self.screenColor = Color.BLUE
        self.penColor = Color.WHITE
        self.spinningFwd = False
        self.spinningRev = False
        self.cancelCalibration = False

    def setup(self):
        self.brain = Brain()
        self.inertial = Inertial()
        self.controller = Controller()
        self.setupScreen()
        self.setupPortMappings()
        self.setupDrivetrain()
        self.setupController()
        self.setupCatapult()
        self.setupIntake()
        self.setupStop()

    def setupPortMappings(self):    
        # Gear ratio is 2:1
        self.wheelLeft = Motor(Ports.PORT7, 2.0, True)
        self.wheelRight = Motor(Ports.PORT12, 2.0, False)
        self.intakeSensor = Distance(Ports.PORT6)
#       self.wheelCenter = Motor(Ports.PORT10, 2.0, True)
        self.catapultRight = Motor(Ports.PORT11,True)
        self.catapultLeft = Motor(Ports.PORT3)
        self.topSensor = Distance(Ports.PORT5)
        self.intakeRight = Motor(Ports.PORT1)
        self.intakeLeft = Motor(Ports.PORT4, True)
        self.catapultSensor = Distance(Ports.PORT2)
        self.LEDLeft = Touchled(Ports. PORT10)
        self.LEDRight = Touchled(Ports. PORT9)
        self.backBumper = Bumper(Ports.PORT8)



    def setupController(self):
        # Delay to make sure events are registered correctly.
        wait(15, MSEC)

    def setupScreen(self):
        if not self.isScreenSetup:
            self.brain.screen.clear_screen()
            self.brain.screen.set_font(FontType.MONO20)
            self.brain.screen.set_pen_color(self.penColor)
            self.brain.screen.set_fill_color(self.screenColor)
            self.brain.screen.set_cursor(1, 1)
            self.isScreenSetup = True
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
        self.setupScreen()
        self.brain.screen.print(message)
        self.brain.screen.new_line()
        print(message)  # For connected terminals

    def setupDriveMotor(self, motor: Motor):
        motor.set_velocity(0, PERCENT)
        motor.set_max_torque(100, PERCENT)
        motor.spin(FORWARD)

    def setupCatapult(self):
        self.catapultRight.set_velocity(50)
        self.catapultLeft.set_velocity(50)
        self.catapultRight.set_stopping(HOLD)
        self.catapultLeft.set_stopping(HOLD)
        self.controller.buttonRDown.pressed(self.windCatapult)
        self.controller.buttonRUp.pressed(self.releaseCatapult)
        self.backBumper.pressed(self.onBumperPressed)
        self.backBumper.released(self.onBumperReleased)


    def setupIntake(self):
        self.intakeRight.set_velocity(100)
        self.intakeLeft.set_velocity(100)
        self.controller.buttonLUp.pressed(self.intakeForward)
        self.controller.buttonLDown.pressed(self.intakeReverse)


    def intakeForward(self):
        self.isCatapultDown()
        if self.isCatapultDown(): # Is the catapult down?
            self.isBallinIntake() #Checks for ball in intake
            while not self.isBallinIntake(): #Until there is a ball in the intake, spin intake
                    print("In the loop")
                    self.intakeRight.spin(REVERSE)
                    self.intakeLeft.spin(REVERSE)
                    wait(100,MSEC)

            print (self.isBallinIntake()) # There is a ball in the intake now. Checking for catapult..
            if self.isBallinCatapult(): #Stop the intake if there is a ball in the catapult already.
                print(self.isBallinCatapult())
                self.intakeRight.stop()
                self.intakeLeft.stop()
            else: # No ball in catapult?
                while not self.isBallinCatapult(): #Until there is a ball in the catapult, spin intake
                    self.intakeRight.spin(REVERSE)
                    self.intakeLeft.spin(REVERSE)
                    wait(100,MSEC)

                while not self.isBallinIntake(): #Until there is a ball in the intake, spin intake
                    self.intakeRight.spin(REVERSE)
                    self.intakeLeft.spin(REVERSE)
                    wait(100,MSEC)
                self.intakeRight.stop()
                self.intakeLeft.stop()
                
                while self.isBallinCatapult():
                    wait(100, MSEC)
                if self.isCatapultDown():
                    self.intakeRight.spin(REVERSE)
                    self.intakeLeft.spin(REVERSE)
                else:
                    self.windCatapult()
                    self.intakeRight.spin(REVERSE)
                    self.intakeLeft.spin(REVERSE)
                
        else: # The catapult is up... somehow
            self.intakeRight.spin(REVERSE) 
            self.intakeLeft.spin(REVERSE)
            self.windCatapult() #lower the catapul

    def intakeReverse(self):
        self.intakeLeft.spin(FORWARD)
        self.intakeRight.spin(FORWARD)

    def isCatapultDown(self):
        return self.catapultSensor.object_distance(MM) < 80
    
    def isBallinIntake(self):
        return self.intakeSensor.object_distance(MM) < 100
    
    def isBallinCatapult(self):
        return self.topSensor.object_distance(MM) < 50
    

    def onBumperPressed(self):
        if self.backBumper.pressing():
            self.brain.play_sound(SoundType.TADA)
            self.LEDLeft.set_color(Color.GREEN)

    def onBumperReleased(self):
        self.LEDLeft.off()

    def releaseCatapult(self): # Down Button
        if self.isCatapultDown():
            self.catapultRight.spin_for(FORWARD, 180, DEGREES, wait=False)
            self.catapultLeft.spin_for(FORWARD, 180, DEGREES)
            if self.controller.buttonEUp.pressing():
                return
            self.isCatapultDown()
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

    def setupDrivetrain(self):
        self.setupDriveMotor(self.wheelLeft)
        self.setupDriveMotor(self.wheelRight)
 #       self.setupDriveMotor(self.wheelCenter)

    def setupStop(self):
        self.controller.buttonFUp.pressed(self.stopAll)

    def stopAll(self):
        self.catapultRight.stop(HOLD)    
        self.catapultLeft.stop(HOLD)    
        self.intakeRight.stop(HOLD)
        self.intakeLeft.stop(HOLD)

    def updateDriveMotor(self, drive: Motor, velocity: float, joystickTolerance: int):
        velocity = velocity**3
        velocity = velocity/10000
        if math.fabs(velocity) > joystickTolerance:
            drive.set_velocity(velocity, PERCENT)
        else:
            drive.set_velocity(0, PERCENT)

    def run(self):
        self.setup()
        self.runManual()
        #self.runAuto()

    def wiggleToPlace(self, headinginDeg: float = 0.0):
        error = (self.inertial.heading() - headinginDeg)/180
        self.wheelRight.set_velocity(30 * (1 + error), PERCENT)
        self.wheelLeft.set_velocity(30 * (1 - error), PERCENT)
        while error < 30 and error > 330:
            wait (1)

    def rotateToPlace(self, headinginDeg: float = 0.0):
        error = (headinginDeg - self.inertial.heading())/180
        self.wheelRight.set_velocity(20 * (1 + error), PERCENT)
        self.wheelLeft.set_velocity(20 * (-1 - error), PERCENT)
        while error > 30 and error < 330:
            wait (1)

    def runManual(self):
        self.isRunning = True
        self.print("Extreme Axolotls!")
        self.print("Ready")
        while self.isRunning:
            strafePercent = self.controller.axisB.position() + self.controller.axisC.position()
            self.updateDriveMotor(self.wheelRight, self.controller.axisD.position(), 5)
            self.updateDriveMotor(self.wheelLeft, self.controller.axisA.position(), 5)
 #           self.updateDriveMotor(self.wheelCenter, strafePercent, 5)
            sleep(100)
        #    print(str(self.eyeLeft.color()))
        #   print(str(self.eyeLeft.brightness())+  ", " + str(self.eyeRight.brightness()))            


# Where it all begins!    
bot = Bot()
bot.run()
