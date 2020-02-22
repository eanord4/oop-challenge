# blackjack game
# eric nordstrom
# python 3.6.4



# one deck
# one player
# basic rules, e.g. no doubling down
# reshuffle when deck goes below 10 cards



from random import shuffle
from time import sleep
from os import name as os_name
windows = os_name == "nt"


# settings
STD_DELAY = 2  # seconds



# data validation for card instantiation
_card_num_range = range(2, 11)
_suits = {
	'C': "♣",
	'S': "♠",
	'H': "♥" if windows else "♡",
	'D': "♦" if windows else "♢"
}



# functions for printing with style

def sleepingpad(delay=1, start="\n", end=""):
	f"""returns a decorator for printing text before and/or after the function and following the function with a time delay; `delay` is multiplied by the standard delay of {STD_DELAY}"""

	def decorator(func):
		def wrapper(*args, **kwargs):
			print(start, end="")
			result = func(*args, **kwargs)
			print(end, end="")
			sleep(delay * STD_DELAY)
			return result
		return wrapper

	return decorator

def sleepprint(msg, delay=1, **kwargs):
	"""print, followed by a time delay"""

	print(msg, **kwargs)
	sleep(delay * STD_DELAY)



# card generation function
def card(rank, suit):
	"""generate a card of the given suit and rank (robust for aces)"""

	if isinstance(rank, str) and rank.lower() in {"a", "ace"} or rank in {1, 11}:
		return Ace(suit)
	return Card(rank, suit)



class _Card_MixIn:

	def __init__(self, suit):

		s = suit.title()

		if s in _suits:
			self.suit = _suits[s]
		elif s in _suits.values():
			self.suit = s
		else:
			raise ValueError(f"{repr(suit)} is not a valid suit.")

	def __repr__(self):
		return self.rank + self.suit

	def __eq__(self, other):
		return self.suit == other.suit and self.rank == other.rank  # intentionally ignores value of Ace

class Card(_Card_MixIn):

	def __init__(self, rank, suit):

		r = rank.lower() if isinstance(rank, str) else rank

		if r in {"j", "jack"}:
			self.value = 10
			self.rank = "J"
		elif r in {"q", "queen"}:
			self.value = 10
			self.rank = "Q"
		elif r in {"k", "king"}:
			self.value = 10
			self.rank = "K"
		elif r in _card_num_range:
			self.value = int(r)
			self.rank = str(self.value)
		elif r in {1, 11, "a", "ace"}:
			raise ValueError("Aces must be created through the Ace class.")
		else:
			raise ValueError(f"{repr(rank)} is not a valid card value.")
		
		_Card_MixIn.__init__(self, suit)

class Ace(Card):

	rank = "A"

	def __init__(self, suit):
		_Card_MixIn.__init__(self, suit)
		self.value = 11

	def harden(self):  # is this a thing?
		"""change the Ace's value from 11 to 1"""

		self.value = 1

class Deck:

	cards = [
		card(rank, suit)
		for rank in ["a"] + list(_card_num_range) + ["j", "q", "k"]
		for suit in _suits
	]

	def __init__(self):
		self.cards = self.cards.copy()
		self.shuffle()

	@sleepingpad(.25)
	def shuffle(self):
		print("The Dealer shuffles the deck.")
		shuffle(self.cards)

	def draw(self):
		return self.cards.pop()

	def __repr__(self):
		return f"Deck containing {len(self.cards)} cards"

	def __len__(self):
		return len(self.cards)

