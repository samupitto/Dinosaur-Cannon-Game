from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto') #Set fullscreen automatically
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, Rotate, Translate, PushMatrix, PopMatrix
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen,FadeTransition
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.core.audio import SoundLoader
import math
import random
import threading
import time
import os


#constant used to abjust the value (dimension,speed) of object when a different resolution is used
ww=Window.width/2520
wh=Window.height/1680



def projectile_dynamics(start_time,projectile,velocity,gravity): #FIXED 24-07-24
    time_elapsed = Clock.get_boottime() - start_time
    x = projectile[0] + velocity[0]
    y = projectile[1] + velocity[1] - (0.5 * gravity * time_elapsed ** 2)
    return x,y

def velocity_decomposition(projectile_vel,angle): #FIXED 24-07-24
    projectile_vel_x = projectile_vel * math.cos(math.radians((angle) + 90))
    projectile_vel_y = projectile_vel * math.sin(math.radians((angle) + 90))
    return projectile_vel_x,projectile_vel_y


def activation(obj,tank,cannon,rotation,rotate):  #Function that manages projectiles Activations
    if not obj.IsActive:
        obj.IsActive=True
        obj.start_time= Clock.get_boottime()
        cannon_tip_x = tank.pos[0] + tank.size[0] / 2
        cannon_tip_y = tank.pos[1] + tank.size[1] / 2 + cannon.size[0] / 2
        obj.set_pos(cannon_tip_x + cannon.size[1] * math.cos(math.radians((rotation.angle) + 90)), cannon_tip_y + cannon.size[1] * math.sin(math.radians((rotation.angle) + 90)))
        if rotate is True:
            obj.set_rotation(rotation.angle +90)
        return obj.start_time and obj.IsActive
#Collision detection function

def collides(rect1, rect2):
    # Extract the top-left corner and dimensions of both rectangles
    r1x, r1y, r1w, r1h = rect1[0][0], rect1[0][1], rect1[1][0], rect1[1][1]
    r2x, r2y, r2w, r2h = rect2[0][0], rect2[0][1], rect2[1][0], rect2[1][1]

    # Check for no overlap 
    if (r1x + r1w <= r2x) or (r2x + r2w <= r1x) or (r1y + r1h <= r2y) or (r2y + r2h <= r1y):
        return False

    else:
        return True                         

def point_up(points,display):
    points += 1
    display = str(points)

def collision_manager(projectiles,objectives): #takes as arguments two list of objects ,then check collision for every pair of objects from different lists
    for proj in projectiles:
        if proj.IsActive:
            for obj in objectives:
                if hasattr(obj,"obj"):
                    if collides((proj.proj.pos,proj.proj.size),(obj.obj.pos,obj.obj.size)):
                        if hasattr(proj,"nondeadly"):
                            proj.IsColliding=True
                        elif hasattr(proj,"reflective") and hasattr(obj,"reflective"):
                            proj.set_rotation(proj.rotation_angle.angle + (180 - (proj.rotation_angle.angle * 2)))
                            proj.proj_velocity_y=-proj.proj_velocity_y
                        elif hasattr(obj,"hard") and not hasattr(proj,"BreakHard"):
                            proj.IsColliding=True
                        else:

                            proj.IsColliding=True
                            obj.IsColliding=True
                    
                    
                else:
                    if collides((proj.proj.pos,proj.proj.size),(obj.pos,obj.size)):
                        proj.IsColliding=True
                        

                    


def get_file_path(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute directory of the current script
    return os.path.join(script_dir, filename)



#LEADERBORD FUNCTION
def read_leaderboard(file_path):
    leaderboard = {}
    if not os.path.exists(file_path): #Check if the file exists
        open(file_path, 'w').close()  # Create the file if it doesn't exist
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                name, points, image_path = line.strip().split(',')
                leaderboard[name] = {'points': int(points), 'image_path': image_path}
    return leaderboard

def write_leaderboard(file_path, leaderboard):
    # Sort leaderboard by points in descending order
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1]['points'], reverse=True)
    with open(file_path, 'w') as file:
        for name, data in sorted_leaderboard:
            file.write(f"{name},{data['points']},{data['image_path']}\n")

def update_leaderboard(file_path, name, points, image_path):
    leaderboard = read_leaderboard(file_path)
    
    # Check if the name already exists and compare points
    if name in leaderboard:
        if points > leaderboard[name]['points']:
            leaderboard[name]['points'] = points
            leaderboard[name]['image_path'] = image_path
    else:
        leaderboard[name] = {'points': points, 'image_path': image_path}  # Add new entry if the name does not exist
    
    write_leaderboard(file_path, leaderboard)

filename = 'leaderboard.txt'
file_path = get_file_path(filename)


#Login session manager functions

login_session= get_file_path('login_session.txt')

def read_login_session():         
    if not os.path.exists(login_session):
        return {"logged_in": False, "username": ""}
    with open(login_session, 'r') as file:
        data = file.read().strip().split(',')
        return {"logged_in": data[0] == 'true', "username": data[1]} if len(data) > 1 else {"logged_in": False, "username": ""} #Check if a user is logged in

def write_login_session(logged_in, username=""):
    with open(login_session, 'w') as file:
        file.write(f"{str(logged_in).lower()},{username}")


class LoginManager:
    def __init__(self):
        self.session = read_login_session()

    def is_logged_in(self):
        return self.session["logged_in"]

    def get_username(self):
        return self.session["username"]

    def login(self, username):
        self.session["logged_in"] = True
        self.session["username"] = username
        write_login_session(True, username)

    def logout(self):
        self.session["logged_in"] = False  #Set the values of the Login state to default (no-one logged in)
        self.session["username"] = ""
        write_login_session(False)
    
    def user_exists(self, username):
        leaderboard = read_leaderboard(get_file_path('leaderboard.txt')) 
        return username in leaderboard

    def add_user_to_leaderboard(self, username, image_path):  #add user to the leaderboard if not already present
        leaderboard = read_leaderboard(get_file_path('leaderboard.txt'))
        leaderboard[username] = {'points': 0, 'image_path': image_path}
        write_leaderboard(get_file_path('leaderboard.txt'), leaderboard)

        
