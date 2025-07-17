from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint
from kivy.lang import Builder

Builder.load_string('''
<PongBall>:
    size: 50, 50
    canvas:
        Ellipse:
            pos: self.pos
            size: self.size
        Color:
            rgb: 0, 0, 0  # Bola preta
            

<PongPaddle>:
    size: 25, 200
    canvas:
        Rectangle:
            pos: self.pos
            size: self.size 
        Color:
            rgb: 0, 0, 0  # Raquete preta    

<PongGame>:
    ball: pong_ball
    player1: left_paddle
    player2: right_paddle
    
    canvas:
        Color:
            rgb: 0.2, 0.2, 0.2
        Rectangle:
            pos: self.pos
            size: self.size
    
    Label:
        pos: root.center_x - 100, root.top - 100
        font_size: 50
        text: root.score_text
        color: 1, 1, 1, 1
    
    PongBall:
        id: pong_ball
        center: root.center
    
    PongPaddle:
        id: left_paddle
        x: root.x
        center_y: root.center_y
    
    PongPaddle:
        id: right_paddle
        x: root.width - self.width
        center_y: root.center_y
''')

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    
    def move(self):
        if not self.parent:
            return
        self.pos = Vector(*self.velocity) + self.pos

    def bounce_paddle(self, paddle):
        if not paddle or not self.parent:
            return
        if self.collide_widget(paddle):
            offset = (self.center_y - paddle.center_y) / (paddle.height / 2)
            bounced = Vector(-1 * self.velocity_x, self.velocity_y)
            self.velocity = bounced * 1.1
            self.velocity_y += offset * 2

class PongPaddle(Widget):
    score = NumericProperty(0)
    
    def bounce_ball(self, ball):
        if ball and self.parent:
            ball.bounce_paddle(self)

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    score_text = StringProperty("0 - 0")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Clock.schedule_once(self._finish_init)
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Player 1 (WASD)
        if keycode[1] == 'w':
            self.player1.center_y += 20
        elif keycode[1] == 's':
            self.player1.center_y -= 20
        
        # Player 2 (Setas)
        elif keycode[1] == 'up':
            self.player2.center_y += 20
        elif keycode[1] == 'down':
            self.player2.center_y -= 20
        
        
        return True
    
    def _finish_init(self, dt):
        if all([self.ball, self.player1, self.player2]):
            self.serve_ball()
        else:
            self.ball = PongBall(center=self.center)
            self.player1 = PongPaddle(x=self.x, center_y=self.center_y)
            self.player2 = PongPaddle(x=self.width-25, center_y=self.center_y)
            for widget in [self.ball, self.player1, self.player2]:
                self.add_widget(widget)
            self.serve_ball()
    
    def serve_ball(self, vel=(4, 0)):
        if not all([self.ball, self.player1, self.player2]):
            return
            
        self.ball.center = self.center
        self.ball.velocity = Vector(vel[0], vel[1]).rotate(randint(0, 360))
        self.update_score()
    
    def update_score(self):
        self.score_text = f"{self.player1.score} - {self.player2.score}"
    
    def update(self, dt):
        if None in (self.ball, self.player1, self.player2):
            return
            
        self.ball.move()
        
        # Colisão com topo e fundo
        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1
        
        # Colisão com raquetes
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)
        
        # Pontuação
        if self.ball.x < self.x:
            self.player2.score += 1
            self.update_score()
            self.serve_ball(vel=(4, 0))
        elif self.ball.x > self.width:
            self.player1.score += 1
            self.update_score()
            self.serve_ball(vel=(-4, 0))
    
    def on_touch_move(self, touch):
        # Mantém o controle por toque opcional
        if None in (self.player1, self.player2):
            return
            
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y

class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    PongApp().run()