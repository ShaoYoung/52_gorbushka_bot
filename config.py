from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Желательно вместо str использовать SecretStr
    # для конфиденциальных данных, например, токена бота
    bot_token: SecretStr

    # Начиная со второй версии pydantic, настройки класса настроек задаются через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан с кодировкой UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# При импорте файла сразу создастся и провалидируется объект конфига, который можно далее импортировать из разных мест
config = Settings()

#
# Macro
#
# 🔵🔴🟠🟡🟢🟣🟤
macro = dict()
macro.update({"белый": chr(9898)})
macro.update({"белая": chr(9898)})
macro.update({"Белый": chr(9898)})
macro.update({" white": chr(9898)})
macro.update({" White": chr(9898)})
macro.update({" WHITE": chr(9898)})
macro.update({"серебристый": chr(9898)})
macro.update({"серебристый": chr(9898)})
macro.update({" silver": chr(9898)})
macro.update({" Silver": chr(9898)})
macro.update({" SILVER": chr(9898)})
macro.update({" cream": chr(9898)})
macro.update({" Cream": chr(9898)})
macro.update({" beige": chr(9898)})
macro.update({" Beige": chr(9898)})
macro.update({" Glow": chr(9898)})

macro.update({"чёрный": chr(9899)})
macro.update({"чёрная": chr(9899)})
macro.update({"Чёрный": chr(9899)})
macro.update({" black": chr(9899)})
macro.update({" Black": chr(9899)})
macro.update({" BLACK": chr(9899)})
macro.update({" midnight": chr(9899)})
macro.update({" Midnight": chr(9899)})
macro.update({" graphite": chr(9899)})
macro.update({" Graphite": chr(9899)})
macro.update({" серый": chr(9899)})
macro.update({" Серый": chr(9899)})
macro.update({" grey": chr(9899)})
macro.update({" Grey": chr(9899)})
macro.update({" GREY": chr(9899)})

macro.update({" olive": chr(0x1FAD2)})
macro.update({" Olive": chr(0x1FAD2)})

macro.update({"зелёный": chr(0x1F7e2)})
macro.update({"зелёная": chr(0x1F7e2)})
macro.update({"Зелёный": chr(0x1F7e2)})
macro.update({" green": chr(0x1F7e2)})
macro.update({" Green": chr(0x1F7e2)})
macro.update({" GREEN": chr(0x1F7e2)})

macro.update({" lime": chr(0x1F7e2)})
macro.update({" Lime": chr(0x1F7e2)})
macro.update({" LIME": chr(0x1F7e2)})

macro.update({" mint": chr(0x1F7e2)})
macro.update({" Mint": chr(0x1F7e2)})
macro.update({" MINT": chr(0x1F7e2)})

macro.update({"красный": chr(0x1F534)})
macro.update({"красная": chr(0x1F534)})
macro.update({"Красный": chr(0x1F534)})
macro.update({" red": chr(0x1F534)})
macro.update({" Red": chr(0x1F534)})
# macro.update( {" RED"       :chr(0x1F534)} )
macro.update({" Burgundy": chr(0x1F534)})

macro.update({"синий": chr(0x1F535)})
macro.update({"синяя": chr(0x1F535)})
macro.update({"Синий": chr(0x1F535)})
macro.update({" blue": chr(0x1F535)})
macro.update({" Blue": chr(0x1F535)})
macro.update({" BLUE": chr(0x1F535)})
macro.update({"синий нептун": chr(0x1F535)})

macro.update({"голубой": chr(0x1F535)})
macro.update({"Голубой": chr(0x1F535)})
macro.update({" lightblue": chr(0x1F535)})
macro.update({" Lightblue": chr(0x1F535)})
macro.update({" LightBlue": chr(0x1F535)})

macro.update({"оранжевый": chr(0x1F7e0)})
macro.update({"Оранжевый": chr(0x1F7e0)})
macro.update({" orange": chr(0x1F7e0)})
macro.update({" Orange": chr(0x1F7e0)})
macro.update({" ORANGE": chr(0x1F7e0)})

