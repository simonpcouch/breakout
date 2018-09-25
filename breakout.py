"""
This program implements the Breakout game.
"""


from pgl import GWindow, GOval, GRect, GLabel
import random

# Constants

GWINDOW_WIDTH = 360               # Width of the graphics window
GWINDOW_HEIGHT = 600              # Height of the graphics window
N_ROWS = 10                       # Number of brick rows
N_COLS = 10                       # Number of brick columns
BRICK_ASPECT_RATIO = 4 / 1        # Width to height ratio of a brick
BRICK_TO_BALL_RATIO = 3 / 2       # Ratio of brick width to ball size
BRICK_TO_PADDLE_RATIO = 2 / 3     # Ratio of brick width to paddle width
BRICK_SEP = 2                     # Separation between bricks
TOP_FRACTION = 0.1                # Fraction of window above bricks
BOTTOM_FRACTION = 0.05            # Fraction of window below paddle
N_BALLS = 3                       # Number of balls in a game
TIME_STEP = 10                    # Time step in milliseconds
INITIAL_Y_VELOCTIY = 3.0          # Starting y velocity downward
MIN_X_VELOCITY = 1.0              # Minimum random x velocity
MAX_X_VELOCITY = 3.0              # Maximum random x velocity

# Derived constants

BRICK_WIDTH = (GWINDOW_WIDTH - (N_COLS + 1) * (BRICK_SEP - 1)) / N_COLS
BRICK_HEIGHT = BRICK_WIDTH / BRICK_ASPECT_RATIO
PADDLE_WIDTH = BRICK_WIDTH / BRICK_TO_PADDLE_RATIO
PADDLE_HEIGHT = BRICK_HEIGHT / BRICK_TO_PADDLE_RATIO
PADDLE_Y = (1 - BOTTOM_FRACTION) * GWINDOW_HEIGHT - PADDLE_HEIGHT
BALL_SIZE = BRICK_WIDTH / BRICK_TO_BALL_RATIO

# Main Program

