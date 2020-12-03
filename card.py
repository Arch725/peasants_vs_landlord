import random
import collections


class Card:
	"""一张牌(能比较大小但不能单独打出)"""

	ordering_rule = {
	'3':1, '4':2, '5':3, '6':4, '7':5, '8':6, '9':7, '+':8, 'J':9, 'Q':10, 'K':11, 'A':12, 
	'2':13, 'm':14, 'M':15
	}

	reverse_ordering_rule = {v: k for k, v in ordering_rule.items()}

	def __init__(self, pattern):
		self.pattern = pattern
		self.size = Card.ordering_rule[pattern]

	def __hash__(self):
		return hash(self.pattern)

	def __repr__(self):
		cls_name = type(self).__name__
		return f'{cls_name}("{self.pattern}")'

	def __str__(self):
		return str(self.pattern)

	def __eq__(self, another_card):
		if isinstance(another_card, Card):
			return self.size == another_card.size
		return False

	def __gt__(self, another_card):
		if isinstance(another_card, Card):
			return self.size > another_card.size
		return NotImplemented

	def __lt__(self, another_card):
		if isinstance(another_card, Card):
			return self.size < another_card.size
		return NotImplemented

	def __ne__(self, another_card):
		return not self == another_card

	def __le__(self, another_card):
		return self < another_card or self == another_card

	def __ge__(self, another_card):
		return self > another_card or self == another_card

	def __add__(self, another_card_or_cards):
		if isinstance(another_card_or_cards, Cards):
			return another_card_or_cards + self
		elif isinstance(another_card_or_cards, Card):
			return Cards(self, another_card)
		else:
			return NotImplemented

	def __mul__(self, scalar):
		if isinstance(scalar, int):
			return Cards([self] * scalar)
		else:
			return NotImplemented

	@property
	def prev(self):
		cls = type(self)
		prev_pattern = Card.reverse_ordering_rule.get(self.size - 1, None)
		if prev_pattern is not None:
			return cls(prev_pattern)

	@property
	def next(self):
		cls = type(self)
		next_pattern = Card.reverse_ordering_rule.get(self.size + 1, None)
		if next_pattern is not None:
			return cls(next_pattern)


