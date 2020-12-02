from card import Card, Cards, AllCards
from message import MessageGetter, MessagePoster, GameExiter


class Person:
	"""人(玩家和机器人的统称)"""

	def __init__(self, name, credits):
		self.name = name
		self.credits = credits
		self.cards = Cards()
		self.identity = None
		self.landlord_score = None

	def set_identity(self, identity):
		self.identity = identity

	def take_cards(self, unsented_cards):
		self.cards += unsented_cards

	def change_credits(self, unchanged_credits):
		self.credits += unchanged_credits


class Player(Person):
	"""玩家"""

	def __init__(self, name, credits):
		super().__init__(name, credits)
		self.is_real = True
		self.output_name = '您'

	def reset_profile(self):
		self.cards = Cards()
		self.identity = None
		self.landlord_score = None

	def set_credits(self, credits):
		self.credits = credits

	def deal_cards(self, last_cards, last_person_identity=None):

		## 先给玩家看自己手中的牌
		MessagePoster.post_hint(hint_type='player_show_cards', unshowed_cards=str(self.cards))

		## 让用户一直出牌, 直到牌大过上家或者放弃出牌
		while True:
			raw_order = MessageGetter.get_order(order_type='deal_cards')

			## 退出游戏
			if isinstance(raw_order, GameExiter):
				return GameExiter()

			## 如果玩家要不起/不要, 则返回None
			if raw_order == 'p':

				## 有牌权出牌不能跳过
				if last_cards is not None:
					MessagePoster.post_hint(hint_type='person_abandon_dealing_cards', output_name=self.output_name)
					return
				else:
					MessagePoster.post_hint(hint_type='player_can_not_skip_deal_cards_without_last_cards')
					continue

			undealed_cards = Cards([Card(pattern) for pattern in raw_order])

			## 牌的验证
			## 牌的子集验证
			if not undealed_cards in self.cards:
				MessagePoster.post_hint(hint_type='invaild_cards_pattern_or_too_many_cards')
				continue
			meta_data = undealed_cards.cal_meta_data()

			## 牌的元数据验证(实际是有效性验证)
			if meta_data is None:
				MessagePoster.post_hint(hint_type='invaild_cards_species')
				continue

			## 出牌
			## 如果是有牌权出牌, 可以直接出
			if last_cards is None:
				MessagePoster.post_hint(hint_type='person_dealed_cards', output_name=self.output_name, unprinted_cards=str(undealed_cards))
				self.cards -= undealed_cards
				return undealed_cards

			## 牌型相符且牌比上家大(考虑到炸弹类型)
			elif undealed_cards > last_cards:
				MessagePoster.post_hint(hint_type='person_dealed_cards', output_name=self.output_name, unprinted_cards=str(undealed_cards))
				self.cards -= undealed_cards
				return undealed_cards			

			## 牌型不符或牌型一样但没有上家大
			else:
				MessagePoster.post_hint(hint_type='cards_size_too_small')
				continue

	def deal_landlord_score(self, last_landlord_score):
		while True:
			landlord_score = MessageGetter.get_order(order_type='landlord_score', min_landlord_score=str(last_landlord_score + 1))
			
			## 退出游戏
			if isinstance(landlord_score, GameExiter):
				return GameExiter()

			## 如果玩家本轮不叫地主, 则返回None
			if landlord_score == 'p':
				MessagePoster.post_hint(hint_type='person_abandon_giving_landlord_score', output_name=self.output_name)
				return

			## 地主分的验证
			landlord_score = int(landlord_score)
			if landlord_score > last_landlord_score:
				MessagePoster.post_hint(hint_type='person_gave_landlord_score', output_name=self.output_name, landlord_score=str(landlord_score))
				return landlord_score
			else:
				MessagePoster.post_hint(hint_type='landlord_score_too_small')


class Robot(Person):
	"""机器人"""

	def __init__(self, name, credits=100):
		super().__init__(name, credits)
		self.is_real = False
		self.output_name = name
		self.cards_blocks = None

	def reset_profile(self):
		self.cards = Cards()
		self.identity = None
		self.landlord_score = None
		self.cards_blocks = None

	def deal_landlord_score(self, last_landlord_score):
		if self.landlord_score is None:
			self.landlord_score = self.cards.cal_confidence()
		if self.landlord_score > last_landlord_score:
			MessagePoster.post_hint(hint_type='person_gave_landlord_score', output_name=self.output_name, landlord_score=str(self.landlord_score))
			return self.landlord_score
		else:
			MessagePoster.post_hint(hint_type='person_abandon_giving_landlord_score', output_name=self.output_name)
			return

	def deal_cards_with_last_cards(self, last_cards, last_person_identity):

		## 不管10以上的同伙的牌
		if self.identity == last_person_identity and last_cards.size >= Card('J').size:
			MessagePoster.post_hint(hint_type='person_abandon_dealing_cards', output_name=self.output_name)
			return
		for undealed_cards in self.cards_blocks[::-1]:
			if undealed_cards > last_cards:
				self.cards_blocks.remove(undealed_cards)
				self.cards -= undealed_cards
				MessagePoster.post_hint(hint_type='person_dealed_cards', output_name=self.output_name, unprinted_cards=str(undealed_cards))
				return undealed_cards
		else:
			MessagePoster.post_hint(hint_type='person_abandon_dealing_cards', output_name=self.output_name)
			return

	def deal_cards_without_last_cards(self):
		undealed_cards = self.cards_blocks.pop()
		self.cards -= undealed_cards
		MessagePoster.post_hint(hint_type='person_dealed_cards', unprinted_cards=str(undealed_cards), output_name=self.output_name)
		return undealed_cards

	def deal_cards(self, last_cards, last_person_identity):
		if self.cards_blocks is None:
			self.cards_blocks = self.cards.separate()
			# for cards_block in self.cards_blocks:
			# 	print(f'{str(cards_block)}, {cards_block.species}, {cards_block.chain_length}, {cards_block.size}')
		if last_cards is not None:
			undealed_cards = self.deal_cards_with_last_cards(last_cards, last_person_identity)
		else:
			undealed_cards = self.deal_cards_without_last_cards()
		return undealed_cards


class People:
	"""三个人组成的环形链表"""

	def __init__(self, player, robot1, robot2):
		self.head = player
		player.next = robot1
		player.prev = robot2
		robot1.next = robot2
		robot1.prev = player
		robot2.next = player
		robot2.prev = robot1

		self.max_name_length = max(list(map(lambda x: len(x.name), [player, robot1, robot2])))

	def set_head(self, person):
		self.head = person

	def get_player(self):
		person = self.head
		while not person.is_real:
			person = person.next
		return person
