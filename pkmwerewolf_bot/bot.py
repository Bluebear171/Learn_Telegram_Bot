from mwt import MWT
@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
  """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
  return [admin.user.id for admin in bot.getChatAdministrators(chat_id)]

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

from telegram.ext import Updater
updater = Updater(token='TOKEN')
dispatcher = updater.dispatcher
chat_ids = [-1001076571533]

from collections import defaultdict
player_scores = defaultdict(lambda: 0)

import json
def store_scores(bot, update):
  if not (update.message.chat_id in chat_ids):
    return
  if not (update.message.from_user.id in get_admin_ids(bot, update.message.chat_id)):
    return
  global player_scores
  json.dump(player_scores, open('scores.txt', 'a'))
  with open('scores.txt', 'a') as f:
    f.write('\n')

def display_scores(bot, update):
  scores_string = ""
  for player, score in sorted(player_scores.items()):
    scores_string += "{} {}\n".format(player, score)
  bot.sendMessage(chat_id=update.message.chat_id, text=scores_string)
  store_scores(bot, update)

def start(bot, update):
  print(update.message.chat_id)
  if not (update.message.chat_id in chat_ids):
    return
  if not (update.message.from_user.id in get_admin_ids(bot, update.message.chat_id)):
    return
  global player_scores
  player_scores = defaultdict(lambda: 0)
  bot.sendMessage(chat_id=update.message.chat_id, text="Game Started!")

def add(bot, update):
  if not (update.message.chat_id in chat_ids):
    return
  if not (update.message.from_user.id in get_admin_ids(bot, update.message.chat_id)):
    return
  player_results = update.message.text.split("\n")
  for player_result in player_results:
    if ("戰鬥力 - 萬年蟲" in player_result):
      player = player_result[:player_result.find(':')]
      player_scores[player] += 2
    if ("戰鬥力 - 菊石獸" in player_result):
      player = player_result[:player_result.find(':')]
      player_scores[player] += 1 

  display_scores(bot, update)

def cancel(bot, update):
  if not (update.message.chat_id in chat_ids):
    return
  if not (update.message.from_user.id in get_admin_ids(bot, update.message.chat_id)):
    return
  player_results = update.message.text.split("\n")
  for player_result in player_results:
    if ("戰鬥力 - 萬年蟲" in player_result):
      player = player_result[:player_result.find(':')]
      player_scores[player] -= 2
    if ("戰鬥力 - 菊石獸" in player_result):
      player = player_result[:player_result.find(':')]
      player_scores[player] -= 1 

  display_scores(bot, update)

def set_score(bot, update):
  if not (update.message.chat_id in chat_ids):
    return
  if not (update.message.from_user.id in get_admin_ids(bot, update.message.chat_id)):
    return
  player, score = update.message.text.replace('/set_score_pkm@hkpkm_bot', '').replace('/set_score_pkm', '').strip().split("|||")
  player_scores[player] = score
  bot.sendMessage(chat_id=update.message.chat_id, text=("Score for " + player + " is setted to " + score))

def merge_score(bot, update):
  if not (update.message.chat_id in chat_ids):
    return
  if not (update.message.from_user.id in get_admin_ids(bot, update.message.chat_id)):
    return
  player1, player2 = update.message.text.replace('/merge_score_pkm', '').replace('@hkpkm_bot', '').strip().split('|||')
  if (player1 in player_scores and player2 in player_scores):
    player_scores[player1] = player_scores[player1] + player_scores[player2]
    del player_scores[player2]
  bot.sendMessage(chat_id=update.message.chat_id, text=("Score for " + player1 + " is setted to " + str(player_scores[player1])))

def set_scores(bot, update):
  global player_scores
  player_scores = json.load(open('scores.txt'))
  with open('scores.txt', 'a') as f:
    f.write('\n')
  display_scores(bot, update)

def helper(bot, update):
  description = """
    /start_pkm to start calculating the score(this command will remove all scores)\n
    /add_pkm to add a game result\n
    /cancel_pkm to delete a game result\n
    /scores_pkm to see scores\n
    /set_score_pkm to set player score\n
    /merge_score_pkm to merge two players\n
    /set_scores_pkm to set scores from file\n
  """
  bot.sendMessage(chat_id=update.message.chat_id, text=description)

from telegram.ext import CommandHandler
start_handler = CommandHandler('start_pkm', start)
dispatcher.add_handler(start_handler)
add_handler = CommandHandler('add_pkm', add)
dispatcher.add_handler(add_handler)
cancel_handler = CommandHandler('cancel_pkm', cancel)
dispatcher.add_handler(cancel_handler)
help_handler = CommandHandler('help_pkm', helper)
dispatcher.add_handler(help_handler)
scores_handler = CommandHandler('scores_pkm', display_scores)
dispatcher.add_handler(scores_handler)
set_score_handler = CommandHandler("set_score_pkm", set_score)
dispatcher.add_handler(set_score_handler)
merge_score_handler = CommandHandler("merge_score_pkm", merge_score)
dispatcher.add_handler(merge_score_handler)
set_scores_handler = CommandHandler('set_scores_pkm', set_scores)
dispatcher.add_handler(set_scores_handler)
updater.start_polling()
