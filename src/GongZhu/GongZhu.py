from .Deck import Deck
from .Card import Card, Suit, Rank
from .Player import Player
from .Trick import Trick
from .CommonDef import *

import random
from datetime import datetime
from gym import Env


'''Change auto to False if you would like to play the game manually.'''
'''This allows you to make all passes, and plays for all four players.'''
'''When auto is True, passing is disabled and the computer plays the'''
'''game by "guess and check", randomly trying moves until it finds a'''
'''valid one.'''


totalTricks = 13


class GongZhuEnv(Env):

    def __init__(self, playersName, minScore=-1000):
        
        random.seed(datetime.now())
        
        self.minScore = minScore
        
        self.roundNum = 0
        self.trickNum = 0  # initialization value such that first round is round 0
        self.dealer = -1  # so that first dealer is 0
        self.currentTrick = Trick()
        self.trickWinner = -1
        self.shootingMoon = False
        self.grandSlam = False

        # Make four players

        self.players = [Player(playersName[0]), Player(playersName[1]), Player(playersName[2]), Player(playersName[3])]

        '''
        Player physical locations:
        Game runs counterclockwise

            p3
        p4        p2
            p1

        '''
        
        self.event = None
        self.round = 0
        
        self.renderInfo = {'printFlag': False, 'Msg': ""}

    def _handleScoring(self):
        """
        The Qs (pig) is worth -100 points
        The Jd (goat) is worth +100 points
        The Tc (transformer) counts as zero points, but doubles your points at the end of a round and adds it to your accumulated points. If at the end of a round, a player has the 10 of clubs and no other point cards, the 10 of clubs is worth +50 points.
        
        Hearts:
            Ace -50 points
            King -40 points
            Queen -30 points
            Jack -20 points
            10 through 5 are worth -10 ~ -5 points respectively.
            4 -10 points
            3 -3 points
            2 -2 points
        """
        
        pig_owner = -1
        goat_owner = -1
        transformer_owner = -1

        pig_score = -100
        goat_score = 100
        transformer_score = 50
        
        hearts_score_list = [0] * 15  # Ranks indicated by numbers 2-14, 2-Ace
        for i in range(len(hearts_score_list)):
            hearts_score_list[i] = -1 * i
        
        hearts_score_list[ace] = -50
        hearts_score_list[king] = -40
        hearts_score_list[queen] = -30
        hearts_score_list[jack] = -20
        hearts_score_list[4] = -10
        
        # check shootingMoon and grandSlam
        for current_player_i in range(len(self.players)): 
            heart_num = 0
            for card in self.players[current_player_i].CardsInRound:        
                if card.suit == Suit(hearts):
                    heart_num += 1
                elif card == Card(queen, spades):
                    pig_owner = current_player_i
                elif card == Card(jack, diamonds):
                    goat_owner = current_player_i
                elif card == Card(10, clubs):
                    transformer_owner = current_player_i
                                
            if heart_num == 13:
                self.shootingMoon = True
                for i in range(len(hearts_score_list)):
                    hearts_score_list[i] *= -1
                pig_score *= -1
                goat_score *= -1
                
                if pig_owner == current_player_i and goat_owner == current_player_i and transformer_owner == current_player_i:
                    self.grandSlam = True
                    goat_score *= -1    # all points card become positive.
                    
        
        temp_score_list = [0, 0, 0, 0]
        for current_player_i in range(len(self.players)):
            hasTransformer = False
            for card in self.players[current_player_i].CardsInRound:
                if card.suit == Suit(hearts):
                    temp_score_list[current_player_i] += hearts_score_list[card.rank.rank]
                elif card == Card(queen, spades):
                    temp_score_list[current_player_i] += pig_score
                elif card == Card(jack, diamonds):
                    temp_score_list[current_player_i] += goat_score
                elif card == Card(10, clubs):
                    hasTransformer = True
            
            if hasTransformer:
                if temp_score_list[current_player_i] == 0:
                    temp_score_list[current_player_i] += transformer_score
                else:
                    temp_score_list[current_player_i] *= 2
                
        for current_player_i in range(len(self.players)):
            self.players[current_player_i].score += temp_score_list[current_player_i]
        
        return temp_score_list
    
    @classmethod
    def _handsToStrList(self, hands):
        output = []
        for card in hands:
            output += [str(card)]
        return output

    def _getFirstTrickStarter(self):
        self.trickWinner = random.randint(0, 3)

    def _dealCards(self):
        i = 0
        while(self.deck.size() > 0):
            self.players[i % len(self.players)].addCard(self.deck.deal())
            i += 1

    def _evaluateTrick(self):
        self.trickWinner = self.currentTrick.winner
        p = self.players[self.trickWinner]
        p.trickWon(self.currentTrick.trick)
        #print(self._printCurrentTrick())
        #print (p.name + " won the trick.")

    # print player's hand
    def _printPlayer(self, i):
        p = self.players[i]
        print (p.name + "'s hand: " + str(p.hand))

    # print all players' hands
    def _printPlayers(self):
        for p in self.players:
            print (p.name + ": " + str(p.hand))

    # show cards played in current trick
    def _printCurrentTrick(self):
        trickStr = '\nCurrent table:\n'
        trickStr += "Trick suit: " + self.currentTrick.suit.__str__() + "\n"
        for i, card in enumerate(self.currentTrick.trick):
            if self.currentTrick.trick[i] is not 0:
                trickStr += self.players[i].name + ": " + str(card) + "\n"
            else:
                trickStr += self.players[i].name + ": None\n"
        
        return trickStr

    
    def _getCurrentTrickStrList(self):
        trick_list = []
        for i, card in enumerate(self.currentTrick.trick):
            if self.currentTrick.trick[i] is not 0:
                trick_list += [{'playerName': self.players[i].name, 'card': str(card) }]
        
        return trick_list
        
    def _event_GameStart(self):
        self.event_data_for_server = {}
        self.event_data_for_client \
        = {'event_name': self.event
           , 'broadcast': True
           , 'data': {
               "players" : [
                   {'playerName': self.players[0].name},
                   {'playerName': self.players[1].name},
                   {'playerName': self.players[2].name},
                   {'playerName': self.players[3].name}
                   ]
               }
           }

        for p in self.players:
            p.score = 0
        self.round = 0
    
        self.renderInfo = {'printFlag': False, 'Msg': ""}
        self.renderInfo['printFlag'] = True
        self.renderInfo['Msg'] = '\n*** GongZhu Start ***\n'
    
    def _event_NewRound(self):

        self.deck = Deck()
        self.deck.shuffle()
        self.roundNum += 1
        self.trickNum = 0
        self.trickWinner = -1
        self.shootingMoon = False
        self.grandSlam = False
        self.dealer = (self.dealer + 1) % len(self.players)
        self._dealCards()
        self.currentTrick = Trick()
        self.round += 1
        for p in self.players:
            p.resetRoundCards()
            p.discardTricks()

        self.event_data_for_client \
        =   { "event_name" : self.event,
                "broadcast" : True,
                "data" : {
                    "players" : [
                       {'playerName': self.players[0].name,
                        'score': self.players[0].score},
                       {'playerName': self.players[1].name,
                        'score': self.players[1].score},
                       {'playerName': self.players[2].name,
                        'score': self.players[2].score},
                       {'playerName': self.players[3].name,
                        'score': self.players[3].score},
                       ],
                    'Round': self.round,
                }
            }
 

        self.event = 'ShowPlayerHand'
        self.event_data_for_server = {'now_player_index': 0}

        self.renderInfo['printFlag'] = True
        self.renderInfo['Msg'] = '\n*** Start Round {0} ***\n'.format(self.round)
        for p in self.players:
            self.renderInfo['Msg'] += '{0}: {1}\n'.format(p.name, p.score)

    def _event_ShowPlayerHand(self):

        if self.event_data_for_server['now_player_index'] < 4:
            now_player_index = self.event_data_for_server['now_player_index']
            self.event_data_for_client \
            =   {"event_name" : self.event,
                 "broadcast" : False,
                 "data" : {
                     'playerName': self.players[now_player_index].name,
                     'hand': self._handsToStrList(sum(self.players[now_player_index].hand.hand, []))
                    }
                }
            self.event_data_for_server['now_player_index'] += 1
        
        else:
            self.event = 'PlayTrick'
            self.event_data_for_server = {'shift': 0}
            self._event_PlayTrick()
    
    def _event_PlayTrick(self):
                
        shift = self.event_data_for_server['shift']
        if self.trickNum == 0 and shift == 0:
            self._getFirstTrickStarter()
            current_player = self.players[self.trickWinner]
            
        else:
            current_player_i = (self.trickWinner + shift)%4
            current_player = self.players[current_player_i]
            
        self.event_data_for_client \
        =   { "event_name" : self.event,
                "broadcast" : False,
                "data" : {
                    'playerName': current_player.name,
                    'hand': self._handsToStrList(sum(current_player.hand.hand, [])),
                    'trickNum': self.trickNum+1,
                    'trickSuit': self.currentTrick.suit.__str__(),
                    'currentTrick': self._getCurrentTrickStrList()
                }
            }

    def _event_PlayTrick_Action(self, action_data):
        
        shift = self.event_data_for_server['shift']
        current_player_i = (self.trickWinner + shift)%4
        current_player = self.players[current_player_i]

            
        addCard = current_player.play(action_data['data']['action']['card'])
        if addCard is not None:

            if self.currentTrick.cardsInTrick == 0:
                self.currentTrick.setTrickSuit(addCard)

            # player tries to play off suit but has trick suit
            if addCard.suit != self.currentTrick.suit:
                if current_player.hasSuit(self.currentTrick.suit):
                    print ("Must play the suit of the current trick.")
                    addCard = None

            if addCard is not None:
                current_player.removeCard(addCard)
                self.currentTrick.addCard(addCard, current_player_i)
                self.event_data_for_server['shift'] += 1
                self.event = 'ShowTrickAction'
                self._event_ShowTrickAction()
            else:
                self.event = 'PlayTrick'
                self._event_PlayTrick()
        
        else:
            self.event = 'PlayTrick'
            self._event_PlayTrick()
            
    def _event_ShowTrickAction(self):

        self.renderInfo['printFlag'] = True
        self.renderInfo['Msg'] = "\n" + self._printCurrentTrick()
        
        self.event_data_for_client \
        =   { "event_name" : self.event,
                "broadcast" : True,
                "data" : {
                    'trickNum': self.trickNum+1,
                    'trickSuit': self.currentTrick.suit.__str__(),
                    'currentTrick': self._getCurrentTrickStrList()
                }
            }
        
        if self.currentTrick.cardsInTrick < 4:
            self.event = 'PlayTrick'
        else:
            self.event = 'ShowTrickEnd'
        
    def _event_ShowTrickEnd(self):
        
        self._evaluateTrick()
        
        cards = []
        for card in self.currentTrick.trick:
            cards += [str(card)]
                 
        self.event_data_for_client \
        =   { "event_name" : self.event,
                "broadcast" : True,
                "data" : {
                    'trickNum': self.trickNum+1,
                    'trickWinner': self.players[self.trickWinner].name,
                    'cards': cards
                }
            }

        self.renderInfo['printFlag'] = True
        self.renderInfo['Msg'] = '\n*** Trick {0} ***\n'.format(self.trickNum+1)
        self.renderInfo['Msg'] += 'Winner: {0}\n'.format(self.players[self.trickWinner].name)
        self.renderInfo['Msg'] += 'cards: {0}\n'.format(cards)
        
        self.currentTrick = Trick()
             
        self.trickNum += 1
        if self.trickNum < 13:
            self.event = 'PlayTrick'
            self.event_data_for_server = {'shift': 0}
        else:
            self.event = 'RoundEnd'
            self.event_data_for_server = {}
                
    def _event_RoundEnd(self):

        this_round_score = self._handleScoring()

        self.event_data_for_client \
        =   { "event_name" : self.event,
                "broadcast" : True,
                "data" : {
                    "players" : [
                       {'playerName': self.players[0].name,
                        'roundCard': self._handsToStrList(self.players[0].CardsInRound),
                        'roundScore': this_round_score[0],
                        'score': self.players[0].score},
                       {'playerName': self.players[1].name,
                        'roundCard': self._handsToStrList(self.players[1].CardsInRound),
                        'roundScore': this_round_score[1],
                        'score': self.players[1].score},
                       {'playerName': self.players[2].name,
                        'roundCard': self._handsToStrList(self.players[2].CardsInRound),
                        'roundScore': this_round_score[2],
                        'score': self.players[2].score},
                       {'playerName': self.players[3].name,
                        'roundCard': self._handsToStrList(self.players[3].CardsInRound),
                        'roundScore': this_round_score[3],
                        'score': self.players[3].score},
                       ],
                    'ShootingMoon': self.shootingMoon,
                    'GrandSlam': self.grandSlam,
                    'Round': self.round,
                }
            }

        self.renderInfo['printFlag'] = True
        self.renderInfo['Msg'] = '\n*** Round {0} End ***\n'.format(self.round)
        for p in self.players:
            self.renderInfo['Msg'] += '{0}: {1}\n'.format(p.name, p.score)
            
        self.renderInfo['Msg'] += '\nShootingMoon: {0}\n'.format(self.shootingMoon)
        self.renderInfo['Msg'] += 'GrandSlam: {0}\n'.format(self.grandSlam)
        
        temp_loser = min(self.players, key=lambda x:x.score)
        # new round if no one has lose
        if temp_loser.score > self.minScore:
            self.event = 'NewRound'
            self.event_data_for_server = {}
        else:
            self.event = 'GameOver'
            self.event_data_for_server = {}
        
        reward = {}
        for current_player_i in range(len(self.players)):
            reward[self.players[current_player_i].name] = this_round_score[current_player_i]
        return reward
        
    def _event_GameOver(self):
        
        winner = max(self.players, key=lambda x:x.score)
        
        self.event_data_for_client \
        =   { "event_name" : self.event,
                "broadcast" : True,
                "data" : {
                    "players" : [
                        {'playerName': self.players[0].name,
                         'score': self.players[0].score},
                        {'playerName': self.players[1].name,
                         'score': self.players[1].score},
                        {'playerName': self.players[2].name,
                         'score': self.players[2].score},
                        {'playerName': self.players[3].name,
                         'score': self.players[3].score}
                        ],
                    'Round': self.round,
                    'Winner': winner.name
                }
            }

        self.renderInfo['printFlag'] = True
        self.renderInfo['Msg'] = '\n*** Game Over ***\n'
        for p in self.players:
            self.renderInfo['Msg'] += '{0}: {1}\n'.format(p.name, p.score)
        
        self.renderInfo['Msg'] += '\nRound: {0}\n'.format(self.round)
        self.renderInfo['Msg'] += 'Winner: {0}\n'.format(winner.name)
        
        self.event = None

    def reset(self):
        
        # Generate a full deck of cards and shuffle it
        self.event = 'GameStart'
        self._event_GameStart()
        observation = self.event_data_for_client
        self.event = 'NewRound'
        self.event_data_for_server = {}
        
        return observation
                
    def render(self):
        
        if self.renderInfo['printFlag']:
            print(self.renderInfo['Msg'])
            self.renderInfo['printFlag'] = False
            self.renderInfo['Msg'] = ""
    

        
    def step(self, action_data):
        observation, reward, done, info = None, None, None, None
            
        if self.event == 'NewRound':
            self._event_NewRound()
     
        elif self.event == 'ShowPlayerHand':
            self._event_ShowPlayerHand()

        elif self.event == 'PlayTrick' or self.event == 'ShowTrickAction' or self.event == 'ShowTrickEnd':
            if action_data != None and action_data['event_name'] == "PlayTrick_Action":
                self._event_PlayTrick_Action(action_data)
            else:
                if self.event == 'PlayTrick':
                    self._event_PlayTrick()
                elif self.event == 'ShowTrickEnd':
                    self._event_ShowTrickEnd()
        
        elif self.event == 'RoundEnd':
            reward = self._event_RoundEnd()
            
        elif self.event == 'GameOver':
            self._event_GameOver()
        
        elif self.event == None:
            self.event_data_for_client = None
            done = True


        observation = self.event_data_for_client
        return observation, reward, done, info
