from src.library.core import *
from src.library.resource_loader import *


# Color functions

def color_darken(color: pygame.Color,
                 factor: int
                ) -> pygame.Color:
    """
    Darken a color by a given percentage.
    Returns Color

    color = original color
    factor = [0,1] percentage to darken the color by. 0 means no change. 1 means black
    """
    if not isinstance(color, pygame.Color):
        color = pygame.Color(color)
    return color.lerp(pygame.Color(0, 0, 0), factor)


def color_lighten(color: pygame.Color,
                  factor: int
                 ) -> pygame.Color:
    """
    Lighten a color by a given percentage.
    Returns Color

    color = original color
    factor = [0,1] percentage to lighten the color by. 0 means no change. 1 means white
    """
    if not isinstance(color, pygame.Color):
        color = pygame.Color(color)
    return color.lerp(pygame.Color(255, 255, 255), factor)


# Surface functions

def blit(dest: pygame.Surface,
         source: pygame.Surface,
         pos: tuple = (0, 0),
         pos_anchor: str = 'topleft',
         debug_outline: bool = False,
         debug_outline_color: pygame.Color = (255, 0, 0)
        ) -> None:
    """
    Use this instead of pygame's blit.
    Returns nothing

    dest = surface to blit to
    source = surface to blit
    pos = position on the dest surface to blit to
    pos_anchor = center, topleft, topright, bottomleft, bottomright, midtop, midbottom, midleft, midright
    debug_outline = True to draw a debug outline around the source surface
    debug_outline_color = color of the debug outline
    """
    if pos_anchor == 'topleft':
        dest.blit(source=source, dest=pos)
    else:
        source_rect = source.get_rect()
        setattr(source_rect, pos_anchor, pos)
        dest.blit(source=source, dest=source_rect)
    
    if debug_outline:
        pygame.draw.rect(dest, debug_outline_color, source_rect, 1)


def get_text(text: str,
             font: dict,
             size: str,
             color: pygame.Color,
             long_shadow: bool = True,
             long_shadow_direction = 'bottom',
             long_shadow_color: pygame.Color = None,
             outline: bool = True,
             outline_color: pygame.Color = colors.mono_35,
            ) -> pygame.Surface:
    """
    Use this to get a text surface
    Returns Surface

    text = text to render
    font = the font dictionary imported from fonts.py
    size = font size key defined in the fonts.py
    color = text color
    """
    text_font = pygame.font.Font(os.path.join(dir.fonts, font['file']), font['sizes'][size])
    text_surface = text_font.render(text=text, antialias=False, color=color)

    deco_distance = get_font_deco_distance(font=font, size=size)

    if long_shadow:
        if long_shadow_color is None:
            long_shadow_color = color_darken(color=color, factor=0.5)
        text_surface = effect_long_shadow(surface=text_surface, direction=long_shadow_direction, distance=deco_distance, color=long_shadow_color)

    if outline:
        text_surface = effect_outline(surface=text_surface, distance=deco_distance, color=outline_color)
        
    return text_surface


def get_font_deco_distance(font: dict,
                           size: str
                          ) -> int:
    """
    Returns int

    font = the font dictionary imported from fonts.py
    size = font size key defined in fonts.py
    """
    font_size = font['sizes'][size]
    pixel_size_divisor = font['pixel_size_divisor']
    return font_size//pixel_size_divisor


def get_image(dir: str,
               name: str,
               mode: str = None,
               colorkey: pygame.Color = (0, 0, 0)
              ) -> pygame.Surface:
    """
    Use this instead of pygame's load image
    Returns Surface

    dir = directory of the image. please use the constants defined in this file
    name = name of the image with .filetype
    mode = 'alpha' for images with pixels that are semi-transparent, 'colorkey' for images with pixels that are fully transparent or fully opaque
    colorkey = color to set as transparent if mode is 'colorkey'
    """
    image = pygame.image.load(os.path.join(dir, name))
    if mode == 'alpha':
        return image.convert_alpha()
    elif mode == 'colorkey':
        image = image.convert()           
        image.set_colorkey(colorkey)
        return image
    else:
        return image.convert()
    

