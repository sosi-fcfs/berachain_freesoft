from art import text2art
from rich.console import Console

def first_message():
    console = Console()
    console.print(text2art("BERACHAIN", font="tarty1"), style="rgb(235,160,63)")

    print("-"*50+"\n")
