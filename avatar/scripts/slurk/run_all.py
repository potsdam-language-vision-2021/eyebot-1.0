import logging 
import time

from avatar.scripts.slurk.game_setup_cli import _setup_game
from avatar.scripts.slurk.game_master_cli import start as start_master
from avatar.scripts.slurk.game_avatar_cli import start as start_avatar

import asyncio
from pyppeteer import launch
import threading


async def one_browser_login(u, p):
    browser = await launch(headless=False, autoClose=False)
    page = await browser.newPage()
    try:
        await page.goto('http://localhost:5000')
        await page.type('#name', u)
        await page.type('#token', p)
        await page.click('#submit')
    except:
        pass
    await browser.disconnect()


async def main(logins):
    await one_browser_login("Master", logins["Master"])
    await asyncio.sleep(2)
    await one_browser_login("Avatar", logins["Avatar"])
    await asyncio.sleep(2)
    await one_browser_login("Player", logins["Player"])


def start_master_thread(logins):
    sio = start_master(logins["Master"], "localhost", None, "5000",
                   "localhost", None, "8000", "None")
    sio.wait()

def start_avatar_thread(logins):
    sio = start_avatar(logins["Avatar"], "localhost", None, "5000", "None")
    sio.wait()    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('websockets').setLevel(logging.INFO)
    logging.getLogger('pyppeteer').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)
    logging.getLogger('socketIO-client').setLevel(logging.INFO)

    # start slurk

    # setup game
    logins = _setup_game("avatar_room", "avatar_game", "avatar_layout", "localhost", "5000", None, "00000000-0000-0000-0000-000000000000")

    # start image server 

    # start master cli
    t_master = threading.Thread(target=start_master_thread,args=(logins,))
    t_master.daemon = True
    t_master.start()
    time.sleep(2)  # sleep so master has time to create room

    # start avatar cli
    t_avatar = threading.Thread(target=start_avatar_thread,args=(logins,))
    t_avatar.daemon = True
    t_avatar.start()    

    task = main(logins)
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task)
        loop.run_forever()
    except KeyboardInterrupt as e:
        task.cancel()
        loop.run_forever()
        task.exception()
    finally:
        loop.close()

    