def get_sprite(sprite_sheet: dict,
                target_sprite: str,
                mode: str = 'colorkey',
                colorkey: pygame.Color = (0, 0, 0)
               ) -> pygame.Surface:
    """
    Use this to get a single sprite from a sprite sheet
    Returns Surface

    sprite_sheet = spritesheet dict defined in spritesheets.py
    target_sprite = name of the sprite to get from the sprite sheet map
    mode = 'alpha' for images with pixels that are semi-transparent, 'colorkey' for images with pixels that are fully transparent or fully opaque
    colorkey = color to set as transparent if mode is 'colorkey'
    """
    shared_data = sprite_sheet['shared_data']
    sprite_data = sprite_sheet['sprites'][target_sprite]
    full_sprite_data = {**shared_data, **sprite_data}

    width = full_sprite_data['width']
    height = full_sprite_data['height']
    x = full_sprite_data['x']
    y = full_sprite_data['y']

    sprite_sheet_image = get_image(dir=dir.sprites, name=sprite_sheet['file'], mode=mode, colorkey=colorkey)
    sprite = pygame.Surface(size=(width, height), flags=pygame.SRCALPHA)
    sprite.blit(source=sprite_sheet_image, dest=(0, 0), area=(x, y, width, height))

    return sprite


def get_sprite_sheet(sprite_sheet: str,
                      mode: str = 'colorkey',
                      colorkey: pygame.Color = (0, 0, 0)
                     ) -> dict:
    """
    Use this to get all sprites from a sprite sheet as set
    Returns dict of Surfaces

    sprite_sheet = spritesheet dict defined in spritesheets.py
    mode = 'alpha' for images with pixels that are semi-transparent, 'colorkey' for images with pixels that are fully transparent or fully opaque
    colorkey = color to set as transparent if mode is 'colorkey'
    """
    sprites = {}
    for sprite_name in sprite_sheet['sprites']:
        sprites[sprite_name] = get_sprite(sprite_sheet=sprite_sheet, target_sprite=sprite_name, mode=mode, colorkey=colorkey)
    
    return sprites


def effect_pixelate(surface: pygame.Surface,
                    pixel_size: int = 2
                   ) -> pygame.Surface:
    """
    Use this to pixelate a surface
    Returns Surface

    surface = surface to pixelate
    pixel_size = size of the pixelation filter
    """
    original_width = surface.get_width()
    original_height = surface.get_height()
    
    scaled_down_surface = pygame.transform.scale(surface=surface, size=(original_width / pixel_size, original_height / pixel_size))
    scaled_up_surface = pygame.transform.scale(surface=scaled_down_surface, size=(original_width, original_height))
    return scaled_up_surface


def effect_grayscale(surface: pygame.Surface
                    ) -> pygame.Surface:
    """
    Use this to grayscale a surface
    Returns Surface

    surface = surface to grayscale
    """
    return pygame.transform.grayscale(surface)


def effect_silhouette(surface: pygame.Surface, 
                      color: pygame.Color = (0, 0, 0)
                     ) -> pygame.Surface:
    """
    Use this to create a silhouette of a surface
    Returns Surface

    surface = surface to create a silhouette of
    color = color of the silhouette
    """
    mask = pygame.mask.from_surface(surface)
    silhouette = mask.to_surface(setcolor=color, unsetcolor=(0,0,0,0))
    return silhouette


def effect_long_shadow(surface: pygame.Surface,
                       direction: str = 'top-left', 
                       distance: int = 1,
                       color: pygame.Color = (255, 255, 255)
                      ) -> pygame.Surface:
    """
    Use this to apply 3D on a surface
    Returns Surface

    surface = surface to apply 3D effect on
    direction = 'top-left', 'top', 'top-right', 'left', 'right', 'bottom-left', 'bottom', 'bottom-right'
    distance = distance of the 3D effect
    color = color of the 3D effect
    """
    shadow_vector = {
        'top-left': (-1, -1),
        'top': (0, -1),
        'top-right': (1, -1),
        'left': (-1, 0),
        'right': (1, 0),
        'bottom-left': (-1, 1),
        'bottom': (0, 1),
        'bottom-right': (1, 1)
    }.get(direction, (0, 0))

    if shadow_vector == (0, 0):
        print('WARNING: invalid long shadow direction')
    
    padding_x = abs(shadow_vector[0])*distance
    padding_y = abs(shadow_vector[1])*distance
    final_surface = pygame.Surface(size=(surface.get_width() + padding_x, surface.get_height() + padding_y), flags=pygame.SRCALPHA)
    
    surface_silhouette = effect_silhouette(surface=surface, color=color)
    
    positions = [(shadow_vector[0]*i, shadow_vector[1]*i) for i in range(1, distance + 1)]
    for pos in positions:
        blit(dest=final_surface, source=surface_silhouette, pos=pos)

    blit(dest=final_surface, source=surface)
    return final_surface


