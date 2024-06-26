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

    def setup(self):
        self.brain = Brain()
        self.inertial = Inertial()
        self.controller = Controller()
        self.setupScreen()
        self.setupPortMappings()
        self.setupDrivetrain()
        self.setupController()
        self.setupCatapult()
        self.setupTensioner()
        self.setupEyes()

    def setupPortMappings(self):    
        # Gear ratio is 2:1
        self.wheelLeft = Motor(Ports.PORT7, 2.0, True)
        self.wheelRight = Motor(Ports.PORT12, 2.0, False)
        self.wheelCenter = Motor(Ports.PORT10, 2.0, False)
        self.catapult = Motor(Ports.PORT11)
        self.eyeLeft = ColorSensor(Ports.PORT2)
        self.eyeRight = ColorSensor(Ports.PORT5)
        self.catapultBumper = Bumper(Ports.PORT8)
        self.tensioner = Motor(Ports.PORT9)

    def setupEyes(self):
        self.eyeLeft.set_light_power(100)
        self.eyeRight.set_light_power(100)

    def setupTensioner(self):
        self.tensioner.set_velocity(100, PERCENT)
        self.tensioner.set_max_torque(100, PERCENT)
        self.controller.buttonRUp.pressed(self.windTensioner)
        self.controller.buttonRDown.pressed(self.unwindTensioner)

        
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

    def onCatapultBumperPressed(self):
        self.catapult.stop()

    def setupCatapult(self):
        self.catapult.set_velocity(50)
        self.catapult.set_stopping(HOLD)
        self.catapultBumper.pressed(self.onCatapultBumperPressed)
        self.controller.buttonLUp.pressed(self.windCatapult)
        self.controller.buttonLDown.pressed(self.releaseCatapult)

    def windCatapult(self):
        if not self.catapultBumper.pressing():
            self.catapult.spin(FORWARD)

    def releaseCatapult(self):
        if self.catapultBumper.pressing():
            self.catapult.spin_for(REVERSE, 600)

    def windTensioner(self):
        self.tensioner.set_stopping(HOLD)
        self.tensioner.spin_for(FORWARD, 180)

    def unwindTensioner(self):
        self.tensioner.set_stopping(COAST)
        self.tensioner.spin_for(REVERSE, 180)

    def setupDrivetrain(self):
        self.setupDriveMotor(self.wheelLeft)
        self.setupDriveMotor(self.wheelRight)
        self.setupDriveMotor(self.wheelCenter)

    def stopAll(self):
        pass
    
    def updateDriveMotor(self, drive: Motor, velocity: float, joystickTolerance: int):
        velocity = velocity**3
        velocity = velocity/10000
        if math.fabs(velocity) > joystickTolerance:
            drive.set_velocity(velocity, PERCENT)
        else:
            drive.set_velocity(0, PERCENT)

    def run(self):
        self.setup()
        #self.runManual()
        self.runAuto()

    def runAuto(self):
        self.print("Extreme Axolotls")
        self.driveToLine()
    
    def driveToLine(self):
        self.isRunning = True
        while self.isRunning: 
            print(str(self.eyeLeft.brightness())+  ", " + str(self.eyeRight.brightness()))
            sleep(500)


    def runManual(self):
        self.isRunning = True
        self.print("Extreme Axolotls!")
        self.print("Ready")
        while self.isRunning:
            strafePercent = self.controller.axisB.position() + self.controller.axisC.position()
            self.updateDriveMotor(self.wheelRight, self.controller.axisD.position(), 5)
            self.updateDriveMotor(self.wheelLeft, self.controller.axisA.position(), 5)
            self.updateDriveMotor(self.wheelCenter, strafePercent, 5)
            sleep(500)
            print(str(self.eyeLeft.color()))
            print(str(self.eyeLeft.brightness())+  ", " + str(self.eyeRight.brightness()))            


# Where it all begins!    
bot = Bot()
bot.run()