# -*- coding: utf-8 -*-
"""
德州扑克3 - 专业手游版
基于Kivy框架的移动端优化版本
支持Android APK构建
"""

import kivy
kivy.require('2.2.1')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (
    NumericProperty, StringProperty, ListProperty, 
    BooleanProperty, ObjectProperty
)
from kivy.config import Config

import random
import math
from enum import Enum
from collections import defaultdict

# 导入音效管理器
from sound_manager import SoundManager, GameSounds
# 导入设置界面
from settings_screen import SettingsPopup, HelpPopup
# 导入动画效果
from ui_animations import AnimationManager, ParticleEffect
# 导入屏幕适配器
from screen_adapter import screen_adapter

# ==============================================
# 游戏常量定义
# ==============================================

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦" 
    CLUBS = "♣"
    SPADES = "♠"

class Rank(Enum):
    TWO = ("2", 2)
    THREE = ("3", 3)
    FOUR = ("4", 4)
    FIVE = ("5", 5)
    SIX = ("6", 6)
    SEVEN = ("7", 7)
    EIGHT = ("8", 8)
    NINE = ("9", 9)
    TEN = ("10", 10)
    JACK = ("J", 11)
    QUEEN = ("Q", 12)
    KING = ("K", 13)
    ACE = ("A", 14)
    
    @property
    def symbol(self):
        return self.value[0]
    
    @property
    def value_num(self):
        return self.value[1]