def effect_outline(surface: pygame.Surface,
                   distance: int = 1,
                   color: pygame.Color = (255, 255, 255),
                   no_corner: bool = False
                  ) -> pygame.Surface:
    """
    Use this to outline a surface
    Returns Surface

    surface = surface to outline
    distance = distance of the outline effect
    color = color of the outline
    no_corner = True for non-corner outline, False for corner outline
    """
    padding_x = 2*distance
    padding_y = 2*distance
    final_surface = pygame.Surface(size=(surface.get_width() + padding_x, surface.get_height() + padding_y), flags=pygame.SRCALPHA)
    
    surface_silhouette = effect_silhouette(surface=surface, color=color)
    
    if not no_corner:
        positions = [(dx + distance, dy + distance) 
                    for dx in range(-distance, distance + 1)
                    for dy in range(-distance, distance + 1)
                    if not (dx == 0 and dy == 0)]
        
        for pos in positions:
            blit(dest=final_surface, source=surface_silhouette, pos=pos)
    else:
        for dx in range(-distance, distance + 1):
            if dx == 0:
                continue
            blit(dest=final_surface, source=surface_silhouette, pos=(dx + distance, distance))
            
        for dy in range(-distance, distance + 1):
            if dy == 0:
                continue
            blit(dest=final_surface, source=surface_silhouette, pos=(distance, dy + distance))

    blit(dest=final_surface, source=surface, pos=(distance, distance))
    return final_surface


# Sound functions

def music_load(music_channel: pygame.mixer.music,
               name: str):
    """
    Use this to load music if the queue is empty
    Returns nothing

    music_channel = pygame.mixer.music channel
    name = name of the music file with .filetype
    """
    music_channel.load(filename=os.path.join(dir.music, name))


def music_queue(music_channel: pygame.mixer.music,
                name: str,
                loops: int = 0
               ) -> None:
    """
    Use this to add music to the queue
    Returns nothing

    music_channel = pygame.mixer.music
    name = name of the music file with .filetype
    loops = number of times to loop the music. 0 means no loop. -1 means infinite loop
    """
    music_channel.queue(filename=os.path.join(dir.music, name), loops=loops)


def sound_play(sound_channel: pygame.mixer.Channel,
               sound_name: str,
               loops: int = 0,
               maxtime: int = 0,
               fade_ms: int = 0
              ) -> None:
    """
    Use this to play sound effects
    Returns nothing

    sound_channel: pygame.mixer.Channel
    sound_name: str = name of the sound effect file with .filetype
    loops: int = number of times to loop the sound effect. 0 means no loop. -1 means infinite loop
    maxtime: int = number of milliseconds to play the sound effect
    fade_ms: int = number of milliseconds to fade the sound effect in or out
    """
    sound = pygame.mixer.Sound(file=os.path.join(dir.sfx, sound_name))
    sound_channel.play(sound, loops=loops, maxtime=maxtime, fade_ms=fade_ms)


# Cursor functions

def set_cursor(cursor: dict,
              ) -> None:
    """
    Use this to set the cursor
    Returns nothing

    image = surface to set as the cursor
    hotspot = hotspot of the cursor
    """
    image = get_sprite(sprite_sheet=spritesheets.cursors, target_sprite=cursor['sprite'])
    hotspot = cursor['hotspot']
    cursor = pygame.cursors.Cursor(hotspot, image)
    pygame.mouse.set_cursor(cursor)
