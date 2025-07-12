"""
🎮 RESPONSIVE ACTION PLATFORMER
===============================

🥊 MOVEMENT FEATURES:
- Smooth momentum-based movement (perfect for dodging)
- Wall sliding and wall jumping
- Dash with invincibility frames (i-frames)
- Double jump system
- Dash jumping combos
- Shooting system with projectiles
- Particle effects and screen shake
- Input buffering for responsive controls

🎯 CONTROLS:
- A/D = Move (smooth acceleration)
- SPACE = Jump/Double Jump (buffered input)
- SHIFT = Dash (with i-frames and cooldown)
- W = Wall Jump
- S = Fast Fall
- LEFT CLICK = Shoot
- TAB = Debug Mode

⚙️ PARAMETER GUIDE:
All movement values are explained with what happens when you increase/decrease them!
"""

import pygame
import math
import random
import time
from pygame.math import Vector2
from pathlib import Path

pygame.init()

# =============================================================================
# MOVEMENT PHYSICS CONSTANTS
# =============================================================================
# 🔧 GROUND MOVEMENT - Smooth momentum system
GROUND_ACCELERATION = 1200.0    # Higher = faster reach max speed, lower = more sliding
GROUND_FRICTION = 800.0         # Higher = faster stopping, lower = more sliding
MAX_GROUND_SPEED = 250.0        # Higher = faster running, lower = slower movement
AIR_ACCELERATION = 800.0        # Higher = more air control, lower = less mid-air correction
AIR_FRICTION = 200.0            # Higher = faster air stopping, lower = floatier feel
MAX_AIR_SPEED = 200.0           # Higher = faster air movement, lower = more restricted

# 🔧 JUMPING SYSTEM - Variable height and double jump
JUMP_VELOCITY = -400.0          # Higher magnitude = higher jumps, lower = shorter hops
DOUBLE_JUMP_VELOCITY = -350.0   # Higher magnitude = stronger double jump
GRAVITY = 1200.0                # Higher = faster falling, lower = floatier feel
FAST_FALL_GRAVITY = 2000.0      # Higher = faster fast fall, lower = more subtle
MAX_FALL_SPEED = 600.0          # Higher = faster terminal velocity, lower = slower max fall

# 🔧 JUMP FEEL IMPROVEMENTS
COYOTE_TIME = 0.15              # Higher = more forgiving edge jumps (seconds)
JUMP_BUFFER_TIME = 0.1          # Higher = more forgiving jump timing (seconds)
VARIABLE_JUMP_CUTOFF = 0.3      # Higher = more jump height control (0-1)

# 🔧 WALL MECHANICS - Sliding and jumping
WALL_SLIDE_SPEED = 100.0        # Higher = faster slide, lower = slower/sticky feel
WALL_JUMP_X_FORCE = 200.0       # Higher = more horizontal push off wall
WALL_JUMP_Y_FORCE = -350.0      # Higher magnitude = higher wall jumps
WALL_STICK_TIME = 0.1           # Higher = longer wall grab time (seconds)

# 🔧 DASH SYSTEM - Speed and invincibility
DASH_SPEED = 400.0              # Higher = faster/longer dash, lower = shorter dash
DASH_DURATION = 0.2             # Higher = longer dash time, lower = quicker dash
DASH_COOLDOWN = 0.8             # Higher = longer wait between dashes, lower = more frequent
IFRAME_DURATION = 0.3           # Higher = longer invincibility, lower = shorter protection
DASH_PARTICLES = 8              # Higher = more dash particles, lower = less visual effect

# 🔧 PROJECTILE SYSTEM
BULLET_SPEED = 500.0            # Higher = faster bullets, lower = slower/more dodgeable
BULLET_LIFETIME = 3.0           # Higher = bullets travel farther, lower = shorter range
FIRE_RATE = 0.25                # Higher = slower firing, lower = rapid fire
BULLET_SIZE = 6                 # Higher = bigger bullets, lower = smaller/harder to see

# 🔧 GAME FEEL SETTINGS
SCREEN_SHAKE_INTENSITY = 8.0    # Higher = more screen shake, lower = subtle shake
PARTICLE_LIFETIME = 1.0         # Higher = longer particle trails, lower = shorter effects
LANDING_PARTICLE_COUNT = 5      # Higher = more landing particles, lower = cleaner look

# =============================================================================
# SETUP AND UTILITIES
# =============================================================================
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Responsive Action Platformer')

clock = pygame.time.Clock()
FPS = 60