def Breakout():
    # "Setup" Stage -------------------------------------------

    # Make the array of bricks
    num_bricks = N_ROWS*N_COLS

    def createBricks():
        colors = ["Red", "Red", "Orange", "Orange", "Green", 
                  "Green", "Cyan", "Cyan", "Blue", "Blue"]
        
        y = GWINDOW_HEIGHT * TOP_FRACTION
        for i in range(N_ROWS):
            color = colors[i]
            x = (GWINDOW_WIDTH / 2) - ((BRICK_WIDTH + (BRICK_SEP - 1))*N_COLS/2)
            for i in range(N_COLS):
                brick = GRect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
                brick.setFilled(True)
                brick.setColor(color)
                gw.add(brick)
                x += BRICK_WIDTH + BRICK_SEP
            y += BRICK_HEIGHT + BRICK_SEP

    # Make the paddle
    paddle = GRect((GWINDOW_WIDTH / 2), 
                   (1 - BOTTOM_FRACTION)*GWINDOW_HEIGHT, 
                   PADDLE_WIDTH, 
                   PADDLE_HEIGHT)
    paddle.setFilled(True)
    def movePaddle(e):
        paddle.move(e.getX() - paddle.getX(), 0)
        if (e.getX() >= gw.getWidth() - PADDLE_WIDTH):
            paddle.setLocation(gw.getWidth() - PADDLE_WIDTH, 
                               (1 - BOTTOM_FRACTION)*GWINDOW_HEIGHT)

    # Create the ball
    def createBall():
        ball = GOval((GWINDOW_WIDTH / 2) - (BALL_SIZE / 2), 
                    (GWINDOW_HEIGHT/2), 
                    BALL_SIZE, 
                    BALL_SIZE)
        ball.setFilled(True)
        return(ball)

    gw = GWindow(GWINDOW_WIDTH, GWINDOW_HEIGHT)
    createBricks()
    gw.add(paddle)
    ball = createBall()
    gw.add(ball)
    gw.addEventListener("mousemove", movePaddle)
    nLives = 3
    def LivesMessage():
        lives_msg = GLabel("Lives: " + str(nLives),
                          (gw.getWidth()*.8),
                          (1-(BOTTOM_FRACTION/20))*GWINDOW_HEIGHT)
        lives_msg.setFont("18px 'Times New Roman'")
        return(lives_msg)
    lives_msg = LivesMessage()
    gw.add(lives_msg)

    # "Play" Stage -----------------------------------------------
    # Make the ball move
    timerBall = None
    timerCollision = None
    vy = 5.0
    vx = random.uniform(-1, 1) * random.uniform(MIN_X_VELOCITY,
                                          MAX_X_VELOCITY)

    def moveBall():
        nonlocal vx, vy
        ball.move(vx, vy)
        # Bounce off the right wall
        if (ball.getX() + BALL_SIZE >= gw.getWidth()):
            vx = -vx
        # Bounce off the left wall
        if (ball.getX() - 3 <= 0):
            vx = -vx
        
        # Bounce off the top
        if (ball.getY() <= 0):
            vy = -vy

    # Check for Collisions
    def collisionActionTop(x, y):
        nonlocal vy, num_bricks
        if gw.getElementAt(x, y) is not None and gw.getElementAt(x, y) != lives_msg:
            vy = -vy
            if (gw.getElementAt(x, y) != paddle):
                gw.remove(gw.getElementAt(x, y))
                num_bricks -= 1
                if (num_bricks == 0):
                    winGame()

    def collisionActionSide(x, y):
        nonlocal vx, num_bricks
        if gw.getElementAt(x, y) is not None and gw.getElementAt(x, y) != lives_msg:
            vx = -vx
            if (gw.getElementAt(x, y) != paddle):
                gw.remove(gw.getElementAt(x, y))
                num_bricks -= 1
                if (num_bricks == 0):
                    winGame()

    def checkCollision():
        nonlocal nLives, timerBall, timerCollision, ball, lives_msg, gw, vx
        # Top of the ball
        collisionActionTop(ball.getX() + (BALL_SIZE/2), 
                           ball.getY() - 1)
        # Bottom of the ball
        collisionActionTop(ball.getX() + (BALL_SIZE/2), 
                           ball.getY() + BALL_SIZE + 1)

        # Left side of the ball
        collisionActionSide(ball.getX() - 1, 
                            ball.getY() + (BALL_SIZE/2))
        # Right side of the ball
        collisionActionSide(ball.getX() + BALL_SIZE + 1, 
                            ball.getY() + (BALL_SIZE/2))
        # Check for collision with bottom of window
        # Also includes 'restart-up' code
        if (ball.getY() + BALL_SIZE >= gw.getHeight()):
            timerBall.stop()
            timerCollision.stop()
            if (nLives > 1):
                gw.remove(lives_msg)
                nLives -= 1
                lives_msg = LivesMessage()
                gw.add(lives_msg)
                gw.remove(ball)
                ball = createBall()
                gw.add(ball)
            elif (nLives == 1):
                gw.remove(lives_msg)
                nLives = 0
                lives_msg = LivesMessage()
                gw.add(lives_msg)
                lose_msg = GLabel("You lose!",
                                  gw.getWidth()/2 - 80,
                                  gw.getHeight()/2)
                lose_msg.setFont("36px 'Times New Roman'")
                gw.add(lose_msg)
            vx = random.uniform(-1, 1) * random.uniform(MIN_X_VELOCITY,
                                                  MAX_X_VELOCITY)

    # Start Moving the Ball and Checking for Collisions Upon Click
    def clickAction(e):
        nonlocal timerBall
        nonlocal timerCollision
        timerBall = gw.createTimer(moveBall, TIME_STEP)
        timerBall.setRepeats(True)
        timerBall.start()
        timerCollision = gw.createTimer(checkCollision, TIME_STEP)
        timerCollision.setRepeats(True)
        timerCollision.start()

    gw.addEventListener("click", clickAction)

    def winGame():
        nonlocal gw, timerBall, timerCollision
        timerBall.stop()
        timerCollision.stop()
        win_msg = GLabel("You win!",
                         gw.getWidth()/2 - 80,
                         gw.getHeight()/2)
        win_msg.setFont("36px 'Times New Roman'")
        gw.add(win_msg)

# Startup Code

if (__name__ == "__main__"):
    Breakout()