#Login Screen 
class LoginScreen(Screen):
    def __init__(self, login_manager, **kwargs):
        super().__init__(**kwargs)
        self.login_manager = login_manager

        layout = FloatLayout()

        #Mascotte image
        layout.add_widget(Image(size_hint=(None, None), size=(600, 1000), pos_hint={'center_x': 0.8, 'center_y': 0.3}, source="./img/mascotte.png"))
        
        # Title Label
        layout.add_widget(Label(text='INSERT YOUR USERNAME', font_size='40sp', bold=True, color=(1, 0, 0, 1), 
                                size_hint=(None, None), size=(300, 50), pos_hint={'center_x': 0.5, 'center_y': 0.9}))

        # Username Input
        self.username_input = LimitedTextInput(hint_text="Enter your username", size_hint=(None, None), size=(300, 50), pos_hint={'center_x': 0.5, 'center_y': 0.6}, multiline=False)
        layout.add_widget(self.username_input)

        # Login Button
        self.login_btn = Button(text="Login", size_hint=(None, None), size=(300, 50), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        self.login_btn.bind(on_release=self.check_username)
        layout.add_widget(self.login_btn)

        # Exit Button
        self.exit_btn = Button(text="Exit", size_hint=(None, None), size=(300, 50), pos_hint={'center_x': 0.5, 'center_y': 0.2})
        self.exit_btn.bind(on_release=self.exit_app)
        layout.add_widget(self.exit_btn)

        self.add_widget(layout)

    def check_username(self, instance): #Check if a player is already registered to the game
        username = self.username_input.text
        if username:
            if self.login_manager.user_exists(username): #If the player is already registered , skip to the main menu, else make them select an avatar
                self.login_manager.login(username)
                App.get_running_app().switch_screen('menu')
            else:
                self.show_avatar_selection()

    def show_avatar_selection(self):
        self.clear_widgets()
        layout = FloatLayout()
        layout.add_widget(Image(size_hint=(None, None), size=(600, 1000), pos_hint={'center_x': 0.8, 'center_y': 0.3}, source="./img/mascotte.png"))
        layout.add_widget(Label(text='CHOOSE YOUR AVATAR', font_size='40sp', bold=True, color=(1, 0, 0, 1), 
                                size_hint=(None, None), size=(300, 50), pos_hint={'center_x': 0.5, 'center_y': 0.9}))

        # Avaible Avatar images
        self.avatar_images = [
            "./img/tricerabro_icon.png",
            "./img/pterodabro_icon.png",
            "./img/stegosabro_icon.png",
            "./img/tyrannobro_icon.png",
            "./img/velocibro_icon.png",
            "./img/brontosabro.png",
            "./img/calciosabro.png",
            "./img/tramontosabro.png",
            "./img/pokersabro.png",
            "./img/gamersabro.png",
            "./img/pancakesabro.png",
            "./img/piscinasabro.png"
        ]
        self.selected_image_index = 0

        # Display the first avatar image
        self.avatar_image = Image(source=self.avatar_images[self.selected_image_index], size_hint=(None, None), size=(500*ww, 500*ww), pos_hint={'center_x': 0.5, 'center_y': 0.6})
        layout.add_widget(self.avatar_image)

        # Left button to switch the image
        self.left_btn = Button(text="<", size_hint=(None, None), size=(100*ww, 100*ww), pos_hint={'center_x': 0.3, 'center_y': 0.6})
        self.left_btn.bind(on_release=self.switch_image_left)
        layout.add_widget(self.left_btn)

        # Right button to switch the image
        self.right_btn = Button(text=">", size_hint=(None, None), size=(100*ww, 100*ww), pos_hint={'center_x': 0.7, 'center_y': 0.6})
        self.right_btn.bind(on_release=self.switch_image_right)
        layout.add_widget(self.right_btn)

        # Save button
        self.save_btn = Button(text="Save", size_hint=(None, None), size=(150*ww, 80*ww), pos_hint={'center_x': 0.5, 'center_y': 0.3})
        self.save_btn.bind(on_release=self.save_user)
        layout.add_widget(self.save_btn)

        self.add_widget(layout)

    def switch_image_left(self, instance):
        self.selected_image_index = (self.selected_image_index - 1) % len(self.avatar_images)
        self.avatar_image.source = self.avatar_images[self.selected_image_index]

    def switch_image_right(self, instance):
        self.selected_image_index = (self.selected_image_index + 1) % len(self.avatar_images)
        self.avatar_image.source = self.avatar_images[self.selected_image_index]

    def save_user(self, instance):      #Save the user data (username and image) and update login state
        username = self.username_input.text
        selected_image = self.avatar_images[self.selected_image_index]
        self.login_manager.add_user_to_leaderboard(username, selected_image)
        self.login_manager.login(username)
        App.get_running_app().switch_screen('menu')

    def exit_app(self, instance):
        App.get_running_app().stop()

class LimitedTextInput(TextInput):   #Textimput class with 11 maxlenght
    def __init__(self, max_length=11, **dinobros):
        super().__init__(**dinobros)
        self.max_length = max_length
        self.bind(on_text=self.on_text)

    def on_text(self, instance, value):
        if len(instance.text) > self.max_length:
            instance.text = instance.text[:self.max_length]


#Leaderboard Screen
class Top3Screen(Screen):
    def __init__(self, **dinobros):
        super(Top3Screen, self).__init__(**dinobros)
        with self.canvas.before:
            self.background= Rectangle(source="./img/podium.png",size=(Window.width,Window.height),pos=(0,0))
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.entries = []
        self.background_music =SoundLoader.load('./music/Jurassic Groove.mp3')

        # Create widgets for the top 3 entries
        for i in range(3):

            #Avatar Image
            img = Image(size_hint=(None, None), size=(300*ww, 300*wh))

            #Name Label
            name_label = Label(text="", size_hint=(None, None), size=(200*ww, 100*wh),bold=True,font_size=40,color=(0, 0, 0, 1))
            
            #Points Label
            points_label = Label(text="", size_hint=(None, None), size=(200*ww, 100*wh),bold=True,font_size=40,color=(1, 0, 0, 1))
            self.entries.append((img, name_label, points_label))
            self.layout.add_widget(img)
            self.layout.add_widget(name_label)
            
            self.layout.add_widget(points_label)

        #Main Menu button
        self.back_btn = Button(text="Back to Menu", size_hint=(None, None), size=(250* ww, 90 * wh),
                                pos_hint={'center_x': 0.49, 'center_y': 0.16},background_color=(194/255, 178/255, 128/255, 1))
        self.back_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('menu'))
        self.layout.add_widget(self.back_btn)
        
        

    def on_pre_enter(self):
        # Update the top 3 entries before entering the screen
        file_path = get_file_path('leaderboard.txt')
        leaderboard = read_leaderboard(file_path)
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1]['points'], reverse=True)

        positions = [
            {'center_x': 0.5, 'center_y': 0.78},  # First place
            {'center_x': 0.345, 'center_y': 0.45},  # Second place (lower left)
            {'center_x': 0.65, 'center_y': 0.45}   # Third place (lower right)
        ]

        for i, (img, name_label, points_label) in enumerate(self.entries):  #Extract the top 3 players 
            if i < len(sorted_leaderboard):
                name, data = sorted_leaderboard[i]
                img.source = data['image_path']
                name_label.text = name
                points_label.text = str(data['points'])

                img.pos_hint = positions[i]
                name_label.pos_hint = {'center_x': positions[i]['center_x'], 'top': img.pos_hint['center_y'] + 0.165}
                points_label.pos_hint = {'center_x': positions[i]['center_x'], 'top': img.pos_hint['center_y'] + 0.14}

                # Make widgets visible
                img.opacity = 1
                name_label.opacity = 1
                points_label.opacity = 1
            else:
                # Hide widgets if there are not enough users
                img.opacity = 0
                name_label.opacity = 0
                points_label.opacity = 0
            
            if self.background_music:
                self.background_music.play()
                self.background_music.loop=True

    def on_leave(self): #Stop the music when leaving the screen
        if self.background_music:
            self.background_music.stop()
    
    


class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical')

        # Title
        layout.add_widget(Label(text="Help", font_size='40sp', bold=True, color=(0, 0, 1, 1), size_hint=(1, None), height=50))

        # ScrollView for the content
        scroll_view = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, padding=20, spacing=30)
        content.bind(minimum_height=content.setter('height'))

        def add_section_title(text, font_size, color):
            content.add_widget(Label(text=text, font_size=font_size, bold=True, color=color, size_hint_y=None, height=40))

        def add_text(text):
            content.add_widget(Label(text=text, color=(1, 1, 1, 1), font_size='20sp', size_hint_y=None, text_size=(Window.width * 0.8, None), halign='left', valign='middle'))

        def add_hotkey_section(title, hotkeys):
            add_section_title(title, '32sp', (0, 0, 1, 1))
            hotkey_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
            hotkey_layout.bind(minimum_height=hotkey_layout.setter('height'))
            for key, function in hotkeys:
                key_layout = BoxLayout(size_hint_y=None, height=40, padding=(10, 5))
                key_layout.add_widget(Label(text=f"{key}: {function}", color=(1, 1, 1, 1), font_size='20sp', size_hint=(0.8, None), height=40))
                hotkey_layout.add_widget(key_layout)
            content.add_widget(hotkey_layout)

        # Adding sections
        add_text("")
        add_section_title("Main Game", '32sp', (0, 0, 1, 1))
        add_text("In the Main modality your objective is to defeat the Dinocyborgs using your arsenal. The modality is subdivised in different levels and in a final boss battle with the powerful Cyrannus.")
        add_text("")
        main_hotkeys = [
            ("D", "Move to the right"),
            ("A", "Move to the left"),
            ("W", "Rotate the cannon clockwise"),
            ("S", "Rotate the cannon counterclockwise"),
            ("L", "Fire the laser"),
            ("Space", "Fire the bullet"),
            ("M", "Fire the Meteor Caller"),
            ("P", "Increase Powerbar"),
            ("O", "Decrease Powerbar"),
        ]
        add_hotkey_section("HotKeys for Main Mode", main_hotkeys)
        add_text("")
        add_section_title("Extinction Modality", '32sp', (0, 0, 1, 1))
        add_text("In the Extinction Modality, your strongest weapon will become your strongest fear. Giant meteors are falling from the sky. In this modality, there is no need to save the day; your only objective is to survive. Your points in this modality will be shown in the Leaderboard.")
        add_text("")
        extinction_hotkeys = [
            ("D", "Move to the right"),
            ("A", "Move to the left"),
            ("W", "Rotate cannon clockwise"),
            ("S", "Rotate cannon counterclockwise"),
            ("Space", "Fire the laser"),
        ]
        add_hotkey_section("HotKeys for Extinction Mode", extinction_hotkeys)
        add_text("")
        content.height = content.minimum_height
        scroll_view.add_widget(content)
        layout.add_widget(scroll_view)

        # Back Button
        back_btn = Button(text="Back to Menu", size_hint=(None, None), size=(200, 50), pos_hint={'center_x': 0.5, 'y': 0.1})
        back_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('menu'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)



    