# Colors for fallback graphics
COLOR_BACKGROUND = (20, 25, 40)     # Dark blue-gray background
COLOR_PLAYER = (100, 150, 255)      # Blue player
COLOR_WALL = (80, 80, 100)          # Gray walls
COLOR_PLATFORM = (60, 100, 60)      # Green platforms
COLOR_BULLET = (255, 255, 100)      # Yellow bullets
COLOR_PARTICLE = (255, 200, 100)    # Orange particles
COLOR_DEBUG = (255, 255, 255)       # White debug text

# Fonts
font_debug = pygame.font.SysFont('Courier', 14)
font_ui = pygame.font.SysFont('Arial', 18)

GAME_DIR = Path(__file__).parent

def load_image_safe(relative_path, fallback_color=(255, 0, 255), size=(64, 64)):
    """Load images with fallback to colored rectangles"""
    try:
        full_path = GAME_DIR / relative_path
        if full_path.exists():
            img = pygame.image.load(str(full_path)).convert_alpha()
            return pygame.transform.scale(img, size)
    except:
        pass
    
    # Create fallback colored rectangle
    surface = pygame.Surface(size)
    surface.fill(fallback_color)
    return surface.convert_alpha()

# =============================================================================
# PARTICLE SYSTEM - Visual feedback for movement
# =============================================================================
class Particle:
    """Individual particle for movement effects"""
    
    def __init__(self, x, y, velocity_x=0, velocity_y=0, color=COLOR_PARTICLE, lifetime=1.0):
        self.position = Vector2(x, y)
        self.velocity = Vector2(velocity_x, velocity_y)
        self.color = color
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.size = random.randint(2, 4)
    
    def update(self, dt):
        """Update particle position and lifetime"""
        self.position += self.velocity * dt
        self.lifetime -= dt
        
        # Apply gravity to particles
        self.velocity.y += 300 * dt
        
        # Fade out over time
        age_ratio = 1.0 - (self.lifetime / self.max_lifetime)
        self.size = max(1, int(4 * (1 - age_ratio)))
        
        return self.lifetime > 0
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw the particle"""
        if self.lifetime > 0:
            age_ratio = self.lifetime / self.max_lifetime
            alpha = int(255 * age_ratio)
            color = (*self.color[:3], alpha)
            
            pos = (int(self.position.x - camera_offset[0]), 
                   int(self.position.y - camera_offset[1]))
            pygame.draw.circle(screen, self.color, pos, self.size)

class ParticleSystem:
    """Manages all particles in the game"""
    
    def __init__(self):
        self.particles = []
    
    def emit_landing_particles(self, x, y, count=LANDING_PARTICLE_COUNT):
        """Create particles when player lands"""
        for _ in range(count):
            vel_x = random.uniform(-50, 50)
            vel_y = random.uniform(-100, -50)
            particle = Particle(x + random.uniform(-10, 10), y, vel_x, vel_y, 
                               COLOR_PARTICLE, PARTICLE_LIFETIME * 0.8)
            self.particles.append(particle)
    
    def emit_dash_particles(self, x, y, direction, count=DASH_PARTICLES):
        """Create particles during dash"""
        for _ in range(count):
            # Particles go opposite to dash direction
            vel_x = -direction.x * random.uniform(100, 200) + random.uniform(-30, 30)
            vel_y = random.uniform(-50, 50)
            particle = Particle(x, y, vel_x, vel_y, (255, 255, 150), PARTICLE_LIFETIME * 0.5)
            self.particles.append(particle)
    
    def emit_wall_slide_particles(self, x, y):
        """Create particles when sliding on wall"""
        if random.random() < 0.3:  # Don't create every frame
            vel_x = random.uniform(-30, 30)
            vel_y = random.uniform(20, 60)
            particle = Particle(x, y, vel_x, vel_y, (150, 150, 150), PARTICLE_LIFETIME * 0.3)
            self.particles.append(particle)
    
    def update(self, dt):
        """Update all particles and remove dead ones"""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen, camera_offset)

# =============================================================================
# PROJECTILE SYSTEM - Shooting mechanics
# =============================================================================
class Bullet:
    """Projectile fired by player"""
    
    def __init__(self, x, y, direction):
        self.position = Vector2(x, y)
        self.velocity = direction * BULLET_SPEED
        self.lifetime = BULLET_LIFETIME
        self.size = BULLET_SIZE
        self.active = True
    
    def update(self, dt, platforms):
        """Update bullet position and check collisions"""
        if not self.active:
            return
        
        self.position += self.velocity * dt
        self.lifetime -= dt
        
        # Remove if lifetime expired
        if self.lifetime <= 0:
            self.active = False
            return
        
        # Check platform collisions
        bullet_rect = pygame.Rect(self.position.x - self.size//2, 
                                 self.position.y - self.size//2, 
                                 self.size, self.size)
        
        for platform in platforms:
            if bullet_rect.colliderect(platform.rect):
                self.active = False
                return
        
        # Remove if off screen
        if (self.position.x < -50 or self.position.x > SCREEN_WIDTH + 50 or
            self.position.y < -50 or self.position.y > SCREEN_HEIGHT + 50):
            self.active = False
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw the bullet"""
        if self.active:
            pos = (int(self.position.x - camera_offset[0]), 
                   int(self.position.y - camera_offset[1]))
            pygame.draw.circle(screen, COLOR_BULLET, pos, self.size)
            # Add a glow effect
            pygame.draw.circle(screen, (255, 255, 200), pos, self.size + 2, 2)

