from turtle import update
import requests
import bs4
import pandas as pd
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

import functions

def start_bot(toto_url, toto_account, bwin_url, bwin_account):
    updater = Updater("5252457967:AAEkTon66pFdtaImQbrpQynU2dchKWAwdzg",
				use_context=True)

    def start(update: Update, context: CallbackContext):
        update.message.reply_text("What's up my man!")

    def findbet(update: Update, context: CallbackContext):
        update.message.reply_text("Okay! That will take just a minute (58s)...")

        update.message.reply_text("Retrieving data...")
        #Getting soups
        soup_bwin = functions.get_html(bwin_url)
        soup_toto = functions.get_html(toto_url)

        #Getting entries
        df_bwin = functions.get_bwin(soup_bwin)
        df_toto = functions.get_toto(soup_toto)

        update.message.reply_text("Calculating...")
        #Getting factors
        global df_factors
        df_factors = functions.get_factors_update(df_bwin, df_toto)
        
        bets = functions.winning_bet(df_factors.loc[df_factors['Bet'] == True],  toto_account, bwin_account)

        if bets.empty==False:
            bet = (bets[bets.Profit == bets.Profit.max()])
            message = "Bet €"+ str(round(bet.iloc[0,2],2))+" on "+str(bet.iloc[0,0])+"("+str(bet.iloc[0,1])+", "+str(bet.iloc[0,3])+") "+ "and"+" bet €"+ str(round(bet.iloc[0,6],2))+" on "+str(bet.iloc[0,4])+"("+str(bet.iloc[0,5])+""+", "+str(bet.iloc[0,7])+") for a profit of €"+str(round(bet.iloc[0,8],2))
        else:
            message = "Unfortunately, no arbitrage opportunities are found."
        update.message.reply_text(message)



    updater.dispatcher.add_handler(CommandHandler('findbet', findbet))

    def showfactors(update: Update, context: CallbackContext):
        message = df_factors[['Team A', 'Team B', 'Factor']].to_string()
        update.message.reply_text(message)

    def isbadpakgay(update: Update, context: CallbackContext):
        update.message.reply_text("Let me check!")
        update.message.reply_text("Yes he is!")

    def artbot(update: Update, context: CallbackContext):
        update.message.reply_audio(audio=open('/Users/maxsavelkoul/Documents/Projecten/Arbitrage Bot/artbitrage/artbat.mp3', 'rb'))

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('showfactors', showfactors))
    updater.dispatcher.add_handler(CommandHandler('isbadpakgay', isbadpakgay))
    updater.dispatcher.add_handler(CommandHandler('artbot', artbot))

    updater.start_polling()