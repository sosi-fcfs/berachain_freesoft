from contracts.BeraStake import BeraStake
from contracts.BeraMultiSwap import BeraMultiSwap
from contracts.BeraAddLiquidity import BeraAddLiquidity

from contracts.BeraStakeStone import StakeStone

from models.accounts import Accounts
from contracts.faucet import Faucet
from models.coins import Coins

from utils.first_message import first_message
from core.client import Client
from utils.logs import logger
from config import *

import threading, time, random


def start_farming(accounts):
    clients = [Client(account) for account in accounts]
    timeouts = {}

    while True:
        time.sleep(10)
        random.shuffle(clients)
        for i, client in enumerate(clients):
            try:
                acc_name = client.acc_name

                if acc_name not in timeouts:
                    timeouts[acc_name] = int(time.time() + random.randint(*delay_start) * (i+1))

                if time.time() >= timeouts[acc_name]:
                    logger.info(f"{acc_name} запуск..")
                    threading.Thread(target=client.start).start()
                    timeouts[acc_name] = int(time.time() + random.randint(*delay_staking))

            except Exception as e:
                logger.error(e)

def check_balances_bgt(accounts):
    def check_balance(account):
        while True:
            try:
                bera = BeraStake(account)
                logger.info(f"{bera.acc_name} - {round(bera.token_balance(coins.BGT.address), 6)} {coins.BGT.coin}")
                break
            except Exception as e:
                logger.error(e)
                time.sleep(5)

    coins = Coins()
    for account in accounts:
        threading.Thread(target=check_balance, args=(account,)).start()

def stakestone_eth(accounts):
    for account in accounts:
        client = StakeStone(account)
        for i in range(10):
            try:
                if ref_code: client.referal(ref_code)
                client.stake(amount_stakestone_eth)
                time.sleep(random.randint(*delay_actions))
                break
            except Exception as err:
                logger.error(f"{client.acc_name} {err}")
                time.sleep(10)

def main():
    accounts_manager = Accounts()
    accounts_manager.loads_accs()
    accounts = accounts_manager.accounts

    action = input("> 1. Запустить фарминг\n"
                   "> 2. Посмотреть балансы BGT\n"
                   "> 3. Застейкать MAINNET ETH на StakeStone\n"
                   "> ")

    print("-"*50+"\n")

    if action == "1":
        start_farming(accounts)
    elif action == "2":
        check_balances_bgt(accounts)
    elif action == "3":
        stakestone_eth(accounts)
    else:
        logger.warning(f"Выбран вариант, которого нет!")

if __name__ == '__main__':
    first_message()
    main()