class Player:

	name = "You"
	possessive = "Your"
	alt_name = "You"
	verb_suffix = ""

	def __init__(self):
		self.reset()
		self.winnings = 0

	def reset(self):
		"""remove all cards"""

		self.hand = []
		self.score = 0
		self.soft = None
		self._has_blackjack = False

	def add_card(self, deck):
		"""move a card from the deck to the player's hand"""

		# draw card
		card = deck.draw()
		
		# inform of drawn card
		sleepprint(f"{self} receive{self.verb_suffix} the {card}.")

		# update hand and score
		self.hand.append(card)
		self.score += card.value

		# harden if neccessary/possible
		if self.score > 21 and self.soft:
			self.harden()
		
		# soften if new card is ace
		if isinstance(card, Ace):
			# at this point the hand cannot be soft

			self.soft = card

			# subsequently harden if necessary (wouldn't have been possible before)
			if self.score > 21:
				self.harden()

		# check for bust
		if self.score > 21:
			self.bust()

	def harden(self):  # is this a thing?
		self.soft.harden()
		self.soft = None
		self.score -= 10

	@sleepingpad(.5)
	def blackjack(self):
		print(f"{self} get{self.verb_suffix} Blackjack!")

	def has_blackjack(self):
		"""TO BE CALLED ONLY WHEN THERE ARE TWO CARDS"""

		self._has_blackjack = \
			"A" in {self.hand[0].rank, self.hand[1].rank} \
			and 10 in {self.hand[0].value, self.hand[1].value}

		return self._has_blackjack

	def check_for_blackjack(self):
		"""TO BE CALLED ONLY WHEN THERE ARE TWO CARDS"""

		if self.has_blackjack():
			self.blackjack()

	@sleepingpad()
	def twenty_one(self):
		"""TO BE CALLED ONLY IF 21 BUT NO BLACKJACK"""

		print(f"{self} get{self.verb_suffix} 21!")

	def hit(self, deck):
		sleepprint(f"{self} hit{self.verb_suffix}.")
		self.add_card(deck)

	def stand(self):
		sleepprint(f"{self} stand{self.verb_suffix}.")

	@sleepingpad()
	def bust(self):
		print(f"{self} bust{self.verb_suffix}!")

	@sleepingpad(.25)
	def place_bet(self):
		return float(input(
			"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n"

			"Place your bet: $"
		))

	@sleepingpad(.25)
	def prompt_play(self):
		return input(f"{self.possessive} move (HIT/STAND): ").lower()

	def play(self, deck):
		"""inform the user of their hand and the dealer's hand; prompt the user and update their hand as necessary"""

		self.print_hand()
		# print(f"{self.possessive} score: {self.print_score()}")
		player_choice = self.prompt_play()

		if player_choice in {"h", "hit"}:
			print()
			self.hit(deck)
			return False
		if player_choice in {"s", "stay", "stand", "hold"}:
			print()
			self.stand()
			return True
		sleepprint("** Not a valid input! **", .25)
		return self.play(deck)

	def _print_hand(self):

		sleepprint(f"{self.possessive} hand:", .125, end="\n\t")

		for card in self.hand:
			sleepprint(str(card), .125, end="\t")

	@sleepingpad(.125)
	def print_hand(self):
		self._print_hand()
		print()

	@sleepingpad(.5)
	def award(self, amount):
		self.winnings += amount
		print(f"{self.alt_name} gain{self.verb_suffix} ${amount:.2f}!")

	def print_score(self):
		return ("Soft " if self.soft else "Hard ") + str(self.score)

	def __str__(self):
		return self.name

	def __repr__(self):
		return f"Player '{self.name}'"

class Dealer(Player):

	name = "The Dealer"
	possessive = "The Dealer's"
	alt_name = "The House"
	verb_suffix = "s"

	def reset(self):
		Player.reset(self)
		self.hole = None

	def play(self, deck):
		"""automatic actions for the dealer"""

		if self.score < 17:
			self.hit(deck)
			stand = False
		else:
			self.stand()
			stand = True

		return stand

	def draw_hole(self, deck):
		"""draw a card but do not show it"""

		self.hole = deck.draw()
		sleepprint(f"The Dealer draws the hole card.")
		self.score = self.hole.value

		if isinstance(self.hole, Ace):
			self.soft = self.hole

	@sleepingpad()
	def reveal(self):
		"""reveal the hole card"""

		print(f"The Dealer reveals the hole card to be the {self.hole}.")

		if self.score == 21:
			sleep(.5 * STD_DELAY)
			print("The Dealer has 21!")

	def deal(self, player, deck):
		sleepprint("\n\tDEAL", .5)
		player.add_card(deck)
		self.draw_hole(deck)
		player.add_card(deck)
		self.add_card(deck)
		self.check_for_blackjack()
		player.check_for_blackjack()

	def has_blackjack(self):
		"""TO BE CALLED ONLY WHEN THERE ARE TWO CARDS"""

		self._has_blackjack = \
			"A" in {self.hole.rank, self.hand[0].rank} \
			and 10 in {self.hole.value, self.hand[0].value}

		return self._has_blackjack

	def check_for_blackjack(self):
		"""TO BE CALLED ONLY WHEN THERE ARE TWO CARDS"""

		if self.hand[0].value == 10 or isinstance(self.hand[0], Ace):  # also, only check when this condition is met.

			sleepprint(f"The Dealer checks the hole card for Blackjack.")

			if self.has_blackjack():
				self.blackjack()
			else:
				sleepprint(f"The Dealer does not have Blackjack.")

	@sleepingpad(.125)
	def print_hand(self):
		self._print_hand()
		sleepprint("*HOLE*", .125)