#Main Menu Screen
class MainMenu(Screen): #the buttons images are part of the background, invisible buttons are placed in the spaces
    def __init__(self, login_manager, **kwargs):
        super().__init__(**kwargs)
        self.login_manager = login_manager
        #Start Button
        self.start_btn = Button(size_hint=(None, None), size=(300, 125), background_color=(0, 0, 0, 0))
        self.start_btn.pos_hint = {'center_x': 0.41, 'center_y': 0.065}
        self.start_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('modality')) #Bind the action to the switch screen function
        self.add_widget(self.start_btn)
        #Exit Game Button
        self.stop_btn = Button(size_hint=(None, None), size=(325, 125), pos_hint={'center_x': 0.74, 'center_y': 0.065}, background_color=(0, 0, 0, 0))
        self.stop_btn.bind(on_release=lambda x: App.get_running_app().stop())
        self.add_widget(self.stop_btn)
        #Option Button
        self.menu_btn = Button(size_hint=(None, None), size=(325, 125), pos_hint={'center_x': 0.583, 'center_y': 0.065}, background_color=(0, 0, 0, 0))
        self.menu_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('option'))
        self.add_widget(self.menu_btn)
        #Help Button
        self.help_btn = Button(size_hint=(None, None), size=(325, 125), pos_hint={'center_x': 0.245, 'center_y': 0.065}, background_color=(0, 0, 0, 0))
        self.help_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('help'))
        self.add_widget(self.help_btn)

        with self.canvas.before:
            self.background = Rectangle(source="./img/dinosaurscreen.png", pos=(0, 0), size=(Window.width, Window.height))

        self.background_music = SoundLoader.load('./music/Your Jurassic Era.mp3')
        self.background_music.loop = True

    
            
            

        



#Option Menu Screen
class OptionMenu(Screen):
    def __init__(self, login_manager, **dinobros):
        super().__init__(**dinobros)
        self.login_manager = login_manager
        layout = FloatLayout()
        #Big Red Text
        layout.add_widget(Label(text='OPTION MENU', font_size='40sp', bold=True, color=(1, 0, 0, 1), 
                                size_hint=(None, None), size=(300, 50), pos_hint={'center_x': 0.5, 'center_y': 0.9}))
        #Music Volume Label
        layout.add_widget(Label(text="MUSIC VOLUME", font_size='30sp', color=(0, 0, 1, 1),
                                  size_hint=(None, None), size=(150 * ww, 50 * wh), pos_hint={'center_x': 0.2, 'center_y': 0.65}))
        #Main Menu Button
        self.main_btn = Button(text="Menu", size_hint=(None, None), size=(300 * ww, 125 * wh), background_color=(1, 1, 1, 1),
                               pos_hint={'center_x': 0.5, 'center_y': 0.6})
        self.main_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('menu'))
        layout.add_widget(self.main_btn)
        #Logout Button
        self.logout_btn = Button(text="Logout", size_hint=(None, None), size=(300 * ww, 125 * wh), background_color=(1, 0, 0, 1),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.2})
        self.logout_btn.bind(on_release=self.logout) #logout function when pressed 
        layout.add_widget(self.logout_btn)
        #Leaderboard button
        self.leaderboard_btn = Button(text="Leaderboard", size_hint=(None, None), size=(300 * ww, 125 * wh), background_color=(0.76, 0.70, 0.50, 1),
                                      pos_hint={'center_x': 0.5, 'center_y': 0.4})
        self.leaderboard_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('leaderboard'))
        layout.add_widget(self.leaderboard_btn)

        # Volume slider
        self.volume_slider = Slider(min=0, max=1, value=App.get_running_app().main_menu.background_music.volume, 
                                    orientation='vertical', size_hint=(None, None), size=(50 * ww, 300 * wh), pos_hint={'center_x': 0.2, 'center_y': 0.4})
        self.volume_slider.bind(value=self.on_volume_change) #change volume of the musics
        layout.add_widget(self.volume_slider)

        self.add_widget(layout)

    def logout(self, instance): #logout (return to default login state) and go to login screen
        self.login_manager.logout()
        App.get_running_app().switch_screen('login')

    def on_volume_change(self, instance, value):
        App.get_running_app().set_volume(value) #return the value of the volume


        
#Choose Modality Screen 
class ModalityMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
           self.background= Rectangle(source="./img/dinosfondo.jpg",pos=(0,0),size=(Window.width,Window.height)) #ugly
        layout = FloatLayout()
        #Main Game Button
        main_game_btn = Button(text="Main Game", size_hint=(None, None), size=(300 * ww, 125 * wh),
                               pos_hint={'center_x': 0.5, 'center_y': 0.65}, background_color=(0.2, 0.6, 0.2, 1))
        main_game_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('game'))
        layout.add_widget(main_game_btn)
        #Secondary Modality (Extintion) Button
        extinction_btn = Button(text="Extinction Modality", size_hint=(None, None), size=(300 * ww, 125 * wh),
                                pos_hint={'center_x': 0.5, 'center_y': 0.45}, background_color=(0.8, 0.2, 0.2, 1))
        extinction_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('est'))
        layout.add_widget(extinction_btn)
        #return to the main menu
        back_to_menu_btn = Button(text="Back to Menu", size_hint=(None, None), size=(300 * ww, 125 * wh),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.25}, background_color=(0.6, 0.6, 0.6, 1))
        back_to_menu_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('menu'))
        layout.add_widget(back_to_menu_btn)

        self.add_widget(layout)



#Bullet Class
class Bullet(Widget):
    def __init__(self, player, cannon, cannon_rotation,powerbar, **dinobros):
        super().__init__(**dinobros)
        self.name="Bulllet"
        self.player = player
        self.cannon = cannon
        self.cannon_rotation = cannon_rotation 
        self.IsActive = False
        self.IsColliding=False
        self.powerbar=powerbar
        with self.canvas:
            self.ellipse_color = Color(1, 1, 1, 1)
            self.proj = Rectangle(size=(15*ww, 15*ww), source=("./img/goma.png"), pos=(3000, 3000))  # Charateristic of the bullet
        

    def set_pos(self, x, y): #Change position of the bullet
        self.proj.pos = (x, y)
    
    def activate_bullet(self):  #Activate the bullet, set position 
            self.bullet_velocity = math.sqrt(1*ww * self.powerbar.powerbar.size[0] / 1)
            activation(self,self.player,self.cannon,self.cannon_rotation,None)
            print(self.start_time)
            print(self.IsActive)

    
    def movement(self):
        x=projectile_dynamics(self.start_time,self.proj.pos,velocity_decomposition(self.bullet_velocity,self.cannon_rotation.angle),98)[0]
        y=projectile_dynamics(self.start_time,self.proj.pos,velocity_decomposition(self.bullet_velocity,self.cannon_rotation.angle),98)[1]
        self.set_pos(x, y)

            # Deactivate bullet if it goes outside the screen
        if x > Window.width or y < Window.height / 15 or x < 0 or self.IsColliding:
            self.IsActive = False
            self.set_pos(x, -8000)
            self.IsColliding = False


class PowerBar(Widget):
    def __init__(self, **dinobros):
        super().__init__(**dinobros)

        with self.canvas:
            self.powerbar_color = Color(0, 2, 1, 1)
            self.powerbar = Rectangle(pos=(Window.width / 1.6, Window.height / 1.15), size=(140*ww, (323 / 3.5)*wh))  # Charateristic of the powerbar

        with self.canvas:
            self.container_powe = Color(1, 1, 1, 1)
            self.container_powe = Rectangle(pos=(Window.width / 1.7, Window.height / 1.2), size=((1423 / 1.5)*ww, (323 / 1.5)*wh), source="./img/powerbar.png") #Outer Frame


