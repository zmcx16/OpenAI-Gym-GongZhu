# OpenAI Gym GongZhu Card Game
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9779d56fea3c4fc7aa03b4c783ae0f17)](https://www.codacy.com/app/zmcx16/OpenAI-Gym-GongZhu?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=zmcx16/OpenAI-Gym-GongZhu&amp;utm_campaign=Badge_Grade)

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
* Use one deck of cards to play (Not Support 拱雙豬).
* Players take turns to play a card in an counterclockwise direction and whoever produces the card of the largest value in the same suit collects all four cards and becomes the next dealer.
* Any card can be played during the first trick.
* All players start with 0 points. The first person go past -1000 points then game over. The player which get highest points is the game winner.
* (Exposure cards function is not implement yet.)

# Scoring
* The Q♠ (pig) is worth -100 points
* The J♦ (goat) is worth +100 points
* The 10♣ (transformer) counts as zero points, but doubles your points at the end of a round and adds it to your accumulated points. If at the end of a round, a player has the 10 of clubs and no other point cards, the 10 of clubs is worth +50 points.
* The Hearts are worth -200 points in total:
    - Ace is worth -50 points
    - King is worth -40 points
    - Queen is worth -30 points
    - Jack is worth -20 points
    - 10 through 5 are worth -10 ~ -5 points respectively.
    - 4 is worth -10 points
    - 3 is worth -3 points
    - 2 is worth -2 points
* All other cards are worth 0 points and do not play a part in scoring.
* Shot the moon(全紅&豬羊變色): If you get all the hearts, you have shot the moon and are awarded +200 points(all Hearts become positive points), and J♦ (goat) become -100 points, Q♠ (pig) become 100 points(豬羊變色).
* Grand Slam(大滿貫): If you get all the points cards(All Hearts, goat, pig and transformer), all scores are into positive points, you can get（200 + 100 + 100）* 2 = +800 points.

# Game Flow
1.	env.reset() -> Start Hearts game, env send the GameStart event to all player.
2.	env send NewRound event to all player.
3.	env send ShowPlayerHand event to each player to get the hand cards.
4.  env send PlayTrick event to the player, the player choose a card and send PlayTrick_Action event to env.
5.  env will send ShowTrickAction event to all players to tell them the player's action.
6.  After all players take a card, env will send ShowTrickEnd event to tell the players that which one win this trick.
7.  After last trick, env will send RoundEnd event to announce which player win this round, if the loser's score < min_score, env send GameOver event to all players and exit the game, or send NewRound event to all players to continue game.

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
        ],
        'Round': 10
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
            ,'roundCard': ['Jh', '7h', 'Th', '2c', 'Jd', '4d', '6d', '8d', 'Kh', '3h', 'Qh', 'Js', 'Ad', '4h', '3s', '2d', '9s', '8s', '4s', '2s']
            ,'roundScore': -20
            ,'score': -495},
            {'playerName': 'Aqua'
            ,'roundCard': ['Jc', 'Kc', '6c', 'Qc', '8c', 'Tc', '9c', '5c', '7d', '7c', '3c', '4c', '8h', 'Ah', '9h', 'Qd', '7s', 'Ac', 'Ks', 'As', 'Td', '6h', '5h', '9d']
            ,'roundScore': -156
            ,'score': -318},
            {'playerName': 'Megumin'
            ,'roundCard': ['Ts', '6s', 'Qs', '5s']
            ,'roundScore': -100
            ,'score': -1009},
            {'playerName': 'Darkness'
            ,'roundCard': ['5d', '3d', '2h', 'Kd']
            ,'roundScore': -2
            ,'score': -827},
        ],
		'ShootingMoon': False,
        'GrandSlam': False,
        'Round': 10
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
            ,'score': -495},
            {'playerName': 'Aqua'
            ,'score': -318},
            {'playerName': 'Megumin'
            ,'score': -1009},
            {'playerName': 'Darkness'
            ,'score': -827}
        ],
        'Round': 10,
        'Winner': 'Aqua'
    }
}
```

# Reference
* https://github.com/danielcorin/Hearts

# License
This project is licensed under the terms of the MIT license.