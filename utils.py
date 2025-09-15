import discord
import random
from FlightRadar24.api import FlightRadar24API

fr_api = FlightRadar24API()

popular_words = open("/home/admin/FlightTracker/dict-popular.txt").read().splitlines()
all_words = set(word.strip() for word in open("/home/admin/FlightTracker/dict-sowpods.txt"))

EMOJI_CODES = {
    "gray": {
        "a":"<:1f1e6:941170970146779218>",
        "b":"<:1f1e7:941170970159353887>", 
        "c":"<:1f1e8:941170970578812999>", 
        "d":"<:1f1e9:941170970528456705>", 
        "e":"<:1f1ea:941170970671054888>", 
        "f":"<:1f1eb:941170970654294066>", 
        "g":"<:1f1ec:941170970662678538>", 
        "h":"<:1f1ed:941170970629136404>", 
        "i":"<:1f1ee:941170970629144597>", 
        "j":"<:1f1ef:941170971052748800>", 
        "k":"<:1f1f0:941170970645913641>", 
        "l":"<:1f1f1:941170970608140378>", 
        "m":"<:1f1f2:941170970595565628>", 
        "n":"<:1f1f3:941170970352316458>", 
        "o":"<:1f1f4:941170970671071302>", 
        "p":"<:1f1f5:941170970515886080>", 
        "q":"<:1f1f6:941170970562031676>", 
        "r":"<:1f1f7:941170970557841429>", 
        "s":"<:1f1f8:941170970578796554>", 
        "t":"<:1f1f9:941170970654289970>", 
        "u":"<:1f1fa:941170970662670336>", 
        "v":"<:1f1fb:941170970578812929>", 
        "w":"<:1f1fc:941170970490699786>", 
        "x":"<:1f1fd:941170970515865680>", 
        "y":"<:1f1fe:941170970314563647>", 
        "z":"<:1f1ff:941170970578800660>"
    },
    "green": {
        "a":"<:1f1e6:941228571115024395>",
        "b":"<:1f1e7:941228570930450453>",
        "c":"<:1f1e8:941228570959831071>",
        "d":"<:1f1e9:941228571358281770>",
        "e":"<:1f1ea:941228571245031455>",
        "f":"<:1f1eb:941228571265990676>",
        "g":"<:1f1ec:941228571266023434>",
        "h":"<:1f1ed:941228571370856448>",
        "i":"<:1f1ee:941228570917879819>",
        "j":"<:1f1ef:941228571257602069>",
        "k":"<:1f1f0:941228571358281779>",
        "l":"<:1f1f1:941228571328938054>",
        "m":"<:1f1f2:941228571035336736>",
        "n":"<:1f1f3:941228571245043723>",
        "o":"<:1f1f4:941228571349884978>",
        "p":"<:1f1f5:941228571307958322>",
        "q":"<:1f1f6:941228571307946024>",
        "r":"<:1f1f7:941228571261808640>",
        "s":"<:1f1f8:941228571286970399>",
        "t":"<:1f1f9:941228571341512734>",
        "u":"<:1f1fa:941228571370848296>",
        "v":"<:1f1fb:941228571165347861>",
        "w":"<:1f1fc:941228571568005131>",
        "x":"<:1f1fd:941228571307966514>",
        "y":"<:1f1fe:941228570922086421>",
        "z":"<:1f1ff:941228571106631693>"
    },
    "yellow": {
        "a":"<:1f1e6:941171158689144902>",
        "b":"<:1f1e7:941171158814953492>",
        "c":"<:1f1e8:941171158726869032>",
        "d":"<:1f1e9:941171158684942346>",
        "e":"<:1f1ea:941171158697512980>",
        "f":"<:1f1eb:941171158655594557>",
        "g":"<:1f1ec:941171158894669854>",
        "h":"<:1f1ed:941171159238606858>",
        "i":"<:1f1ee:941171159314083880>",
        "j":"<:1f1ef:941171159133736991>",
        "k":"<:1f1f0:941171159146315786>",
        "l":"<:1f1f1:941171159460888586>",
        "m":"<:1f1f2:941171159196639292>",
        "n":"<:1f1f3:941171159167299656>",
        "o":"<:1f1f4:941171158760439853>",
        "p":"<:1f1f5:941171159154700318>",
        "q":"<:1f1f6:941171159251165184>",
        "r":"<:1f1f7:941171159142137877>",
        "s":"<:1f1f8:941171159263760455>",
        "t":"<:1f1f9:941171158924009553>",
        "u":"<:1f1fa:941171159226007582>",
        "v":"<:1f1fb:941171159209226310>",
        "w":"<:1f1fc:941171158873702421>",
        "x":"<:1f1fd:941171159188258837>",
        "y":"<:1f1fe:941171158965972993>",
        "z":"<:1f1ff:941171159368601682>"
        }
}