# =============================================================================
# SCREEN SHAKE SYSTEM - Impact feedback
# =============================================================================
class ScreenShake:
    """Creates camera shake for impact feedback"""
    
    def __init__(self):
        self.trauma = 0.0  # 0-1 trauma level
        self.offset = Vector2(0, 0)
    
    def add_trauma(self, amount):
        """Add trauma (0-1), higher values = more shake"""
        self.trauma = min(1.0, self.trauma + amount)
    
    def update(self, dt):
        """Update shake offset and decay trauma"""
        if self.trauma > 0:
            # Quadratic shake intensity for more dramatic effect
            shake_intensity = self.trauma * self.trauma * SCREEN_SHAKE_INTENSITY
            
            self.offset.x = random.uniform(-shake_intensity, shake_intensity)
            self.offset.y = random.uniform(-shake_intensity, shake_intensity)
            
            # Decay trauma over time
            self.trauma = max(0, self.trauma - dt * 2.0)  # 2.0 = decay speed
        else:
            self.offset = Vector2(0, 0)
    
    def get_offset(self):
        """Get current camera offset for shaking"""
        return (int(self.offset.x), int(self.offset.y))

# =============================================================================
# INPUT BUFFER SYSTEM - Responsive controls
# =============================================================================
class InputBuffer:
    """Buffers inputs to make controls feel more responsive"""
    
    def __init__(self):
        self.jump_buffer = 0.0
        self.dash_buffer = 0.0
    
    def buffer_jump(self):
        """Buffer a jump input"""
        self.jump_buffer = JUMP_BUFFER_TIME
    
    def buffer_dash(self):
        """Buffer a dash input"""
        self.dash_buffer = JUMP_BUFFER_TIME
    
    def consume_jump(self):
        """Use buffered jump and clear it"""
        if self.jump_buffer > 0:
            self.jump_buffer = 0
            return True
        return False
    
    def consume_dash(self):
        """Use buffered dash and clear it"""
        if self.dash_buffer > 0:
            self.dash_buffer = 0
            return True
        return False
    
    def update(self, dt):
        """Update buffer timers"""
        self.jump_buffer = max(0, self.jump_buffer - dt)
        self.dash_buffer = max(0, self.dash_buffer - dt)

# =============================================================================
# PLATFORM CLASS
# =============================================================================
class Platform:
    """Simple platform for collision"""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen, camera_offset=(0, 0)):
        offset_rect = self.rect.copy()
        offset_rect.x -= camera_offset[0]
        offset_rect.y -= camera_offset[1]
        pygame.draw.rect(screen, COLOR_PLATFORM, offset_rect)
        pygame.draw.rect(screen, (100, 150, 100), offset_rect, 2)

