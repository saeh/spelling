from gtts import gTTS
import os
import random

from time import sleep

def load_word_list() -> list[str]:
    """Load the word list from file.

    Returns:
        list[str]: A list of spelling words
    """
    with open("words.txt", "r") as fp:
        data = fp.read()
    return data.split("\n")


def create_sound_file(word: str) -> str:
    """Turn a word into a sound file

    Args:
        word (str): The word to put into a sound file

    Returns:
        str: The filename of the soundfile created
    """
    myobj = gTTS(text=word, lang="en", slow=False)
    fname = f"word_files/{word}.mp3"
    myobj.save(fname)
    return fname


def play_word_sound(fname: str) -> None:
    """Play the sound file

    Args:
        fname (str): The filename of the audio to play
    """
    os.system(f"afplay {fname}")


def game_loop_one_word(word: str, fname: str) -> bool:
    
    play_word_sound(fname)
    print("----------------------------------------------------------")
    print("At the prompt enter your spelling of the word just played")
    print("Input '?' to replay the sound of the word")
    print("----------------------------------------------------------")
    user_input = input(">")

    if user_input == "?":
        print("Replaying Sound")
        play_word_sound(fname)
        user_input = input(">")

    if user_input == word:
        # Win
        print(f"Correct! - {word}")
        return True
    else:
        print(f"Wrong! You spelled {user_input}. It should be {word}")
        return False




if __name__ == "__main__":
    words = load_word_list()
    
    # 10 Word loop
    score: int = 0
    results: dict[str, list[str]] = {"correct": [], "wrong": []}
    for i in range(10):
        word = random.choice(words)
        fname = create_sound_file(word)
        word_result = game_loop_one_word(word, fname)
        if word_result:
            score += 1
            results["correct"].append(word)
        else:
            results["wrong"].append(word)
        sleep(3)
