from src.library.essentials import *
from src.template.BaseState import BaseState
from src.entities.Wind import Wind
from src.states.Menu_TitleState import Menu_TitleState
import tween

class MenuState(BaseState):
    def __init__(self, parent, stack):
        BaseState.__init__(self, parent, stack)

        self.substate_stack = []

        self.ready = False
        self.load_assets()
        self.ready = True

        self.finished_boot_up = False
        
        utils.music_load(music_channel=self.parent.music_channel, name='menu_intro.ogg')
        utils.music_queue(music_channel=self.parent.music_channel, name='menu_loop.ogg', loops=-1)
        self.parent.music_channel.play()

        self.tween_list = []
        if not self.finished_boot_up:
            self.bootup_tween_chain(skip=constants.skip_bootup)
        else:
            self.bootup_tween_chain(skip=True)


    #Main methods

    def load_assets(self):
        # Load white overlay
        self.overlay = pygame.Surface(size=(self.parent.canvas_width, self.parent.canvas_height), flags=pygame.SRCALPHA)
        self.overlay_props = {'alpha': 255}
        self.overlay.fill(color=(*colors.white, self.overlay_props['alpha']))
        
        # Load intro assets
        self.logo = utils.load_image(dir=dir.graphics, name='namsom_logo.png', mode='colorkey')
        self.logo = pygame.transform.scale_by(surface=self.logo, factor=7)
        self.surface_logo = pygame.Surface(size=(self.logo.get_width(), self.logo.get_height()+50), flags=pygame.SRCALPHA)
        self.surface_logo_props = {'y_offset': 0, 'alpha': 0, 'scale': 0.7}
        utils.blit(dest=self.surface_logo, source=self.logo)
        text_props = {'font': fonts.retro_arcade, 'size': 'small'}
        text_deco_distance = utils.get_font_deco_distance(text_props['font'], text_props['size'])
        text = utils.get_text(text='PRESENTS', font=text_props['font'], size=text_props['size'], color=colors.mono_100)
        text = utils.effect_long_shadow(surface=text,
                                        direction='bottom',
                                        distance=text_deco_distance,
                                        color=utils.color_lighten(color=colors.mono_100,factor=0.75))
        text = utils.effect_outline(surface=text, distance=text_deco_distance, color=colors.white)
        utils.blit(dest=self.surface_logo, 
                   source=text,
                   pos=(self.surface_logo.get_width()/2, self.surface_logo.get_height()/2 + 30),
                   pos_anchor='midtop')

        # Load menu background assets
        self.sky = utils.load_image(dir=dir.menu_bg, name='1_sky.png', mode='colorkey')
        self.parallax_list = [
            {
                'image': utils.load_image(dir=dir.menu_bg, name='2_cloud_1.png', mode='colorkey'),
                'x_offset': 0,
                'x_step': 0.5,
            },
            {
                'image': utils.load_image(dir=dir.menu_bg, name='3_cloud_2.png', mode='colorkey'),
                'x_offset': 0,
                'x_step': 2.5,
            },
            {
                'image': utils.load_image(dir=dir.menu_bg, name='4_cloud_3.png', mode='colorkey'),
                'x_offset': 0,
                'x_step': 7,
            },
        ]
        self.landscape_list = [
            {
                'image': utils.load_image(dir=dir.menu_bg, name='5_landscape_1.png', mode='colorkey'),
                'y_offset': 200,
            },
            {
                'image': utils.load_image(dir=dir.menu_bg, name='6_landscape_2.png', mode='colorkey'),
                'y_offset': 400,
            },
            {
                'image': utils.load_image(dir=dir.menu_bg, name='7_landscape_3.png', mode='colorkey'),
                'y_offset': 1000,
            },
        ]
        self.noise_overlay = utils.load_image(dir=dir.menu_bg, name='8_noise.png', mode='alpha')

        # Load wind
        self.wind_entities_list = []
        self.winds_props = {'y_offset': 1000}
        self.wind_spawn_rate_per_second = 0.85
        self.wind_sprites = utils.load_sprite_sheet(sprite_sheet=spritesheets.wind, mode='alpha')
        for wind_sprite in self.wind_sprites:
            self.wind_sprites[wind_sprite] = pygame.transform.scale_by(self.wind_sprites[wind_sprite], (4, 2))

        # Initiate menu background surface
        self.menu_bg = pygame.Surface(size=(self.parent.canvas_width, self.parent.canvas_height))
        self.menu_bg_pixel_size = 2

        # Load game logo
        self.game_logo = utils.load_image(dir=dir.graphics, name='game_logo.png', mode='colorkey')
        self.game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=4)
        self.game_logo_props = {'scale': 0.5, 'alpha': 0}

        # Load menu options
        self.title_options_list = [
            {
                'text': 'Play',
                'color': colors.white,
            },
            {
                'text': 'Records',
                'color': colors.white,
            },
            {
                'text': 'Settings',
                'color': colors.white,
            },
            {
                'text': 'Quit',
                'color': colors.white,
            },
        ]
        self.title_options_surfaces = []
        for i, option in enumerate(self.title_options_list):
            text_props = {'font': fonts.lf2, 'size': 'medium'}
            text_deco_distance = utils.get_font_deco_distance(font=text_props['font'], size=text_props['size'])
            text = utils.get_text(text=option['text'], font=text_props['font'], size=text_props['size'], color=option['color'])
            text = utils.effect_long_shadow(surface=text,
                                            direction='bottom',
                                            distance=text_deco_distance,
                                            color=utils.color_darken(color=option['color'], factor=0.5))
            text = utils.effect_outline(surface=text, distance=text_deco_distance, color=colors.mono_50)
            rect = text.get_rect(center=(self.parent.canvas_width / 2, 340 + i * 80))
            self.title_options_surfaces.append({
                'surface': text,
                'rect': rect,
                'scale': 0.5,
                'alpha': 0,
            })


    def update(self, dt, events):
        if self.ready:

            print('substate_stack:', self.substate_stack)

            # Update substates
            if self.substate_stack:
                self.substate_stack[-1].update(dt=dt, events=events)

            # Update tweens
            tween.update(passed_time=dt)

            # Update parallax
            for layer in self.parallax_list:
                layer['x_offset'] -= layer['x_step']*self.menu_bg_pixel_size*dt
                if abs(layer['x_offset']) > layer['image'].get_width():
                    layer['x_offset'] = 0

            # Update winds
            for wind in self.wind_entities_list:
                wind.update_y_offset(y_offset=self.winds_props['y_offset'])
                if wind.active:
                    wind.update(dt=dt, events=[])
                else:
                    self.wind_entities_list.remove(wind)

            spawn_rate = self.wind_spawn_rate_per_second * dt
            spawns = int(spawn_rate)
            spawn_chance = spawn_rate - spawns
            for _ in range(spawns):
                self.wind_entities_list.append(Wind(surface=self.menu_bg, sprites=self.wind_sprites))

            if random.random() <= spawn_chance:
                self.wind_entities_list.append(Wind(surface=self.menu_bg, sprites=self.wind_sprites))


    def render(self, canvas):
        if self.ready:

            # Build background

            ## Render sky to menu_bg
            utils.blit(dest=self.menu_bg, source=self.sky)

            ## Render parallax to menu_bg
            for layer in self.parallax_list:
                num_duplicates = math.ceil(self.parent.canvas_width/layer['image'].get_width()) + 1
                for i in range(num_duplicates):
                    utils.blit(dest=self.menu_bg, source=layer['image'], pos=(layer['image'].get_width()*i + layer['x_offset'], 0))

            ## Render landscape to menu_bg
            for layer in self.landscape_list:
                utils.blit(dest=self.menu_bg, source=layer['image'], pos=(0, layer['y_offset']))

            ## Render winds to menu_bg
            for wind in self.wind_entities_list:
                wind.render()
            utils.blit(dest=self.menu_bg, source=self.noise_overlay)

            ## Render final menu_bg to canvas
            utils.blit(dest=canvas, source=utils.effect_pixelate(surface=self.menu_bg, pixel_size=self.menu_bg_pixel_size))

            # Build intro

            ## Render overlay
            if hasattr(self, 'overlay'):
                processed_overlay = self.overlay.copy()
                processed_overlay.set_alpha(self.overlay_props['alpha'])
                utils.blit(dest=canvas, source=processed_overlay)

            ## Render logo
            if hasattr(self, 'surface_logo'):
                processed_surface_logo = pygame.transform.scale_by(surface=self.surface_logo, factor=self.surface_logo_props['scale'])
                processed_surface_logo.set_alpha(self.surface_logo_props['alpha'])
                utils.blit(dest=canvas,
                        source=processed_surface_logo,
                        pos=(self.parent.canvas_width/2, self.parent.canvas_height/2 - 20 + self.surface_logo_props['y_offset']),
                        pos_anchor='center')
                
            # Render substates

            if not self.substate_stack:
                ## Render game logo
                processed_game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=self.game_logo_props['scale'])
                processed_game_logo.set_alpha(self.game_logo_props['alpha'])
                utils.blit(dest=canvas, source=processed_game_logo, pos=(self.parent.canvas_width/2, 150), pos_anchor='center')

                ## Render menu options
                for i, option in enumerate(self.title_options_surfaces):
                    processed_option = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
                    processed_option.set_alpha(option['alpha'])
                    utils.blit(dest=canvas, source=processed_option, pos=option['rect'].center, pos_anchor='center')

            else:
                self.substate_stack[-1].render(canvas=canvas)
                

    #Class methods
  
    def bootup_tween_chain(self, skip=False):
        if not skip:
            delay = 0
            self.tween_list.append(tween.to(container=self.surface_logo_props,
                                            key='alpha',
                                            end_value=255,
                                            time=2,
                                            ease_type=tweencurves.easeOutCubic,
                                            delay=delay))
            self.tween_list.append(tween.to(container=self.surface_logo_props,
                                            key='scale',
                                            end_value=1,
                                            time=3,
                                            ease_type=tweencurves.easeOutCubic,
                                            delay=delay))

            delay = 1.75
            self.tween_list.append(tween.to(container=self.overlay_props,
                                            key='alpha',
                                            end_value=0,
                                            time=2,
                                            ease_type=tweencurves.easeOutQuad,
                                            delay=delay))
            for layer in self.landscape_list:
                self.tween_list.append(tween.to(container=layer,
                                                key='y_offset',
                                                end_value=0,
                                                time=3.25,
                                                ease_type=tweencurves.easeOutQuint,
                                                delay=delay))
                
            self.tween_list.append(tween.to(container=self.winds_props,
                                            key='y_offset',
                                            end_value=0,
                                            time=3.25,
                                            ease_type=tweencurves.easeOutQuint,
                                            delay=delay))
            self.tween_list.append(tween.to(container=self.surface_logo_props,
                                            key='y_offset',
                                            end_value=-500,
                                            time=3.25,
                                            ease_type=tweencurves.easeOutQuint,
                                            delay=delay).on_complete(self.finish_bootup))
            
            delay = 4
            self.tween_list.append(tween.to(container=self.game_logo_props,
                                            key='scale',
                                            end_value=1,
                                            time=0.75,
                                            ease_type=tweencurves.easeOutElastic,
                                            delay=delay))
            self.tween_list.append(tween.to(container=self.game_logo_props,
                                            key='alpha',
                                            end_value=255,
                                            time=0.1,
                                            ease_type=tweencurves.easeOutCirc,
                                            delay=delay))
            
            for option in self.title_options_surfaces:
                delay += 0.125
                self.tween_list.append(tween.to(container=option,
                                                key='scale',
                                                end_value=1,
                                                time=0.5,
                                                ease_type=tweencurves.easeOutElastic,
                                                delay=delay))
                self.tween_list.append(tween.to(container=option,
                                                key='alpha',
                                                end_value=255,
                                                time=0.1,
                                                ease_type=tweencurves.easeOutCirc,
                                                delay=delay))
                
        else:
            self.finish_bootup()


    def finish_bootup(self):
        self.finished_boot_up = True

        # Clear intro assets
        del self.surface_logo
        del self.surface_logo_props
        del self.overlay
        del self.overlay_props

        # Set props to final values
        for layer in self.landscape_list:
            layer['y_offset'] = 0
            self.winds_props['y_offset'] = 0
            self.game_logo_props['scale'] = 1
            self.game_logo_props['alpha'] = 255
            for option in self.title_options_surfaces:
                option['scale'] = 1
                option['alpha'] = 255

        # Convert surfaces to static
        self.game_logo = pygame.transform.scale_by(surface=self.game_logo, factor=self.game_logo_props['scale'])
        for option in self.title_options_surfaces:
            option['surface'] = pygame.transform.scale_by(surface=option['surface'], factor=option['scale'])
        
        # Initiate substate
        Menu_TitleState(parent=self, stack=self.substate_stack).enter_state()