# =============================================================================
# RESPONSIVE PLAYER CLASS - Advanced movement system
# =============================================================================
class ResponsivePlayer:
    """Player with smooth, responsive movement perfect for action games"""
    
    def __init__(self, x, y):
        # POSITION AND PHYSICS
        self.position = Vector2(x, y)      # Float position for smooth movement
        self.velocity = Vector2(0, 0)      # Current velocity
        self.rect = pygame.Rect(x-16, y-24, 32, 48)  # Collision rectangle
        
        # MOVEMENT STATE
        self.on_ground = False             # Standing on solid ground
        self.was_on_ground = False         # Previous frame ground state
        self.grounded_timer = 0.0          # Time since leaving ground (coyote time)
        
        # WALL INTERACTION
        self.on_wall = False               # Touching wall
        self.wall_direction = 0            # -1 = left wall, 1 = right wall
        self.wall_slide_timer = 0.0        # Time sliding on wall
        
        # JUMPING SYSTEM
        self.jumps_used = 0                # Number of jumps used (max 2)
        self.jump_held = False             # Is jump button held for variable height
        self.jump_held_time = 0.0          # How long jump has been held
        
        # DASH SYSTEM
        self.dashing = False               # Currently dashing
        self.dash_timer = 0.0              # Time left in dash
        self.dash_direction = Vector2(0, 0) # Direction of current dash
        self.dash_cooldown = 0.0           # Time until next dash available
        self.invulnerable = False          # I-frames active
        self.iframe_timer = 0.0            # Time left in i-frames
        self.iframe_flash_timer = 0.0      # For visual flashing
        
        # SHOOTING SYSTEM
        self.bullets = []                  # Active bullets
        self.fire_cooldown = 0.0           # Time until next shot
        
        # VISUAL FEEDBACK
        self.facing_direction = 1          # 1 = right, -1 = left
        self.landed_this_frame = False     # For particle effects
        
        # ANIMATION SYSTEM (reusing your sprite loading)
        self.scale = 1.5
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0=idle, 1=run, 2=jump, 3=dash
        self.update_time = pygame.time.get_ticks()
        self.flip = False
        
        self._load_animations()
    
    def _load_animations(self):
        """Load player animations with fallbacks (using your system)"""
        animation_types = ['idle', 'running', 'jumping', 'dash']
        fallback_colors = [
            (100, 150, 255),  # Blue idle
            (150, 255, 100),  # Green running  
            (255, 150, 100),  # Orange jumping
            (255, 255, 100),  # Yellow dash
        ]
        
        for i, animation in enumerate(animation_types):
            temp_list = []
            animation_folder = GAME_DIR / "img" / "player" / animation
            
            # Try to load from files
            if animation_folder.exists():
                image_files = [f for f in animation_folder.iterdir() 
                             if f.suffix.lower() in ['.png', '.jpg', '.bmp']]
                image_files.sort()
                
                for img_file in image_files:
                    try:
                        img = pygame.image.load(str(img_file)).convert_alpha()
                        scaled_width = int(64 * self.scale)
                        scaled_height = int(64 * self.scale)
                        img = pygame.transform.scale(img, (scaled_width, scaled_height))
                        temp_list.append(img)
                    except:
                        pass
            
            # Create fallback if no frames loaded
            if not temp_list:
                fallback_surface = pygame.Surface((int(64 * self.scale), int(64 * self.scale)))
                fallback_surface.fill(fallback_colors[i])
                
                frame_count = [4, 6, 4, 6][i]
                for frame in range(frame_count):
                    color_variant = list(fallback_colors[i])
                    color_variant[0] = max(0, min(255, color_variant[0] + (frame * 10 - 20)))
                    frame_surface = pygame.Surface((int(64 * self.scale), int(64 * self.scale)))
                    frame_surface.fill(color_variant)
                    temp_list.append(frame_surface)
            
            self.animation_list.append(temp_list)
    
    def handle_input(self, keys, mouse_buttons, mouse_pos, input_buffer):
        """Process player input with buffering"""
        
        # MOVEMENT INPUT - Smooth acceleration
        move_input = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_input = -1
            self.facing_direction = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_input = 1
            self.facing_direction = 1
        
        # GROUND MOVEMENT - Different physics on ground vs air
        if self.on_ground:
            target_speed = move_input * MAX_GROUND_SPEED
            speed_diff = target_speed - self.velocity.x
            
            if abs(speed_diff) > 0.1:
                # Accelerate towards target speed
                accel_rate = GROUND_ACCELERATION if move_input != 0 else GROUND_FRICTION
                acceleration = speed_diff * accel_rate / MAX_GROUND_SPEED
                self.velocity.x += acceleration * (1/60)  # Frame rate independent
            else:
                self.velocity.x = target_speed
        else:
            # AIR MOVEMENT - Less control but still responsive
            target_speed = move_input * MAX_AIR_SPEED
            speed_diff = target_speed - self.velocity.x
            
            if abs(speed_diff) > 0.1:
                accel_rate = AIR_ACCELERATION if move_input != 0 else AIR_FRICTION
                acceleration = speed_diff * accel_rate / MAX_AIR_SPEED
                self.velocity.x += acceleration * (1/60)
        
        # JUMPING INPUT - Variable height with double jump
        if keys[pygame.K_space] or keys[pygame.K_w]:
            if not self.jump_held:  # Just pressed jump
                self.jump_held = True
                self.jump_held_time = 0
                
                # Can jump if: on ground + coyote time, or have jumps remaining
                can_jump = ((self.on_ground or self.grounded_timer < COYOTE_TIME) and self.jumps_used == 0) or \
                          (self.jumps_used == 1 and not self.on_ground)
                
                # Try buffered jump first
                if input_buffer.consume_jump() or can_jump:
                    self.perform_jump()
                else:
                    # Buffer the input for later
                    input_buffer.buffer_jump()
        else:
            if self.jump_held:  # Just released jump
                self.jump_held = False
                # Cut jump short if released early (variable height)
                if self.velocity.y < 0 and self.jump_held_time < VARIABLE_JUMP_CUTOFF:
                    self.velocity.y *= 0.5
        
        # Update jump hold time
        if self.jump_held:
            self.jump_held_time += 1/60
        
        # DASH INPUT - Powerful movement with cooldown
        if keys[pygame.K_lshift] or keys[pygame.K_rshift]:
            if self.dash_cooldown <= 0 and not self.dashing:
                # Determine dash direction
                dash_dir = Vector2(move_input if move_input != 0 else self.facing_direction, 0)
                
                # Allow up/down dashing in air
                if not self.on_ground:
                    if keys[pygame.K_s]:
                        dash_dir.y = 1
                    elif keys[pygame.K_w]:
                        dash_dir.y = -0.5  # Slight upward dash
                
                if dash_dir.length() > 0:
                    self.start_dash(dash_dir.normalize())
        
        # FAST FALL INPUT
        if keys[pygame.K_s] and not self.on_ground and self.velocity.y > 0:
            self.velocity.y = min(self.velocity.y * 1.5, MAX_FALL_SPEED)
        
        # SHOOTING INPUT
        if mouse_buttons[0] and self.fire_cooldown <= 0:  # Left click
            self.shoot(mouse_pos)
    
    def perform_jump(self):
        """Execute a jump with proper sound/particle feedback"""
        if self.jumps_used == 0:
            # First jump - full power
            self.velocity.y = JUMP_VELOCITY
            self.jumps_used = 1
            self.on_ground = False
            self.grounded_timer = 999  # Disable coyote time
            print("First Jump!")
        elif self.jumps_used == 1:
            # Double jump - slightly weaker
            self.velocity.y = DOUBLE_JUMP_VELOCITY
            self.jumps_used = 2
            print("Double Jump!")
    
    def start_dash(self, direction):
        """Begin dash with i-frames and particle effects"""
        self.dashing = True
        self.dash_timer = DASH_DURATION
        self.dash_direction = direction
        self.dash_cooldown = DASH_COOLDOWN
        
        # Grant invincibility frames
        self.invulnerable = True
        self.iframe_timer = IFRAME_DURATION
        
        # Set dash velocity
        self.velocity = direction * DASH_SPEED
        
        print(f"Dash! Direction: {direction}")
    
    def shoot(self, mouse_pos):
        """Fire a bullet towards mouse position"""
        # Calculate direction to mouse
        player_screen_pos = Vector2(self.rect.centerx, self.rect.centery)
        mouse_vec = Vector2(mouse_pos)
        direction = (mouse_vec - player_screen_pos).normalize()
        
        # Create bullet
        bullet = Bullet(self.rect.centerx, self.rect.centery, direction)
        self.bullets.append(bullet)
        self.fire_cooldown = FIRE_RATE
        
        print("Pew!")
    
    def update(self, dt, platforms, particle_system, screen_shake, input_buffer):
        """Main update loop with all systems"""
        
        # UPDATE TIMERS
        self.grounded_timer += dt
        self.dash_timer = max(0, self.dash_timer - dt)
        self.dash_cooldown = max(0, self.dash_cooldown - dt)
        self.iframe_timer = max(0, self.iframe_timer - dt)
        self.iframe_flash_timer += dt
        self.fire_cooldown = max(0, self.fire_cooldown - dt)
        
        # UPDATE DASH STATE
        if self.dashing and self.dash_timer <= 0:
            self.dashing = False
            # Reduce velocity after dash to prevent infinite speed
            self.velocity *= 0.5
        
        # UPDATE INVINCIBILITY
        if self.iframe_timer <= 0:
            self.invulnerable = False
        
        # APPLY GRAVITY (unless dashing)
        if not self.dashing and not self.on_ground:
            gravity = GRAVITY
            # Fast fall
            if self.velocity.y > 0:
                gravity *= 1.5  # Fall faster than rising
            
            self.velocity.y += gravity * dt
            self.velocity.y = min(self.velocity.y, MAX_FALL_SPEED)
        
        # WALL SLIDING PHYSICS
        if self.on_wall and not self.on_ground and self.velocity.y > 0 and not self.dashing:
            # Slow down falling when on wall
            self.velocity.y = min(self.velocity.y, WALL_SLIDE_SPEED)
            self.wall_slide_timer += dt
            
            # Emit particles occasionally
            if random.random() < 0.3:
                particle_system.emit_wall_slide_particles(
                    self.rect.centerx + self.wall_direction * 20, 
                    self.rect.centery + random.randint(-10, 10)
                )
        else:
            self.wall_slide_timer = 0
        
        # WALL JUMPING
        if self.on_wall and input_buffer.consume_jump() and not self.dashing:
            # Jump away from wall
            self.velocity.x = -self.wall_direction * WALL_JUMP_X_FORCE
            self.velocity.y = WALL_JUMP_Y_FORCE
            self.jumps_used = 1  # Wall jump counts as first jump
            print(f"Wall Jump! Direction: {-self.wall_direction}")
        
        # MOVE AND COLLIDE
        self.was_on_ground = self.on_ground
        self._move_and_collide(platforms, dt)
        
        # LANDING DETECTION for particles and screen shake
        if self.on_ground and not self.was_on_ground:
            self.landed_this_frame = True
            self.jumps_used = 0  # Reset jumps on landing
            self.grounded_timer = 0  # Reset coyote time
            
            # Create landing particles and screen shake
            landing_velocity = abs(self.velocity.y)
            if landing_velocity > 200:  # Only for significant impacts
                particle_system.emit_landing_particles(self.rect.centerx, self.rect.bottom)
                screen_shake.add_trauma(min(0.3, landing_velocity / 1000))
        else:
            self.landed_this_frame = False
        
        # DASH PARTICLES
        if self.dashing:
            particle_system.emit_dash_particles(
                self.rect.centerx, self.rect.centery, 
                -self.dash_direction  # Particles go opposite direction
            )
        
        # UPDATE BULLETS
        self.bullets = [b for b in self.bullets if b.active]
        for bullet in self.bullets:
            bullet.update(dt, platforms)
        
        # UPDATE BUFFERS
        input_buffer.update(dt)
        
        # UPDATE ANIMATIONS
        self._update_animation()
    
    def _move_and_collide(self, platforms, dt):
        """Movement with collision detection"""
        
        # HORIZONTAL MOVEMENT
        self.position.x += self.velocity.x * dt
        self.rect.centerx = int(self.position.x)
        
        # Check horizontal collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.x > 0:  # Moving right
                    self.rect.right = platform.rect.left
                    self.position.x = self.rect.centerx
                elif self.velocity.x < 0:  # Moving left
                    self.rect.left = platform.rect.right
                    self.position.x = self.rect.centerx
                self.velocity.x = 0
        
        # SCREEN BOUNDARIES (horizontal)
        if self.rect.left < 0:
            self.rect.left = 0
            self.position.x = self.rect.centerx
            self.velocity.x = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.position.x = self.rect.centerx
            self.velocity.x = 0
        
        # VERTICAL MOVEMENT
        self.position.y += self.velocity.y * dt
        self.rect.centery = int(self.position.y)
        
        # Reset ground and wall states
        self.on_ground = False
        self.on_wall = False
        self.wall_direction = 0
        
        # Check vertical collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity.y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.position.y = self.rect.centery
                    self.velocity.y = 0
                    self.on_ground = True
                elif self.velocity.y < 0:  # Rising
                    self.rect.top = platform.rect.bottom
                    self.position.y = self.rect.centery
                    self.velocity.y = 0
        
        # GROUND COLLISION (bottom of screen)
        ground_level = SCREEN_HEIGHT - 50
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.position.y = self.rect.centery
            self.velocity.y = 0
            self.on_ground = True
        
        # WALL DETECTION
        wall_thickness = 50
        if not self.on_ground and not self.dashing:
            if self.rect.left <= wall_thickness and self.velocity.x <= 0:
                self.on_wall = True
                self.wall_direction = -1
            elif self.rect.right >= SCREEN_WIDTH - wall_thickness and self.velocity.x >= 0:
                self.on_wall = True
                self.wall_direction = 1
    
    def _update_animation(self):
        """Update sprite animation"""
        ANIMATION_COOLDOWN = 150
        
        # Determine animation state
        new_action = self.action
        
        if self.dashing:
            new_action = 3  # Dash
        elif not self.on_ground:
            new_action = 2  # Jump/Fall
        elif abs(self.velocity.x) > 10:
            new_action = 1  # Run
        else:
            new_action = 0  # Idle
        
        # Update animation if changed
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
        
        # Update frame
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0
        
        # Update sprite flipping
        if self.velocity.x > 0.1:
            self.flip = False
        elif self.velocity.x < -0.1:
            self.flip = True
    
    def draw(self, screen, camera_offset=(0, 0), show_debug=False):
        """Draw player with all visual effects"""
        
        # Don't draw if invisible during i-frames
        if self.invulnerable and int(self.iframe_flash_timer * 10) % 2:
            return  # Flashing effect
        
        # Calculate sprite position
        sprite_rect = self.animation_list[self.action][self.frame_index].get_rect()
        sprite_rect.center = (self.rect.centerx - camera_offset[0], 
                             self.rect.centery - camera_offset[1])
        
        # Draw sprite
        current_sprite = self.animation_list[self.action][self.frame_index]
        flipped_sprite = pygame.transform.flip(current_sprite, self.flip, False)
        screen.blit(flipped_sprite, sprite_rect)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen, camera_offset)
        
        # DEBUG VISUALS
        if show_debug:
            debug_rect = self.rect.copy()
            debug_rect.x -= camera_offset[0]
            debug_rect.y -= camera_offset[1]
            pygame.draw.rect(screen, (255, 0, 0), debug_rect, 2)
            
            # Velocity vector
            if self.velocity.length() > 1:
                start = (self.rect.centerx - camera_offset[0], 
                        self.rect.centery - camera_offset[1])
                end = (start[0] + self.velocity.x * 0.1, 
                       start[1] + self.velocity.y * 0.1)
                pygame.draw.line(screen, (0, 255, 0), start, end, 3)
        
        # DASH COOLDOWN INDICATOR
        if self.dash_cooldown > 0:
            bar_width = 30
            bar_height = 4
            bar_x = self.rect.centerx - bar_width // 2 - camera_offset[0]
            bar_y = self.rect.bottom + 10 - camera_offset[1]
            
            # Background
            pygame.draw.rect(screen, (50, 50, 50), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Progress
            progress = 1 - (self.dash_cooldown / DASH_COOLDOWN)
            progress_width = bar_width * progress
            pygame.draw.rect(screen, (0, 255, 255), 
                           (bar_x, bar_y, progress_width, bar_height))

# =============================================================================
# GAME SYSTEMS AND LEVELS
# =============================================================================
def create_action_level():
    """Create a level designed for fast movement and dodging"""
    platforms = []
    
    # Ground platforms
    platforms.append(Platform(100, SCREEN_HEIGHT - 150, 200, 30))
    platforms.append(Platform(400, SCREEN_HEIGHT - 200, 300, 30))
    platforms.append(Platform(800, SCREEN_HEIGHT - 150, 200, 30))
    platforms.append(Platform(1200, SCREEN_HEIGHT - 250, 300, 30))
    
    # Floating platforms for vertical movement
    platforms.append(Platform(200, SCREEN_HEIGHT - 350, 150, 20))
    platforms.append(Platform(500, SCREEN_HEIGHT - 400, 150, 20))
    platforms.append(Platform(900, SCREEN_HEIGHT - 450, 150, 20))
    platforms.append(Platform(1300, SCREEN_HEIGHT - 350, 150, 20))
    
    # High platforms
    platforms.append(Platform(350, SCREEN_HEIGHT - 550, 200, 20))
    platforms.append(Platform(750, SCREEN_HEIGHT - 600, 200, 20))
    platforms.append(Platform(1100, SCREEN_HEIGHT - 550, 200, 20))
    
    return platforms

def draw_environment(screen, platforms, camera_offset=(0, 0)):
    """Draw the game world"""
    # Background
    screen.fill(COLOR_BACKGROUND)
    
    # Platforms
    for platform in platforms:
        platform.draw(screen, camera_offset)
    
    # Walls
    wall_thickness = 50
    wall_left = pygame.Rect(-camera_offset[0], -camera_offset[1], 
                           wall_thickness, SCREEN_HEIGHT)
    wall_right = pygame.Rect(SCREEN_WIDTH - wall_thickness - camera_offset[0], 
                            -camera_offset[1], wall_thickness, SCREEN_HEIGHT)
    
    pygame.draw.rect(screen, COLOR_WALL, wall_left)
    pygame.draw.rect(screen, COLOR_WALL, wall_right)
    
    # Ground
    ground = pygame.Rect(-camera_offset[0], SCREEN_HEIGHT - 50 - camera_offset[1], 
                        SCREEN_WIDTH, 50)
    pygame.draw.rect(screen, (40, 80, 40), ground)

def draw_debug_info(screen, player, input_buffer):
    """Draw debug information"""
    lines = [
        "=== RESPONSIVE MOVEMENT DEBUG ===",
        f"Position: ({player.position.x:.1f}, {player.position.y:.1f})",
        f"Velocity: ({player.velocity.x:.1f}, {player.velocity.y:.1f})",
        f"On Ground: {player.on_ground} | On Wall: {player.on_wall} (dir: {player.wall_direction})",
        f"Jumps Used: {player.jumps_used}/2 | Coyote: {player.grounded_timer:.2f}",
        f"Dashing: {player.dashing} | Dash Cooldown: {player.dash_cooldown:.1f}",
        f"I-Frames: {player.invulnerable} | Timer: {player.iframe_timer:.2f}",
        f"Wall Slide Timer: {player.wall_slide_timer:.2f}",
        f"Jump Buffer: {input_buffer.jump_buffer:.2f}",
        f"Active Bullets: {len(player.bullets)}",
        "",
        "=== CONTROLS ===",
        "A/D - Move (smooth momentum)",
        "SPACE - Jump/Double Jump",
        "SHIFT - Dash (with i-frames)",
        "W (on wall) - Wall Jump", 
        "S (in air) - Fast Fall",
        "LEFT CLICK - Shoot",
        "TAB - Toggle Debug",
        "",
        "=== MOVEMENT TIPS ===",
        "• Jump timing is buffered for responsiveness",
        "• Dash grants temporary invincibility", 
        "• Wall sliding slows your fall",
        "• Double jump resets on landing",
        "• Dash + Jump = Dash Jump combo!",
    ]
    
    y = 10
    for line in lines:
        text_surface = font_debug.render(line, True, COLOR_DEBUG)
        screen.blit(text_surface, (10, y))
        y += 16

def draw_ui(screen):
    """Draw minimal UI"""
    lines = [
        "🎮 RESPONSIVE ACTION PLATFORMER",
        "",
        "MOVEMENT:",
        "A/D - Move with momentum",
        "SPACE - Jump/Double Jump",
        "SHIFT - Dash (i-frames)",
        "W - Wall Jump",
        "S - Fast Fall",
        "CLICK - Shoot",
        "",
        "FEATURES:",
        "• Smooth momentum movement",
        "• Wall sliding & jumping", 
        "• Dash with invincibility",
        "• Input buffering",
        "• Particle effects",
        "• Screen shake feedback",
        "",
        "TAB - Debug Mode",
    ]
    
    y = 10
    for line in lines:
        text_surface = font_debug.render(line, True, COLOR_DEBUG)
        screen.blit(text_surface, (10, y))
        y += 18

# =============================================================================
# MAIN GAME LOOP
# =============================================================================
def main():
    """Main game loop with responsive movement system"""
    
    # Initialize game objects
    player = ResponsivePlayer(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    platforms = create_action_level()
    particle_system = ParticleSystem()
    screen_shake = ScreenShake()
    input_buffer = InputBuffer()
    
    # Game state
    show_debug = False
    
    # Main loop
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    show_debug = not show_debug
                    print(f"Debug: {'ON' if show_debug else 'OFF'}")
                elif event.key == pygame.K_SPACE:
                    input_buffer.buffer_jump()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    input_buffer.buffer_dash()
        
        # Get input states
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        # Update game objects
        player.handle_input(keys, mouse_buttons, mouse_pos, input_buffer)
        player.update(dt, platforms, particle_system, screen_shake, input_buffer)
        particle_system.update(dt)
        screen_shake.update(dt)
        
        # Camera offset for screen shake
        camera_offset = screen_shake.get_offset()
        
        # Render everything
        draw_environment(screen, platforms, camera_offset)
        particle_system.draw(screen, camera_offset)
        player.draw(screen, camera_offset, show_debug)
        
        # UI
        if show_debug:
            draw_debug_info(screen, player, input_buffer)
        else:
            draw_ui(screen)
        
        # Update display
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()

# =============================================================================
# 🎮 PARAMETER TUNING GUIDE
# =============================================================================
"""
🔧 MOVEMENT FEEL ADJUSTMENTS:

GROUND MOVEMENT:
- GROUND_ACCELERATION (1200): Higher = snappier start, Lower = more gradual
- GROUND_FRICTION (800): Higher = quicker stop, Lower = more sliding
- MAX_GROUND_SPEED (250): Higher = faster running, Lower = more control

AIR MOVEMENT:
- AIR_ACCELERATION (800): Higher = more air control, Lower = more commitment
- AIR_FRICTION (200): Higher = quicker air stop, Lower = floaty feel
- MAX_AIR_SPEED (200): Higher = faster air movement

JUMPING:
- JUMP_VELOCITY (-400): Higher magnitude = higher jumps
- GRAVITY (1200): Higher = faster falling, Lower = floaty feel
- COYOTE_TIME (0.15): Higher = more forgiving, Lower = more precise

DASH SYSTEM:
- DASH_SPEED (400): Higher = faster/longer dash
- DASH_DURATION (0.2): Higher = longer dash time
- IFRAME_DURATION (0.3): Higher = longer invincibility

WALL MECHANICS:
- WALL_SLIDE_SPEED (100): Higher = faster slide, Lower = more grip
- WALL_JUMP_X_FORCE (200): Higher = more push from wall

GAME FEEL:
- SCREEN_SHAKE_INTENSITY (8): Higher = more dramatic shake
- PARTICLE_LIFETIME (1.0): Higher = longer trails
- LANDING_PARTICLE_COUNT (5): Higher = more particles

🎯 RECOMMENDED STARTING VALUES:
- For faster gameplay: Increase speeds, reduce friction
- For more control: Decrease speeds, increase friction  
- For easier gameplay: Increase coyote time, buffer time
- For harder gameplay: Reduce assist timers, increase gravity

The current values are tuned for responsive action gameplay perfect for dodging!
"""