class HandType(Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

# 颜色定义
COLORS = {
    'bg': (0.06, 0.08, 0.12, 1),           # 背景
    'table': (0.1, 0.27, 0.16, 1),        # 牌桌
    'table_border': (0.18, 0.35, 0.22, 1),
    'player_card': (0.14, 0.16, 0.22, 1), # 玩家卡片
    'player_card_active': (0.22, 0.24, 0.3, 1),
    'text_white': (0.96, 0.96, 0.98, 1),
    'text_gray': (0.7, 0.73, 0.78, 1),
    'text_gold': (1.0, 0.84, 0.0, 1),
    'text_green': (0.31, 0.86, 0.47, 1),
    'text_red': (1.0, 0.35, 0.35, 1),
    'text_blue': (0.35, 0.67, 1.0, 1),
    'chip_gold': (1.0, 0.84, 0.0, 1),
    'pot_gold': (1.0, 0.88, 0.24, 1),
    'btn_green': (0.27, 0.75, 0.31, 1),
    'btn_red': (0.9, 0.31, 0.31, 1),
    'btn_blue': (0.31, 0.59, 0.9, 1),
    'btn_yellow': (0.9, 0.75, 0.24, 1),
    'btn_gray': (0.39, 0.43, 0.51, 1),
    'card_red': (0.86, 0.24, 0.24, 1),
    'card_black': (0.16, 0.16, 0.16, 1),
    'card_face': (0.98, 0.98, 0.98, 1),
    'card_back': (0.31, 0.12, 0.12, 1),
    'status_bar': (0.1, 0.12, 0.16, 1),
}

# ==============================================
# 扑克牌类
# ==============================================

class Card:
    """扑克牌类"""
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self.face_up = True
        
    def __str__(self):
        return f"{self.rank.symbol}{self.suit.value}"
    
    def __repr__(self):
        return self.__str__()
    
    def get_color(self):
        """获取花色颜色"""
        return COLORS['card_red'] if self.suit in [Suit.HEARTS, Suit.DIAMONDS] else COLORS['card_black']
    
    def get_symbol(self):
        """获取显示符号"""
        return self.suit.value

# ==============================================
# 牌桌类
# ==============================================

class PokerTable:
    """牌桌类"""
    def __init__(self):
        self.pot = 0
        self.current_bet = 0
        self.small_blind = 100
        self.big_blind = 200
        self.community_cards = []
        self.deck = self._create_deck()
    
    def _create_deck(self):
        """创建一副牌"""
        deck = []
        for suit in Suit:
            for rank in Rank:
                deck.append(Card(suit, rank))
        random.shuffle(deck)
        return deck
    
    def reset_deck(self):
        """重置牌堆"""
        self.deck = self._create_deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
    
    def deal_card(self):
        """发一张牌"""
        if len(self.deck) == 0:
            self.reset_deck()
        return self.deck.pop()
    
    def deal_community(self, count):
        """发公共牌"""
        cards = []
        for _ in range(count):
            cards.append(self.deal_card())
        self.community_cards.extend(cards)
        return cards

# ==============================================
# 玩家类
# ==============================================

class Player:
    """玩家类"""
    def __init__(self, name, is_human=False, chips=1000):
        self.name = name
        self.is_human = is_human
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
        self.position = 0
        self.is_active = False
    
    def reset_hand(self):
        """重置手牌状态"""
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
        self.is_active = False
    
    def bet(self, amount):
        """下注"""
        if amount >= self.chips:
            amount = self.chips
            self.all_in = True
        
        self.chips -= amount
        self.current_bet += amount
        return amount
    
    def fold(self):
        """弃牌"""
        self.folded = True
    
    def can_act(self):
        """是否可以行动"""
        return not self.folded and not self.all_in and self.chips > 0

# ==============================================
# 游戏逻辑类
# ==============================================

class TexasHoldemGame:
    """德州扑克游戏逻辑类"""
    def __init__(self):
        self.table = PokerTable()
        self.players = self._create_players()
        
        # 游戏状态
        self.game_state = "preflop"  # preflop, flop, turn, river, showdown, finished
        self.current_player_idx = 0
        self.is_hand_active = False
        self.winners = []
        
        # UI状态
        self.feedback = ""
        self.is_waiting = False
        self.wait_until = 0
        self.hand_count = 1
        
        # 开始游戏
        self.start_new_hand()
    
    def _create_players(self):
        """创建玩家"""
        players = []
        
        # 人类玩家（底部）
        human = Player("玩家", is_human=True, chips=10000)
        human.position = 4  # 底部位置
        
        # AI玩家
        ai_data = [
            ("AI玩家1", 5000),
            ("AI玩家2", 8000),
            ("AI玩家3", 6000),
            ("AI玩家4", 7000),
        ]
        
        for i, (name, chips) in enumerate(ai_data):
            player = Player(name, is_human=False, chips=chips)
            player.position = i
            players.append(player)
        
        # 将人类玩家添加到末尾（底部位置）
        players.append(human)
        
        return players
    
    def start_new_hand(self):
        """开始新的一手牌"""
        self.table.reset_deck()
        self.game_state = "preflop"
        self.current_player_idx = 0
        self.winners = []
        self.feedback = ""
        self.is_waiting = False
        
        # 重置玩家状态
        for player in self.players:
            player.reset_hand()
            # 发两张手牌
            player.hand = [self.table.deal_card(), self.table.deal_card()]
            # 人类玩家手牌正面，AI玩家背面
            player.hand[0].face_up = player.is_human
            player.hand[1].face_up = player.is_human
        
        # 下盲注
        self._post_blinds()
        
        self.is_hand_active = True
        self.hand_count += 1
    
    def _post_blinds(self):
        """下盲注（修正版）"""
        # 找到按钮位置（假设第一个玩家是按钮）
        button_position = 0
        
        # 小盲注：按钮后第一个玩家
        small_blind_position = (button_position + 1) % len(self.players)
        # 大盲注：小盲注后第一个玩家
        big_blind_position = (small_blind_position + 1) % len(self.players)
        
        # 下盲注
        small_blind_amount = min(self.players[small_blind_position].chips, self.table.small_blind)
        big_blind_amount = min(self.players[big_blind_position].chips, self.table.big_blind)
        
        self.players[small_blind_position].bet(small_blind_amount)
        self.players[big_blind_position].bet(big_blind_amount)
        
        self.table.pot = small_blind_amount + big_blind_amount
        self.table.current_bet = self.table.big_blind
        
        # 从大盲后开始行动
        self.current_player_idx = (big_blind_position + 1) % len(self.players)
    
    def handle_player_action(self, action):
        """处理玩家行动"""
        if not self.is_hand_active:
            return False
        
        player = self.players[self.current_player_idx]
        if not player.is_human:
            return False
        
        if action == "fold":
            player.fold()
            self.feedback = f"{player.name} 弃牌"
            self._advance_game()
            
        elif action == "check":
            if self.table.current_bet > player.current_bet:
                self.feedback = "不能过牌，需要跟注"
                return False
            else:
                self.feedback = f"{player.name} 过牌"
                self._advance_game()
                
        elif action == "call":
            call_amount = self.table.current_bet - player.current_bet
            if call_amount > 0:
                amount = player.bet(call_amount)
                self.table.pot += amount
                self.feedback = f"{player.name} 跟注 {amount:,}"
            else:
                self.handle_player_action("check")
                return True
                
            self._advance_game()
            
        elif action == "raise":
            # 简化加注：加注到当前下注的2倍
            raise_to = max(self.table.current_bet * 2, self.table.big_blind * 2)
            raise_amount = raise_to - player.current_bet
            
            if raise_amount > player.chips:
                return self.handle_player_action("all_in")
            
            amount = player.bet(raise_amount)
            self.table.pot += amount
            self.table.current_bet = raise_to
            self.feedback = f"{player.name} 加注到 {raise_to:,}"
            
            self._advance_game()
            
        elif action == "all_in":
            all_in_amount = player.chips
            amount = player.bet(all_in_amount)
            self.table.pot += amount
            if player.current_bet > self.table.current_bet:
                self.table.current_bet = player.current_bet
            
            self.feedback = f"{player.name} 全下 {all_in_amount:,}"
            self._advance_game()
        
        return True
    
    def _advance_game(self):
        """推进游戏到下一状态"""
        # 找到下一个可以行动的玩家
        start_idx = self.current_player_idx
        while True:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            player = self.players[self.current_player_idx]
            
            if player.can_act():
                break
            
            if self.current_player_idx == start_idx:
                # 所有玩家都已行动，进入下一阶段
                self._next_street()
                return
        
        # 如果是AI玩家，设置等待时间
        current_player = self.players[self.current_player_idx]
        if not current_player.is_human:
            self.is_waiting = True
            self.wait_until = Clock.get_time() + random.uniform(0.5, 1.5)
    
    def _next_street(self):
        """进入下一阶段"""
        if self.game_state == "preflop":
            self.game_state = "flop"
            self.table.deal_community(3)
            self.feedback = "翻牌发出"
            
        elif self.game_state == "flop":
            self.game_state = "turn"
            self.table.deal_community(1)
            self.feedback = "转牌发出"
            
        elif self.game_state == "turn":
            self.game_state = "river"
            self.table.deal_community(1)
            self.feedback = "河牌发出"
            
        elif self.game_state == "river":
            self.game_state = "showdown"
            self.feedback = "摊牌阶段"
            # 在摊牌阶段显示所有手牌
            for player in self.players:
                if not player.folded:
                    for card in player.hand:
                        card.face_up = True
            
            # 延迟一段时间后确定赢家
            self.is_waiting = True
            self.wait_until = Clock.get_time() + 2.0
            return
        
        # 重置下注轮
        self.table.current_bet = 0
        for player in self.players:
            player.current_bet = 0
        
        # 找到第一个未弃牌的玩家开始行动
        for i, player in enumerate(self.players):
            if not player.folded:
                self.current_player_idx = i
                break
    
    def _determine_winner(self):
        """确定赢家（简化版）"""
        active_players = [p for p in self.players if not p.folded]
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.table.pot
            self.winners = [winner]
        else:
            # 简化：随机选择一个赢家
            winner = random.choice(active_players)
            winner.chips += self.table.pot
            self.winners = [winner]
        
        # 显示所有手牌
        for player in self.players:
            for card in player.hand:
                card.face_up = True
        
        self.game_state = "finished"
        self.is_hand_active = False
        self.feedback = f"{self.winners[0].name} 赢得 {self.table.pot:,}"
        
        # 设置自动开始下一局的计时
        self.is_waiting = True
        self.wait_until = Clock.get_time() + 3
    
    def update(self, dt):
        """更新游戏逻辑"""
        current_time = Clock.get_time()
        
        # AI行动
        if self.is_hand_active and self.is_waiting and current_time > self.wait_until:
            player = self.players[self.current_player_idx]
            if not player.is_human:
                self._process_ai_action(player)
                self.is_waiting = False
        
        # showdown阶段处理
        if self.game_state == "showdown" and self.is_waiting and current_time > self.wait_until:
            self._determine_winner()
            self.is_waiting = False
        
        # 自动开始新手牌
        if self.game_state == "finished" and self.is_waiting and current_time > self.wait_until:
            self.start_new_hand()
    
    def _process_ai_action(self, player):
        """处理AI行动（智能版）"""
        if not player.can_act():
            return
        
        # 计算手牌强度
        hand_strength = self._calculate_hand_strength(player)
        
        # 考虑位置因素（按钮位置优势）
        position_factor = self._get_position_factor(player)
        
        # 考虑下注历史
        bet_history_factor = self._get_bet_history_factor()
        
        # 智能决策
        action = self._make_ai_decision(player, hand_strength, position_factor, bet_history_factor)
        
        # 执行AI行动
        if action == "fold":
            player.fold()
            self.feedback = f"{player.name} 弃牌"
        elif action == "check":
            if self.table.current_bet > player.current_bet:
                # 不能过牌则跟注
                call_amount = self.table.current_bet - player.current_bet
                if call_amount > 0:
                    amount = player.bet(call_amount)
                    self.table.pot += amount
                    self.feedback = f"{player.name} 跟注 {amount:,}"
                else:
                    self.feedback = f"{player.name} 过牌"
            else:
                self.feedback = f"{player.name} 过牌"
        elif action == "call":
            call_amount = self.table.current_bet - player.current_bet
            if call_amount > 0:
                amount = player.bet(call_amount)
                self.table.pot += amount
                self.feedback = f"{player.name} 跟注 {amount:,}"
            else:
                self.feedback = f"{player.name} 过牌"
        elif action == "raise":
            # 智能加注：根据手牌强度决定加注额度
            raise_multiplier = 1.5 + (hand_strength * 1.5)  # 1.5-3倍
            raise_to = max(self.table.current_bet * raise_multiplier, self.table.big_blind * 2)
            raise_amount = raise_to - player.current_bet
            
            if raise_amount > player.chips:
                # 加注额度超过筹码，改为全下
                all_in_amount = player.chips
                amount = player.bet(all_in_amount)
                self.table.pot += amount
                if player.current_bet > self.table.current_bet:
                    self.table.current_bet = player.current_bet
                self.feedback = f"{player.name} 全下 {all_in_amount:,}"
            else:
                amount = player.bet(raise_amount)
                self.table.pot += amount
                self.table.current_bet = raise_to
                self.feedback = f"{player.name} 加注到 {raise_to:,}"
        elif action == "all_in":
            all_in_amount = player.chips
            amount = player.bet(all_in_amount)
            self.table.pot += amount
            if player.current_bet > self.table.current_bet:
                self.table.current_bet = player.current_bet
            self.feedback = f"{player.name} 全下 {all_in_amount:,}"
        
        self._advance_game()
    
    def _calculate_hand_strength(self, player):
        """计算手牌强度（0-1）"""
        # 简化版手牌强度计算
        ranks = [card.rank.value_num for card in player.hand]
        suits = [card.suit for card in player.hand]
        
        # 高牌
        max_rank = max(ranks)
        high_card_strength = (max_rank - 2) / 12.0  # 2-14映射到0-1
        
        # 对子
        pair_strength = 0
        if ranks[0] == ranks[1]:
            pair_strength = 0.3 + (max_rank - 2) / 12.0 * 0.3
        
        # 同花潜力
        flush_potential = 0
        if suits[0] == suits[1]:
            flush_potential = 0.2
        
        # 连牌潜力
        straight_potential = 0
        rank_diff = abs(ranks[0] - ranks[1])
        if rank_diff <= 4:
            straight_potential = 0.2 - (rank_diff * 0.05)
        
        return min(1.0, high_card_strength + pair_strength + flush_potential + straight_potential)
    
    def _get_position_factor(self, player):
        """获取位置优势因子"""
        # 按钮位置优势：越晚行动优势越大
        total_players = len(self.players)
        player_index = self.players.index(player)
        
        # 计算相对于按钮的位置
        button_distance = (player_index - self.current_player_idx) % total_players
        position_advantage = 1.0 - (button_distance / total_players)
        
        return position_advantage
    
    def _get_bet_history_factor(self):
        """获取下注历史因子"""
        # 计算当前下注轮的激进程度
        if self.table.current_bet == 0:
            return 0.0  # 无人下注
        
        # 下注额相对于大盲注的比例
        bet_aggressiveness = self.table.current_bet / self.table.big_blind
        
        return min(1.0, bet_aggressiveness / 5.0)  # 归一化到0-1
    
    def _make_ai_decision(self, player, hand_strength, position_factor, bet_history_factor):
        """智能决策"""
        # 基础决策权重
        base_weights = {
            "fold": 0.1,
            "check": 0.3,
            "call": 0.4,
            "raise": 0.15,
            "all_in": 0.05
        }
        
        # 根据手牌强度调整权重
        if hand_strength > 0.7:  # 强牌
            base_weights["fold"] = 0.01
            base_weights["raise"] = 0.4
            base_weights["all_in"] = 0.1
        elif hand_strength < 0.3:  # 弱牌
            base_weights["fold"] = 0.3
            base_weights["raise"] = 0.05
        
        # 根据位置调整权重
        if position_factor > 0.7:  # 有利位置
            base_weights["raise"] *= 1.5
            base_weights["check"] *= 1.2
        else:  # 不利位置
            base_weights["fold"] *= 1.3
            base_weights["call"] *= 0.8
        
        # 根据下注历史调整权重
        if bet_history_factor > 0.5:  # 激进的下注环境
            base_weights["fold"] *= 1.5
            base_weights["call"] *= 0.7
        
        # 筹码管理
        chip_ratio = player.chips / (self.table.big_blind * 10)  # 相对于10个大盲
        if chip_ratio < 0.5:  # 短筹码
            base_weights["all_in"] *= 2.0
            base_weights["fold"] *= 0.5
        elif chip_ratio > 3.0:  # 深筹码
            base_weights["raise"] *= 1.3
        
        # 归一化权重
        total = sum(base_weights.values())
        normalized_weights = {k: v/total for k, v in base_weights.items()}
        
        # 选择行动
        actions = list(normalized_weights.keys())
        weights = list(normalized_weights.values())
        
        return random.choices(actions, weights=weights)[0]

# ==============================================
# Kivy UI组件
# ==============================================

class PokerButton(Button):
    """扑克游戏按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = COLORS['btn_green']
        self.color = COLORS['text_white']
        self.font_size = screen_adapter.get_font_size(16)
        self.size_hint = (0.18, 0.08)  # 使用相对尺寸，确保最小触摸目标
        
        # 确保最小触摸目标为44x44像素
        min_width = max(self.size_hint[0] * Window.width, 44)
        min_height = max(self.size_hint[1] * Window.height, 44)
        self.size_hint = (min_width / Window.width, min_height / Window.height)

class CardWidget(Widget):
    """卡牌显示组件"""
    card = ObjectProperty(None)
    
    def __init__(self, card, **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.size_hint = (None, None)
        # 使用屏幕比例计算卡牌尺寸
        self.width = Window.width * 0.08  # 屏幕宽度的8%
        self.height = self.width * 1.4   # 标准卡牌比例
    
    def on_card(self, instance, value):
        self.canvas.clear()
        with self.canvas:
            if self.card.face_up:
                # 绘制卡牌正面
                Color(*COLORS['card_face'])
                Rectangle(pos=self.pos, size=self.size)
                
                # 边框
                Color(0.2, 0.2, 0.2, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
                
                # 花色和点数
                card_color = self.card.get_color()
                Color(*card_color)
                
                # 左上角点数
                points_label = Label(text=self.card.rank.symbol, font_size='14sp')
                points_label.texture_update()
                self.canvas.add(points_label.canvas)
                
                # 中间花色
                suit_label = Label(text=self.card.suit.value, font_size='24sp')
                suit_label.texture_update()
                self.canvas.add(suit_label.canvas)
                
            else:
                # 绘制卡牌背面
                Color(*COLORS['card_back'])
                Rectangle(pos=self.pos, size=self.size)
                
                # 边框
                Color(0.16, 0.06, 0.06, 1)
                Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
                
                # 背面图案
                Color(0.63, 0.16, 0.16, 1)
                Ellipse(pos=(self.center_x - 15, self.center_y - 15), size=(30, 30))

class PlayerCardUI(BoxLayout):
    """玩家信息卡片"""
    player = ObjectProperty(None)
    is_active = BooleanProperty(False)
    
    def __init__(self, player, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        
        # 使用屏幕适配器获取尺寸
        layout_config = screen_adapter.get_optimal_layout_config()
        self.width = layout_config['player_card_width']
        self.height = layout_config['player_card_height']
        
        self.padding = [10, 5]
        self.spacing = 2
        
        self.background_color = COLORS['player_card_active'] if self.is_active else COLORS['player_card']
        
        # 玩家名字（确保可读性）
        name_label = Label(
            text=player.name[:6] + "..." if len(player.name) > 6 else player.name,
            color=COLORS['text_white'] if not player.folded else COLORS['text_gray'],
            font_size=screen_adapter.get_font_size(14),
            text_size=(self.width - 20, None),
            halign='center'
        )
        self.add_widget(name_label)
        
        # 筹码数量
        chips_label = Label(
            text=f"{player.chips:,}",
            color=COLORS['chip_gold'],
            font_size=screen_adapter.get_font_size(16),
            text_size=(self.width - 20, None),
            halign='center'
        )
        self.add_widget(chips_label)
        
        # 当前下注
        if player.current_bet > 0:
            bet_label = Label(
                text=f"下注: {player.current_bet:,}",
                color=COLORS['text_gold'],
                font_size=screen_adapter.get_font_size(12),
                text_size=(self.width - 20, None),
                halign='center'
            )
            self.add_widget(bet_label)
        
        # 状态指示
        status_text = ""
        if player.folded:
            status_text = "弃牌"
        elif player.all_in:
            status_text = "全下"
        
        if status_text:
            status_label = Label(
                text=status_text,
                color=COLORS['text_red'] if player.folded else COLORS['text_gold'],
                font_size=screen_adapter.get_font_size(10),
                text_size=(self.width - 20, None),
                halign='center'
            )
            self.add_widget(status_label)

class PokerGameWidget(BoxLayout):
    """主游戏界面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.game = TexasHoldemGame()
        
        # 获取屏幕适配配置
        layout_config = screen_adapter.get_optimal_layout_config()
        
        # 状态栏
        self.status_bar = BoxLayout(size_hint=(1, layout_config['status_bar_height'] / Window.height))
        self.status_bar.background_color = COLORS['status_bar']
        
        title_label = Label(
            text="德州扑克3",
            color=COLORS['text_white'],
            font_size=screen_adapter.get_font_size(24)
        )
        self.status_bar.add_widget(title_label)
        
        hand_label = Label(
            text=f"牌局 #{self.game.hand_count}",
            color=COLORS['text_gray'],
            font_size=screen_adapter.get_font_size(14)
        )
        self.status_bar.add_widget(hand_label)
        
        self.add_widget(self.status_bar)
        
        # 游戏区域
        self.game_area = FloatLayout(size_hint=(1, layout_config['game_area_height'] / Window.height))
        self.add_widget(self.game_area)
        
        # 操作按钮区域
        self.button_area = BoxLayout(
            size_hint=(1, layout_config['button_area_height'] / Window.height), 
            padding=[20, 10]
        )
        self._create_buttons()
        self.add_widget(self.button_area)
        
        # 绑定窗口大小变化事件
        Window.bind(on_resize=self._on_window_resize)
        
        # 更新游戏逻辑（降低频率到30FPS，节省性能）
        Clock.schedule_interval(self.game.update, 1.0/30.0)
        Clock.schedule_interval(self.update_display, 1.0/30.0)
        
        # 性能优化：避免频繁重绘
        self._last_display_time = 0
        self._display_interval = 1.0/30.0  # 30FPS
    
    def _on_window_resize(self, window, width, height):
        """窗口大小变化处理"""
        # 重新布局界面
        self._update_layout()
    
    def _update_layout(self):
        """更新布局"""
        # 获取新的布局配置
        layout_config = screen_adapter.get_optimal_layout_config()
        
        # 更新状态栏高度
        self.status_bar.size_hint = (1, layout_config['status_bar_height'] / Window.height)
        
        # 更新游戏区域高度
        self.game_area.size_hint = (1, layout_config['game_area_height'] / Window.height)
        
        # 更新按钮区域高度
        self.button_area.size_hint = (1, layout_config['button_area_height'] / Window.height)
        
        # 强制刷新界面
        self.update_display(0)
    
    def _create_buttons(self):
        """创建操作按钮"""
        actions = [
            ("弃牌", "fold", "red"),
            ("过牌", "check", "blue"),
            ("跟注", "call", "green"),
            ("加注", "raise", "yellow"),
            ("全下", "all_in", "blue")
        ]
        
        # 增加按钮间距，防止误触
        self.button_area.spacing = 10
        
        for text, action, color in actions:
            btn = PokerButton(text=text)
            btn.background_color = COLORS[f'btn_{color}']
            btn.bind(on_press=lambda instance, act=action: self.on_button_press(act))
            self.button_area.add_widget(btn)
    
    def on_button_press(self, action):
        """按钮点击处理"""
        self.game.handle_player_action(action)
    
    def update_display(self, dt):
        """更新显示（性能优化版）"""
        current_time = Clock.get_time()
        
        # 性能优化：只在必要时重绘
        if current_time - self._last_display_time < self._display_interval:
            return
        
        self._last_display_time = current_time
        
        # 清除游戏区域
        self.game_area.clear_widgets()
        
        # 绘制牌桌
        self._draw_table()
        
        # 绘制底池
        self._draw_pot()
        
        # 绘制公共牌
        self._draw_community_cards()
        
        # 绘制玩家卡片
        self._draw_player_cards()
        
        # 绘制反馈信息
        self._draw_feedback()
        
        # 绘制赢家信息
        if self.game.game_state == "finished":
            self._draw_winner_overlay()
    
    def _draw_table(self):
        """绘制牌桌"""
        table_width = self.game_area.width * 0.7  # 牌桌宽度为游戏区域的70%
        table_height = table_width * 0.8  # 牌桌高度为宽度的80%
        
        with self.game_area.canvas:
            Color(*COLORS['table'])
            Ellipse(
                pos=(
                    self.game_area.center_x - table_width/2, 
                    self.game_area.center_y - table_height/2
                ),
                size=(table_width, table_height)
            )
    
    def _draw_pot(self):
        """绘制底池"""
        pot_width = self.game_area.width * 0.4  # 底池宽度为游戏区域的40%
        pot_height = pot_width * 0.3  # 高度为宽度的30%
        
        pot_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(pot_width, pot_height),
            pos=(
                self.game_area.center_x - pot_width/2, 
                self.game_area.center_y - pot_height/2
            )
        )
        
        pot_label = Label(
            text="底池",
            color=COLORS['text_gold'],
            font_size='2.5%'  # 使用百分比字体
        )
        
        pot_amount = Label(
            text=f"{self.game.table.pot:,}",
            color=COLORS['pot_gold'],
            font_size='3.5%'  # 使用百分比字体
        )
        
        pot_layout.add_widget(pot_label)
        pot_layout.add_widget(pot_amount)
        self.game_area.add_widget(pot_layout)
    
    def _draw_community_cards(self):
        """绘制公共牌"""
        if not self.game.table.community_cards:
            return
        
        # 根据屏幕尺寸计算布局
        card_width = self.game_area.width * 0.08  # 卡牌宽度
        card_height = card_width * 1.4  # 卡牌高度
        layout_width = card_width * 5 + 20  # 5张卡牌加间距
        layout_height = card_height
        
        cards_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(layout_width, layout_height),
            pos=(
                self.game_area.center_x - layout_width/2, 
                self.game_area.center_y + self.game_area.height * 0.1
            )
        )
        
        for card in self.game.table.community_cards:
            card_widget = CardWidget(card=card)
            cards_layout.add_widget(card_widget)
        
        self.game_area.add_widget(cards_layout)
    
    def _draw_player_cards(self):
        """绘制玩家卡片"""
        # 使用屏幕适配器获取玩家位置
        positions = screen_adapter.get_player_positions(self.game_area)
        
        for i, (x, y) in enumerate(positions):
            if i < len(self.game.players):
                player = self.game.players[i]
                ui_card = PlayerCardUI(player=player)
                ui_card.pos = (x, y)
                
                # 标记当前行动玩家
                ui_card.is_active = (i == self.game.current_player_idx)
                
                self.game_area.add_widget(ui_card)
    
    def _draw_feedback(self):
        """绘制反馈信息"""
        if self.game.feedback:
            feedback_width = self.game_area.width * 0.8
            feedback_height = self.game_area.height * 0.05
            
            feedback_label = Label(
                text=self.game.feedback,
                color=COLORS['text_white'],
                font_size='2%',  # 使用百分比字体
                size_hint=(None, None),
                size=(feedback_width, feedback_height),
                pos=(
                    self.game_area.center_x - feedback_width/2, 
                    self.game_area.y + feedback_height * 0.5
                )
            )
            self.game_area.add_widget(feedback_label)
    
    def _draw_winner_overlay(self):
        """绘制赢家覆盖层"""
        if not self.game.winners:
            return
        
        overlay = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1)
        )
        overlay.background_color = (0, 0, 0, 0.7)
        
        # 使用相对尺寸计算赢家框大小
        winner_width = self.game_area.width * 0.6
        winner_height = winner_width * 0.5
        
        winner_box = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(winner_width, winner_height),
            pos=(
                self.game_area.center_x - winner_width/2, 
                self.game_area.center_y - winner_height/2
            )
        )
        
        winner_title = Label(
            text="牌局结束!",
            color=COLORS['text_white'],
            font_size='3%'  # 使用百分比字体
        )
        
        winner_name = Label(
            text=self.game.winners[0].name,
            color=COLORS['text_green'],
            font_size='3.5%'  # 使用百分比字体
        )
        
        win_text = Label(
            text="赢得底池",
            color=COLORS['text_gray'],
            font_size='2.5%'  # 使用百分比字体
        )
        
        pot_amount = Label(
            text=f"{self.game.table.pot:,}",
            color=COLORS['pot_gold'],
            font_size='4%'  # 使用百分比字体
        )
        
        countdown = Label(
            text="3秒后开始新牌局...",
            color=COLORS['text_blue'],
            font_size='2%'  # 使用百分比字体
        )
        
        winner_box.add_widget(winner_title)
        winner_box.add_widget(winner_name)
        winner_box.add_widget(win_text)
        winner_box.add_widget(pot_amount)
        winner_box.add_widget(countdown)
        
        overlay.add_widget(winner_box)
        self.game_area.add_widget(overlay)