macro.update({"золотой": chr(0x1F7e0)})
macro.update({"Золотой": chr(0x1F7e0)})
macro.update({" gold": chr(0x1F7e0)})
macro.update({" Gold": chr(0x1F7e0)})
macro.update({" GOLD": chr(0x1F7e0)})

macro.update({"жёлтый": chr(0x1F7e1)})
macro.update({"Жёлтый": chr(0x1F7e1)})
macro.update({" yellow": chr(0x1F7e1)})
macro.update({" Yellow": chr(0x1F7e1)})
macro.update({" YELLOW": chr(0x1F7e1)})
macro.update({"песочный": chr(0x1F7e1)})
macro.update({"песочная": chr(0x1F7e1)})

macro.update({"фиолетовый": chr(0x1F7e3)})
macro.update({"Фиолетовый": chr(0x1F7e3)})
macro.update({" violet": chr(0x1F7e3)})
macro.update({" Violet": chr(0x1F7e3)})
macro.update({" VIOLET": chr(0x1F7e3)})

macro.update({" lavender": chr(0x1F7e3)})
macro.update({" Lavender": chr(0x1F7e3)})
macro.update({" lavanda": chr(0x1F7e3)})
macro.update({" Lavanda": chr(0x1F7e3)})
macro.update({" LAVANDA": chr(0x1F7e3)})

macro.update({" lavender": chr(0x1F7e3)})
macro.update({" Lavender": chr(0x1F7e3)})

macro.update({" purple": chr(0x1F7e3)})
macro.update({" Purple": chr(0x1F7e3)})
macro.update({" PURPLE": chr(0x1F7e3)})

macro.update({"коричневый": chr(0x1F7e4)})
macro.update({"Коричневый": chr(0x1F7e4)})
macro.update({" brown": chr(0x1F7e4)})
macro.update({" Brown": chr(0x1F7e4)})
macro.update({" BROWN": chr(0x1F7e4)})

macro.update({"розовый": chr(0x1F338)})
macro.update({"Розовый": chr(0x1F338)})
macro.update({" pink": chr(0x1F338)})
macro.update({" Pink": chr(0x1F338)})
macro.update({" PINK": chr(0x1F338)})

macro.update({" natural": chr(0x2699)})
macro.update({" Natural": chr(0x2699)})
macro.update({" NATURAL": chr(0x2699)})

macro.update({" starlight": chr(0x1F31F)})
macro.update({" Starlight": chr(0x1F31F)})
macro.update({" StarLight": chr(0x1F31F)})

# 👗
macro.update({"бирюзовый": chr(0x1F457)})
macro.update({"бирюзовая": chr(0x1F457)})