class Mirror(Widget):
    def __init__(self, **dinobros):
        super().__init__(**dinobros)
        self.vertical = False
        self.name="Mirror"
        self.IsColliding=False
        self.reflective=True
        with self.canvas:
            self.mirror_color = Color(0, 0.5, 0.7, 0.5)
            self.obj = Rectangle(size=(350*ww, 30*wh), pos=(Window.width / 2 - 175*ww, Window.height / 2)) #Charateristic of the mirror
        

    #Change the orientation of the mirror 
    def setVertical(self):  
        self.vertical = True
        x = self.obj.size[0]
        y = self.obj.size[1]
        self.obj.size = (y, x)

    def setHorizontal(self):
        self.vertical = False
        x = self.obj.size[0]
        y = self.obj.size[1]
        self.obj.size = (x, y)

    def posMirror(self, x, y): #set the position of the mirror
        self.obj.pos = (x, y)


class Laser(Widget):
    def __init__(self, player, cannon, cannon_rotation, **kwargs): #take data from tank class
        super().__init__(**kwargs)
        self.player = player
        self.cannon = cannon
        self.cannon_rotation = cannon_rotation
        self.start_time=None
        self.IsActive = False
        self.IsColliding=False
        self.reflective=True
        self.color_target = [random.random() for _ in range(3)] #Change color

        with self.canvas:
            self.laser_color = Color(1, 0, 0, 1)
            PushMatrix()
            self.laser_translation = Translate(0, 0)
            self.rotation_angle = Rotate(angle=0, origin=(0, 0))
            self.laser = Rectangle(size=(100, 15), pos=(3000, 3000))
            PopMatrix()
        with self.canvas:
            self.proj=Color(0,0,0,0)
            self.proj=Rectangle(size=(15,15),pos=(3000,3000))


        Clock.schedule_interval(self.update_color, 1 / 60)

    def set_trans_laser(self, x, y): 
        self.laser_translation.x = x
        self.laser_translation.y = y

    def set_pos_laser(self, x, y):
        self.laser.pos = (x, y)

    def set_pos(self,x,y):
        self.proj.pos=(x,y)

    def set_rotation(self, angle): 
        self.rotation_angle.angle = angle

    def update_color(self, dt): #Multiccolor!
        color_diff = [self.color_target[i] - self.laser_color.rgba[i] for i in range(3)]
        if all(abs(diff) < 0.01 for diff in color_diff):
            self.color_target = [random.random() for _ in range(3)]
        new_color = [self.laser_color.rgba[i] + color_diff[i] * dt * 8 for i in range(3)]
        self.laser_color.rgba = new_color + [1]

    def activate_laser(self): #Activate the laser, set the inclination and speed
        self.set_pos_laser(0,0)
        self.proj_velocity_x = velocity_decomposition(30,self.cannon_rotation.angle)[0]
        self.proj_velocity_y = velocity_decomposition(30,self.cannon_rotation.angle)[1]
        activation(self,self.player,self.cannon,self.cannon_rotation,True)
            
    
    def movement(self):
        
        x = projectile_dynamics(self.start_time,self.proj.pos,(self.proj_velocity_x,self.proj_velocity_y),0)[0]
        y = projectile_dynamics(self.start_time,self.proj.pos,(self.proj_velocity_x,self.proj_velocity_y),0)[1]
        self.set_pos(x, y)
        self.set_trans_laser(self.proj.pos[0],self.proj.pos[1])

        if x > Window.width or y < Window.height / 15 or y > Window.height or x < 0 or self.IsColliding: #deactivate if collides or outside window
            self.IsActive = False
            self.set_trans_laser(0, -5000)
            self.IsColliding = False

    

#Enemy Class
class Velociraptor(Widget):
    def __init__(self, **dinobros):
        super().__init__(**dinobros)
        self.enemy_music = SoundLoader.load('./music/roar.mp3')
        self.IsColliding=False

        with self.canvas:
            self.obj = Color(1, 1, 1, 1)
            self.obj = Rectangle(source="./img/winipo.png", pos=(Window.width / 1.5, Window.height / 18), size=(250*ww, 400*wh)) #Enemy Charateristic

#Main Character 
class Tank(Widget):
    def __init__(self,keys, **dinobros):
        super().__init__(**dinobros) #the cannon is composed by the main body and a part able to rotate, they move togheder
        self.keyPressed=keys
        self.IsColliding=False
        self.collision_left=False
        self.collision_right=False
        self.IsActive=True
        self.nondeadly=True
        with self.canvas:
            #dimensions
            sizex = Window.width / 10
            sizey = Window.height / 10
            posx = Window.width / 30
            posy = Window.height / 15
            Color(1, 1, 1, 1)

            
            PushMatrix()  # Prevent everything from rotating
            cannon_base_x = posx + sizex / 2
            cannon_base_y = posy + sizey / 2
            self.cannon_size = ((sizex / 1.35) / 4.5, sizey)
            self.cannon_translation = Translate(cannon_base_x, cannon_base_y)
            self.cannon_rotation = Rotate(origin=(0, self.cannon_size[1] / 4))

            self.cannon = Rectangle(source="./img/Cannons.png", pos=(-self.cannon_size[0] / 2, self.cannon_size[1] / 4), size=self.cannon_size)
            PopMatrix()

            self.proj = Rectangle(source="./img/TankV1.png", pos=(posx, posy), size=(sizex, sizey))

    def movement(self):
            step_size = Window.width / 8 * 0.02  # Velocità di movimento
            rotation_speed = 45 * 0.02  # Velocità di rotazione

            # Movimento del 'player' e aggiornamento della posizione del 'cannon'
            if "a" in self.keyPressed and not self.collision_left:
                new_x = max(self.proj.pos[0] - step_size, 0)  # Non oltrepassare il bordo sinistro
                self.proj.pos = (new_x, self.proj.pos[1])
                self.IsColliding=False
                
            if "d" in self.keyPressed and not self.collision_right:
                max_x = Window.width - self.proj.size[0]
                new_x = min(self.proj.pos[0] + step_size, max_x)  # Non oltrepassare il bordo destro
                self.proj.pos = (new_x, self.proj.pos[1])
                self.IsColliding=False
                

            self.cannon_translation.x = self.proj.pos[0] + self.proj.size[0] / 2
            self.cannon_translation.y = self.proj.pos[1] + self.proj.size[1] / 2

            if "w" in self.keyPressed:
                if self.cannon_rotation.angle + rotation_speed <= 90:  # limite superiore a +90 gradi
                    self.cannon_rotation.angle += rotation_speed
            if "s" in self.keyPressed:
                if self.cannon_rotation.angle - rotation_speed >= -90:  # limite inferiore a -90 gradi
                    self.cannon_rotation.angle -= rotation_speed

#Best Object in the game, the Meteor (Bomb)
class Meteor(Widget):
    def __init__(self,pos,**dinobros):
        super().__init__(**dinobros)
        self.BreakHard=True
        self.IsActive=True
        self.IsColliding=False
        if pos is None: #the meteor functions vary by modality. in the main game pos is the Middle of the Screen , in the extintion Modality is None so the position change for every meteor generated.
            self.meteor_spawn=random.randint(100,Window.width - 200)
        else:
            self.meteor_spawn=pos
        
        with self.canvas:
            PushMatrix()
            self.meteor = Color(1, 1, 1, 1)
            self.meteor_rotation = Rotate(angle=0, origin=(self.meteor_spawn, Window.height +350*wh))
            self.meteor = Rectangle(size=(200*ww, 350*wh), pos=(self.meteor_spawn, Window.height+350*wh), source="./img/meteor.png") #Meteor Charaterstci
            PopMatrix()
        with self.canvas:
            self.proj = Color(0, 0, 0, 0)
            self.proj = Rectangle(size=(200*ww, 200*ww), pos=self.meteor.pos) #Since rotation caused problems with collisions, the Meteor is followed by a non-rotated object wich collisions are calculated.


    def set_check(self, x, y): #proj position
        self.proj.pos = (x, y)

    def boom(self, x, y): #meteor position
        self.meteor.pos = (x, y)

    def set_rotation(self, px, py): #set the rotation of the meteor in a way that will hit a point in the screen
        dx = px + 40*ww - self.meteor_spawn
        dy = py - (Window.height+350*wh)
        angle = math.atan2(dy, dx)
        # print(math.degrees(angle))
        self.meteor_rotation.angle = math.degrees(angle) + 90

    

