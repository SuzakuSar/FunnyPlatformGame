"""
🎮 EDUCATIONAL PLATFORMER - ENHANCED GROUND POUND SYSTEM
========================================================

📚 LEARNING OBJECTIVES:
✅ Proper sprite scaling and visual consistency
✅ Robust collision detection (no more ground snap bugs!)
✅ Custom explosion animations with frame management
✅ ENHANCED GROUND POUND SYSTEM with smart buffering
✅ Consistent naming conventions and code organization
✅ Performance optimization techniques
✅ Multiple approaches to common problems with trade-offs

🔧 NEW GROUND POUND FEATURES:
✅ Height requirement prevents bounce spam
✅ Jump buffering before impact for super bounces
✅ Directional momentum on impact
✅ Visual feedback and state management
✅ Educational comments explaining mechanics

🎯 CONTROLS:
- A/D or ←/→ = Move
- SPACE = Jump (hold for higher)
- SHIFT + WASD = Dash (8-directional)
- G/Q = Throw Grenade
- S/↓ = Ground Pound (in air, above bounce height)
- W/↑ = Climb ledge / Reset if stuck
- TAB = Toggle debug mode
- ESC = Quit

🎮 ENHANCED GROUND POUND MECHANICS:
- Hold SPACE just before impact = Super bounce (1.5x higher)
- Hold direction during impact = Directional momentum boost
- Minimum height requirement prevents bounce spamming
- Visual effects and state feedback
"""

import pygame
import math
import random
import os
from enum import Enum
from pygame.math import Vector2

# Initialize Pygame
pygame.init()

# =============================================================================
# 🔧 ENHANCED CONFIGURATION SYSTEM
# =============================================================================

class GameConfig:
    """
    🎛️ Centralized game configuration with enhanced ground pound system
    
    DESIGN PHILOSOPHY: Keep all tunable values in one place for easy balancing.
    This follows the "Single Source of Truth" principle - when you need to
    change ground pound mechanics, you only look in one place.
    """
    
    # 🏃 MOVEMENT PHYSICS
    GROUND_ACCELERATION = 1400      
    GROUND_FRICTION = 0.88          
    GROUND_MAX_SPEED = 240          
    
    AIR_ACCELERATION = 900          
    AIR_FRICTION = 0.97             
    AIR_MAX_SPEED = 220             
    
    # 🦘 JUMPING SYSTEM
    JUMP_STRENGTH = -425            
    DOUBLE_JUMP_STRENGTH = -400     
    GRAVITY = 1150                  
    MAX_FALL_SPEED = 520           
    JUMP_CUT_MULTIPLIER = 0.4      
    MIN_JUMP_TIME = 0.1            
    
    # 🎯 COLLISION SYSTEM
    COLLISION_TOLERANCE = 1.0      
    MAX_PENETRATION = 2.0          
    
    # 🕰️ COYOTE TIME & JUMP BUFFERING
    COYOTE_TIME = 0.12             
    JUMP_BUFFER = 0.18             
    
    # 🧱 WALL MECHANICS
    WALL_SLIDE_SPEED = 100
    WALL_JUMP_X_FORCE = 280
    WALL_JUMP_Y_FORCE = -380
    WALL_JUMP_MOMENTUM_TIME = 0.2
    
    # ⚡ DASH SYSTEM
    DASH_SPEED = 380
    DASH_DURATION = 0.15
    DASH_COOLDOWN = 0.6
    DASH_INVINCIBILITY_TIME = 0.25
    
    # 💥 ENHANCED GROUND POUND SYSTEM
    # EDUCATIONAL: These values are carefully tuned for satisfying gameplay
    GROUND_POUND_SPEED = 450                    # Downward velocity during pound
    GROUND_POUND_BOUNCE = -180                  # Base bounce height
    GROUND_POUND_MIN_HEIGHT = 120               # Minimum height above ground to trigger
    GROUND_POUND_COOLDOWN = 0.3                 # Cooldown after bounce to prevent spam
    
    # Enhanced ground pound mechanics
    GROUND_POUND_SUPER_BOUNCE_MULTIPLIER = 1.5  # Jump buffer multiplier
    GROUND_POUND_SUPER_BOUNCE_BUFFER = 0.2      # Time window before impact to buffer jump
    GROUND_POUND_MOMENTUM_BOOST = 1.8           # Directional momentum multiplier
    GROUND_POUND_MAX_MOMENTUM = 320             # Maximum horizontal velocity from momentum
    
    # Visual feedback
    GROUND_POUND_SCREEN_SHAKE_INTENSITY = 8    # Screen shake on impact
    GROUND_POUND_SCREEN_SHAKE_DURATION = 0.15  # Shake duration
    
    # 🎨 VISUAL SCALING
    BASE_SPRITE_SIZE = (128, 128)   
    ENTITY_SCALE_FACTOR = 0.5       
    BULLET_SIZE = (48, 48)          
    BULLET_SCALE_FACTOR = 0.33      
    GRENADE_SIZE = (24, 24)         
    GRENADE_SCALE_FACTOR = 1.0      
    
    # 🌍 WORLD DIMENSIONS
    WORLD_WIDTH = 2400
    WORLD_HEIGHT = 1200
    RESPAWN_Y_THRESHOLD = 1000
    
    # 🎮 DISPLAY SETTINGS
    DEFAULT_WINDOW_WIDTH = 1200
    DEFAULT_WINDOW_HEIGHT = 800
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 600
    TARGET_FPS = 60
    
    # 👾 ENEMY CONFIGURATION
    ENEMY_SIGHT_RANGE = 320
    ENEMY_SHOOT_RANGE = 280
    ENEMY_SHOOT_COOLDOWN = 1.5
    ENEMY_GROUND_SPEED = 60
    ENEMY_FLYING_SPEED = 90
    ENEMY_WANDER_RANGE = 150
    ENEMY_WANDER_SPEED = 30
    
    # 🔫 PROJECTILE SETTINGS
    BULLET_SPEED = 220
    BULLET_LIFETIME = 3.5
    
    # 💣 GRENADE PHYSICS
    GRENADE_THROW_COOLDOWN = 1.0
    GRENADE_DAMAGE = 75
    GRENADE_EXPLOSION_RADIUS = 85
    GRENADE_FRICTION = 0.7
    GRENADE_BOUNCE_FACTOR = 0.5
    GRENADE_GRAVITY = 500
    GRENADE_FUSE_TIME = 3.0
    EXPLOSION_ANIMATION_DURATION = 0.8

# =============================================================================
# 🎨 SPRITE SYSTEM (UNCHANGED FROM WORKING VERSION)
# =============================================================================

