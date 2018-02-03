from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application import Platform, Base, Games, User

engine = create_engine('sqlite:///gamescatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

User1 = User(name="me", email="chefweller@gmail.com",
             picture='https://beebom-redkapmedia.netdna-ssl.com/wp-content/uploads/2016/01/Reverse-Image-Search-Engines-Apps-And-Its-Uses-2016.jpg')
session.add(User1)
session.commit()
# Games for PC
platform1 = Platform(name="PC")

session.add(platform1)
session.commit()

game1 = Games(user_id=1, name="PUBG", description="PlayerUnknown's Battlegrounds is a multiplayer online battle royale video game developed by PUBG Corporation, a subsidiary of Korean publisher Bluehole",
              price="$30.00", genre="Battle Royale", platform=platform1)

session.add(game1)
session.commit()


game2 = Games(user_id=1, name="Overwatch", description="Overwatch is a team-based multiplayer online first-person shooter video game developed and published by Blizzard Entertainment. It was released in May 2016 for Windows",
              price="$40.00", genre="Hero Shooter", platform=platform1)

session.add(game2)
session.commit()

game3 = Games(user_id=1, name="Getting Over It", description="Getting Over It with Bennett Foddy is a video game developed by QWOP creator Bennett Foddy. The game was released as part of the October 2017 Humble Monthly, on October 6, 2017",
              price="TBD", genre="Puzzle", platform=platform1)

session.add(game3)
session.commit()

game4 = Games(user_id=1, name="Leage of Legends", description="League of Legends is a multiplayer online battle arena video game developed and published by Riot Games for Microsoft Window",
              price="0.00", genre="MOBA", platform=platform1)

session.add(game4)
session.commit()

# Games for Xbox
platform2 = Platform(name="XBOX ONE")

session.add(platform2)
session.commit()


game1 = Games(user_id=1, name="Cuphead", description="Cuphead is a run and gun indie video game developed and published by StudioMDHR. As the title character Cuphead, the player fights a series of bosses in order to repay a debt to the devil",
              price="20.00", genre="Platformer", platform=platform2)

session.add(game1)
session.commit()

game2 = Games(
    user_id=1, name="Forza 7", description="Forza Motorsport 7 is a racing video game developed by Turn 10 Studios and published by Microsoft Studios, serving as the tenth installment in the Forza series", price="$40", genre="Racing", platform=platform2)

session.add(game2)
session.commit()

game3 = Games(user_id=1, name="Ori and the Blind forest", description="Ori and the Blind Forest is a platform-adventure MetrHalo Wars 2 is a real-time strategy video game developed by 343 Industries and Creative Assembly",
              price="20.00", genre="Platformer", platform=platform2)

session.add(game3)
session.commit()

game4 = Games(user_id=1, name="Halo Wars 2", description="Halo Wars 2 is a real-time strategy video game developed by 343 Industries and Creative Assembly",
              price="40.00", genre="RTS", platform=platform2)

session.add(game4)
session.commit()

# Games for Playstation 4
platform3 = Platform(name="Playstation 4")

session.add(platform3)
session.commit()


game1 = Games(user_id=1, name="Horizon Zero Dawn", description="Horizon Zero Dawn is an action role-playing video game developed by Guerrilla Games and published by Sony Interactive Entertainment for PlayStation 4 ",
              price="$40.00", genre="ARPG", platform=platform3)

session.add(game1)
session.commit()

game2 = Games(user_id=1, name="Uncharted the lost legacy", description="Uncharted: The Lost Legacy is an action-adventure game developed by Naughty Dog and published by Sony Interactive Entertainment",
              price="$40.00", genre="Action", platform=platform3)

session.add(game2)
session.commit()

game3 = Games(user_id=1, name="Persona 5", description="Persona 5 is a role-playing video game developed by Atlus for the PlayStation 3 and PlayStation 4 video game console",
              price="$40.00", genre="JRPG", platform=platform3)

session.add(game3)
session.commit()

game4 = Games(user_id=1, name="Destiny 2", description="Destiny 2 is an online-only multiplayer first-person shooter video game developed by Bungie and published by Activisio",
              price="$50.00", genre="MMOFPS", platform=platform3)

session.add(game4)
session.commit()

# Games for Nintendo SWitch
platform4 = Platform(name="NINTENDO SWITCH ")

session.add(platform4)
session.commit()

game1 = Games(user_id=1, name="Super Mario Odyssey", description="Super Mario Odyssey is a 3D platform video game developed and published by Nintendo for the Nintendo Switc",
              price="$55.00", genre="Platformer", platform=platform4)

session.add(game1)
session.commit()

game2 = Games(user_id=1, name="Splatoon 2", description="Splatoon 2 is a team-based third-person shooter video game developed and published by Nintendo for the Nintendo Switch",
              price="$55.00", genre="TPOMS", platform=platform4)


session.add(game2)
session.commit()

game3 = Games(user_id=1, name="The Legend of Zelda: Breath of the wild", description="The Legend of Zelda: Breath of the Wild is an action-adventure game developed and published by Nintendo for the Nintendo Switch and Wii U video game console",
              price="$55.00", genre="ARPG", platform=platform4)

session.add(game3)
session.commit()

game4 = Games(user_id=1, name="Mario Kart 8: Deluxe", description="Mario Kart 8 is a kart racing video game and the eighth major installment in the Mario Kart series, developed and published by Nintendo",
              price="$55.00", genre="Racing", platform=platform4)

session.add(game4)
session.commit()

print "added new games!"