# ⌚️
macro.update({"Часы": chr(0x231A)})
macro.update({"часы": chr(0x231A)})
# 🔌
macro.update({"СЗУ": chr(0x1F50C)})
# 🔋
macro.update({"АКБ": chr(0x1F50B)})
# 🖊
macro.update({"PEN": chr(0x1F58A)})
macro.update({"стилус": chr(0x1F58A)})
# Наушники- 🎼🎧
macro.update({"наушники": str(chr(0x1F3BC)) + str(chr(0x1F3A7))})
# Колонка- 🔊🎼
macro.update({"колонка": str(chr(0x1F50A)) + str(chr(0x1F3BC))})
# 🎤
macro.update({"микрофон": chr(0x1F3A4)})
# 🎮
macro.update({"игра": chr(0x1F3AE)})
# 💿
macro.update({"диск": chr(0x1F4BF)})
# Клавиатура -⌨️
macro.update({"клавиатура": chr(0x2328)})
# 📦
macro.update({"коробка": chr(0x1F4E6)})
# 💦
macro.update({"[WR]": chr(0x1F4A6)})
# 🔨
macro.update({"[Shock]": chr(0x1F528)})
# Apple 🍎
macro.update({"apple": chr(0x1F34E)})
macro.update({"Apple": chr(0x1F34E)})
macro.update({"APPLE": chr(0x1F34E)})
macro.update({"iphone": chr(0x1F34E)})
macro.update({"iPhone": chr(0x1F34E)})
macro.update({"IPHONE": chr(0x1F34E)})
# ;-💎
# macro.update( {";"          :chr(0x1F48E) } )
# ‼️
macro.update({"[!]": chr(0x203C)})
# {-❤️
macro.update({"[{]": chr(0x2764)})
# ⚡️
macro.update({"[~]": chr(0x26A1)})
# 🔥
macro.update({"[^]": chr(0x1F525)})
# 💥
macro.update({"[X]": chr(0x1F4A5)})
# ⭐️
macro.update({"[*]": chr(0x2B50)})
# 🧊
macro.update({"[-]": chr(0x1F9CA)})
# 💻
macro.update({"[.]": chr(0x1F4BB)})
# 📹
macro.update({"[o]": chr(0x1F4F9)})
# 💎
macro.update({"[&]": chr(0x1F48E)})
# 🔮
macro.update({"[@]": chr(0x1F52E)})
# 📍
macro.update({"[V]": chr(0x1F4CD)})
# % -🚛
macro.update({"%.": chr(0x1F69B)})
# G 📲
macro.update({"G.": chr(0x1F4F2)})
# T- 📺
macro.update({"T.": chr(0x1F4FA)})
# X-📱
macro.update({"X.": chr(0x1F4F1)})
# O-♻️
macro.update({"O.": chr(0x267B)})
# H-❇️
macro.update({"H.": chr(0x2747)})
# Кабель -🌀
macro.update({"Кабель": chr(0x1F300)})
macro.update({"кабель": chr(0x1F300)})
# фото-📸
macro.update({"фото": chr(0x1F4F8)})
# S-💠
macro.update({"S.": chr(0x1F4A0)})
# M-Ⓜ️
macro.update({"M.": chr(0x24C2)})
# I-✳️
macro.update({"I.": chr(0x2733)})
# D-💜
macro.update({"D.": chr(0x1F49C)})
# P-🔷
macro.update({"P.": chr(0x1F537)})
# R-🍋
macro.update({"R.": chr(0x1F34B)})
# F-📳
macro.update({"F.": chr(0x1F4F3)})
# U-⭕️
macro.update({"U.": chr(0x2B55)})
# N-🔢
macro.update({"N.": chr(0x1F522)})
# Home-🏠
macro.update({"Home": chr(0x1F3E0)})
# J.🪝
macro.update({"J.": chr(0x1FA9D)})
# L.-🔘
macro.update({"L.": chr(0x1F518)})
# решётка-#⃣
macro.update({"решётка": chr(0x23) + chr(0x20E3)})
macro.update({"Решётка": chr(0x23) + chr(0x20E3)})
# new -🆕
macro.update({"new": chr(0x1F195)})
macro.update({"New": chr(0x1F195)})

#
# RU EN CH rst
#
macro.update({" RU ": " " + chr(0x1F1F7) + chr(0x1F1FA) + " "})
macro.update({" EU ": " " + chr(0x1F1EA) + chr(0x1F1FA) + " "})
macro.update({" CN ": " " + chr(0x1F1E8) + chr(0x1F1F3) + " "})
macro.update({" US ": " " + chr(0x1F1FA) + chr(0x1F1F8) + " "})
macro.update({" LLA ": " " + chr(0x1F1FA) + chr(0x1F1F8) + " "})
macro.update({" KZ ": " " + chr(0x1F1F0) + chr(0x1F1FF) + " "})
macro.update({" JP ": " " + chr(0x1F1EF) + chr(0x1F1F5) + " "})
macro.update({" HK ": " " + chr(0x1F1ED) + chr(0x1F1F0) + " "})