class SpriteManager:
    """🎨 Centralized sprite loading with consistent scaling"""
    
    @staticmethod
    def load_sprite(file_path, size, fallback_color, scale_factor):
        try:
            if os.path.exists(file_path):
                image = pygame.image.load(file_path).convert_alpha()
                scaled_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
                return pygame.transform.scale(image, scaled_size)
            else:
                scaled_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
                surface = pygame.Surface(scaled_size, pygame.SRCALPHA)
                surface.fill(fallback_color)
                return surface
        except Exception as e:
            print(f"Warning: Failed to load sprite {file_path}: {e}")
            scaled_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
            surface = pygame.Surface(scaled_size, pygame.SRCALPHA)
            surface.fill(fallback_color)
            return surface
    
    @staticmethod
    def load_animation_sequence(folder_path, size, fallback_color, scale_factor, frame_count=4):
        frames = []
        
        if os.path.exists(folder_path):
            try:
                image_files = [f for f in os.listdir(folder_path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
                image_files.sort()
                
                for filename in image_files:
                    full_path = os.path.join(folder_path, filename)
                    frame = SpriteManager.load_sprite(full_path, size, fallback_color, scale_factor)
                    frames.append(frame)
            except Exception as e:
                print(f"Warning: Failed to load animation from {folder_path}: {e}")
        
        if not frames:
            for i in range(frame_count):
                color_offset = (i * 20 - 40)
                animated_color = tuple(
                    max(0, min(255, color_component + color_offset)) 
                    for color_component in fallback_color
                )
                
                scaled_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
                surface = pygame.Surface(scaled_size, pygame.SRCALPHA)
                surface.fill(animated_color)
                frames.append(surface)
        
        return frames

class AnimationController:
    """🎬 Animation state management"""
    
    def __init__(self):
        self.animations = {}
        self.current_animation = "idle"
        self.frame_index = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.1
        
    def add_animation(self, name, frames, speed=0.1):
        self.animations[name] = {
            'frames': frames,
            'speed': speed
        }
        
    def set_animation(self, new_animation_name):
        if (new_animation_name != self.current_animation and 
            new_animation_name in self.animations):
            self.current_animation = new_animation_name
            self.frame_index = 0
            self.animation_timer = 0.0
            
    def update(self, delta_time):
        if self.current_animation not in self.animations:
            return
            
        self.animation_timer += delta_time
        animation_data = self.animations[self.current_animation]
        
        if self.animation_timer >= animation_data['speed']:
            self.animation_timer = 0.0
            frame_count = len(animation_data['frames'])
            self.frame_index = (self.frame_index + 1) % frame_count
                
    def get_current_frame(self):
        if self.current_animation in self.animations:
            animation_data = self.animations[self.current_animation]
            return animation_data['frames'][self.frame_index]
        return None

# =============================================================================
# 📹 ENHANCED CAMERA SYSTEM WITH SCREEN SHAKE
# =============================================================================

class ScalingCamera:
    """
    📹 Camera with screen shake support for ground pound feedback
    
    EDUCATIONAL: Screen shake is a powerful game feel technique that provides
    tactile feedback for impacts. Multiple approaches:
    1. Simple random offset (current approach - easy to implement)
    2. Sine wave oscillation (smoother, more predictable)
    3. Physics-based spring system (most realistic, complex)
    4. Curve-based animation (most control, requires animation system)
    """
    
    def __init__(self, screen_size, world_size):
        # Screen and world dimensions
        self.base_screen_size = Vector2(screen_size)
        self.current_screen_size = Vector2(screen_size)
        self.world_size = Vector2(world_size)
        self.scale_factor = 1.0
        
        # Camera position (in world coordinates)
        self.position = Vector2(0.0, 0.0)
        self.target_position = Vector2(0.0, 0.0)
        
        # Camera behavior parameters
        self.follow_speed = 6.0
        self.deadzone_radius = 60
        self.look_ahead_distance = 80
        
        # Screen shake system
        self.shake_timer = 0.0
        self.shake_intensity = 0.0
        self.shake_offset = Vector2(0, 0)
        
        # Vertical constraints
        self.min_y = 0
        self.max_y = max(0, world_size[1] - screen_size[1])
        
    def add_screen_shake(self, intensity, duration):
        """
        Add screen shake effect
        
        EDUCATIONAL: Screen shake timing is crucial for game feel:
        - Too short: Effect barely noticeable
        - Too long: Becomes annoying and disorienting
        - Too intense: Makes game unplayable
        - Too weak: No impact on player experience
        
        Sweet spot is usually 0.1-0.3 seconds for impacts.
        """
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_timer = max(self.shake_timer, duration)
        
    def update_screen_size(self, new_screen_size):
        self.current_screen_size = Vector2(new_screen_size)
        self.scale_factor = min(
            new_screen_size[0] / self.base_screen_size.x,
            new_screen_size[1] / self.base_screen_size.y
        )
        self.max_y = max(0, self.world_size.y - new_screen_size[1] / self.scale_factor)
        
    def update(self, player_position, player_velocity, delta_time):
        # Update screen shake
        if self.shake_timer > 0:
            self.shake_timer -= delta_time
            
            # Generate random shake offset
            shake_amount = self.shake_intensity * (self.shake_timer / 0.15)  # Fade out over time
            self.shake_offset = Vector2(
                random.uniform(-shake_amount, shake_amount),
                random.uniform(-shake_amount, shake_amount)
            )
        else:
            self.shake_offset = Vector2(0, 0)
        
        # Standard camera following logic
        screen_center_offset = (self.current_screen_size / self.scale_factor) / 2
        target_x = player_position.x - screen_center_offset.x
        target_y = player_position.y - screen_center_offset.y
        
        if player_velocity.x > 50:
            target_x += self.look_ahead_distance
        elif player_velocity.x < -50:
            target_x -= self.look_ahead_distance
            
        self.target_position = Vector2(target_x, target_y)
        
        # Calculate movement with horizontal wrapping
        movement_vector = self.target_position - self.position
        
        world_width = self.world_size.x
        if abs(movement_vector.x) > world_width / 2:
            if movement_vector.x > 0:
                movement_vector.x -= world_width
            else:
                movement_vector.x += world_width
        
        # Apply deadzone
        movement_distance = movement_vector.length()
        
        if movement_distance > self.deadzone_radius:
            excess_distance = movement_distance - self.deadzone_radius
            move_amount = excess_distance * self.follow_speed * delta_time
            
            if movement_distance > 0:
                movement_direction = movement_vector / movement_distance
                self.position += movement_direction * move_amount
        
        # Apply constraints
        self.position.y = max(self.min_y, min(self.max_y, self.position.y))
        self.position.x = self.position.x % world_width
    
    def get_render_offset(self):
        """Get the offset for rendering objects on screen with shake"""
        base_offset = Vector2(
            int(-self.position.x * self.scale_factor),
            int(-self.position.y * self.scale_factor)
        )
        
        # Add shake offset (scaled for screen size)
        shake_contribution = self.shake_offset * self.scale_factor
        
        return base_offset + shake_contribution
    
    def world_to_screen_position(self, world_position):
        camera_x = self.position.x
        world_x = world_position.x
        
        dx = world_x - camera_x
        if dx > self.world_size.x / 2:
            world_x -= self.world_size.x
        elif dx < -self.world_size.x / 2:
            world_x += self.world_size.x
            
        screen_x = (world_x - self.position.x) * self.scale_factor + self.shake_offset.x
        screen_y = (world_position.y - self.position.y) * self.scale_factor + self.shake_offset.y
        
        return Vector2(screen_x, screen_y)

# =============================================================================
# 🤸 ENHANCED PLAYER CONTROLLER WITH GROUND POUND SYSTEM
# =============================================================================

class MovementState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    JUMPING = "jumping"
    FALLING = "falling"
    WALL_SLIDING = "wall_sliding"
    DASHING = "dashing"
    GROUND_POUNDING = "ground_pounding"
    LEDGE_GRABBING = "ledge_grabbing"

class Player:
    """
    🤸 Enhanced player controller with sophisticated ground pound system
    
    EDUCATIONAL: Ground pound mechanics can be implemented in several ways:
    
    1. Simple Trigger System (basic approach):
       - Just check if button pressed and in air
       - Can lead to spamming and poor game feel
       
    2. Cooldown-Based System (better):
       - Add cooldown timer between uses
       - Prevents spamming but still limited
       
    3. Context-Aware System (current approach - best):
       - Height requirements prevent bounce spam
       - Jump buffering adds skill-based mechanics
       - Directional momentum rewards precise timing
       - Multiple feedback systems enhance game feel
    """
    
    def __init__(self, spawn_x, spawn_y, render_scale_factor=1.0):
        # Position and collision
        self.position = Vector2(float(spawn_x), float(spawn_y))
        self.spawn_position = Vector2(spawn_x, spawn_y)
        self.collision_rect = pygame.Rect(spawn_x, spawn_y, 32, 48)
        self.render_scale_factor = render_scale_factor
        
        # Physics state
        self.velocity = Vector2(0.0, 0.0)
        self.max_speed = GameConfig.GROUND_MAX_SPEED
        
        # Collision state tracking
        self.is_on_ground = False
        self.was_on_ground = False
        self.standing_platform = None
        self.is_on_wall = False
        self.wall_direction = 0
        self.is_grabbing_ledge = False
        self.ledge_grab_timer = 0.0
        
        # Movement control
        self.movement_locked = False
        self.stuck_detection_timer = 0.0
        
        # Jumping system
        self.jump_count = 0
        self.max_jumps = 2
        self.jump_time_remaining = 0.0
        self.can_cut_jump = False
        self.coyote_time_remaining = 0.0
        self.jump_buffer_timer = 0.0
        
        # Special abilities
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.dash_direction = Vector2(0, 0)
        self.is_invincible = False
        self.invincibility_timer = 0.0
        self.dash_jump_window_timer = 0.0
        
        # Wall mechanics
        self.wall_jump_momentum_timer = 0.0
        
        # ENHANCED GROUND POUND SYSTEM
        # EDUCATIONAL: State management for complex mechanics requires
        # multiple variables to track different aspects of the ability
        self.is_ground_pounding = False
        self.ground_pound_cooldown_timer = 0.0
        self.ground_pound_start_height = 0.0           # Height when ground pound started
        self.ground_pound_super_bounce_buffer = 0.0    # Jump buffer before impact
        self.ground_pound_directional_input = Vector2(0, 0)  # Direction held during impact
        
        # State management
        self.current_state = MovementState.IDLE
        self.previous_state = MovementState.IDLE
        self.facing_right = True
        
        # Visual effects
        self.squash_stretch_scale = Vector2(1.0, 1.0)
        
        # Player stats
        self.health = 100
        self.max_health = 100
        self.grenade_cooldown_timer = 0.0
        self.max_grenades = 3
        self.remaining_grenades = 3
        
        # Animation system
        self.animation_controller = AnimationController()
        self._initialize_animations()
        
    def _initialize_animations(self):
        """Load all player animations with proper scaling"""
        sprite_base_path = "sprites/player"
        
        animation_definitions = {
            "idle": (f"{sprite_base_path}/idle", (100, 150, 255)),
            "running": (f"{sprite_base_path}/running", (120, 170, 255)),
            "jumping": (f"{sprite_base_path}/jumping", (140, 190, 255)),
            "falling": (f"{sprite_base_path}/falling", (80, 130, 255)),
            "wall_sliding": (f"{sprite_base_path}/wall_sliding", (160, 200, 255)),
            "dashing": (f"{sprite_base_path}/dashing", (255, 150, 100)),
            "ground_pounding": (f"{sprite_base_path}/ground_pounding", (255, 100, 100)),
        }
        
        effective_scale = GameConfig.ENTITY_SCALE_FACTOR * self.render_scale_factor
        
        for animation_name, (folder_path, fallback_color) in animation_definitions.items():
            frames = SpriteManager.load_animation_sequence(
                folder_path, 
                GameConfig.BASE_SPRITE_SIZE, 
                fallback_color, 
                effective_scale
            )
            self.animation_controller.add_animation(animation_name, frames)
            
    def update_render_scale(self, new_scale_factor):
        if new_scale_factor != self.render_scale_factor:
            self.render_scale_factor = new_scale_factor
            self._initialize_animations()
    
    def get_height_above_ground(self, platforms):
        """
        Calculate height above nearest ground platform
        
        EDUCATIONAL: Height calculation approaches:
        1. Raycast downward (current approach - accurate but can be expensive)
        2. Track last ground position (fast but can be inaccurate)
        3. Spatial partitioning lookup (best for many platforms)
        4. Pre-computed height map (fastest, requires level preprocessing)
        """
        min_distance = float('inf')
        
        # Cast ray downward to find nearest ground
        for platform in platforms:
            # Check if we're roughly above this platform
            platform_left = platform.rect.left
            platform_right = platform.rect.right
            
            # Add some margin for edge cases
            if (self.position.x >= platform_left - 50 and 
                self.position.x <= platform_right + 50 and
                self.position.y <= platform.rect.top):
                
                distance = platform.rect.top - self.position.y
                min_distance = min(min_distance, distance)
        
        return min_distance if min_distance != float('inf') else 0
    
    def update(self, delta_time, input_manager, platforms, enemies, grenades, camera=None):
        # Handle horizontal world wrapping
        self.position.x = self.position.x % GameConfig.WORLD_WIDTH
        
        # Check for fall-death respawn
        if self.position.y > GameConfig.RESPAWN_Y_THRESHOLD:
            self.respawn()
            return
            
        # Store previous state
        self.was_on_ground = self.is_on_ground
        self.previous_state = self.current_state
        
        # Process input
        self._process_input(input_manager, grenades, platforms, camera)
        
        # Update all timers
        self._update_timers(delta_time)
        
        # Apply movement and physics
        if not self.movement_locked:
            self._update_movement_and_physics(delta_time, input_manager, platforms, camera)
            
        # Handle collisions
        self._handle_collisions_improved(platforms, delta_time, camera)
        
        # Update collision rect position
        self.collision_rect.centerx = int(self.position.x)
        self.collision_rect.centery = int(self.position.y)
        
        # Update visual state and animations
        self._update_movement_state()
        self._update_visual_effects(delta_time)
        
        # Update animation controller
        self.animation_controller.set_animation(self.current_state.value)
        self.animation_controller.update(delta_time)
        
    def _process_input(self, input_manager, grenades, platforms, camera):
        """Enhanced input processing with ground pound logic"""
        # Get input states
        move_left = input_manager.is_held('move_left')
        move_right = input_manager.is_held('move_right')
        move_up = input_manager.is_held('move_up')
        move_down = input_manager.is_held('move_down')
        jump_pressed = input_manager.is_pressed('jump')
        jump_held = input_manager.is_held('jump')
        dash_pressed = input_manager.is_pressed('dash')
        grenade_pressed = input_manager.is_pressed('grenade')
        ground_pound_pressed = input_manager.is_pressed('ground_pound')
        
        # Store directional input for ground pound momentum
        self.ground_pound_directional_input = Vector2(0, 0)
        if move_left:
            self.ground_pound_directional_input.x = -1
        if move_right:
            self.ground_pound_directional_input.x = 1
        
        # Emergency movement reset
        if move_up and self.movement_locked:
            self.movement_locked = False
            self.stuck_detection_timer = 0.0
            self.velocity.x = 0
            print("🔧 Movement unlocked!")
        
        # Handle grenade throwing
        if (grenade_pressed and self.grenade_cooldown_timer <= 0 and 
            self.remaining_grenades > 0):
            self._throw_grenade(grenades)
        
        # ENHANCED GROUND POUND INPUT PROCESSING
        # EDUCATIONAL: Complex input handling requires checking multiple conditions
        # to prevent unwanted triggers and ensure satisfying gameplay
        if ground_pound_pressed:
            self._try_start_ground_pound(platforms, camera)
        
        # Ground pound jump buffer
        # EDUCATIONAL: Jump buffering allows players to input slightly early
        # for more responsive controls. This is especially important for
        # time-sensitive mechanics like the ground pound super bounce.
        if jump_pressed and self.is_ground_pounding:
            self.ground_pound_super_bounce_buffer = GameConfig.GROUND_POUND_SUPER_BOUNCE_BUFFER
            print("🚀 Ground pound super bounce buffered!")
        
        # Store movement input for physics update
        self.movement_input = {
            'left': move_left,
            'right': move_right,
            'up': move_up,
            'down': move_down,
            'jump_pressed': jump_pressed,
            'jump_held': jump_held,
            'dash_pressed': dash_pressed
        }
        
    def _try_start_ground_pound(self, platforms, camera):
        """
        Attempt to start ground pound with enhanced validation
        
        EDUCATIONAL: Input validation approaches:
        1. Simple boolean check (basic)
        2. State-based validation (better) 
        3. Context-aware validation (current approach - best)
           - Checks multiple conditions
           - Provides user feedback
           - Prevents unwanted triggers
        """
        # Check if ground pound is available
        if self.is_ground_pounding:
            return  # Already ground pounding
            
        if self.ground_pound_cooldown_timer > 0:
            print(f"⏱️ Ground pound on cooldown: {self.ground_pound_cooldown_timer:.1f}s")
            return
            
        if self.is_on_ground:
            print("🚫 Must be in air to ground pound!")
            return
            
        # Check height requirement
        height_above_ground = self.get_height_above_ground(platforms)
        if height_above_ground < GameConfig.GROUND_POUND_MIN_HEIGHT:
            print(f"🚫 Too low to ground pound! Need {GameConfig.GROUND_POUND_MIN_HEIGHT}px, at {height_above_ground:.0f}px")
            return
        
        # All checks passed - start ground pound!
        self._start_ground_pound()
        print(f"💥 Ground pound started from height {height_above_ground:.0f}px!")
    
    def _start_ground_pound(self):
        """Enhanced ground pound initiation"""
        self.is_ground_pounding = True
        self.ground_pound_start_height = self.position.y
        self.velocity.x = 0  # Stop horizontal movement
        self.velocity.y = GameConfig.GROUND_POUND_SPEED
        
        # Reset state flags
        self.can_cut_jump = False
        self.dash_timer = 0.0
        
        print("💥 Ground pound initiated!")
    
    def _handle_ground_pound_impact(self, camera):
        """
        Handle ground pound impact with enhanced mechanics
        
        EDUCATIONAL: Game feel enhancement techniques demonstrated:
        1. Screen shake - tactile feedback
        2. Enhanced bounce - rewards timing
        3. Directional momentum - adds skill element
        4. Visual/audio cues - player understanding
        5. State management - prevents bugs
        """
        if not self.is_ground_pounding:
            return
            
        print("💥 Ground pound impact!")
        
        # Add screen shake for impact feedback
        if camera:
            camera.add_screen_shake(
                GameConfig.GROUND_POUND_SCREEN_SHAKE_INTENSITY, 
                GameConfig.GROUND_POUND_SCREEN_SHAKE_DURATION
            )
        
        # Calculate bounce strength
        base_bounce = GameConfig.GROUND_POUND_BOUNCE
        
        # Check for super bounce (jump buffered before impact)
        if self.ground_pound_super_bounce_buffer > 0:
            bounce_strength = base_bounce * GameConfig.GROUND_POUND_SUPER_BOUNCE_MULTIPLIER
            print("🚀 SUPER BOUNCE activated!")
        else:
            bounce_strength = base_bounce
        
        # Apply bounce
        self.velocity.y = bounce_strength
        
        # Apply directional momentum if holding direction
        if self.ground_pound_directional_input.length() > 0:
            momentum_velocity = (self.ground_pound_directional_input.x * 
                               GameConfig.GROUND_POUND_MOMENTUM_BOOST * 
                               GameConfig.GROUND_MAX_SPEED)
            
            # Cap momentum to prevent excessive speed
            momentum_velocity = max(-GameConfig.GROUND_POUND_MAX_MOMENTUM, 
                                  min(GameConfig.GROUND_POUND_MAX_MOMENTUM, momentum_velocity))
            
            self.velocity.x = momentum_velocity
            print(f"🏃 Directional momentum: {momentum_velocity:.0f} ({['LEFT', 'RIGHT'][self.ground_pound_directional_input.x > 0]})")
        
        # End ground pound state
        self.is_ground_pounding = False
        self.ground_pound_cooldown_timer = GameConfig.GROUND_POUND_COOLDOWN
        self.ground_pound_super_bounce_buffer = 0.0
        
        # Visual feedback
        self.squash_stretch_scale = Vector2(1.4, 0.6)  # Impact squash
    
    def _update_timers(self, delta_time):
        """Update all gameplay timers including ground pound"""
        timer_names = [
            'coyote_time_remaining', 'jump_buffer_timer', 'dash_timer', 
            'dash_cooldown_timer', 'invincibility_timer', 'dash_jump_window_timer',
            'wall_jump_momentum_timer', 'jump_time_remaining', 'ledge_grab_timer',
            'grenade_cooldown_timer', 'stuck_detection_timer', 
            'ground_pound_cooldown_timer', 'ground_pound_super_bounce_buffer'
        ]
        
        for timer_name in timer_names:
            current_value = getattr(self, timer_name, 0)
            if current_value > 0:
                setattr(self, timer_name, current_value - delta_time)
                
        # Update invincibility state
        if self.invincibility_timer <= 0:
            self.is_invincible = False
            
        # Stuck detection
        if (abs(self.velocity.x) < 5 and abs(self.velocity.y) < 5 and 
            not self.is_on_ground):
            self.stuck_detection_timer += delta_time
            if self.stuck_detection_timer > 1.0:
                self.movement_locked = True
                print("⚠️ Movement locked! Press UP to reset.")
    
    def _update_movement_and_physics(self, delta_time, input_manager, platforms, camera):
        """Enhanced movement handling with ground pound logic"""
        input_data = self.movement_input
        
        # Handle different movement states
        if self.dash_timer > 0:
            self._handle_dash_movement()
        elif self.is_ground_pounding:
            self._handle_ground_pound_movement()
        elif self.is_grabbing_ledge and self.ledge_grab_timer <= 0:
            self._handle_ledge_grab_movement(input_data['up'], input_data['down'], delta_time)
        else:
            # Normal movement
            self._handle_horizontal_movement(input_data['left'], input_data['right'], delta_time)
            self._handle_jumping(input_data['jump_pressed'], input_data['jump_held'], delta_time)
            self._apply_gravity(delta_time)
            
        # Handle special ability inputs
        if input_data['dash_pressed'] and self.dash_cooldown_timer <= 0:
            self._start_dash(input_data['left'], input_data['right'], 
                           input_data['up'], input_data['down'])
    
    def _handle_ground_pound_movement(self):
        """
        Handle movement during ground pound
        
        EDUCATIONAL: Ground pound movement design choices:
        1. Lock horizontal movement (current approach - focuses on vertical impact)
        2. Allow limited air control (more forgiving but less focused)
        3. Accelerate downward over time (more realistic physics)
        4. Constant speed (predictable timing, current choice)
        """
        # Lock to constant downward speed
        self.velocity.y = GameConfig.GROUND_POUND_SPEED
        
        # Minimal horizontal influence (slight air control)
        if abs(self.velocity.x) > 50:
            self.velocity.x *= 0.95  # Gradually reduce horizontal speed
    
    def _handle_horizontal_movement(self, move_left, move_right, delta_time):
        """Handle horizontal movement with different physics for ground vs air"""
        # Choose physics parameters based on ground contact
        if self.is_on_ground:
            acceleration = GameConfig.GROUND_ACCELERATION
            friction = GameConfig.GROUND_FRICTION
            self.max_speed = GameConfig.GROUND_MAX_SPEED
        else:
            acceleration = GameConfig.AIR_ACCELERATION
            friction = GameConfig.AIR_FRICTION
            self.max_speed = GameConfig.AIR_MAX_SPEED
            
        # Apply input-based acceleration
        if (move_left and not (self.wall_jump_momentum_timer > 0 and 
                              self.wall_direction == 1)):
            if self.velocity.x > -self.max_speed:
                self.velocity.x -= acceleration * delta_time
                self.velocity.x = max(self.velocity.x, -self.max_speed)
            self.facing_right = False
            
        elif (move_right and not (self.wall_jump_momentum_timer > 0 and 
                                 self.wall_direction == -1)):
            if self.velocity.x < self.max_speed:
                self.velocity.x += acceleration * delta_time
                self.velocity.x = min(self.velocity.x, self.max_speed)
            self.facing_right = True
        else:
            # Apply friction when no input
            if abs(self.velocity.x) > 10:
                self.velocity.x *= friction
            else:
                self.velocity.x = 0
                
        # Reset stuck timer when moving
        if abs(self.velocity.x) > 20:
            self.stuck_detection_timer = 0.0
    
    def _handle_jumping(self, jump_pressed, jump_held, delta_time):
        """Enhanced jumping system with coyote time and jump buffering"""
        # Update jump buffer
        if jump_pressed:
            self.jump_buffer_timer = GameConfig.JUMP_BUFFER
            
        # Update coyote time
        if self.is_on_ground:
            self.jump_count = 0
            self.coyote_time_remaining = GameConfig.COYOTE_TIME
        elif self.coyote_time_remaining > 0 and self.jump_count == 0:
            self.jump_count = 0
            
        # Determine if we can jump and what type
        can_jump = False
        jump_velocity = 0
        
        if self.jump_buffer_timer > 0:
            if self.is_on_ground or self.coyote_time_remaining > 0:
                can_jump = True
                jump_velocity = GameConfig.JUMP_STRENGTH
                self.jump_count = 1
                self.coyote_time_remaining = 0
            elif self.jump_count < self.max_jumps and not self.is_on_wall:
                can_jump = True
                jump_velocity = GameConfig.DOUBLE_JUMP_STRENGTH
                self.jump_count += 1
            elif self.is_on_wall and self.wall_direction != 0:
                can_jump = True
                jump_velocity = GameConfig.WALL_JUMP_Y_FORCE
                self.velocity.x = GameConfig.WALL_JUMP_X_FORCE * -self.wall_direction
                self.wall_jump_momentum_timer = GameConfig.WALL_JUMP_MOMENTUM_TIME
                self.jump_count = 1
                self.is_on_wall = False
                
        # Apply dash jump bonus
        if can_jump and self.dash_jump_window_timer > 0:
            jump_velocity *= 1.1
            self.velocity.x *= 1.3
            self.dash_jump_window_timer = 0
            
        # Execute jump
        if can_jump:
            self.velocity.y = jump_velocity
            self.jump_buffer_timer = 0
            self.jump_time_remaining = GameConfig.MIN_JUMP_TIME
            self.can_cut_jump = True
            self.is_on_ground = False
            self.stuck_detection_timer = 0
            
        # Handle variable jump height (jump cutting)
        if (not jump_held and self.can_cut_jump and 
            self.jump_time_remaining <= 0 and self.velocity.y < 0):
            self.velocity.y *= GameConfig.JUMP_CUT_MULTIPLIER
            self.can_cut_jump = False
            
    def _apply_gravity(self, delta_time):
        """Apply gravity with wall sliding"""
        if not self.is_on_ground:
            if self.is_on_wall and self.velocity.y > 0:
                self.velocity.y = min(self.velocity.y, GameConfig.WALL_SLIDE_SPEED)
            else:
                self.velocity.y += GameConfig.GRAVITY * delta_time
                
            self.velocity.y = min(self.velocity.y, GameConfig.MAX_FALL_SPEED)
    
    def _start_dash(self, left, right, up, down):
        """Initiate dash ability"""
        dash_x, dash_y = 0, 0
        
        if left: dash_x = -1
        if right: dash_x = 1
        if up: dash_y = -1
        if down: dash_y = 1
        
        if dash_x == 0 and dash_y == 0:
            dash_x = 1 if self.facing_right else -1
            
        direction = Vector2(dash_x, dash_y)
        if direction.length() > 0:
            direction.normalize_ip()
            
        self.dash_direction = direction
        self.velocity = direction * GameConfig.DASH_SPEED
        self.dash_timer = GameConfig.DASH_DURATION
        self.dash_cooldown_timer = GameConfig.DASH_COOLDOWN
        self.is_invincible = True
        self.invincibility_timer = GameConfig.DASH_INVINCIBILITY_TIME
        self.dash_jump_window_timer = 0.25
        self.is_ground_pounding = False  # Cancel ground pound if dashing
        self.movement_locked = False
        self.stuck_detection_timer = 0
        
    def _handle_dash_movement(self):
        self.velocity = self.dash_direction * GameConfig.DASH_SPEED
        
    def _handle_ledge_grab_movement(self, move_up, move_down, delta_time):
        self.velocity = Vector2(0, 0)
        
        if move_up:
            self.position.y -= 180 * delta_time
            self.is_grabbing_ledge = False
            self.ledge_grab_timer = 0.2
        elif move_down:
            self.is_grabbing_ledge = False
            self.ledge_grab_timer = 0.2
    
    def _handle_collisions_improved(self, platforms, delta_time, camera=None):
        """Enhanced collision detection with ground pound impact handling"""
        # Store previous state
        self.was_on_ground = self.is_on_ground
        
        # Reset collision states
        self.is_on_ground = False
        self.is_on_wall = False
        self.wall_direction = 0
        
        # HORIZONTAL MOVEMENT
        if abs(self.velocity.x) > 0.1:
            new_x = self.position.x + self.velocity.x * delta_time
            new_x = new_x % GameConfig.WORLD_WIDTH
            
            temp_rect = pygame.Rect(
                new_x - self.collision_rect.width // 2,
                self.position.y - self.collision_rect.height // 2,
                self.collision_rect.width,
                self.collision_rect.height
            )
            
            horizontal_collision = False
            for platform in platforms:
                if temp_rect.colliderect(platform.rect):
                    if self.velocity.x > 0:
                        self.position.x = platform.rect.left - self.collision_rect.width // 2 - GameConfig.COLLISION_TOLERANCE
                        if self.dash_timer <= 0:
                            self.velocity.x = 0
                        self.is_on_wall = True
                        self.wall_direction = 1
                    else:
                        self.position.x = platform.rect.right + self.collision_rect.width // 2 + GameConfig.COLLISION_TOLERANCE
                        if self.dash_timer <= 0:
                            self.velocity.x = 0
                        self.is_on_wall = True
                        self.wall_direction = -1
                    horizontal_collision = True
                    break
            
            if not horizontal_collision:
                self.position.x = new_x
        
        # VERTICAL MOVEMENT WITH GROUND POUND DETECTION
        if abs(self.velocity.y) > 0.1:
            new_y = self.position.y + self.velocity.y * delta_time
            
            temp_rect = pygame.Rect(
                self.position.x - self.collision_rect.width // 2,
                new_y - self.collision_rect.height // 2,
                self.collision_rect.width,
                self.collision_rect.height
            )
            
            vertical_collision = False
            for platform in platforms:
                if temp_rect.colliderect(platform.rect):
                    if self.velocity.y > 0:  # Falling down
                        # Landing on platform
                        self.position.y = platform.rect.top - self.collision_rect.height // 2
                        
                        # Check for ground pound impact
                        if self.is_ground_pounding:
                            self._handle_ground_pound_impact(camera)
                        else:
                            self.velocity.y = 0
                            
                        self.is_on_ground = True
                        self.standing_platform = platform
                        self.stuck_detection_timer = 0
                        
                        if (not self.was_on_ground and not self.is_ground_pounding and 
                            self.ledge_grab_timer <= 0):
                            self._simple_ledge_check(platform)
                            
                    else:  # Moving up - hitting ceiling
                        self.position.y = platform.rect.bottom + self.collision_rect.height // 2
                        self.velocity.y = 0
                        self.can_cut_jump = False
                    
                    vertical_collision = True
                    break
            
            if not vertical_collision:
                self.position.y = new_y
        
        # GROUND STATE UPDATE
        if not self.is_on_ground:
            ground_check = pygame.Rect(
                self.position.x - self.collision_rect.width // 2,
                self.position.y + self.collision_rect.height // 2,
                self.collision_rect.width,
                3
            )
            
            for platform in platforms:
                if ground_check.colliderect(platform.rect):
                    ground_y = platform.rect.top - self.collision_rect.height // 2
                    if abs(self.position.y - ground_y) <= GameConfig.COLLISION_TOLERANCE:
                        self.position.y = ground_y
                        
                        # Handle ground pound impact on snap-to-ground
                        if self.is_ground_pounding:
                            self._handle_ground_pound_impact(camera)
                        else:
                            self.velocity.y = 0
                            
                        self.is_on_ground = True
                        self.standing_platform = platform
                    break
        
        # Penetration correction
        self._fix_wall_penetration(platforms)
    
    def _fix_wall_penetration(self, platforms):
        """Simple penetration correction - prevents stuck states"""
        player_rect = pygame.Rect(
            self.position.x - self.collision_rect.width // 2,
            self.position.y - self.collision_rect.height // 2,
            self.collision_rect.width,
            self.collision_rect.height
        )
        
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                overlap_left = player_rect.right - platform.rect.left
                overlap_right = platform.rect.right - player_rect.left
                overlap_top = player_rect.bottom - platform.rect.top
                overlap_bottom = platform.rect.bottom - player_rect.top
                
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                
                if min_overlap > GameConfig.MAX_PENETRATION:
                    if min_overlap == overlap_left:
                        self.position.x = platform.rect.left - self.collision_rect.width // 2 - 1
                        self.velocity.x = min(0, self.velocity.x)
                    elif min_overlap == overlap_right:
                        self.position.x = platform.rect.right + self.collision_rect.width // 2 + 1
                        self.velocity.x = max(0, self.velocity.x)
                    elif min_overlap == overlap_top:
                        self.position.y = platform.rect.top - self.collision_rect.height // 2 - 1
                        
                        # Handle ground pound impact during penetration correction
                        if self.is_ground_pounding and self.velocity.y > 0:
                            self._handle_ground_pound_impact(None)  # No camera reference available here
                        else:
                            self.velocity.y = min(0, self.velocity.y)
                            
                        self.is_on_ground = True
                        self.standing_platform = platform
                    elif min_overlap == overlap_bottom:
                        self.position.y = platform.rect.bottom + self.collision_rect.height // 2 + 1
                        self.velocity.y = max(0, self.velocity.y)
                        self.can_cut_jump = False
                    
                    break
    
    def _simple_ledge_check(self, platform):
        ledge_check_distance = self.collision_rect.width // 2 + 8
        ledge_check_x = self.position.x + (
            ledge_check_distance if self.facing_right else -ledge_check_distance
        )
        
        if ((self.facing_right and ledge_check_x > platform.rect.right + 3) or 
            (not self.facing_right and ledge_check_x < platform.rect.left - 3)):
            self.is_grabbing_ledge = True
            self.is_on_ground = False
    
    def _throw_grenade(self, grenades):
        throw_distance = 250
        target_x = self.position.x + (throw_distance if self.facing_right else -throw_distance)
        target_y = self.position.y - 60
        
        grenade = Grenade(
            self.position.x, self.position.y - 10, 
            target_x, target_y, 
            self.render_scale_factor
        )
        grenades.append(grenade)
        
        self.remaining_grenades -= 1
        self.grenade_cooldown_timer = GameConfig.GRENADE_THROW_COOLDOWN
        
        print(f"💣 Grenade thrown! Remaining: {self.remaining_grenades}")
    
    def _update_movement_state(self):
        """Enhanced movement state management with ground pound"""
        if self.dash_timer > 0:
            self.current_state = MovementState.DASHING
        elif self.is_ground_pounding:
            self.current_state = MovementState.GROUND_POUNDING
        elif self.is_grabbing_ledge:
            self.current_state = MovementState.LEDGE_GRABBING
        elif self.is_on_wall and not self.is_on_ground and self.velocity.y > 0:
            self.current_state = MovementState.WALL_SLIDING
        elif not self.is_on_ground:
            if self.velocity.y < -100:
                self.current_state = MovementState.JUMPING
            elif self.velocity.y > 100:
                self.current_state = MovementState.FALLING
            else:
                if self.previous_state in [MovementState.JUMPING, MovementState.FALLING]:
                    self.current_state = self.previous_state
                else:
                    self.current_state = MovementState.JUMPING if self.velocity.y < 0 else MovementState.FALLING
        else:
            if abs(self.velocity.x) > 50:
                self.current_state = MovementState.RUNNING
            else:
                self.current_state = MovementState.IDLE
    
    def _update_visual_effects(self, delta_time):
        """Enhanced visual effects with ground pound feedback"""
        target_scale_x, target_scale_y = 1.0, 1.0
        
        # Landing squash
        if self.is_on_ground and self.velocity.y == 0 and not self.was_on_ground:
            target_scale_x, target_scale_y = 1.3, 0.7
        # Jump stretch
        elif self.velocity.y < -200:
            target_scale_x, target_scale_y = 0.8, 1.2
        # Dash effects
        elif self.dash_timer > 0:
            if abs(self.velocity.x) > abs(self.velocity.y):
                target_scale_x, target_scale_y = 1.4, 0.8
            else:
                target_scale_x, target_scale_y = 0.8, 1.4
        # Ground pound charging effect
        elif self.is_ground_pounding:
            target_scale_x, target_scale_y = 0.9, 1.3
                
        # Smooth interpolation to target
        interpolation_speed = 10 * delta_time
        self.squash_stretch_scale.x += (target_scale_x - self.squash_stretch_scale.x) * interpolation_speed
        self.squash_stretch_scale.y += (target_scale_y - self.squash_stretch_scale.y) * interpolation_speed
    
    def respawn(self):
        self.position = Vector2(self.spawn_position)
        self.velocity = Vector2(0, 0)
        self.health = self.max_health
        self.remaining_grenades = self.max_grenades
        self.is_on_ground = False
        self.is_ground_pounding = False
        self.dash_cooldown_timer = 0
        self.grenade_cooldown_timer = 0
        self.ground_pound_cooldown_timer = 0
        self.movement_locked = False
        self.stuck_detection_timer = 0
        print("💀 Player respawned!")
        
    def take_damage(self, damage_amount):
        if not self.is_invincible:
            self.health -= damage_amount
            self.health = max(0, self.health)
            
            self.is_invincible = True
            self.invincibility_timer = 1.0
            
            print(f"💔 Player took {damage_amount} damage! Health: {self.health}")
            
            if self.health <= 0:
                self.respawn()
    
    def render(self, screen, camera):
        screen_position = camera.world_to_screen_position(self.position)
        
        current_frame = self.animation_controller.get_current_frame()
        
        if current_frame:
            frame_width = int(current_frame.get_width() * self.squash_stretch_scale.x)
            frame_height = int(current_frame.get_height() * self.squash_stretch_scale.y)
            
            scaled_frame = pygame.transform.scale(current_frame, (frame_width, frame_height))
            
            if not self.facing_right:
                scaled_frame = pygame.transform.flip(scaled_frame, True, False)
                
            # Enhanced visual effects for ground pound
            if self.is_ground_pounding:
                # Add red tint for ground pound
                ground_pound_surface = scaled_frame.copy()
                ground_pound_surface.fill((255, 100, 100, 100), special_flags=pygame.BLEND_ADD)
                scaled_frame = ground_pound_surface
            elif self.invincibility_timer > 0 and int(pygame.time.get_ticks() / 100) % 2:
                flash_surface = scaled_frame.copy()
                flash_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_ADD)
                scaled_frame = flash_surface
                
            sprite_rect = scaled_frame.get_rect(center=(int(screen_position.x), int(screen_position.y)))
            screen.blit(scaled_frame, sprite_rect)
        else:
            color = (255, 255, 0) if self.is_invincible else (100, 150, 255)
            if self.is_ground_pounding:
                color = (255, 100, 100)
            
            size = int(64 * camera.scale_factor)
            fallback_rect = pygame.Rect(
                int(screen_position.x - size//2), 
                int(screen_position.y - size//2), 
                size, size
            )
            pygame.draw.rect(screen, color, fallback_rect)
            
        # Health bar
        self._render_health_bar(screen, screen_position, camera.scale_factor)
        
    def _render_health_bar(self, screen, screen_position, scale_factor):
        health_ratio = self.health / self.max_health
        bar_width = int(40 * scale_factor)
        bar_height = int(6 * scale_factor)
        bar_x = int(screen_position.x - bar_width // 2)
        bar_y = int(screen_position.y - 35 * scale_factor)
        
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))

# =============================================================================
# 💣 GRENADE SYSTEM (UNCHANGED FROM WORKING VERSION)
# =============================================================================

class Grenade:
    """💣 Enhanced grenade with custom explosion animation support"""
    
    def __init__(self, start_x, start_y, target_x, target_y, render_scale_factor=1.0):
        self.position = Vector2(start_x, start_y)
        self.start_position = Vector2(start_x, start_y)
        self.render_scale_factor = render_scale_factor
        
        direction_vector = Vector2(target_x - start_x, target_y - start_y)
        distance = direction_vector.length()
        
        if direction_vector.length() > 0:
            direction_vector.normalize_ip()
            
        self.velocity = direction_vector * min(350, distance * 2.2)
        self.velocity.y -= 120
        
        self.gravity = GameConfig.GRENADE_GRAVITY
        self.friction = GameConfig.GRENADE_FRICTION
        self.bounce_factor = GameConfig.GRENADE_BOUNCE_FACTOR
        
        self.fuse_time_remaining = GameConfig.GRENADE_FUSE_TIME
        self.has_exploded = False
        self.explosion_animation_timer = 0.0
        
        self.collision_rect = pygame.Rect(start_x-6, start_y-6, 12, 12)
        
        self.sprite = SpriteManager.load_sprite(
            "sprites/grenade.png", 
            GameConfig.GRENADE_SIZE, 
            (100, 200, 100), 
            GameConfig.GRENADE_SCALE_FACTOR * render_scale_factor
        )
        
        self.rotation_angle = 0.0
        self.rotation_speed = 180.0
        
        self.explosion_frames = self._load_explosion_animation()
        
    def _load_explosion_animation(self):
        explosion_folder = "sprites/explosion"
        explosion_size = (128, 128)
        fallback_color = (255, 100, 0)
        
        frames = SpriteManager.load_animation_sequence(
            explosion_folder,
            explosion_size,
            fallback_color,
            self.render_scale_factor,
            frame_count=8
        )
        
        if not os.path.exists(explosion_folder):
            frames = self._create_procedural_explosion()
            
        return frames
        
    def _create_procedural_explosion(self):
        frames = []
        explosion_size = int(128 * self.render_scale_factor)
        
        for frame_index in range(8):
            frame_surface = pygame.Surface((explosion_size, explosion_size), pygame.SRCALPHA)
            
            center = explosion_size // 2
            progress = frame_index / 7.0
            
            for ring in range(4):
                radius = int((30 + ring * 15) * progress)
                alpha = int(255 * (1.0 - progress) * (1.0 - ring * 0.2))
                
                if radius > 0 and alpha > 0:
                    if ring == 0:
                        color = (255, 255, 255, alpha)
                    elif ring == 1:
                        color = (255, 255, 0, alpha)
                    elif ring == 2:
                        color = (255, 150, 0, alpha)
                    else:
                        color = (255, 50, 0, alpha)
                    
                    ring_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                    pygame.draw.circle(ring_surface, color, (radius, radius), radius)
                    
                    frame_surface.blit(ring_surface, (center - radius, center - radius))
            
            frames.append(frame_surface)
            
        return frames
    
    def update(self, delta_time, platforms):
        if self.has_exploded:
            self.explosion_animation_timer += delta_time
            return self.explosion_animation_timer > GameConfig.EXPLOSION_ANIMATION_DURATION
            
        self.fuse_time_remaining -= delta_time
        
        if self.fuse_time_remaining <= 0:
            self.explode()
            return False
            
        self.velocity.y += self.gravity * delta_time
        
        old_position = Vector2(self.position)
        
        self.position += self.velocity * delta_time
        self.position.x = self.position.x % GameConfig.WORLD_WIDTH
        
        ground_friction_multiplier = 1.0
        for platform in platforms:
            ground_check_rect = pygame.Rect(
                int(self.position.x) - 6, 
                int(self.position.y) + 5, 
                12, 2
            )
            if ground_check_rect.colliderect(platform.rect):
                ground_friction_multiplier = self.friction
                break
                
        if ground_friction_multiplier < 1.0:
            self.velocity.x *= ground_friction_multiplier
        
        self.collision_rect.centerx = int(self.position.x)
        self.collision_rect.centery = int(self.position.y)
        
        for platform in platforms:
            if self.collision_rect.colliderect(platform.rect):
                if old_position.y <= platform.rect.top and self.velocity.y > 0:
                    self.position.y = platform.rect.top - 6
                    self.velocity.y = -self.velocity.y * self.bounce_factor
                    self.velocity.x *= 0.8
                elif old_position.x <= platform.rect.left and self.velocity.x > 0:
                    self.position.x = platform.rect.left - 6
                    self.velocity.x = -self.velocity.x * self.bounce_factor
                elif old_position.x >= platform.rect.right and self.velocity.x < 0:
                    self.position.x = platform.rect.right + 6
                    self.velocity.x = -self.velocity.x * self.bounce_factor
                break
                
        self.rotation_angle += self.rotation_speed * delta_time
        
        return False
        
    def explode(self):
        self.has_exploded = True
        self.explosion_animation_timer = 0.0
        print(f"💥 Grenade exploded at ({self.position.x:.0f}, {self.position.y:.0f})!")
        
    def get_explosion_radius(self):
        return GameConfig.GRENADE_EXPLOSION_RADIUS
        
    def render(self, screen, camera):
        screen_position = camera.world_to_screen_position(self.position)
        
        if not self.has_exploded:
            if self.sprite:
                rotated_sprite = pygame.transform.rotate(self.sprite, self.rotation_angle)
                sprite_rect = rotated_sprite.get_rect(center=(int(screen_position.x), int(screen_position.y)))
                screen.blit(rotated_sprite, sprite_rect)
                
                spark_offset = Vector2(
                    math.cos(math.radians(self.rotation_angle)) * 12 * camera.scale_factor,
                    math.sin(math.radians(self.rotation_angle)) * 12 * camera.scale_factor
                )
                spark_position = screen_position + spark_offset
                spark_radius = max(2, int(3 * camera.scale_factor))
                
                fuse_color = (255, 200, 0) if self.fuse_time_remaining > 1.0 else (255, 100, 100)
                pygame.draw.circle(screen, fuse_color, 
                                 (int(spark_position.x), int(spark_position.y)), spark_radius)
            else:
                color = (200, 255, 200) if self.fuse_time_remaining > 1 else (255, 100, 100)
                size = max(4, int(6 * camera.scale_factor))
                pygame.draw.circle(screen, color, (int(screen_position.x), int(screen_position.y)), size)
        else:
            if self.explosion_frames:
                animation_progress = self.explosion_animation_timer / GameConfig.EXPLOSION_ANIMATION_DURATION
                frame_index = int(animation_progress * len(self.explosion_frames))
                frame_index = min(frame_index, len(self.explosion_frames) - 1)
                
                explosion_frame = self.explosion_frames[frame_index]
                explosion_rect = explosion_frame.get_rect(center=(int(screen_position.x), int(screen_position.y)))
                screen.blit(explosion_frame, explosion_rect)

# =============================================================================
# 💥 BULLET SYSTEM (UNCHANGED FROM WORKING VERSION)
# =============================================================================

class Bullet:
    """💥 Bullet projectile with improved scaling"""
    
    def __init__(self, start_x, start_y, target_x, target_y, render_scale_factor=1.0):
        self.position = Vector2(start_x, start_y)
        self.render_scale_factor = render_scale_factor
        
        direction = Vector2(target_x - start_x, target_y - start_y)
        if direction.length() > 0:
            direction.normalize_ip()
        
        self.velocity = direction * GameConfig.BULLET_SPEED
        self.lifetime_remaining = GameConfig.BULLET_LIFETIME
        
        self.collision_rect = pygame.Rect(start_x-3, start_y-3, 6, 6)
        
        effective_scale = GameConfig.BULLET_SCALE_FACTOR * render_scale_factor
        self.sprite = SpriteManager.load_sprite(
            "sprites/bullet.png", 
            GameConfig.BULLET_SIZE, 
            (255, 255, 0), 
            effective_scale
        )
        
        self.angle = math.degrees(math.atan2(direction.y, direction.x))
        
    def update(self, delta_time):
        self.lifetime_remaining -= delta_time
        
        if self.lifetime_remaining <= 0:
            return False
            
        self.position += self.velocity * delta_time
        self.position.x = self.position.x % GameConfig.WORLD_WIDTH
        
        self.collision_rect.centerx = int(self.position.x)
        self.collision_rect.centery = int(self.position.y)
        
        return True
        
    def render(self, screen, camera):
        screen_position = camera.world_to_screen_position(self.position)
        
        if self.sprite:
            rotated_sprite = pygame.transform.rotate(self.sprite, -self.angle)
            sprite_rect = rotated_sprite.get_rect(center=(int(screen_position.x), int(screen_position.y)))
            screen.blit(rotated_sprite, sprite_rect)
        else:
            radius = max(3, int(5 * camera.scale_factor))
            pygame.draw.circle(screen, (255, 255, 0), 
                             (int(screen_position.x), int(screen_position.y)), radius)
            pygame.draw.circle(screen, (255, 150, 0), 
                             (int(screen_position.x), int(screen_position.y)), max(1, radius//2))

# =============================================================================
# 👾 ENEMY SYSTEM (UNCHANGED FROM WORKING VERSION)
# =============================================================================

class EnemyType(Enum):
    GROUND = "ground"
    FLYING = "flying"

class Enemy:
    """👾 AI-driven enemy with ground/flying variants"""
    
    def __init__(self, x, y, enemy_type=EnemyType.GROUND, render_scale_factor=1.0):
        self.position = Vector2(x, y)
        self.enemy_type = enemy_type
        self.render_scale_factor = render_scale_factor
        self.collision_rect = pygame.Rect(x-16, y-16, 32, 32)
        self.velocity = Vector2(0, 0)
        
        # AI state
        self.target_player = None
        self.can_see_player = False
        self.last_known_player_position = None
        self.patrol_center = Vector2(x, y)
        self.patrol_direction = 1
        self.patrol_range = GameConfig.ENEMY_WANDER_RANGE
        self.ai_state = "wandering"
        
        # Wandering behavior
        self.wander_timer = 0.0
        self.wander_direction = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.wander_direction.length() > 0:
            self.wander_direction.normalize_ip()
        self.wander_change_interval = random.uniform(2, 5)
        
        # Combat
        self.shoot_cooldown_timer = 0.0
        self.health = 50
        self.max_health = 50
        
        # Physics (ground enemies only)
        self.is_on_ground = False
        self.gravity = 800 if enemy_type == EnemyType.GROUND else 0
        
        # Animation
        self.animation_controller = AnimationController()
        self._load_enemy_animations()
        
    def _load_enemy_animations(self):
        sprite_path = f"sprites/enemy_{self.enemy_type.value}"
        fallback_colors = {
            EnemyType.GROUND: (200, 100, 100),
            EnemyType.FLYING: (100, 200, 100)
        }
        
        animation_names = ["idle", "walking", "shooting", "alert", "wandering"]
        effective_scale = GameConfig.ENTITY_SCALE_FACTOR * self.render_scale_factor
        
        for animation_name in animation_names:
            frames = SpriteManager.load_animation_sequence(
                f"{sprite_path}/{animation_name}",
                GameConfig.BASE_SPRITE_SIZE,
                fallback_colors[self.enemy_type],
                effective_scale
            )
            self.animation_controller.add_animation(animation_name, frames)
            
    def update(self, delta_time, player, platforms, bullets):
        self.shoot_cooldown_timer -= delta_time
        self.wander_timer += delta_time
        
        self.position.x = self.position.x % GameConfig.WORLD_WIDTH
        
        self.can_see_player = self._has_line_of_sight(player, platforms)
        
        if self.can_see_player:
            self.last_known_player_position = Vector2(player.position)
            self.ai_state = "combat"
            self._execute_combat_behavior(player, bullets, delta_time)
        elif self.last_known_player_position and self.ai_state != "wandering":
            self.ai_state = "investigating"
            self._execute_investigation_behavior(delta_time)
        else:
            self.ai_state = "wandering"
            self._execute_wandering_behavior(delta_time)
            
        self.position += self.velocity * delta_time
        
        if self.enemy_type == EnemyType.GROUND:
            self._apply_ground_physics(delta_time, platforms)
        
        self.collision_rect.centerx = int(self.position.x)
        self.collision_rect.centery = int(self.position.y)
        
        self.animation_controller.update(delta_time)
        
    def _has_line_of_sight(self, player, platforms):
        distance = (player.position - self.position).length()
        
        if distance > GameConfig.ENEMY_SIGHT_RANGE:
            return False
            
        direction = player.position - self.position
        if direction.length() == 0:
            return True
            
        direction.normalize_ip()
        
        ray_steps = int(distance / 8)
        for step in range(ray_steps):
            check_position = self.position + direction * (step * 8)
            check_rect = pygame.Rect(int(check_position.x)-2, int(check_position.y)-2, 4, 4)
            
            for platform in platforms:
                if check_rect.colliderect(platform.rect):
                    return False
                    
        return True
        
    def _execute_wandering_behavior(self, delta_time):
        self.animation_controller.set_animation("wandering")
        
        if self.wander_timer >= self.wander_change_interval:
            self.wander_timer = 0.0
            self.wander_change_interval = random.uniform(2, 6)
            
            if random.random() < 0.3:
                self.wander_direction = Vector2(0, 0)
            else:
                angle = random.uniform(0, 2 * math.pi)
                self.wander_direction = Vector2(math.cos(angle), math.sin(angle))
                
                if self.enemy_type == EnemyType.GROUND:
                    self.wander_direction.y = 0
                    if self.wander_direction.length() > 0:
                        self.wander_direction.normalize_ip()
        
        if self.enemy_type == EnemyType.GROUND:
            speed = GameConfig.ENEMY_GROUND_SPEED * 0.5
        else:
            speed = GameConfig.ENEMY_FLYING_SPEED * 0.3
            
        self.velocity = self.wander_direction * speed
        
        distance_from_center = (self.position - self.patrol_center).length()
        if distance_from_center > self.patrol_range:
            return_direction = (self.patrol_center - self.position).normalize()
            self.velocity = return_direction * speed
        
    def _execute_combat_behavior(self, player, bullets, delta_time):
        self.animation_controller.set_animation("alert")
        
        distance = (player.position - self.position).length()
        
        if self.enemy_type == EnemyType.GROUND:
            if distance > GameConfig.ENEMY_SHOOT_RANGE:
                direction = (player.position - self.position).normalize()
                self.velocity.x = direction.x * GameConfig.ENEMY_GROUND_SPEED
                self.animation_controller.set_animation("walking")
            elif distance < 100:
                direction = (self.position - player.position).normalize()
                self.velocity.x = direction.x * GameConfig.ENEMY_GROUND_SPEED * 0.5
                self.animation_controller.set_animation("walking")
            else:
                self.velocity.x = 0
        else:
            if distance > GameConfig.ENEMY_SHOOT_RANGE:
                direction = (player.position - self.position).normalize()
                self.velocity = direction * GameConfig.ENEMY_FLYING_SPEED
                self.animation_controller.set_animation("walking")
            elif distance < 120:
                direction = (self.position - player.position).normalize()
                self.velocity = direction * GameConfig.ENEMY_FLYING_SPEED * 0.6
                self.animation_controller.set_animation("walking")
            else:
                self.velocity = Vector2(0, 0)
        
        if (self.shoot_cooldown_timer <= 0 and 
            distance <= GameConfig.ENEMY_SHOOT_RANGE):
            bullet = Bullet(
                self.position.x, self.position.y, 
                player.position.x, player.position.y, 
                self.render_scale_factor
            )
            bullets.append(bullet)
            self.shoot_cooldown_timer = GameConfig.ENEMY_SHOOT_COOLDOWN
            self.animation_controller.set_animation("shooting")
            
    def _execute_investigation_behavior(self, delta_time):
        if self.last_known_player_position:
            distance = (self.last_known_player_position - self.position).length()
            
            if distance > 30:
                direction = (self.last_known_player_position - self.position).normalize()
                if self.enemy_type == EnemyType.GROUND:
                    self.velocity.x = direction.x * GameConfig.ENEMY_GROUND_SPEED * 0.7
                else:
                    self.velocity = direction * GameConfig.ENEMY_FLYING_SPEED * 0.7
                self.animation_controller.set_animation("walking")
            else:
                self.last_known_player_position = None
                self.velocity = Vector2(0, 0)
                self.animation_controller.set_animation("idle")
                
    def _apply_ground_physics(self, delta_time, platforms):
        if self.enemy_type != EnemyType.GROUND:
            return
            
        self.velocity.y += self.gravity * delta_time
        self.velocity.y = min(self.velocity.y, 500)
        
        self.is_on_ground = False
        temp_rect = pygame.Rect(
            int(self.position.x) - 16, 
            int(self.position.y) - 16 + int(self.velocity.y * delta_time), 
            32, 32
        )
        
        for platform in platforms:
            if temp_rect.colliderect(platform.rect) and self.velocity.y > 0:
                self.position.y = platform.rect.top - 16
                self.velocity.y = 0
                self.is_on_ground = True
                break
                
    def take_damage(self, damage_amount):
        self.health -= damage_amount
        return self.health <= 0
        
    def render(self, screen, camera):
        screen_position = camera.world_to_screen_position(self.position)
        
        current_frame = self.animation_controller.get_current_frame()
        
        if current_frame:
            sprite_rect = current_frame.get_rect(center=(int(screen_position.x), int(screen_position.y)))
            screen.blit(current_frame, sprite_rect)
        else:
            if self.enemy_type == EnemyType.GROUND:
                color = (200, 100, 100) if self.can_see_player else (150, 80, 80)
            else:
                color = (100, 200, 100) if self.can_see_player else (80, 150, 80)
                
            size = int(32 * camera.scale_factor)
            fallback_rect = pygame.Rect(
                int(screen_position.x - size//2), 
                int(screen_position.y - size//2), 
                size, size
            )
            pygame.draw.rect(screen, color, fallback_rect)
            
        self._render_health_bar(screen, screen_position, camera.scale_factor)
        
    def _render_health_bar(self, screen, screen_position, scale_factor):
        health_ratio = self.health / self.max_health
        bar_width = int(24 * scale_factor)
        bar_height = int(4 * scale_factor)
        bar_x = int(screen_position.x - bar_width // 2)
        bar_y = int(screen_position.y - 25 * scale_factor)
        
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))

# =============================================================================
# 🎮 ENHANCED INPUT MANAGER WITH GROUND POUND
# =============================================================================

class InputManager:
    """🎮 Enhanced input handling with ground pound controls"""
    
    def __init__(self):
        self.keys_currently_held = set()
        self.keys_pressed_this_frame = set()
        
        # Enhanced control mappings with ground pound
        self.control_mappings = {
            'move_left': [pygame.K_a, pygame.K_LEFT],
            'move_right': [pygame.K_d, pygame.K_RIGHT],
            'move_up': [pygame.K_w, pygame.K_UP],
            'move_down': [pygame.K_s, pygame.K_DOWN],
            'jump': [pygame.K_SPACE],
            'dash': [pygame.K_LSHIFT, pygame.K_RSHIFT],
            'grenade': [pygame.K_g, pygame.K_q],
            'ground_pound': [pygame.K_s, pygame.K_DOWN],  # Same as move_down for simplicity
        }
        
    def update(self, events):
        self.keys_pressed_this_frame.clear()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_pressed_this_frame.add(event.key)
                self.keys_currently_held.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_currently_held.discard(event.key)
                
    def is_pressed(self, action):
        return any(key in self.keys_pressed_this_frame 
                  for key in self.control_mappings.get(action, []))
        
    def is_held(self, action):
        return any(key in self.keys_currently_held 
                  for key in self.control_mappings.get(action, []))

# =============================================================================
# 🧱 PLATFORM CLASS (UNCHANGED)
# =============================================================================

class Platform:
    """🧱 Simple colored platform for level geometry"""
    
    def __init__(self, x, y, width, height, color=(120, 120, 120)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        
    def render(self, screen, camera):
        screen_position = camera.world_to_screen_position(Vector2(self.rect.topleft))
        
        if screen_position.x < -self.rect.width * camera.scale_factor:
            screen_position.x += GameConfig.WORLD_WIDTH * camera.scale_factor
        elif screen_position.x > camera.current_screen_size.x:
            screen_position.x -= GameConfig.WORLD_WIDTH * camera.scale_factor
            
        screen_rect = pygame.Rect(
            int(screen_position.x), int(screen_position.y),
            int(self.rect.width * camera.scale_factor),
            int(self.rect.height * camera.scale_factor)
        )
        
        pygame.draw.rect(screen, self.color, screen_rect)
        pygame.draw.rect(screen, tuple(max(0, c-40) for c in self.color), 
                        screen_rect, max(1, int(2 * camera.scale_factor)))

# =============================================================================
# 🎮 ENHANCED MAIN GAME CLASS
# =============================================================================

class PlatformerGame:
    """
    🎮 Enhanced main game class with ground pound system
    
    EDUCATIONAL: Enhanced game loop demonstrating:
    1. Complex player input handling
    2. Visual feedback systems (screen shake)
    3. State management across systems
    4. Educational debugging tools
    """
    
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode(
            (GameConfig.DEFAULT_WINDOW_WIDTH, GameConfig.DEFAULT_WINDOW_HEIGHT),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("🎮 Enhanced Educational Platformer - Ground Pound System")
        self.clock = pygame.time.Clock()
        
        self.screen_size = (GameConfig.DEFAULT_WINDOW_WIDTH, GameConfig.DEFAULT_WINDOW_HEIGHT)
        self.scale_factor = 1.0
        
        world_dimensions = (GameConfig.WORLD_WIDTH, GameConfig.WORLD_HEIGHT)
        self.camera = ScalingCamera(self.screen_size, world_dimensions)
        self.input_manager = InputManager()
        
        self.player = Player(200, 400, self.scale_factor)
        self.platforms = self._create_level_geometry()
        self.enemies = self._create_enemy_encounters()
        self.bullets = []
        self.grenades = []
        
        self.debug_mode_enabled = False
        self.ui_font = pygame.font.Font(None, 24)
        
    def handle_window_resize(self, new_size):
        actual_width = max(GameConfig.MIN_WINDOW_WIDTH, new_size[0])
        actual_height = max(GameConfig.MIN_WINDOW_HEIGHT, new_size[1])
        self.screen_size = (actual_width, actual_height)
        
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
        
        self.camera.update_screen_size(self.screen_size)
        self.scale_factor = self.camera.scale_factor
        
        self.player.update_render_scale(self.scale_factor)
        for enemy in self.enemies:
            enemy.render_scale_factor = self.scale_factor
            enemy._load_enemy_animations()
        for grenade in self.grenades:
            grenade.render_scale_factor = self.scale_factor
        for bullet in self.bullets:
            bullet.render_scale_factor = self.scale_factor
            
        print(f"🔄 Window resized to {self.screen_size}, scale: {self.scale_factor:.2f}")
        
    def _create_level_geometry(self):
        platforms = []
        
        ground_color = (139, 69, 19)
        platform_positions = [
            (0, 600, 400, 100),
            (600, 600, 400, 100),
            (1200, 600, 400, 100),
            (1800, 600, 400, 100),
        ]
        
        for x, y, w, h in platform_positions:
            platforms.append(Platform(x, y, w, h, ground_color))
        
        platform_color = (100, 100, 100)
        floating_positions = [
            (300, 500, 150, 20),
            (700, 450, 120, 20),
            (200, 350, 100, 20),
            (900, 400, 140, 20),
            (1300, 350, 100, 20),
            (1600, 500, 150, 20),
            (2000, 400, 120, 20),
        ]
        
        for x, y, w, h in floating_positions:
            platforms.append(Platform(x, y, w, h, platform_color))
        
        wall_color = (80, 80, 80)
        wall_positions = [
            (550, 300, 20, 200),
            (1100, 200, 20, 250),
            (1800, 300, 20, 200),
        ]
        
        for x, y, w, h in wall_positions:
            platforms.append(Platform(x, y, w, h, wall_color))
        
        upper_color = (140, 140, 140)
        upper_positions = [
            (100, 200, 200, 20),
            (800, 150, 180, 20),
            (1500, 200, 200, 20),
        ]
        
        for x, y, w, h in upper_positions:
            platforms.append(Platform(x, y, w, h, upper_color))
        
        return platforms
        
    def _create_enemy_encounters(self):
        enemies = []
        
        ground_enemy_positions = [
            (350, 570), (950, 570), (1350, 570),
            (350, 470), (950, 370),
        ]
        
        for x, y in ground_enemy_positions:
            enemies.append(Enemy(x, y, EnemyType.GROUND, self.scale_factor))
            
        flying_enemy_positions = [
            (500, 300), (1000, 250), (1500, 350),
            (200, 180), (1800, 200),
        ]
        
        for x, y in flying_enemy_positions:
            enemies.append(Enemy(x, y, EnemyType.FLYING, self.scale_factor))
            
        return enemies
        
    def update_game_logic(self, delta_time):
        # Update player with camera reference for screen shake
        self.player.update(delta_time, self.input_manager, self.platforms, 
                          self.enemies, self.grenades, self.camera)
        
        self.camera.update(self.player.position, self.player.velocity, delta_time)
        
        for enemy in self.enemies[:]:
            enemy.update(delta_time, self.player, self.platforms, self.bullets)
            
        for bullet in self.bullets[:]:
            if not bullet.update(delta_time):
                self.bullets.remove(bullet)
                continue
                
            if (bullet.collision_rect.colliderect(self.player.collision_rect) and 
                not self.player.is_invincible):
                self.player.take_damage(25)
                self.bullets.remove(bullet)
                continue
                
            hit_platform = False
            for platform in self.platforms:
                if bullet.collision_rect.colliderect(platform.rect):
                    self.bullets.remove(bullet)
                    hit_platform = True
                    break
                    
        for grenade in self.grenades[:]:
            should_remove = grenade.update(delta_time, self.platforms)
            
            if should_remove:
                if grenade.has_exploded:
                    explosion_center = grenade.position
                    explosion_radius = grenade.get_explosion_radius()
                    
                    for enemy in self.enemies[:]:
                        distance = (enemy.position - explosion_center).length()
                        if distance <= explosion_radius:
                            if enemy.take_damage(GameConfig.GRENADE_DAMAGE):
                                self.enemies.remove(enemy)
                                
                self.grenades.remove(grenade)
                continue
                
            if grenade.position.y > GameConfig.RESPAWN_Y_THRESHOLD:
                self.grenades.remove(grenade)
                
        # Player dash attack vs enemies
        if self.player.dash_timer > 0:
            for enemy in self.enemies[:]:
                if self.player.collision_rect.colliderect(enemy.collision_rect):
                    if enemy.take_damage(50):
                        self.enemies.remove(enemy)
                        
    def render_frame(self):
        """Render complete game frame"""
        # Draw sky gradient background
        self._render_sky_background()
        
        # Render game objects in correct order (back to front)
        for platform in self.platforms:
            platform.render(self.screen, self.camera)
            
        for enemy in self.enemies:
            enemy.render(self.screen, self.camera)
            
        for bullet in self.bullets:
            bullet.render(self.screen, self.camera)
            
        for grenade in self.grenades:
            grenade.render(self.screen, self.camera)
            
        # Player rendered last (on top)
        self.player.render(self.screen, self.camera)
        
        # UI rendered last (always on top)
        self._render_user_interface()
        
        if self.debug_mode_enabled:
            self._render_debug_information()
            
        # Present the completed frame
        pygame.display.flip()
        
    def _render_sky_background(self):
        """Render gradient sky background"""
        screen_height = self.screen_size[1]
        
        for y in range(screen_height):
            color_ratio = y / screen_height
            
            red_component = int(50 + (120 - 50) * color_ratio)
            green_component = int(80 + (180 - 80) * color_ratio)
            blue_component = int(120 + (220 - 120) * color_ratio)
            
            line_color = (red_component, green_component, blue_component)
            pygame.draw.line(self.screen, line_color, (0, y), (self.screen_size[0], y))
        
    def _render_user_interface(self):
        """Enhanced UI rendering with ground pound information"""
        ui_scale = max(0.8, min(1.5, self.scale_factor))
        
        # Player health bar
        self._render_player_health_bar(ui_scale)
        
        # Enhanced game statistics with ground pound info
        self._render_enhanced_game_statistics(ui_scale)
        
        # Window information
        self._render_window_information(ui_scale)
        
    def _render_player_health_bar(self, ui_scale):
        """Render player health bar in top-left corner"""
        health_ratio = self.player.health / self.player.max_health
        
        bar_width = int(250 * ui_scale)
        bar_height = int(25 * ui_scale)
        bar_x = 20
        bar_y = 20
        
        pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        current_health_width = int(bar_width * health_ratio)
        pygame.draw.rect(self.screen, (255, 0, 0), (bar_x, bar_y, current_health_width, bar_height))
        
        border_thickness = max(1, int(2 * ui_scale))
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), border_thickness)
        
        font_size = max(16, int(20 * ui_scale))
        health_font = pygame.font.Font(None, font_size)
        health_text = health_font.render(
            f"Health: {int(self.player.health)}/{int(self.player.max_health)}", 
            True, (255, 255, 255)
        )
        self.screen.blit(health_text, (bar_x, bar_y + bar_height + 5))
        
    def _render_enhanced_game_statistics(self, ui_scale):
        """Render enhanced game statistics with ground pound info"""
        font_size = max(16, int(20 * ui_scale))
        stats_font = pygame.font.Font(None, font_size)
        
        base_x = 20
        base_y = 70
        line_spacing = 25
        
        # Calculate height above ground for ground pound availability
        height_above_ground = self.player.get_height_above_ground(self.platforms)
        
        # Ground pound status
        if self.player.is_ground_pounding:
            gp_status = "💥 GROUND POUNDING!"
            gp_color = (255, 100, 100)
        elif self.player.ground_pound_cooldown_timer > 0:
            gp_status = f"⏱️ Cooldown: {self.player.ground_pound_cooldown_timer:.1f}s"
            gp_color = (255, 200, 100)
        elif self.player.is_on_ground:
            gp_status = "🚫 Need to be in air"
            gp_color = (150, 150, 150)
        elif height_above_ground < GameConfig.GROUND_POUND_MIN_HEIGHT:
            gp_status = f"🚫 Too low ({height_above_ground:.0f}/{GameConfig.GROUND_POUND_MIN_HEIGHT}px)"
            gp_color = (255, 150, 150)
        else:
            gp_status = f"✅ Ready! ({height_above_ground:.0f}px high)"
            gp_color = (100, 255, 100)
        
        # Statistics to display
        statistics = [
            (f"Enemies: {len(self.enemies)}", (255, 255, 255)),
            (f"Grenades: {self.player.remaining_grenades}/{self.player.max_grenades}", (255, 255, 255)),
            (f"Bullets: {len(self.bullets)}", (255, 255, 255)),
            ("", (255, 255, 255)),  # Spacer
            ("💥 GROUND POUND:", (255, 255, 100)),
            (gp_status, gp_color),
        ]
        
        # Add ground pound super bounce status
        if self.player.ground_pound_super_bounce_buffer > 0:
            statistics.append((f"🚀 Super bounce buffered!", (100, 255, 255)))
        
        for index, (stat_text, color) in enumerate(statistics):
            if stat_text:  # Skip empty lines
                text_surface = stats_font.render(stat_text, True, color)
                self.screen.blit(text_surface, (base_x, base_y + index * line_spacing))
        
    def _render_window_information(self, ui_scale):
        """Render window and scaling information"""
        font_size = max(16, int(20 * ui_scale))
        info_font = pygame.font.Font(None, font_size)
        
        window_info_text = f"Window: {self.screen_size[0]}x{self.screen_size[1]} (Scale: {self.scale_factor:.2f})"
        text_surface = info_font.render(window_info_text, True, (255, 255, 255))
        
        text_y = self.screen_size[1] - 25
        self.screen.blit(text_surface, (20, text_y))
        
    def _render_debug_information(self):
        """Enhanced debug information with ground pound details"""
        # Calculate height above ground for debugging
        height_above_ground = self.player.get_height_above_ground(self.platforms)
        
        debug_lines = [
            f"Player Position: ({self.player.position.x:.1f}, {self.player.position.y:.1f})",
            f"Player Velocity: ({self.player.velocity.x:.1f}, {self.player.velocity.y:.1f})",
            f"Movement State: {self.player.current_state.value}",
            f"On Ground: {self.player.is_on_ground}",
            f"Standing Platform: {self.player.standing_platform is not None}",
            f"On Wall: {self.player.is_on_wall} (direction: {self.player.wall_direction})",
            f"Movement Locked: {self.player.movement_locked}",
            "",
            "💥 GROUND POUND DEBUG:",
            f"Is Ground Pounding: {self.player.is_ground_pounding}",
            f"Height Above Ground: {height_above_ground:.1f}px",
            f"Min Height Required: {GameConfig.GROUND_POUND_MIN_HEIGHT}px",
            f"Cooldown Timer: {self.player.ground_pound_cooldown_timer:.2f}s",
            f"Super Bounce Buffer: {self.player.ground_pound_super_bounce_buffer:.2f}s",
            f"Directional Input: ({self.player.ground_pound_directional_input.x}, {self.player.ground_pound_directional_input.y})",
            "",
            f"Camera Position: ({self.camera.position.x:.1f}, {self.camera.position.y:.1f})",
            f"Camera Shake: {self.camera.shake_timer:.2f}s (intensity: {self.camera.shake_intensity:.1f})",
            f"Render Scale: {self.scale_factor:.2f}",
            "",
            "🎮 ENHANCED CONTROLS:",
            "A/D = Move, SPACE = Jump",
            "SHIFT + WASD = Dash",
            "G/Q = Grenade, S = Ground Pound",
            "W = Climb/Reset, TAB = Debug",
            "",
            "💥 GROUND POUND MECHANICS:",
            "• Must be in air above min height",
            "• Hold SPACE before impact = Super bounce",
            "• Hold direction during impact = Momentum",
            "• Screen shake and visual feedback",
            "• Cooldown prevents bounce spam",
            "",
            "🔧 SIMPLE COLLISION DEBUG:",
            f"Collision Tolerance: {GameConfig.COLLISION_TOLERANCE}",
            f"Max Penetration: {GameConfig.MAX_PENETRATION}", 
            f"Simple penetration correction prevents stuck states",
        ]
        
        debug_font_size = max(14, int(16 * min(1.2, self.scale_factor)))
        debug_font = pygame.font.Font(None, debug_font_size)
        
        for line_index, debug_line in enumerate(debug_lines):
            if debug_line:
                text_surface = debug_font.render(debug_line, True, (255, 255, 255))
                
                background_rect = pygame.Rect(5, 5 + line_index * 18, text_surface.get_width() + 10, 18)
                background_surface = pygame.Surface((background_rect.width, background_rect.height))
                background_surface.set_alpha(180)
                background_surface.fill((0, 0, 0))
                self.screen.blit(background_surface, background_rect)
                
                self.screen.blit(text_surface, (10, 10 + line_index * 18))
        
    def run_game_loop(self):
        """
        Enhanced main game loop with ground pound system
        
        EDUCATIONAL: This enhanced game loop demonstrates several important
        concepts for complex game mechanics:
        
        1. State Management: Ground pound system requires tracking multiple
           states (height, cooldown, buffering) across frames
           
        2. User Feedback: Multiple feedback mechanisms (visual, audio, screen shake)
           help players understand the complex mechanics
           
        3. Input Buffering: Allowing slightly early input makes controls feel
           more responsive, especially for time-sensitive mechanics
           
        4. Height Requirements: Preventing ability spam through contextual
           requirements rather than simple cooldowns
           
        5. Educational Debugging: Comprehensive debug output helps understand
           how complex systems interact
        """
        game_running = True
        
        # Enhanced startup messages
        print("🎮 Enhanced Educational Platformer Started!")
        print("")
        print("✅ ENHANCED GROUND POUND SYSTEM:")
        print("  - Height requirement prevents bounce spam")
        print("  - Jump buffering before impact = super bounce (1.5x)")
        print("  - Directional momentum on impact")
        print("  - Screen shake feedback")
        print("  - Visual state indicators")
        print("")
        print("🔧 GROUND POUND MECHANICS:")
        print("  1. Must be in air above minimum height (120px)")
        print("  2. Press S/DOWN to initiate ground pound")
        print("  3. Hold SPACE just before impact for super bounce")
        print("  4. Hold LEFT/RIGHT during impact for momentum boost")
        print("  5. Cooldown prevents bounce spamming")
        print("")
        print("🎯 EDUCATIONAL FEATURES:")
        print("  - Multiple validation approaches demonstrated")
        print("  - Input buffering for responsive controls")
        print("  - Context-aware ability availability")
        print("  - Visual feedback systems (screen shake)")
        print("  - State management across complex systems")
        print("")
        print("🔧 COLLISION APPROACH:")
        print("- Standard horizontal/vertical collision (proven to work)")
        print("- Simple penetration detection and correction") 
        print("- Fixes stuck states without breaking normal movement")
        print("- Enhanced with ground pound impact detection")
        print("")
        print("🎮 CONTROLS:")
        print("- A/D or ←/→: Move")
        print("- SPACE: Jump (hold for variable height)")
        print("- SHIFT + WASD: 8-directional dash")
        print("- G/Q: Throw grenade")
        print("- S/↓: Ground pound (when in air, above min height)")
        print("- W/↑: Climb ledge / Emergency reset")
        print("- TAB: Toggle enhanced debug mode")
        print("- ESC: Quit")
        print("")
        print("💡 TIP: Try combining ground pound with other abilities!")
        print("🔧 Use TAB for detailed ground pound debugging!")
        
        while game_running:
            delta_time = self.clock.tick(GameConfig.TARGET_FPS) / 1000.0
            
            # Process input events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    game_running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_window_resize((event.w, event.h))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_running = False
                    elif event.key == pygame.K_TAB:
                        self.debug_mode_enabled = not self.debug_mode_enabled
                        print(f"🔧 Debug mode: {'ON' if self.debug_mode_enabled else 'OFF'}")
                        
            # Update input manager
            self.input_manager.update(events)
            
            # Update game logic
            self.update_game_logic(delta_time)
            
            # Render frame
            self.render_frame()
            
        # Cleanup
        pygame.quit()

# =============================================================================
# 🚀 GAME ENTRY POINT
# =============================================================================

def main():
    """
    Enhanced main entry point for the game
    
    EDUCATIONAL: This enhanced version demonstrates proper error handling
    and cleanup for complex game systems. The ground pound system adds
    several new potential failure points that need to be handled gracefully.
    """
    try:
        # Create and run the enhanced game
        game = PlatformerGame()
        game.run_game_loop()
        
    except Exception as e:
        print(f"❌ Game crashed with error: {e}")
        import traceback
        traceback.print_exc()
        
    except KeyboardInterrupt:
        print("🛑 Game interrupted by user")
        
    finally:
        # Ensure Pygame is properly cleaned up
        pygame.quit()
        print("🎮 Enhanced game shut down cleanly")

# =============================================================================
# 📚 EDUCATIONAL SUMMARY - ENHANCED GROUND POUND SYSTEM
# =============================================================================

"""
🎓 ENHANCED EDUCATIONAL SUMMARY - GROUND POUND MECHANICS:
========================================================

🎯 NEW CONCEPTS DEMONSTRATED:

1. **CONTEXT-AWARE ABILITY SYSTEMS**:
   - Height requirements prevent ability spam
   - State validation with user feedback
   - Multiple conditions for ability availability

2. **INPUT BUFFERING FOR COMPLEX MECHANICS**:
   - Jump buffering before ground pound impact
   - Time windows for enhanced abilities
   - Responsive controls for time-sensitive actions

3. **MULTI-LAYERED FEEDBACK SYSTEMS**:
   - Screen shake for impact feedback
   - Visual state indicators
   - Audio cues (could be extended)
   - UI status updates

4. **ENHANCED STATE MANAGEMENT**:
   - Multiple timers for complex abilities
   - State transitions with validation
   - Persistent state across frames

🔧 GROUND POUND IMPLEMENTATION APPROACHES:

**APPROACH 1: Simple Trigger System (Basic)**
```python
if ground_pound_pressed and not is_on_ground:
    start_ground_pound()
```
✅ Simple to implement
❌ Can be spammed, poor game feel
❌ No skill-based mechanics

**APPROACH 2: Cooldown-Based System (Better)**
```python
if ground_pound_pressed and not is_on_ground and cooldown <= 0:
    start_ground_pound()
    cooldown = GROUND_POUND_COOLDOWN
```
✅ Prevents spamming
✅ Still simple to implement
❌ Doesn't prevent bounce spam specifically
❌ No skill rewards

**APPROACH 3: Context-Aware System (Current - Best)**
```python
def try_start_ground_pound():
    if is_ground_pounding: return
    if ground_pound_cooldown > 0: return  
    if is_on_ground: return
    if get_height_above_ground() < MIN_HEIGHT: return
    start_ground_pound()
```
✅ Prevents bounce spam specifically
✅ Contextual validation
✅ User feedback for why ability unavailable
✅ Skill-based mechanics (height requirement)

🎮 ENHANCED MECHANICS BREAKDOWN:

**Height Requirement System:**
- Calculates distance to nearest platform below
- Prevents ground pound when too close to ground
- Eliminates the bounce spam glitch
- Provides clear feedback to player

**Jump Buffering System:**
- Allows SPACE input slightly before impact
- Creates "super bounce" effect (1.5x height)
- Rewards precise timing
- Enhances skill ceiling

**Directional Momentum System:**
- Reads directional input during impact
- Applies momentum in held direction
- Caps maximum momentum to prevent exploitation
- Adds horizontal movement options

**Screen Shake Feedback:**
- Triggers on ground pound impact
- Provides tactile feedback
- Enhances sense of impact
- Multiple implementation approaches available

🔍 DEBUGGING AND VALIDATION TECHNIQUES:

**Height Calculation Methods:**
1. **Raycast Downward (Current)**:
   - Cast ray from player position downward
   - Find intersection with nearest platform
   - Most accurate for complex level geometry

2. **Track Last Ground Position**:
   - Remember Y position when last on ground
   - Calculate difference from current position
   - Faster but less accurate with moving platforms

3. **Spatial Partitioning Lookup**:
   - Pre-divide world into grid cells
   - Look up platforms in cells below player
   - Best performance for large numbers of platforms

**Input Validation Patterns:**
```python
# Pattern 1: Early Return Validation (Current)
def try_ability():
    if condition1: return
    if condition2: return
    if condition3: return
    execute_ability()

# Pattern 2: Boolean Chain Validation
def try_ability():
    if condition1 and condition2 and condition3:
        execute_ability()

# Pattern 3: Exception-Based Validation
def try_ability():
    try:
        validate_condition1()
        validate_condition2()
        validate_condition3()
        execute_ability()
    except InvalidConditionError as e:
        provide_feedback(e)
```

🎯 GAME FEEL ENHANCEMENT TECHNIQUES:

**Screen Shake Implementation:**
- Random offset approach (current - simple)
- Sine wave oscillation (smoother)
- Physics-based spring system (realistic)
- Curve-based animation (most control)

**Visual Feedback Layers:**
1. Sprite animation changes
2. Color tinting during abilities
3. Squash and stretch effects
4. Screen shake for impacts
5. UI status indicators

**Audio Integration Points** (for future enhancement):
- Ground pound initiation sound
- Impact sound with pitch variation
- Super bounce audio cue
- Directional momentum swoosh

🔧 PERFORMANCE CONSIDERATIONS:

**Height Calculation Optimization:**
- Cache platform positions in spatial grid
- Only check platforms in relevant cells
- Use broad-phase collision detection
- Limit raycast steps for performance

**State Management Efficiency:**
- Group related timers in structures
- Use bitfields for boolean states
- Minimize memory allocations per frame
- Cache frequently calculated values

🚀 EXTENSION POSSIBILITIES:

**Additional Ground Pound Mechanics:**
- Charged ground pound (hold longer = stronger)
- Area of effect damage on impact
- Platform destruction capabilities
- Chain ground pounds with increasing power

**Combo System Integration:**
- Ground pound -> dash combos
- Aerial ability sequences
- Timing-based bonus multipliers
- Style points for complex maneuvers

**Environmental Interactions:**
- Different effects on different surface types
- Breakable platforms
- Bouncy surfaces with modified physics
- Secret areas accessible via ground pound

Remember: Complex mechanics require careful tuning and extensive playtesting!
The best implementation balances complexity with intuitive player understanding.
"""

if __name__ == "__main__":
    main()