class Caller(Widget):
    def __init__(self,player, cannon, cannon_rotation,powerbar,**dinobros):
        super().__init__(**dinobros)
        self.player = player
        self.cannon = cannon
        self.cannon_rotation = cannon_rotation 
        self.IsActive= False
        self.meteor_active=False
        self.IsColliding=False
        self.nondeadly=True
        self.powerbar=powerbar
        self.meteor_sound = SoundLoader.load('./music/meteor.mp3')
        self.caller_sound = SoundLoader.load('./music/caller.mp3')
        self.caller_sound.volume = 0.1
        self.impact_sound = SoundLoader.load('./music/impatto.mp3')
        with self.canvas:
            self.proj = Color(1, 1, 1, 1)
            self.proj = Rectangle(size=(80*ww, 80*ww), pos=(3000, 3000), source="./img/meteor_caller.png")  # Caller Object Charateristic (object thrown by tank)

    def set_pos(self, x, y): #caller object position
        self.proj.pos = (x, y)
    
    def activate_caller(self): #Activate the caller, set position
        
            self.caller_velocity = math.sqrt(0.8*ww* self.powerbar.powerbar.size[0] / 2.5)
            activation(self,self.player,self.cannon,self.cannon_rotation,None)
            #Calculate velocity base on cannon rotation
            
    
    def movement(self):
        
            

        
        x = projectile_dynamics(self.start_time,self.proj.pos,velocity_decomposition(self.caller_velocity,self.cannon_rotation.angle),98)[0]
        y = projectile_dynamics(self.start_time,self.proj.pos,velocity_decomposition(self.caller_velocity,self.cannon_rotation.angle),98)[1]
        self.set_pos(x, y)
            # print(self.mc.caller.pos)

            
        if x > Window.width or y < Window.height / 15 or x < 0 or self.IsColliding:
                
            self.IsColliding = False
            self.meteor_active = True
            self.IsActive= False
            self.meteor_sound.play()

#Power Ups Class, not yet implemented in the game
class PowerUps(Widget):
    def __init__(self, **dinobros): 
        super().__init__(**dinobros)
        self.power_selector=random.randint(0,2)
        self.power_icon = None

        with self.canvas:
            if self.power_selector==0:
                self.power_icon=Color(0.0, 0.75, 1.0, 1)
                self.power_icon = Rectangle(size=(50*ww,50*ww),pos=(3000,3000))
            elif self.power_selector==1:        
                self.power_icon = Color(1,0,0,1)
                self.power_icon = Rectangle(size=(50*ww,50*ww),pos=(3000,3000))
            elif self.power_selector==2:           
                self.power_icon= (1,1,1,1)
                self.power_icon = Rectangle(size=(50*ww,50*ww),pos=(3000,3000))
                

    def activation(self,x,y):
        self.power_icon.pos=(x,y)
           
#the power ups are given by hitting meteors in the Extintion modality, their purpuse is to let the user be able to achive greater scores.
#each color will be associated to a different power (not yet implemented)
    


#Flying enemy
class Pterodactyl(Widget):
    def __init__(self, **dinobros):
        super().__init__(**dinobros)

        self.GoRight = True
        self.GoDown = True
        self.IsColliding=False
        self.name="PTERO"

        with self.canvas:
            self.ptero = Color(1, 1, 1, 1)
            self.ptero = Rectangle(size=(300*ww, 300*ww), pos=(100*ww, 1200*wh), source="./img/ptero.png")
        with self.canvas:
            self.obj=Color(0,0,0,0)
            self.obj=Rectangle(size=(300*ww, 300*ww), pos=(100*ww, 1200*wh))

    def fly(self): #Make the enemy move from left to right with sloght up and down movement
        if self.ptero.pos[0] < Window.width - 300*ww and self.GoRight:
            self.ptero.size = (300*ww, 300*ww)
            self.ptero.pos = (self.ptero.pos[0] + 5, self.ptero.pos[1])
            self.obj.pos=self.ptero.pos
        else:
            self.GoRight = False
            self.ptero.size = (-300*ww, 300*ww)
            self.ptero.pos = (self.ptero.pos[0] - 5, self.ptero.pos[1])
            self.obj.pos=(self.ptero.pos[0]-300,self.ptero.pos[1])
            if self.ptero.pos[0] < 300*ww:
                self.GoRight = True

        if self.ptero.pos[1] > 1100*wh and self.GoDown:
            self.ptero.pos = (self.ptero.pos[0], self.ptero.pos[1] - 1)
        else:
            self.GoDown = False
            self.ptero.pos = (self.ptero.pos[0], self.ptero.pos[1] + 1)
            if self.ptero.pos[1] > 1250*wh:
                self.GoDown = True
        

#Rock Class. (Perpetio and Rock Share the same class, only the image and collision detection is changed")
class Rock(Widget):
    def __init__(self, **dinobros):
        super().__init__(**dinobros)
        self.IsColliding=False
        self.hard=True
        with self.canvas:
            self.obj = Color(1, 1, 1, 1)
            self.obj = Rectangle(size=(450*ww, 550*wh), pos=(Window.width / 2 - 100*ww, -50*wh), source="./img/roccia_grossa.png")


#Final Boss Class
class Boss(Widget):
    def __init__(self, **dinobros):
        super().__init__(**dinobros)
        self.target_hit=False
        self.boss_battle=False
        
        #The boss is defeatable by hitting those weak points
        self.punti_deboli=[(Window.width - 800*ww, 550*wh),(Window.width - 820*ww, 920*wh),(Window.width - 820*ww, 320*wh),(Window.width - 580*ww, 730*wh),(Window.width - 360*ww, 560*wh), (Window.width - 850*ww, 630*wh),(Window.width - 200*ww, 480*wh),(Window.width - 820*ww, 120*wh) ]

        #LifeBar
        with self.canvas:
            self.boss_canvas = Rectangle(size=(-1024, 962), pos=(Window.width, 3000), source="./img/bossosauro.png")
            self.lifebar= Color(1,0,0,1)
            self.lifebar = Rectangle (size=(550*ww,30*wh),pos=(Window.width - 812*ww, 3100*wh))

        #Telekinetic Aurea (not implemented)
        with self.canvas:
            self.aura= Color(0.5,0,0.5,0.6)
            self.aura= Ellipse(size=(80,80),pos=(3000,3000))

            
        #Personalized Hitbox
        with self.canvas:
            self.color = Color(0, 0, 0, 0)
            self.hitbox1 = Ellipse(size=(280*ww, 280*wh), pos=(Window.width - 950*ww, 700*wh))
            self.hitbox2 = Ellipse(size=(430*ww, 430*wh), pos=(Window.width - 800*ww, 350*wh))
            self.hitbox3 = Rectangle(size=(180*ww, 330*wh), pos=(Window.width - 800*ww, 100*wh))
            self.hitbox4 = Rectangle(size=(480*ww, 130*wh), pos=(Window.width - 550*ww, 400*wh))
        
        
        with self.canvas:
            self.obj= Color(0.8,0.5,1,1)
            self.obj= Ellipse(size=(100,100),pos=(0,9000), source="./img/target.png")
            self.IsColliding=False
        
    def target_pos(self): #Set the position of the weak points
        self.obj.pos=random.choice(self.punti_deboli)
        self.lifebar.size = (self.lifebar.size[0]-50*ww,30)
    

    #Boss Laser (not implemented), the mechanism will be similar to the meteor one.
    def laser(self, px, py):
        dx = px - 800
        dy = py - 600
        angle = math.atan2(dy, dx)
        # print(math.degrees(angle))
        

