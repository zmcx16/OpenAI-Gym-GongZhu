# OpenAI Gym GongZhu Card Game
* Implement an OpenAI Gym GongZhu Card Game simulation environment, easy to collect game data to use it in Machine Learning and Reinforcement Learning, the main game logic is fork from https://github.com/danielcorin/Hearts.

# Requirement
```
pip install gym
```

# Demo
```
python run_example.py
```

# Support Agent
* Human
* Random 

# Description
* Use a deck of cards to play (Not Support 拱雙豬).
* All players start with 0 points. The first person go past -1000 points then game over. The player which get highest points is the game winner.
* Any card can be played during the first trick.
* (Exposure cards function is not implement yet.)

# Scoring
* The J♦ (goat) is worth +100 points
* The Q♠ (pig) is worth -100 points
* The 10♣ (transformer) counts as zero points, but doubles your points at the end of a round and adds it to your accumulated points. If at the end of a round, a player has the 10 of clubs and no other point cards, the 10 of clubs is worth +50 points (or +100 if exposed: see below).
* The Hearts are worth -200 points in total:
   Ace -50 points
   King -40 points
   Queen -30 points
   Jack -20 points
   10 through 5 are worth -10 points
   4 through 2 are worth no points
* All other cards are worth 0 points and do not play a part in scoring.
* Shot the moon: If you get all the hearts, you have shot the moon and are awarded +200 points.
* etc...

# Game Flow
1.	env.reset() -> Start Hearts game, env send the GameStart event to all player.
2.	env send NewRound event to all player.
3.	env send ShowPlayerHand event to each player to get the hand cards.
4.  env send PlayTrick event to the player, the player choose a card and send PlayTrick_Action event to env.
5.  env will send ShowTrickAction event to all players to tell them the player's action.
6.  After all players take a card, env will send ShowTrickEnd event to tell the players that which one win this trick.
7.  After last trick, env will send RoundEnd event to announce which player win this round, if the loser's score > max_score, env send GameOver event to all players and exit the game, or send NewRound event to all players to continue game.

# API
* GameStart
```
{
    "event_name" : "GameStart",
    "broadcast" : True,
    "data" : {
        "players" : [
            {'playerName': 'Kazuma'},
            {'playerName': 'Aqua'},
            {'playerName': 'Megumin'},
            {'playerName': 'Darkness'}
        ]
    }

}
```

* NewRound
```
{
    "event_name" : "NewRound",
    "broadcast" : True,
    "data" : {
        "players" : [
            {'playerName': 'Kazuma'
            ,'score': 0},
            {'playerName': 'Aqua'
            ,'score': 0},
            {'playerName': 'Megumin'
            ,'score': 0},
            {'playerName': 'Darkness'
            ,'score': 0}
        ]
    }
}
```

* ShowPlayerHand
```
{
    "event_name" : "ShowPlayerHand",
    "broadcast" : Fasle,
    "data" : {
        'playerName': 'Kazuma', 
        'hand': ['Ac', '6d', '7d', '9d', 'Jd', 'Qd', '3s', '3h', '6h', 'Jh', 'Qh', 'Kh', 'Ah']
    }
}
```

* PlayTrick
```
{
    "event_name" : "PlayTrick",
    "broadcast" : False,
    "data" : {
        'playerName': 'Kazuma', 
        'hand': ['7d', '9d', 'Jd', 'Qd', '3s', '3h', '6h', 'Jh', 'Qh', 'Kh', 'Ah'],
        'trickNum': 3,
        'trickSuit': 's',               //first player this value = "Unset"
        'currentTrick': [
            {'playerName': 'Megumin'
            ,'card': '9s'},
            {'playerName': 'Darkness'
            ,'card': '7s'}
		],
		'IsHeartsBroken': False
    }

}
```

* PlayTrick_Action
```
{
    "event_name" : "PlayTrick_Action",
    "data" : {
        'playerName': 'Kazuma', 
        'action': {'card': '3s'}
    }
}
```

* ShowTrickAction
```
{
    "event_name" : "ShowTrickAction",
    "broadcast" : True,
    "data" : {
        'trickNum': 3,
        'trickSuit': 'c',
        'currentTrick': [
            {'playerName': 'Kazuma'
            ,'card': '3s'},
            {'playerName': 'Megumin'
            ,'card': '9s'},
            {'playerName': 'Darkness'
            ,'card': '7s'}
		],
        'IsHeartsBroken': False
    }
}
```

* ShowTrickEnd
```
{
    "event_name" : "ShowTrickEnd",
    "broadcast" : True,
    "data" : {
        'trickNum': 3,
        'trickWinner': 'Megumin',
        'cards': ['3s', '2s', '9s', '7s'],
		'IsHeartsBroken': False
    }
}
```

* RoundEnd
```
{
    "event_name" : "RoundEnd",
    "broadcast" : True,
    "data" : {
        "players" : [
            {'playerName': 'Kazuma'
            ,'score': 10},
            {'playerName': 'Aqua'
            ,'score': 13},
            {'playerName': 'Megumin'
            ,'score': 3},
            {'playerName': 'Darkness'
            ,'score': 0}
        ],
		'ShootingMoon': False,
        'Round': 3
    }
}
```

* GameOver
```
{
    "event_name" : "GameOver",
    "broadcast" : True,
    "data" : {
        "players" : [
            {'playerName': 'Kazuma'
            ,'score': 0},
            {'playerName': 'Aqua'
            ,'score': 120},
            {'playerName': 'Megumin'
            ,'score': 36},
            {'playerName': 'Darkness'
            ,'score': 26}
        ],
        'Round': 7,
        'Winner': 'Kazuma'
    }
}
```

# Reference
* https://github.com/danielcorin/Hearts

# License
This project is licensed under the terms of the MIT license.