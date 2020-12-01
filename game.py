import os
import re
import json
import random

from person import Person, Player, Robot, People
from card import Card, Cards, AllCards
from message import MessageGetter, MessagePoster, GameExiter


class Game:
	"""一局游戏"""

	def __init__(self):
		self.initialized = False
		MessagePoster.post_hint(hint_type='welcome')
		self.enter()
		self.game_credits = None
		self.all_cards = AllCards()
		self.initialized = True

	def enter(self, default_player_credits=100):
		user_name = MessageGetter.get_order(order_type='user_name')
		if isinstance(user_name, GameExiter):
			self.exit()

		## 数据文件不存在时, 直接新建数据
		if os.path.exists(f'{user_name}.json'):
			try:
				with open(f'{user_name}.json') as f:
					user_profile = json.load(f)

				## 当数据文件合法时, 询问玩家是否覆盖数据
				## 如果覆盖, 则重置积分
				if user_profile['user_name'] == user_name and isinstance(user_profile['credits'], int):
					while True:
						overload_data_order = MessageGetter.get_order(order_type='overload_data')
						if isinstance(overload_data_order, GameExiter):
							self.exit()
							continue
						else:
							break
					if overload_data_order == 'y':
						credits = default_player_credits
					else:
						credits = user_profile['credits']
				else:
					raise ValueError
			except Exception as e:
				MessagePoster.post_hint(hint_type='overload_broken_data')

		else:
			credits = default_player_credits

		player = Player(name=user_name, credits=credits)
		robot1 = Robot(name='robot1')
		robot2 = Robot(name='robot2')
		self.people = People(player, robot1, robot2)

	def reset(self):
		self.game_credits = None
		self.all_cards.shuffle()

		## 重置每个人的身份和牌
		person = self.people.head
		for i in range(3):
			person.reset_profile()
			person = person.next

	def double_game_credits(self):
		self.game_credits *= 2

	def send_cards(self):
		"""发牌"""

		MessagePoster.post_hint(hint_type='new_game')
		MessagePoster.post_hint(hint_type='start_sending_cards')
		person = self.people.head
		for i in range(3):
			unsent_cards = self.all_cards.give_cards(17)
			person.take_cards(unsent_cards)
			person = person.next

	def send_landlord_cards(self, landlord):
		unsent_cards = self.all_cards.give_cards(3)
		landlord.take_cards(unsent_cards)

	def decide_landlord(self):

		## 先给玩家看一下自己的牌
		person = self.people.get_player()
		MessagePoster.post_hint(hint_type='player_show_cards', unshowed_cards=str(person.cards))

		## 展示地主应得的3张底牌
		MessagePoster.post_hint(hint_type='show_landlord_cards', landlord_cards=str(self.all_cards))

		## 叫地主的次数
		decision_cnt = 0

		## 跳过的次数, 跳过2次后, 下一个人就是赢家
		pass_cnt = 0

		person = self.people.head
		last_landlord_score = 0

		## 两轮都没能确定地主后, 随机决定地主
		while decision_cnt / 3 < 2:
			landlord_score = person.deal_landlord_score(last_landlord_score)

			if isinstance(landlord_score, GameExiter):
				self.exit()
				continue

			if landlord_score == 3:
				last_landlord_score = landlord_score
				break
			elif landlord_score is None:

				## 只有有人叫过地主时, pass_cnt才有效
				if last_landlord_score > 0:
					pass_cnt += 1

					## 此时下一个人是地主
					if pass_cnt == 2:
						person = person.next
						break

			## 此时意味着叫了地主, 但是没到3分
			else:
				pass_cnt = 0
				last_landlord_score = landlord_score

			person = person.next
			decision_cnt += 1
		
		## 随机决定地主
		else:
			MessagePoster.post_hint(hint_type='system_will_decide_landlord_randomly')
			choice_steps = random.randint(0, 3)
			for i in range(choice_steps):
				person = person.next

			## 如果没人叫过地主, 则设置地主分为1分
			if last_landlord_score == 0:
				last_landlord_score = 1

		## 对每个人设置身份
		person.set_identity('landlord')
		person.next.set_identity('peasant')
		person.next.next.set_identity('peasant')

		## 把3张底牌给地主
		self.send_landlord_cards(person)

		## 如果地主是玩家, 给玩家看一下现有的牌
		if person.is_real:
			MessagePoster.post_hint(hint_type='player_show_cards', unshowed_cards=str(person.cards))

		## 设置地主先出牌
		self.people.set_head(person)

		## 最终的地主分数就是该局的分数
		self.game_credits = last_landlord_score

		## 宣布地主以及本局的分数
		MessagePoster.post_hint(
			hint_type='announce_landlord', 
			landlord_name=person.output_name, 
			peasant1_name=person.next.output_name, 
			peasant2_name=person.next.next.output_name
		)
		MessagePoster.post_hint(hint_type='announce_game_credits', game_credits=str(self.game_credits))	

	def deal_cards(self):
		person = self.people.head
		last_cards = None
		last_person_identity = None
		pass_cnt = 0

		## 提示游戏正式开始
		MessagePoster.post_hint(hint_type='formly_start_game')	

		## 开始出牌
		while True:

			## 新的一轮牌
			if last_cards is None:
				MessagePoster.post_hint(hint_type='new_round')

			dealed_cards = person.deal_cards(last_cards, last_person_identity)

			if isinstance(dealed_cards, GameExiter):
				self.exit()
				continue
			elif dealed_cards is None:
				pass_cnt += 1
				if pass_cnt == 2:
					last_cards = None
					last_person_identity = None
			else:
				last_cards = dealed_cards
				last_person_identity = person.identity
				pass_cnt = 0

				## 炸弹使积分翻倍
				if dealed_cards.is_bumb():
					MessagePoster.post_hint(hint_type='double_game_credits', output_name=person.output_name)
					self.double_game_credits()

				## 牌空说明有人出完了牌
				if person.cards.is_empty():
					break
			person = person.next

		## 将赢家设置为链表的头
		self.people.set_head(person)

	def check_results(self):

		## 把赢家找出来
		person = self.people.head

		## 宣布胜利者并计分
		if person.is_real:
			if person.identity == 'landlord':
				MessagePoster.post_hint(hint_type='win_as_landlord')
			else:
				MessagePoster.post_hint(hint_type='win_as_peasant1')
		elif person.identity == 'landlord':
			MessagePoster.post_hint(hint_type='lose_as_peasant')
		elif (person.next.is_real and person.next.identity == 'peasant') or \
		(person.next.next.is_real and person.next.next.identity == 'peasant'):
			MessagePoster.post_hint(hint_type='win_as_peasant2')
		else:
			MessagePoster.post_hint(hint_type='lose_as_landlord')

		## 计分
		if person.identity == 'landlord':
			person.change_credits(self.game_credits * 2)
			person.next.change_credits(-self.game_credits)
			person.next.next.change_credits(-self.game_credits)
		else:
			person.change_credits(self.game_credits)
			if person.next.identity == 'landlord':
				person.next.change_credits(-2 * self.game_credits)
				person.next.next.change_credits(self.game_credits)
			else:
				person.next.change_credits(self.game_credits)
				person.next.next.change_credits(-2 * self.game_credits)

	def show_credit_board(self):

		## 用户名左右的空格数
		empty_space_length = 4

		## 最长用户名的长度, 供后面对齐时用
		max_name_length = self.people.max_name_length

		## 标题与内容的分割线
		## 3代表' | ', 5代表'xx分'
		title_line = f'{"-" * (max_name_length + empty_space_length + 3 + 5)}'

		## 标题
		title = '积分榜'.center(len(title_line))

		title_info = [title, title_line]
		credit_info = []

		person = self.people.head
		for i in range(3):
			credit_info.append(f'{person.name.center(max_name_length + empty_space_length)} | {person.credits}分')
			person = person.next

		## 按现有积分降序
		credit_info = sorted(credit_info, key=lambda x: int(re.findall('(\d+)分', x)[0]), reverse=True)

		credit_board = '\n'.join(title_info + credit_info)
		MessagePoster.post_hint(hint_type='show_credit_board', credit_board=credit_board)

	def check_continue(self):
		while True:
			if_continue = MessageGetter.get_order(order_type='continue_game')
			if if_continue == 'y':
				self.reset()
				break
			else:
				self.exit()
				continue

	def exit(self):
		confirm_exit = MessageGetter.get_order(order_type='confirm_exit')
		if confirm_exit == 'n':
			return

		if not self.initialized:
			exit()

		player = self.people.get_player()

		user_profile = {
		'user_name': player.name,
		'credits': player.credits
		}

		save_data_order = MessageGetter.get_order(order_type='save_data')
		if save_data_order == 'y':
			with open(f'{player.name}.json', 'w') as f:
				json.dump(user_profile, f)

		## 退出整个程序
		MessagePoster.post_hint(hint_type='thank_you')
		exit()