#Main Game (oldest part of the code)
class GameScreen(Screen):
    def on_enter(self):
        self.main_active = True
        if self.background_music:
            self.background_music.play()
        Clock.schedule_interval(self.update, 1 / 60)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        
        # Initialize all widgets and add them to the screen
        self.setup_widgets()
    
    def on_leave(self):
        self.cleanup()

    def cleanup(self):
        self.main_active = False
        Clock.unschedule(self.update)
        if self.background_music:
            self.background_music.stop()
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
           

        # Remove all widgets
        self.clear_widgets()

        # Reset variables
        self.laser.IsActive = False
        self.bullet.IsActive = False
        self.IsActive= False
        self.meteor_active = False
        self.enemy.IsColliding = False
        self.pt.IsColliding = False
        self.boss.boss_battle = False
        self.point_counter = 1

    def __init__(self, **dinobros):  # initialization
        super().__init__(**dinobros)

        self.main_active = False
        self.is_colliding = False
        self.collision_left = False
        self.collision_right = False
        self.caller_colliding = False
        self.meteor_active = False
        self.meteor_colliding = False
        
        
        self.telecinesi = False
        self.ptero_dead = False
        
        

        self.point_counter = 1

        self.background_music = SoundLoader.load('./music/Survive the dinos.mp3')  # music
        if self.background_music:
            self.background_music.loop = True  # Loop the music

        self.keyPressed = set()

    

    def setup_widgets(self):
        self.objects=[]
        self.projectiles=[]
        with self.canvas.before:
            self.background = Rectangle(source="./img/background1.png", pos=(0, 0), size=(Window.width, Window.height))
        
        self.back_btn = Button(text="Back to Menu", size_hint=(None, None), size=(250 * ww, 90 * wh),
                               pos_hint={'center_x': 0.05, 'center_y': 0.05}, background_color=(194 / 255, 178 / 255, 128 / 255, 1))
        self.back_btn.bind(on_release=lambda x: App.get_running_app().switch_screen('menu'))
        self.add_widget(self.back_btn)

        self.powerbar = PowerBar()
        self.add_widget(self.powerbar)

        self.rock = Rock()
        self.add_widget(self.rock)
        self.objects.append(self.rock)

        self.pt = Pterodactyl()
        self.add_widget(self.pt)
        self.objects.append(self.pt)

        self.tank = Tank(self.keyPressed)
        self.add_widget(self.tank)
        self.projectiles.append(self.tank)

        self.laser = Laser(self.tank.proj, self.tank.cannon, self.tank.cannon_rotation)
        self.add_widget(self.laser)
        self.projectiles.append(self.laser)
        

        self.mirror1 = Mirror()
        self.add_widget(self.mirror1)
        self.objects.append(self.mirror1)

        self.enemy = Velociraptor()
        self.add_widget(self.enemy)
        self.objects.append(self.enemy)

        self.bullet = Bullet(self.tank.proj, self.tank.cannon, self.tank.cannon_rotation,self.powerbar)
        self.add_widget(self.bullet)  # if u move that up the Tank will became RGB (if not outdated)
        self.projectiles.append(self.bullet)

        self.mc = Meteor(Window.width / 2)  # initialize the meteor spawn in the middle of the screen (design choice)
        self.add_widget(self.mc)
        self.projectiles.append(self.mc)

        self.caller=Caller(self.tank.proj, self.tank.cannon, self.tank.cannon_rotation,self.powerbar)
        self.add_widget(self.caller)
        self.projectiles.append(self.caller)

        self.points = Button(text=str(self.point_counter), font_size=80 * ww, size=(500 * ww, 500 * ww), background_color=(0, 0, 0, 0), bold=True, outline_color=(1, 0, 0, 1), pos_hint={'center_x': 0.1, 'center_y': 0.9})
        self.add_widget(self.points)

        self.boss = Boss()
        self.add_widget(self.boss)
        self.objects.append(self.boss)
        
        

        Clock.schedule_interval(self.laser.update_color, 0)

        
        self.enemy.enemy=self.enemy.obj
        self.player = self.tank.proj
        self.cannon = self.tank.cannon
        self.mc.caller=self.caller.proj
        self.cannon_size = self.tank.cannon_size
        self.cannon_translation = self.cannon_translation = self.tank.cannon_translation
        self.cannon_rotation = self.tank.cannon_rotation
        self.meteor_velocity_x = -25 * ww * math.cos(math.radians((self.mc.meteor_rotation.angle) + 90))
        self.meteor_velocity_y = -25 * ww * math.sin(math.radians((self.mc.meteor_rotation.angle) + 90))
        self.boss.pos = (1000 * ww, 100 * wh)

        self.dead_time = 0
        self.dead_time_ptero = 0

    def point_up(self):
        self.point_counter += 1
        self.points.text = str(self.point_counter)



    def _on_keyboard_closed(self):
        if self.main_active: #outdated 
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers): #hotkeys
        if self.main_active:
            self.keyPressed.add(text)
            if keycode[1] == 'spacebar' and not self.laser.IsActive:
                self.bullet.activate_bullet()
                self.telecinesi=False
            if keycode[1] == "l" and not self.bullet.IsActive:
                self.laser.activate_laser()

            if keycode[1] == "m" and not self.caller.IsActive and not self.meteor_active:
                self.caller.activate_caller()
                self.caller.caller_sound.play()

            #if keycode[1] == "c":
                #if self.mirror1.vertical:
                    #self.mirror1.setHorizontal()
                #else:
                    #self.mirror1.setVertical()

           # if keycode[1] == "z": #debugging
                #self.boss.target_pos()

            """if keycode[1] == "b":
                

                self.boss.boss_battle= not self.boss.boss_battle  #Boss battle modality
                if self.boss.boss_battle:
                    self.boss.target_pos()
                    self.boss.boss_canvas.pos=(Window.width,100)
                    self.boss.lifebar.size,self.boss.lifebar.pos = (500*ww,30*wh), (Window.width - 812*ww , 1100*wh)
                    self.enemy.IsColliding=True
                    self.pt.IsColliding=True
                    self.ptero_dead=True
                    self.background_music.stop()
                    self.background_music=SoundLoader.load('./music/CYRANNUS ROARING.mp3')
                    self.background_music.play()
                    self.background_music.loop = True 
                else:
                    self.boss.target.pos=(0,9000)
                    self.boss.boss_canvas.pos=(Window.width,3000)
                    self.boss.lifebar.pos = (3300,5000)
                    self.background_music.stop()
                    self.background_music=SoundLoader.load('./music/Survive the dinos.mp3')
                    self.background_music.play()
                    self.background_music.loop = True 
                #print(self.boss.boss_battle)"""
        

    def _on_key_up(self, keyboard, keycode):
        if self.main_active:
            text = keycode[1]
            if text in self.keyPressed:
                self.keyPressed.remove(text)




    def update(self, dt): 

        collision_manager(self.projectiles,self.objects) #function that manager all the collisions

        if self.point_counter%9==0:
            self.boss.boss_battle=True
            self.boss.target_pos()
            self.point_up()
            self.boss.boss_canvas.pos=(Window.width,100*ww)
            self.boss.lifebar.size,self.boss.lifebar.pos = (500*ww,30*wh), (Window.width - 812*ww , 1100*wh)
            self.enemy.IsColliding=True
            self.pt.IsColliding=True
            self.ptero_dead=True
            self.background_music.stop()
            self.background_music=SoundLoader.load('./music/CYRANNUS ROARING.mp3')
            self.background_music.play()
            self.background_music.loop = True 
            self.objects.append(self.boss.hitbox1)
            self.objects.append(self.boss.hitbox2)
            self.objects.append(self.boss.hitbox3)
            self.objects.append(self.boss.hitbox4)

        if self.boss.lifebar.size[0]<=0 and self.boss.boss_battle: #check if the boss battle state is active and if the boss is defeated
            #App.get_running_app().switch_screen('menu')
            self.point_counter+=10
            self.point_up()
            self.boss.boss_battle=False #return to default settings
            self.boss.boss_canvas.pos=(Window.width,3000)
            self.boss.lifebar.pos = (3300,10000)
            self.background_music.stop()
            self.background_music=SoundLoader.load('./music/Survive the dinos.mp3')
            self.background_music.play()
            self.background_music.loop = True 
            self.boss.obj.pos=(0,9000)
            self.objects.remove(self.boss.hitbox1)
            self.objects.remove(self.boss.hitbox2)
            self.objects.remove(self.boss.hitbox3)
            self.objects.remove(self.boss.hitbox4)
        
        if self.rock.IsColliding:
            self.rock.obj.pos=(-10000,10000)
            
            
        self.mirror1.mirror=self.mirror1.obj
        self.bullet.ellipse=self.bullet.proj

        #The mirror will be carried by the pterodactyil
        if self.pt.GoRight and not self.ptero_dead:
            self.mirror1.posMirror(self.pt.ptero.pos[0], self.pt.ptero.pos[1] - 250)
        elif not self.pt.GoRight and not self.ptero_dead:
            if self.mirror1.vertical:
                self.mirror1.posMirror(self.pt.ptero.pos[0] - 30, self.pt.ptero.pos[1] - 250)

            if not self.mirror1.vertical:
                self.mirror1.posMirror(self.pt.ptero.pos[0] - 300, self.pt.ptero.pos[1] - 250)

        if self.ptero_dead and self.mirror1.mirror.pos[1] > 100:
            self.mirror1.posMirror(self.mirror1.mirror.pos[0], self.mirror1.mirror.pos[1] - 30)
            if self.mirror1.mirror.pos[1] <120:
                self.mirror1.posMirror(self.mirror1.mirror.pos[0], -2000)

        #respawn mechanig for debugging purpose 
        if self.enemy.IsColliding:
            self.enemy.IsColliding = False
            self.point_up()
            self.dead_time = Clock.get_boottime()
            if not self.boss.boss_battle:

                
                self.enemy.enemy_music.play()
            self.enemy.enemy.pos = (-3000, -3000)
        if (Clock.get_boottime() - self.dead_time) > 5 and not self.boss.boss_battle:
            self.enemy.enemy.pos = (Window.width / 1.5, Window.height / 18)

        if self.pt.IsColliding:
            self.ptero_dead=True
            self.pt.IsColliding = False
            self.point_up()
            self.dead_time_ptero = Clock.get_boottime()
            if not self.boss.boss_battle:
                
                self.enemy.enemy_music.play()
            self.pt.ptero.pos = (self.pt.ptero.pos[0], -5000)

        if (Clock.get_boottime() - self.dead_time_ptero) > 5 and self.ptero_dead and not self.boss.boss_battle:
            self.pt.ptero.pos = (self.pt.ptero.pos[0], 1200)
            self.ptero_dead = False


        if self.boss.boss_battle:
            if self.boss.IsColliding:
                self.boss.IsColliding=False
                self.boss.target_pos()

        if not self.tank.IsColliding:
            self.tank.collision_left = False
            self.tank.collision_right = False

        if self.tank.IsColliding and (self.player.pos[0] < self.enemy.enemy.pos[0]):
            self.tank.collision_right = True
            

        if self.tank.IsColliding and (self.player.pos[0] > self.enemy.enemy.pos[0]):
            self.tank.collision_left = True

        

        #MOVEMENTS

        # muzzle velocity (powerbar dimension)
        if "p" in self.keyPressed and not self.bullet.IsActive:
            if self.powerbar.powerbar.size[0] <= 720*ww:
                self.powerbar.powerbar.size = (self.powerbar.powerbar.size[0] + 5*ww, self.powerbar.powerbar.size[1])

        if "o" in self.keyPressed and not self.bullet.IsActive:
            if self.powerbar.powerbar.size[0] >= 100*ww:
                self.powerbar.powerbar.size = (self.powerbar.powerbar.size[0] - 5*ww, self.powerbar.powerbar.size[1])

        
        self.tank.movement() #FIXED 24-07-24,moved hotkeys into class

        if self.bullet.IsActive: #Fire Bullet when active
            self.bullet.movement() #FIXED 24-07-24 , moved logic into class #classe generale movimento

        # Fire Laser Movement when active
        if self.laser.IsActive:
            self.laser.movement() #FIXED 24-07-24 , moved logic into class

        #same things as explained up
        if self.caller.IsActive:
            self.mc.set_rotation(self.mc.caller.pos[0], self.mc.caller.pos[1])
            self.caller.movement()

        #when meteor active, let proj follow meteor set it back after
        if self.caller.meteor_active:
            self.proj_velocity_x = 25*ww * math.cos(math.radians((self.mc.meteor_rotation.angle) - 90))
            self.proj_velocity_y = 25*ww * math.sin(math.radians((self.mc.meteor_rotation.angle) - 90))
            x = self.mc.meteor.pos[0] + self.meteor_velocity_x
            y = self.mc.meteor.pos[1] + self.meteor_velocity_y
            self.mc.boom(x, y)
            self.mc.set_check(self.mc.proj.pos[0] + self.proj_velocity_x, self.mc.proj.pos[1] + self.proj_velocity_y)

            if self.mc.meteor.pos[1] < -150:
                self.caller.set_pos(6000,10000) #Solution to Meteor Caller Object Problem, the object was still colliding with the Rock.
                self.caller_colliding=False
                self.caller.meteor_active = False
                self.meteor_colliding = False
                self.caller.impact_sound.play()
                self.caller.meteor_sound.stop()

                self.mc.meteor.pos = (self.mc.meteor_spawn, Window.height + 350)
                self.mc.proj.pos = self.mc.meteor.pos

        self.pt.fly() #make it fly