def generate_colored_word(guess: str, answer: str) -> str:
    """
    Builds a string of emoji codes where each letter is
    colored based on the key:
    - Same letter, same place: Green
    - Same letter, different place: Yellow
    - Different letter: Gray
    Args:
        word (str): The word to be colored
        answer (str): The answer to the word
    Returns:
        str: A string of emoji codes
    """
    colored_word = [EMOJI_CODES["gray"][letter] for letter in guess]
    guess_letters = list(guess)
    answer_letters = list(answer)
    # change colors to green if same letter and same place
    for i in range(len(guess_letters)):
        print(guess_letters[i])
        if guess_letters[i] == answer_letters[i].lower():
            colored_word[i] = EMOJI_CODES["green"][guess_letters[i]]
            answer_letters[i] = None
            guess_letters[i] = None
    # change colors to yellow if same letter and not the same place
    for i in range(len(guess_letters)):
        if guess_letters[i] is not None and guess_letters[i].upper() in answer_letters:
            colored_word[i] = EMOJI_CODES["yellow"][guess_letters[i]]
            answer_letters[answer_letters.index(guess_letters[i].upper())] = None
    return "".join(colored_word)

def generate_blanks() -> str:
    """
    Generate a string of 5 blank white square emoji characters
    Returns:
        str: A string of white square emojis
    """
    return "\N{WHITE MEDIUM SQUARE}" * 3

def generate_puzzle_embed(user: discord.User, puzzle_id: int, ctx) -> discord.Embed:
    embed = discord.Embed(title="Airportle")
    embed.description = "\n".join([generate_blanks()] * 6)
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(
        text=f"ID: {puzzle_id} ︱ To play, use the command /play!\n"
        "To guess, reply to this message!"
    )
    return embed

async def update_embed(embed: discord.Embed, guess: str, message: discord.Message) -> discord.Embed:
    """
    Updates the embed with the new guesses
    Args:
        embed (discord.Embed): The embed to be updated
        puzzle_id (int): The puzzle ID
        guess (str): The guess made by the user
    Returns:
        discord.Embed: The updated embed
    """
    puzzle_id = int(embed.footer.text.split()[1])
    answer = popular_words[puzzle_id]
    colored_word = generate_colored_word(guess, answer)
    empty_slot = generate_blanks()
    # replace the first blank with the colored word
    embed.description = embed.description.replace(empty_slot, colored_word, 1)
    # check for game over
    num_empty_slots = embed.description.count(empty_slot)
    res = await fr_api.get_airport(answer)
    try:
        name = res['name']
        country = res['position']['country']['name']
        city = res['position']['region']['city']
    except:
        name = "Not Available"
        country = "Not Available"
        city = "Not Available"
    if guess == answer.lower():
        await message.reply(f"Great job! You got the correct airport: ``{name}({answer})`` which is in ``{city}, {country}``!")
        if num_empty_slots == 0:
            embed.description += "\n\nPhew!"
        if num_empty_slots == 1:
            embed.description += "\n\nGreat!"
        if num_empty_slots == 2:
            embed.description += "\n\nSplendid!"
        if num_empty_slots == 3:
            embed.description += "\n\nImpressive!"
        if num_empty_slots == 4:
            embed.description += "\n\nMagnificent!"
        if num_empty_slots == 5:
            embed.description += "\n\nGenius!"
    elif num_empty_slots == 0:
        embed.description += f"\n\nThe answer was ``{name}({answer})`` which is in ``{city}, {country}``!"
    return embed


def is_valid_word(word: str) -> bool:
    """
    Validates a word
    Args:
        word (str): The word to validate
    Returns:
        bool: Whether the word is valid
    """
    if word in all_words:
        return True
    else:
        return False



def random_puzzle_id() -> int:
    """
    Generates a random puzzle ID
    Returns:
        int: A random puzzle ID
    """
    return random.randint(0, len(popular_words) - 1)


def is_game_over(embed: discord.Embed) -> bool:
    """
    Checks if the game is over in the embed
    Args:
        embed (discord.Embed): The embed to check
    Returns:
        bool: Whether the game is over
    """
    return "\n\n" in embed.description
