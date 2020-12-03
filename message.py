import re


class GameExiter:
	"""虚类, 代表退出游戏的信号"""

	def __init__(self):
		pass


class MessageGetter:
	"""请玩家发指令"""

	get_dict = {
	'deal_cards': '请您出牌(输入"p"跳过本轮): ',
	'user_name': '请输入用户名(只接受英文字母和下划线, 且首位不是下划线)',
	'confirm_exit': '是否确实要退出(y/n): ',
	'save_data': '是否保存现有积分(y/n): ',
	'overload_data': '用户已存在, 是否覆盖数据(y/n): ',
	'landlord_score': '您地主叫几分(最少叫min_landlord_score分, 最多叫3分, 输入"p"跳过本轮)?',
	'continue_game': '是否继续游戏(y/n)?'
	}

	legal_pattern = {
	'deal_cards': re.compile('^([23456789+JQKAmM]+|p)$'),
	'user_name': re.compile('^[a-zA-Z]+[a-zA-Z_]*$'),
	'confirm_exit': re.compile('^[yn]{1}$'),
	'save_data': re.compile('^[yn]{1}$'),
	'overload_data': re.compile('^[yn]{1}$'),
	'landlord_score': re.compile('^[123p]{1}$'),
	'continue_game': re.compile('^[yn]{1}$')
	}

	def is_legal(order_type, raw_order):
		return re.match(MessageGetter.legal_pattern.get(order_type, '.*'), raw_order) is not None

	def get_order(order_type, **kwargs):
		guidance_message = MessageGetter.get_dict[order_type]
		while True:
			for k, v in kwargs.items():
				guidance_message = guidance_message.replace(k, v)
			raw_order = input(guidance_message)

			## 为避免死循环, 在确认退出或保存用户数据时不能再输入'exit'
			if raw_order == 'exit' and order_type not in {'confirm_exit', 'save_data'}:
				return GameExiter()
			if MessageGetter.is_legal(order_type, raw_order):
				return raw_order
			else:
				MessagePoster.post_hint(hint_type='invaild_input')


class MessagePoster:
	"""向玩家发指令"""

	post_dict = {
	'player_show_cards': '您当前的牌为: unshowed_cards',
	'new_game': '----- 新的一局牌 -----',
	'formly_start_game': '----- 游戏正式开始 -----',
	'new_round': '----- 新的一轮牌 -----',
	'start_sending_cards': '----- 开始发牌 -----',
	'person_abandon_dealing_cards': 'output_name要不起！',
	'person_abandon_giving_landlord_score': 'output_name本轮不叫地主！',
	'invaild_cards_pattern_or_too_many_cards': '无效的牌/您没有该牌, 请重新出牌!',
	'invaild_cards_species': '无效的牌组合, 请重新出牌!',
	'cards_size_too_small': '牌没能大过上家, 请重新出牌!',
	'landlord_score_too_small': '您地主叫分没能超过上家, 请重新叫分!',
	'person_dealed_cards': 'output_name本轮出牌为: unprinted_cards',
	'double_game_credits': 'output_name出了炸弹, 本局分数翻倍!',
	'person_gave_landlord_score': 'output_name本轮叫分为: landlord_score',
	'overload_broken_data': '用户数据已损坏, 将为您新建数据',
	'announce_landlord': '地主已产生: landlord_name是地主, peasant1_name和peasant2_name是农民!',
	'announce_game_credits': '本局分数为game_credits分!',
	'invaild_input': '输入不合法, 请重新输入!',
	'show_landlord_cards': '地主牌为: landlord_cards',
	'win_as_landlord': '恭喜, 您打败了农民!',
	'win_as_peasant1': '恭喜, 您带领农民打败了地主!',
	'win_as_peasant2': '恭喜, 您被carry着打败了地主!',
	'lose_as_peasant': '很遗憾, 你们被地主打败了!',
	'lose_as_landlord': '很遗憾, 您被农民们打败了!',
	'show_credit_board': 'credit_board',
	'system_will_decide_landlord_randomly': '连续两轮没有人叫地主, 系统将随机决定地主(本局分数为1分)!',
	'player_can_not_skip_deal_cards_without_last_cards': '您不能跳过有牌权出牌, 请重新出牌!',
	'welcome': '欢迎玩斗地主游戏!\n出牌时, "+"代表10, "m"代表小王, "M"代表大王\n输入"exit"退出',
	'thank_you': '游戏退出, 欢迎下次再来玩~'
	}

	def post_hint(hint_type, **kwargs):
		guidance_message = MessagePoster.post_dict[hint_type]
		for k, v in kwargs.items():
			guidance_message = guidance_message.replace(k, v)
		print(guidance_message)
