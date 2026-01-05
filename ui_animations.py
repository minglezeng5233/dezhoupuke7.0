# -*- coding: utf-8 -*-
"""
德州扑克3 - 界面动画效果
增强游戏视觉效果和用户体验
"""

from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock
import random

class AnimationManager:
    """动画管理器"""
    
    def __init__(self):
        self.animations = {}
    
    def fade_in(self, widget, duration=0.5):
        """淡入动画"""
        widget.opacity = 0
        anim = Animation(opacity=1, duration=duration)
        anim.start(widget)
    
    def fade_out(self, widget, duration=0.5):
        """淡出动画"""
        anim = Animation(opacity=0, duration=duration)
        anim.start(widget)
    
    def slide_in(self, widget, direction='left', duration=0.5):
        """滑动进入动画"""
        original_pos = widget.pos[:]
        
        if direction == 'left':
            widget.pos = (-widget.width, widget.y)
        elif direction == 'right':
            widget.pos = (widget.parent.width, widget.y)
        elif direction == 'top':
            widget.pos = (widget.x, widget.parent.height)
        elif direction == 'bottom':
            widget.pos = (widget.x, -widget.height)
        
        anim = Animation(pos=original_pos, duration=duration)
        anim.start(widget)
    
    def bounce(self, widget, scale=1.2, duration=0.3):
        """弹跳动画"""
        original_scale = widget.scale
        
        anim = Animation(scale=scale, duration=duration/2) + \
               Animation(scale=original_scale, duration=duration/2)
        anim.start(widget)
    
    def shake(self, widget, intensity=10, duration=0.3):
        """震动动画"""
        original_pos = widget.pos[:]
        
        def shake_step(dt):
            widget.pos = (
                original_pos[0] + random.randint(-intensity, intensity),
                original_pos[1] + random.randint(-intensity, intensity)
            )
        
        def reset_pos(dt):
            widget.pos = original_pos
        
        Clock.schedule_interval(shake_step, 0.05)
        Clock.schedule_once(lambda dt: Clock.unschedule(shake_step), duration)
        Clock.schedule_once(reset_pos, duration)
    
    def pulse(self, widget, min_opacity=0.5, max_opacity=1.0, duration=1.0):
        """脉动动画"""
        anim = (
            Animation(opacity=max_opacity, duration=duration/2) + 
            Animation(opacity=min_opacity, duration=duration/2)
        )
        anim.repeat = True
        anim.start(widget)
    
    def deal_card_animation(self, card_widget, target_pos, duration=0.8):
        """发牌动画"""
        # 保存原始位置
        original_pos = card_widget.pos[:]
        
        # 移动动画
        anim = Animation(
            pos=target_pos,
            duration=duration,
            transition='out_back'
        )
        
        # 旋转动画（如果牌是背面）
        if not card_widget.card.face_up:
            anim &= Animation(rotation_y=360, duration=duration)
        
        anim.start(card_widget)
        
        return anim
    
    def chip_drop_animation(self, widget, target_pos, duration=0.5):
        """筹码掉落动画"""
        # 抛物线动画
        anim = Animation(
            pos=target_pos,
            duration=duration,
            transition='out_bounce'
        )
        anim.start(widget)
        
        return anim

class ParticleEffect(Widget):
    """粒子效果"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (10, 10)
        self.particles = []
    
    def create_confetti(self, count=20, duration=2.0):
        """创建五彩纸屑效果"""
        colors = [
            (1, 0, 0, 1),    # 红色
            (0, 1, 0, 1),    # 绿色  
            (0, 0, 1, 1),    # 蓝色
            (1, 1, 0, 1),    # 黄色
            (1, 0, 1, 1),    # 紫色
        ]
        
        for i in range(count):
            particle = Widget()
            particle.size = (random.randint(5, 15), random.randint(5, 15))
            particle.pos = (
                self.center_x - particle.width/2,
                self.center_y - particle.height/2
            )
            particle.color = random.choice(colors)
            
            # 粒子运动
            anim = Animation(
                x=particle.x + random.randint(-100, 100),
                y=particle.y + random.randint(50, 150),
                rotation=random.randint(0, 360),
                duration=duration * random.uniform(0.8, 1.2)
            )
            anim.start(particle)
            
            self.particles.append(particle)
            self.add_widget(particle)
        
        # 清理粒子
        Clock.schedule_once(self._clear_particles, duration + 0.5)
    
    def _clear_particles(self, dt):
        """清理粒子"""
        for particle in self.particles:
            self.remove_widget(particle)
        self.particles.clear()

class CardFlipAnimation:
    """卡牌翻转动画"""
    
    def __init__(self):
        pass
    
    def flip_card(self, card_widget, duration=0.6):
        """翻转卡牌"""
        # 翻转动画
        anim1 = Animation(rotation_y=90, duration=duration/2)
        anim2 = Animation(rotation_y=0, duration=duration/2)
        
        def flip_face(dt):
            card_widget.card.face_up = not card_widget.card.face_up
        
        anim1.bind(on_complete=lambda *args: Clock.schedule_once(flip_face, 0))
        anim = anim1 + anim2
        anim.start(card_widget)
        
        return anim

class ProgressBar(Widget):
    """进度条组件"""
    
    progress = NumericProperty(0)  # 0-1
    color = ListProperty([0.2, 0.6, 0.8, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(progress=self._update_display)
    
    def _update_display(self, instance, value):
        """更新显示"""
        self.canvas.clear()
        with self.canvas:
            # 背景
            Color(0.3, 0.3, 0.3, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # 进度
            Color(*self.color)
            progress_width = self.width * self.progress
            Rectangle(pos=self.pos, size=(progress_width, self.height))
            
            # 边框
            Color(0.1, 0.1, 0.1, 1)
            Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
    
    def animate_progress(self, target_progress, duration=1.0):
        """动画进度"""
        anim = Animation(progress=target_progress, duration=duration)
        anim.start(self)
        
        return anim