#there is only one object for each type, the obkect will not be deleted, but displaced and the re-positioned every time


#---------------------------------------------------------------------------------------------------------------------------

#SECONDARY MODALITY, EXTINTION

 # Maximum number of active meteors
MAX_METEORS = 4
UPDATE_INTERVAL=1/30



class Estinzione(Screen):
    def apocalypse_thread(self):  #set the threading to not make the game explode
        while self.Ext_mode and not self._stop_event.is_set():
            if len(self.meteors) < MAX_METEORS:
                self.schedule_apocalypse()
            time.sleep(self.meteor_interval)
            #print("thread")

    def schedule_apocalypse(self):
        Clock.schedule_once(self.Apocalypse, self.meteor_interval) #launch a meteor

    def on_enter(self): 
        if self.background_music:
            self.background_music.play()
        self.point_counter = 0
        self.meteor_interval = 2
        self.meteor_speed = 15 * ww
        self.Ext_mode = True
       
    
        self._stop_event = threading.Event()  # Initialize the stop event

        # Check if the thread is already running
        if not hasattr(self, '_thread') or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.apocalypse_thread)
            self._thread.daemon = True  # Set thread as daemon to avoid blocking exit
            self._thread.start()
        else:
            print("Thread alrdy running")

        self.update_event = Clock.schedule_interval(self.update, 0)
        self.survival_points_event = Clock.schedule_interval(self.survival_points, 3)

        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)

    def on_leave(self): #stop events on exit
        self.Ext_mode = False
        Clock.unschedule(self.update_event)
        Clock.unschedule(self.survival_points_event)

        self._stop_event.set()  # Signal the thread to stop

        if hasattr(self, '_thread') and self._thread.is_alive():
            self._thread.join()  # Wait for the thread to finish

        self.cleanup()

    def cleanup(self): #set to initial condition (outdated)
        self.laser.IsActive = False
        self.laser.IsColliding = False
        self.is_colliding = False
        self.meteor_speed = 15 * ww
        self.meteor_interval = 2
        self.time_elapsed = 0
        self.meteors = []
        self.meteors_to_remove = []
        self.player.pos = (Window.width / 30, Window.height / 15)
        self.cannon_rotation.angle = 0

        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard = None

        for meteor in self.meteors:
            self.remove_widget(meteor)
        self.meteors.clear()
        self.background_music.stop()

    def __init__(self, **dinobros):
        super().__init__(**dinobros)

        self.point_counter = 0
        #poins Counter
        self.points = Button(text=str(self.point_counter), font_size=80, size=(500, 500), background_color=(0, 0, 0, 0), bold=True, outline_color=(1, 0, 0, 1), pos_hint={'center_x': 0.1, 'center_y': 0.9})
        self.add_widget(self.points)

        
        self.is_colliding = False
        self.Ext_mode = False
        self.meteor_speed = 15 * ww

        self.meteors = []
        self.meteors_to_remove = []  # List to mark meteors for removal
        self.meteor_interval = 2  # Initial interval in seconds
        self.time_elapsed = 0
        self.background_music = SoundLoader.load('./music/End of Days.mp3')
        self.background_music.loop = True
        self.keyPressed = set()
        
        self.tank = Tank(self.keyPressed)
        self.add_widget(self.tank)
        self.laser = Laser(self.tank.proj,self.tank.cannon,self.tank.cannon_rotation)
        self.add_widget(self.laser)
        self.projectiles.append(self.laser)


        

        with self.canvas.before:
            self.background = Rectangle(source="./img/estinzione_background.png", pos=(0, 0), size=(Window.width, Window.height))

        self.player = self.tank.proj
        self.cannon = self.tank.cannon
        self.cannon_size = self.tank.cannon_size
        self.cannon_translation = self.tank.cannon_translation
        self.cannon_rotation = self.tank.cannon_rotation

    def point_up(self): #addo one point
        self.point_counter += 1
        self.points.text = str(self.point_counter)

    def get_point_counter(self):
        return self.point_counter

    def powerupss(self): #make the powerups fall (not implemented yet) an let the player pick them up
        self.on_ground = False
        power = PowerUps()
        self.add_widget(power)
        power.activation(self.laser.laser_translation.x, self.laser.laser_translation.y)
        self.time = Clock.get_boottime()

        def power_fall(power, dt):
            if power.power_icon.pos[1] > 150:
                power.activation(power.power_icon.pos[0], power.power_icon.pos[1] - 10)
            else:
                if (Clock.get_boottime() - self.time) > 3:
                    self.remove_widget(power)
                Clock.unschedule(power_fall)

            if collides((power.power_icon.pos, power.power_icon.size), (self.tank.player.pos, self.tank.player.size)):
                self.remove_widget(power)

        Clock.schedule_interval(lambda dt, power=power: power_fall(power, dt), 1 / 60)


    #Regulate the falling of the metors
    def Apocalypse(self, dt):
        if self.Ext_mode and len(self.meteors) < MAX_METEORS:
            target = random.randint(100, Window.width - 100) #select the target (point where the meteor will fall)
            meteor = Meteor(None) #the meteor will be initialized to a random x position, FIXED 24-07-24
            collision_manager(self.projectiles,meteor)
            self.add_widget(meteor)
            self.meteors.append(meteor)

            self.meteor_velocity_x = -self.meteor_speed * math.cos(math.radians((meteor.meteor_rotation.angle) + 90))
            self.meteor_velocity_y = -self.meteor_speed * math.sin(math.radians((meteor.meteor_rotation.angle) + 90))

            self.meteor_interval = max(0.4, self.meteor_interval * 0.97) #increase the frequency and speed of meteors each iteration to make the game harder)
            self.meteor_speed = min(30 * ww, self.meteor_speed + 0.1)

            def update_meteor(meteor, dt): #meteor movement and collisions
                if not self.Ext_mode:
                    return

                meteor.set_rotation(target, 100 * wh)
                x = meteor.meteor.pos[0] + self.meteor_velocity_x
                y = meteor.meteor.pos[1] + self.meteor_velocity_y
                meteor.boom(x, y)
                proj_velocity_x = self.meteor_speed * math.cos(math.radians((meteor.meteor_rotation.angle) - 90))
                proj_velocity_y = self.meteor_speed * math.sin(math.radians((meteor.meteor_rotation.angle) - 90))
                meteor.set_check(meteor.proj.pos[0] + proj_velocity_x, meteor.proj.pos[1] + proj_velocity_y)

                if y < -400 * wh:
                    Clock.unschedule(update_meteor)
                    self.meteors_to_remove.append(meteor)
                if self.laser.IsActive:
                    if collides(((self.laser.laser_translation.x, self.laser.laser_translation.y), (0, 50)), (meteor.proj.pos, meteor.proj.size)):
                        meteor.proj.pos = (0, -3000)
                        Clock.unschedule(update_meteor)
                        self.meteors_to_remove.append(meteor)
                        #self.powerupss()
                        self.point_up()
                        self.laser.IsColliding = True

                if collides((meteor.proj.pos, meteor.proj.size), (self.tank.proj.pos, self.tank.proj.size)):
                    Clock.unschedule(update_meteor)
                    self.meteors_to_remove.append(meteor)
                    username = App.get_running_app().login_manager.get_username()
                    leaderboard = read_leaderboard(file_path)
                    image_path = leaderboard[username]['image_path']
                    update_leaderboard(file_path, username, self.point_counter, image_path)
                    self.background_music.stop()
                    App.get_running_app().switch_screen('leaderboard')
                    

            Clock.schedule_interval(lambda dt, meteor=meteor: update_meteor(meteor, dt), 1 / 60)

    
    def _on_keyboard_closed(self):
        if self.Ext_mode:
            if self._keyboard:
                self._keyboard.unbind(on_key_down=self._on_key_down)
                self._keyboard.unbind(on_key_up=self._on_key_up)
                self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if self.Ext_mode:
            self.keyPressed.add(text)

    def _on_key_up(self, keyboard, keycode):
        if self.Ext_mode:
            text = keycode[1]
            if text in self.keyPressed:
                self.keyPressed.remove(text)
            if " " in self.keyPressed:
                self.keyPressed.remove(" ")

    def survival_points(self, dt):
        self.point_up()

    def update(self, dt):  #update functions, regulate laser, tank
        if self.Ext_mode:
            collision_manager(self.projectiles,meteor)
            if self.laser.IsActive:
                self.laser.movement() #FIXED 24-07-24

            self.tank.movement() #CHANGED , tank movement
            if " " in self.keyPressed and not self.laser.IsActive:
                self.laser.activate_laser()   #FIXED 24-07-24 , moved logic into class

            # Remove meteors marked for removal
            for meteor in self.meteors_to_remove:
                if meteor in self.meteors:
                    self.remove_widget(meteor)
                    self.meteors.remove(meteor)
            self.meteors_to_remove.clear()