class Cards:
	"""(一张或几张)牌的集合"""

	def __init__(self, *args, species=None, chain_length=None, size=None):
		self.data = []
		for card_or_cards_list in args:
			if isinstance(card_or_cards_list, Card):
				self.data.append(card_or_cards_list)
			elif isinstance(card_or_cards_list, list):
				for card in card_or_cards_list:
					if not isinstance(card, Card):
						raise TypeError('Cards must be built by card!')
					self.data.append(card)
			else:
				raise TypeError('Cards must be built by card!')

		self.species = species
		self.chain_length = chain_length
		self.size = size

	def __contains__(self, some_card_or_cards):
		if isinstance(some_card_or_cards, Cards):
			dummy_cards = list(self.data)
			for card in some_card_or_cards:
				try:
					dummy_cards.remove(card)
				except:
					return False
			else:
				return True
		else:
			return some_card_or_cards in self.data

	def __len__(self):
		return len(self.data)

	def __iter__(self):
		return iter(self.data)

	def __add__(self, another_card_or_cards):
		"""
		+
		已经有牌型的元数据的牌运算时, 需要重新计算元数据
		如果运算后的元数据不合法, 则不能完成此次运算
		"""
		
		if isinstance(another_card_or_cards, Cards):
			new_instance = Cards(self.data + another_card_or_cards.data)
			if self.is_completed():
				meta_data = new_instance.cal_meta_data()
				if meta_data is not None:
					return new_instance
				else:
					raise ValueError('Invaild species of the added cards!')
			else:
				return new_instance
		elif isinstance(another_card_or_cards, Card):
			new_instance = Cards(self.data + [another_card_or_cards.data])
			if self.is_completed():
				meta_data = new_instance.cal_meta_data()
				if meta_data is not None:
					return new_instance
				else:
					raise ValueError('Invaild species of the added cards!')
			else:
				return new_instance
		else:
			return NotImplemented

	def __sub__(self, another_card_or_cards):
		"""
		-
		已经有牌型的元数据的牌运算时, 需要重新计算元数据
		如果运算后的元数据不合法, 则不能完成此次运算
		如果减数不是被减数的子集, 则不能完成此次运算
		"""

		if isinstance(another_card_or_cards, Cards):

			if another_card_or_cards not in self:
				raise ValueError('Can only subtract a subset of cards!')
			new_instance_data = self.data[:]
			for card in another_card_or_cards:
				new_instance_data.remove(card)
			new_instance = Cards(new_instance_data)
			if self.is_completed():
				meta_data = new_instance.cal_meta_data()
				if meta_data is not None:
					return new_instance
				else:
					raise ValueError('Invaild species of the subtracted cards!')
			else:
				return new_instance
		elif isinstance(another_card_or_cards, Card):
			if another_card_or_cards not in self:
				raise ValueError('Can only subtract a subset of cards!')
			new_instance = Cards(self.data.remove(another_card_or_cards))
			if self.is_completed():
				meta_data = new_instance.cal_meta_data()
				if meta_data is not None:
					return new_instance
				else:
					raise ValueError('Invaild species of the subtracted cards!')
			else:
				return new_instance
		else:
			return NotImplemented

	def __iadd__(self, another_card_or_cards):
		"""
		+=
		已经有牌型的元数据的牌运算时, 需要重新计算元数据
		如果运算后的元数据不合法, 则不能完成此次运算
		"""
		
		if isinstance(another_card_or_cards, Cards):
			self.data += another_card_or_cards.data
			if self.is_completed():
				meta_data = self.cal_meta_data()
				if meta_data is not None:
					return self
				else:
					self.data -= another_card_or_cards.data
					raise ValueError('Invaild species of the added cards!')
			else:
				return self
		elif isinstance(another_card_or_cards, Card):
			self.data.append(another_card_or_cards)
			if self.is_completed():
				meta_data = self.cal_meta_data()
				if meta_data is not None:
					return self
				else:
					self.data.pop()
					raise ValueError('Invaild species of the added cards!')
			else:
				return self
		else:
			return NotImplemented

	def __isub__(self, another_card_or_cards):
		"""
		-=
		已经有牌型的元数据的牌运算时, 需要重新计算元数据
		如果运算后的元数据不合法, 则不能完成此次运算
		如果减数不是被减数的子集, 则不能完成此次运算
		"""

		if isinstance(another_card_or_cards, Cards):
			if another_card_or_cards not in self:
				raise ValueError('Can only subtract a subset of cards!')
			for card in another_card_or_cards:
				self.data.remove(card)
			if self.is_completed():
				meta_data = self.cal_meta_data()
				if meta_data is not None:
					return self
				else:
					self.data += another_card_or_cards.data
					raise ValueError('Invaild species of the subtracted cards!')
			else:
				return self
		elif isinstance(another_card_or_cards, Card):
			if another_card_or_cards not in self:
				raise ValueError('Can only subtract a subset of cards!')
			self.data.remove(another_card_or_cards)
			if self.is_completed():
				meta_data = self.cal_meta_data()
				if meta_data is not None:
					return self
				else:
					self.data.append(another_card_or_cards)
					raise ValueError('Invaild species of the subtracted cards!')
			else:
				return self
		else:
			return NotImplemented

	## 只有拥有了species等属性的牌才能相互比较
	def __eq__(self, another_cards):
		if not isinstance(another_cards, Cards):
			return NotImplemented
		if not self.is_completed() or not another_cards.is_completed():
			raise TypeError('Can not compare two cards without species!')
		return self.species == another_cards.species and self.chain_length == another_cards.chain_length and self.size == another_cards.size
		
	def __gt__(self, another_cards):
		if not isinstance(another_cards, Cards):
			return NotImplemented
		if not self.is_completed() or not another_cards.is_completed():
			raise TypeError('Can not compare two cards without species!')

		if (self.species == 'two_jokers' and another_cards.species != 'two_jokers') \
		or (self.is_bumb() and not another_cards.is_bumb()):
			return True
		elif self.species != another_cards.species or self.chain_length != another_cards.chain_length:
			return False
		else:
			return self.size > another_cards.size

	def __lt__(self, another_cards):
		if not isinstance(another_cards, Cards):
			return NotImplemented
		if not self.is_completed() or not another_cards.is_completed():
			raise TypeError('Can not compare two cards without species!')

		if (self.species != 'two_jokers' and another_cards.species == 'two_jokers') \
		or (not self.is_bumb() and another_cards.is_bumb()):
			return True
		elif self.species != another_cards.species or self.chain_length != another_cards.chain_length:
			return False
		else:
			return self.size < another_cards.size

	def __ne__(self, another_cards):
		return not self == another_cards

	def __le__(self, another_cards):
		return self < another_cards or self == another_cards

	def __ge__(self, another_cards):
		return self > another_cards or self == another_cards

	def __repr__(self):
		cls_name = type(self).__name__
		return f'{cls_name}({", ".join([repr(card) for card in sorted(self, reverse=True)])})'

	def __str__(self, join_str=''):
		return join_str.join([str(card) for card in sorted(self, reverse=True)])

	def is_empty(self):
		return len(self.data) == 0

	def is_completed(self):
		return self.species is not None and self.chain_length is not None and self.size is not None

	def sort(self):
		"""对牌聚合后排序"""

		if self.is_empty():
			return collections.Counter()
		agged_cards = collections.Counter(self.data)
		return collections.Counter(dict(sorted(sorted(agged_cards.items(), key=lambda x: x[0], reverse=True), key=lambda x: x[1], reverse=True)))

	## 以下是一些公共函数库
	def get_max_appearence(self, sorted_cards):
		"""获取出现次数最多的牌的出现次数"""

		sorted_cards_items = list(sorted_cards.items())
		return sorted_cards_items[0][1]

	def get_min_appearence(self, sorted_cards):
		"""获取出现次数最少的牌的出现次数"""

		sorted_cards_items = list(sorted_cards.items())
		return sorted_cards_items[-1][1]

	def value_filter(self, sorted_cards, value):
		return [k for k, v in sorted_cards.items() if v == value]

	def split(self, sorted_cards):
		"""将排序后牌分为主牌和副牌"""	

		max_card_appearance = self.get_max_appearence(sorted_cards)
		major_cards = self.value_filter(sorted_cards, max_card_appearance)
		other_appearences = [v for v in sorted_cards.values() if v != max_card_appearance]

		return major_cards, other_appearences

	def is_continuous(self, cards_sample):
		"""
		判断主牌是否连续
		主牌: 三带一/三带二/四带一中三个的和四个的部分
		"""

		continuous_length = 1

		## 最小的牌
		card = cards_sample[-1]

		while continuous_length < len(cards_sample):
			if card.next not in cards_sample:
				return False
			card = card.next
			continuous_length += 1
		else:
			return True

	def is_mutil_chain_length(self, major_cards, max_card_appearence, chain_length_standard=5):
		"""判断是否是多链节牌"""

		## 多链节牌的三个要素:
		## 1. 连线牌最大的牌不能大于A
		## 2. 牌的主牌部分必须连续
		## 3. 连线牌的长度必须 >= 最小链节数
		if len(major_cards) == 0:
			return False
		return major_cards[0] <= Card('A') \
		and self.is_continuous(major_cards) \
		and len(major_cards) * max_card_appearence >= chain_length_standard

	## 真人持牌时需要的函数, 主要用于确认牌的合法性
	def is_bumb(self):
		return (self.species == 'quadra' and self.chain_length == 1) or self.species == 'two_jokers'

	def cal_meta_data(self):
		"""从牌中获得牌的种类和牌的链节长度"""

		sorted_cards = self.sort()
		major_cards, other_appearences = self.split(sorted_cards)
		max_card_appearence = self.get_max_appearence(sorted_cards)
		min_card_appearence = self.get_min_appearence(sorted_cards)
		is_mutil_chain_length = self.is_mutil_chain_length(major_cards, max_card_appearence)
		self.size = major_cards[0].size

		if Card('M') in self and Card('m') in self:
			self.species, self.chain_length, self.size = 'two_jokers', 1, 10000
			return self.species, self.chain_length, self.size
	
		## 单牌
		if max_card_appearence == min_card_appearence == 1:
			if is_mutil_chain_length or len(major_cards) == 1:
				self.species, self.chain_length, self.size = 'single', len(major_cards), major_cards[0].size
				return self.species, self.chain_length

		## 双牌
		if max_card_appearence == min_card_appearence == 2: 
			if is_mutil_chain_length or len(major_cards) == 1:
				self.species, self.chain_length, self.size = 'double', len(major_cards), major_cards[0].size
				return self.species, self.chain_length, self.size	

		## 三牌
		if max_card_appearence == 3:
			if min_card_appearence == 3:
				if is_mutil_chain_length or len(major_cards) == 1:
					self.species, self.chain_length, self.size = 'triple', len(major_cards), major_cards[0].size
					return self.species, self.chain_length, self.size		

			## 三带一/三带二
			if is_mutil_chain_length or len(major_cards) == 1:
				if len(major_cards) == len(other_appearences) and len(major_cards) == sum(other_appearences) / 2:
					self.species, self.chain_length, self.size = 'triple_and_double', len(major_cards), major_cards[0].size
					return self.species, self.chain_length, self.size
			
				if len(major_cards) == sum(other_appearences):
					self.species, self.chain_length, self.size = 'triple_and_single', len(major_cards), major_cards[0].size
					return self.species, self.chain_length, self.size

		## 四牌
		if max_card_appearence == 4:
			if min_card_appearence == 4:
				if is_mutil_chain_length or len(major_cards) == 1:
					self.species, self.chain_length, self.size = 'quadra', len(major_cards), major_cards[0].size * 100
					return self.species, self.chain_length, self.size

			## 四带一
			if is_mutil_chain_length or len(major_cards) == 1:
				if len(major_cards) == sum(other_appearences):
					self.species, self.chain_length, self.size = 'quadra_and_single', len(major_cards), major_cards[0].size
					return self.species, self.chain_length, self.size

		## 牌型不合法时, 返回None
		return

	## 以下是机器人持牌时需要的函数, 用于估计手中牌的好坏或从牌整体中提取合法的牌
	def set_meta_data(self, species, chain_length, size):
		self.species = species
		self.chain_length = chain_length
		self.size = size

	def has_bumb(self, sorted_cards):
		return len(self.value_filter(sorted_cards, 4)) > 0 \
		or self.has_big_joker() \
		or self.has_small_joker()

	def has_big_joker(self):
		return Card('M') in self

	def has_small_joker(self):
		return Card('m') in self

	def has_enough_certain_cards(self, sorted_cards, certain_card, cnt_standard=2):
		return sorted_cards.get(certain_card, 0) >= cnt_standard

	def has_long_lines(self, sorted_cards, chain_length_standard=8):

		## 单/双/三牌有一个符合条件即可
		for i in range(1, 4):
			certain_sorted_cards = self.value_filter(sorted_cards, i)
			if self.is_mutil_chain_length(certain_sorted_cards, i, chain_length_standard=8):
				return True
		return False

	def has_small_median(self, sorted_cards, standard_card=Card('J')):
		index = 0
		for card, cnt in sorted_cards.items():
			index += cnt
			if index > len(self) // 2:
				return card < standard_card

	def has_useless_small_single_cards(self, sorted_cards, standard_card=Card('J'), cnt_standard=5):
		certain_sorted_cards = self.value_filter(sorted_cards, 1)
		return len(certain_sorted_cards) >= cnt_standard and not self.is_continuous(certain_sorted_cards)

	def cal_confidence(self):
		"""检测牌是否足够大"""

		confidence = 0
		sorted_cards = self.sort()

		## 加分项:
		## 如果有双王/炸弹, 信心+2
		if self.has_bumb(sorted_cards):
			confidence += 2

		## 如果有一个大王, 信心+1
		if self.has_big_joker():
			confidence += 1

		## 如果有一个小王1个2, 信心+1
		if self.has_small_joker() and self.has_enough_certain_cards(sorted_cards, certain_card=Card('2'), cnt_standard=1):
			confidence += 1

		## 如果有2个2, 信心+1
		if self.has_enough_certain_cards(sorted_cards, certain_card=Card('2'), cnt_standard=2):
			confidence += 1

		## 如果有长连线(3个三牌/4个双牌/8个单牌), 信心+1
		if self.has_long_lines(sorted_cards):
			confidence += 1

		## 减分项:
		## 如果中位数小于J, 信心-1
		if self.has_small_median(sorted_cards):
			confidence -= 1

		## 如果小于J的单牌多于5个且不能连成线, 信心-1
		if self.has_useless_small_single_cards(sorted_cards):
			confidence -= 1

		return confidence

	def separate(self):
		"""将手中的所有牌分成一个个牌块, 每个牌块是完全的牌"""

		## 这里的排序规则是特殊的: 按照出现次数降序, 并列时按照牌大小升序
		## 这里采用list而不是dict: dict在迭代过程中不能修改
		sorted_cards_data = sorted(sorted(collections.Counter(self.data).items(), key=lambda x: x[0]), key=lambda x: x[1], reverse=True)

		## 牌块们
		cards_blocks = []

		## 先把大小王挑走
		if self.has_big_joker() and self.has_small_joker():
			cards_block = Cards(Card('M'), Card('m'), species='two_jokers', chain_length=1, size=10000)
			cards_blocks.append(cards_block)
			sorted_cards_data.remove((Card('M'), 1))
			sorted_cards_data.remove((Card('m'), 1))

		## 再把炸弹挑走
		cards_block = Cards()
		for card, cnt in sorted_cards_data:
			if cnt == 4:
				cards_block += card * 4
				sorted_cards_data.remove((card, 4))
				cards_block.set_meta_data(species='quadra', chain_length=1, size=card.size * 100)
				cards_blocks.append(cards_block)
				## 策略: 不主动生成四牌连线和四带一(这样会损害炸)

			## 如果不是4说明四牌已经被挑完(sorted_cards_data是按牌数降序的)
			else:
				break

		## 再把三个的挑走(此时已经没有4个的了)
		## 策略: 先把所有三个连续的挑出来, 再配牌
		while True:
			cards_block = Cards()
			for card, cnt in sorted_cards_data:

				## 找到起点
				if cnt == 3:
					cards_block += card * 3	
					sorted_cards_data.remove((card, 3))	
					break

			## for全程没有break说明已经没有3个的了, 退出循环
			else:
				break

			## 计算链长
			chain_length = 1

			## 对于三牌, 不需要检查chain_length, 因为任意长度都合法(不像双牌, 链长为2时就不合法)
			while len([k for k in self if k == card.next]) == 3 and card.next <= Card('A'):
				cards_block += card.next * 3
				sorted_cards_data.remove((card.next, 3))
				chain_length += 1
				card = card.next
				
			## 最大的三牌就是整个三牌的大小
			size = card.size

			## 寻找副牌
			## 配牌顺序: 三带一, 三带二, 三个
			## 2及以上的不参与匹配
			single_side_cards = [k for k, v in sorted_cards_data if v == 1 and k < Card('2')]
			double_side_cards = [k for k, v in sorted_cards_data if v == 2 and k < Card('2')]

			## 如果单牌足够配, 则配单牌
			if len(single_side_cards) >= chain_length:
				species = 'triple_and_single'
				for card in single_side_cards[:chain_length]:
					cards_block += card
					sorted_cards_data.remove((card, 1))

			## 如果单牌+双牌才够配(双牌自己不够配), 则需要双牌的帮助
			elif len(single_side_cards) + 2 * len(double_side_cards) >= chain_length \
			and len(double_side_cards) < chain_length:
				species = 'triple_and_single'

				## 如果单牌和三牌的数量差偶数个, 则单牌全部用于匹配
				if (chain_length - len(single_side_cards)) % 2 == 0:
					for card in single_side_cards:
						cards_block += card
						sorted_cards_data.remove((card, 1))
					for card in double_side_cards[:(chain_length - len(single_side_cards)) / 2]:
						cards_block += card
						sorted_cards_data.remove((card, 2))

				## 如果单牌和三牌的数量差奇数个, 则单牌除了最大的单牌之外其他的用于匹配
				else:
					for card in single_side_cards[:-1]:
						cards_block += card
						sorted_cards_data.remove((card, 1))
					for card in double_side_cards[:(chain_length - len(single_side_cards) + 1) / 2]:
						cards_block += card
						sorted_cards_data.remove((card, 2))		
			
			## 如果双牌够配, 则形成三带二
			elif len(double_side_cards) >= chain_length:
				species = 'triple_and_double'
				for card in double_side_cards[:chain_length]:
					cards_block += card
					sorted_cards_data.remove((card, 2))

			## 如果所有单双牌加一起都不够配, 那就不配	
			else:	
				species = 'triple'

			cards_block.set_meta_data(species=species, chain_length=chain_length, size=size)
			cards_blocks.append(cards_block)

		## 再把双牌挑走
		while True:
			cards_block = Cards()
			for card, cnt in sorted_cards_data:

				## 找到起点
				if cnt == 2:
					cards_block += card * 2
					sorted_cards_data.remove((card, 2))
					break

			## for全程没有break说明已经没有2个的了, 退出循环
			else:
				break

			## 计算链长
			chain_length = 1

			## 考虑到链节不能过短的问题, 设立一个暂存区
			tmp_cards = []

			## 对于双牌, 链长 < 3时就不合法
			while len([k for k in self if k == card.next]) == 2 and card.next <= Card('A'):
				tmp_cards.append(card.next)
				chain_length += 1
				card = card.next

			## 链节长度 = 1或 >= 3 时, 将暂存区存入; 否则舍弃暂存区
			if chain_length >= 3 or chain_length == 1:
				for tmp_card in tmp_cards:
					cards_block += tmp_card * 2
					sorted_cards_data.remove((tmp_card, 2))
			else:

				## 此时为了找最大的牌, 需要往前调len(tmp_cards)个
				for i in range(len(tmp_cards)):
					card = card.prev
					chain_length -= 1			

			## 最大的双牌就是整个双牌的大小
			size = card.size

			cards_block.set_meta_data(species='double', chain_length=chain_length, size=size)
			cards_blocks.append(cards_block)

		## 剩下的都是单牌
		while True:
			cards_block = Cards()
			for card, cnt in sorted_cards_data:

				## 找到起点
				cards_block += card * 1
				sorted_cards_data.remove((card, 1))
				break

			## for全程没有break说明已经空了, 退出循环
			else:
				break

			## 计算链长
			chain_length = 1

			## 考虑到链节不能过短的问题, 设立一个暂存区
			tmp_cards = []

			## 对于单牌, 链长 < 5时就不合法
			while len([k for k in self if k == card.next]) == 1 and card.next <= Card('A'):
				tmp_cards.append(card.next)
				chain_length += 1
				card = card.next

			## 链节长度 = 1或 >= 5 时, 将暂存区存入; 否则舍弃暂存区
			if chain_length >= 5 or chain_length == 1:
				for tmp_card in tmp_cards:
					cards_block += tmp_card
					sorted_cards_data.remove((tmp_card, 1))
			else:

				## 此时为了找最大的牌, 需要往前调len(tmp_cards)个
				for i in range(len(tmp_cards)):
					card = card.prev
					chain_length -= 1				

			## 最大的单牌就是整个单牌的大小
			size = card.size

			cards_block.set_meta_data(species='single', chain_length=chain_length, size=size)
			cards_blocks.append(cards_block)

		## 将牌块按照牌大小降序排列
		cards_blocks = sorted(cards_blocks, key=lambda x: x.size, reverse=True)
		return cards_blocks


class AllCards(Cards):
	""""""

	def __init__(self):
		self.species = None
		self.chain_length = None
		self.size = None
		self.shuffle()

	def shuffle(self):
		self.data = [Card(pattern) for pattern in list('A23456789+JQK' * 4) + ['m', 'M']]

	def give_cards(self, n):
		sent_cards = Cards(random.sample(list(self), n))
		self -= sent_cards
		return sent_cards