class Game:

	@sleepingpad(.5, start="\n\n")
	def __init__(self):
		self.deck = range(0)  # to trigger shuffling upon first hand
		self.player = Player()
		self.dealer = Dealer()
		self.hands_played = 0
		print(
			"~~~ BLACKJACK ~~~\n"
			"      (S17)"
		)

	def play_hand(self):
		"""play a hand of Blackjack!"""

		# start up
		self.player.reset()
		self.dealer.reset()
		bet = self.player.place_bet()
		self.dealer.deal(self.player, self.deck)
		sleepprint(f"\nThere are {len(self.deck)} cards left in the deck.")
		winner, loser = self.check_win(False)
		player_21 = dealer_stand = False

		# loop through player decisions
		while not winner:

			# get player's play
			self.dealer.print_hand()
			player_stand = self.player.play(self.deck)

			if player_stand and dealer_stand:
				# must check for win
				winner, loser = self.check_win(True)
				continue

			# check for bust
			if self.player.score > 21:
				winner, loser = self.win(self.dealer)
				continue

			# check for player 21
			if self.player.score == 21:
				self.player.twenty_one()

			dealer_stand = self.dealer.play(self.deck)
			winner, loser = self.check_win(player_stand and dealer_stand)

		# reveal hole card
		self.dealer.reveal()

		# award winnings
		if winner is not True:
			award = 1.5 ** winner._has_blackjack * bet
			winner.award(award)
			loser.winnings -= award

		# report total winnings
		if self.player.winnings < 0:
			sleepprint(f"You are in the red with ${self.dealer.winnings:.2f} in losses.")
		else:
			sleepprint(
				f"Your winnings so far: ${self.player.winnings:.2f}\n"
				"Keep it up!"
			)

	@sleepingpad(.5)
	def push(self):
		print("It's a push!")
		return True, None

	@sleepingpad(.5)
	def win(self, winner):
		print(f"** {winner.name} win{winner.verb_suffix}! **")
		loser = self.dealer if winner is self.player else self.player
		return winner, loser

	def check_win(self, both_stand):
		"""returns the winning player if win found; True if a push; None if no result yet"""

		# both stand
		if both_stand:
			if self.player.score > self.dealer.score:
				return self.win(self.player)
			if self.dealer.score > self.player.score:
				return self.win(self.dealer)
			return self.push()

		# blackjack
		if self.player._has_blackjack:
			if self.dealer._has_blackjack:
				return self.push()
			return self.win(self.player)
		elif self.dealer._has_blackjack:
			return self.win(self.dealer)

		# 21
		if self.player.score == 21:
			if self.dealer.score == 21:
				return self.push()
			return self.win(self.player)
		elif self.dealer.score == 21:
			return self.win(self.dealer)

		# dealer bust
		if self.dealer.score > 21:
			return self.win(self.player)

		# still in play
		return None, None

	@sleepingpad(.25)
	def play(self):
		while self.prompt_play():

			if len(self.deck) <= 10:
				self.deck = Deck()

			self.play_hand()

		print("Thanks for playing!")

	def prompt_play(self):

		user_input = input("\nPress ENTER to play a new hand!")
		sleep(STD_DELAY * .25)

		if user_input == "":
			return True
		elif user_input.lower() != "exit":
			sleepprint("** Not a valid input! **", .25)
			return self.prompt_play()



if __name__ == "__main__":
	game = Game()
	game.play()