# ==============================================
# 主应用类
# ==============================================

class TexasHoldem3App(App):
    """德州扑克3主应用"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "德州扑克3"
    
    def build(self):
        """构建应用界面"""
        # 移动端优化配置
        self._configure_for_mobile()
        
        return PokerGameWidget()
    
    def _configure_for_mobile(self):
        """移动端配置"""
        # 设置默认窗口大小（竖屏优化）
        Window.size = (720, 1280)
        
        # 设置最小尺寸限制，确保游戏可玩性
        Window.minimum_width = 360  # 最小宽度，适应小屏手机
        Window.minimum_height = 640  # 最小高度
        
        # 启用多点触控（移动端触摸支持）
        Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
        
        # 强制竖屏模式（德州扑克游戏通常固定竖屏）
        screen_adapter.force_portrait_mode()
        
        # 允许窗口调整大小（开发测试用）
        Config.set('graphics', 'resizable', 1)
        
        # 设置DPI缩放，适应不同分辨率
        Config.set('graphics', 'dpi', 96)
        
        # 优化触摸体验
        Config.set('postproc', 'retain_time', 50)
        Config.set('postproc', 'retain_distance', 10)
        
        print("移动端配置完成")
        print(f"窗口尺寸: {Window.size}")
        print(f"屏幕方向: {'竖屏' if screen_adapter.is_portrait else '横屏'}")
        print(f"适配范围: {Window.minimum_width}x{Window.minimum_height} 到 全屏")
        
        # 显示适配信息
        layout_config = screen_adapter.get_optimal_layout_config()
        print(f"布局配置: 状态栏{layout_config['status_bar_height']:.0f}px, "
              f"游戏区域{layout_config['game_area_height']:.0f}px, "
              f"卡牌{layout_config['card_width']:.0f}px")

# ==============================================
# 程序入口
# ==============================================

if __name__ == '__main__':
    print("德州扑克3 - 专业手游版")
    print("=" * 50)
    print("游戏特点:")
    print("  1. 基于Kivy框架的移动端优化")
    print("  2. 5人桌德州扑克")
    print("  3. 完整的游戏流程")
    print("  4. 支持Android APK构建")
    print("=" * 50)
    
    TexasHoldem3App().run()