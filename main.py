from game import Game
from card import Card, Cards, AllCards
from message import MessageGetter, MessagePoster, GameExiter
from person import Person, Player, Robot, People

def main():

	## 初始化游戏
	game = Game()

	## 一次循环代表一局
	while True:

		## 发牌
		game.send_cards()

		## 叫地主
		game.decide_landlord()

		## 出牌
		game.deal_cards()

		## 计算得分
		game.check_results()

		## 展示积分排行榜
		game.show_credit_board()

		## 是否继续游戏
		game.check_continue()

if __name__ == '__main__':
	main()