#App class
class MyApp(App):
    def build(self):
        self.volume=1
        self.login_manager = LoginManager()
        self.sm = ScreenManager(transition=FadeTransition(duration=0.1))
        self.main_menu = MainMenu(self.login_manager, name='menu')
        self.leaderboard_menu = Top3Screen(name='leaderboard')
        self.game = GameScreen(name='game')
        self.help_screen = HelpScreen(name='help')

        if not self.login_manager.is_logged_in(): #check if an user is logged in if it is display login screen , if not main menu
            self.sm.add_widget(LoginScreen(self.login_manager, name='login'))
            self.sm.add_widget(self.main_menu)
        else:
            self.sm.add_widget(self.main_menu)
            self.sm.add_widget(LoginScreen(self.login_manager, name='login'))

        if self.login_manager.is_logged_in():
            self.sm.current = 'menu'
        else:
            self.sm.current = 'login'

        self.main_menu.background_music.play()
        return self.sm

    def switch_screen(self, screen_name): #Switch Screen Function, create the screen 
        if screen_name not in self.sm.screen_names:
            if screen_name == 'game':
                self.sm.add_widget(self.game)
            elif screen_name == 'menu':
                self.sm.add_widget(self.main_menu)
            elif screen_name == "login":
                self.sm.add_widget(LoginScreen(self.login_manager, name='login'))
            elif screen_name == 'est':
                self.extintion_menu = Estinzione(name='est')
                self.sm.add_widget(self.extintion_menu)
                self.extintion_menu.background_music.volume = self.volume
            elif screen_name == 'option':
                self.sm.add_widget(OptionMenu(self.login_manager, name='option'))
            elif screen_name == 'modality':
                self.sm.add_widget(ModalityMenu(name='modality'))
            elif screen_name == 'leaderboard':
                self.sm.add_widget(self.leaderboard_menu)
            elif screen_name == 'help':
                self.sm.add_widget(self.help_screen)

        if screen_name in ['game', 'est', 'leaderboard']: #stop the main theme when in one of those screen
            self.main_menu.background_music.stop()
        else:
            if not self.main_menu.background_music.state == 'play':
                self.main_menu.background_music.play()

        self.sm.current = screen_name

        # Remove all other screens except the current one
        for screen in self.sm.screens[:]:
            if screen.name != screen_name:
                self.sm.remove_widget(screen)
                #print("removed",screen)

    def set_volume(self, volume): #set the music volumes (data based from the slider in the option menu)
        self.main_menu.background_music.volume = volume
        self.volume=volume
        if hasattr(self, 'leaderboard_menu'):
            self.leaderboard_menu.background_music.volume = volume
        if hasattr(self, 'game'):
            self.game.background_music.volume = volume



if __name__ == "__main__":
    app = MyApp()
    app.run() 