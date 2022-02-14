from importlib.resources import path
import requests
import bs4
import pandas as pd
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_html(url, badpak):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1080")

    if badpak:
        driver = webdriver.Chrome(path)
    else:
        driver = webdriver.Chrome(r'/Users/maxsavelkoul/Documents/Projecten/Arbitrage Bot/artbitrage')
    driver.get(url)

    time.sleep(15)
    # exception for toto
    try:
        driver.find_element_by_xpath(
            "//*[@id='main-content-region']/div/div/div/div/div/main/section[1]/div[4]/div[2]/div/div/div[2]/div/article/div/div/div[1]/article/div[2]/div/div[2]/div/div[2]/div/a").click()
        time.sleep(8)
    except:
        pass

    content = driver.page_source
    driver.quit()
    return bs4.BeautifulSoup(content, features="html.parser")


# Data collection for BWIN
def get_bwin(soup):
    away_teams = []
    home_teams = []
    A_odds = []
    B_odds = []

    for element in soup.find_all('div', {'class': 'grid-event-wrapper'}):

        # teamnames
        both = element.find_all('div', {'class': 'participants-pair-game'})
        fixture = []
        for team in both:
            text = team.text
            lst = text.split(' @  ')
        try:
            teamA = lst[0][1:]
            teamB = lst[1]
        except:
            teamA = 'N/A'
            teamB = 'N/A'
        # Odds
        all_nums = element.find_all('ms-option-group', {'class': 'grid-option-group grid-group'})
        nums = []
        for num in all_nums:
            nums.append(num.text)
        try:
            teamA_odds = nums[2][:-4]
            teamB_odds = nums[2][4:]
        except:
            teamA_odds = 'N/A'
            teamB_odds = 'N/A'

        # For df
        away_teams.append(teamA)
        home_teams.append(teamB)
        A_odds.append(teamA_odds)
        B_odds.append(teamB_odds)

    # Putting into df
    df = pd.DataFrame({'Team A': away_teams, 'Team B': home_teams, 'Odds A': A_odds, 'Odds B': B_odds})

    return df


# Data collection for Toto
def get_toto(soup):
    away_teams = []
    home_teams = []
    A_odds = []
    B_odds = []
    for element in soup.find_all('div', {'class': 'event-list__item__content'}):

        # teamnames
        both = element.find_all('div', {'class': 'event-card__body__name'})
        for team in both:
            text = team.text
            lst = text.split('Tegen')
        try:
            teamA = lst[1]
            teamB = lst[0]
        except:
            teamA = 'N/A'
            teamB = 'N/A'
        # Odds
        all_nums = element.find_all('span', {'class': 'button--outcome__price'})
        nums = []
        for num in all_nums:
            nums.append(num.text)
        try:
            teamA_odds = nums[3]
            dec_A = teamA_odds.split(',')
            teamA_odds = '.'.join(dec_A)
            teamB_odds = nums[2]
            dec_B = teamB_odds.split(',')
            teamB_odds = '.'.join(dec_B)
        except:
            teamA_odds = 'N/A'
            teamB_odds = 'N/A'

        # For df
        away_teams.append(teamA)
        home_teams.append(teamB)
        A_odds.append(teamA_odds)
        B_odds.append(teamB_odds)

    # Putting into df
    df = pd.DataFrame({'Team A': away_teams, 'Team B': home_teams, 'Odds A': A_odds, 'Odds B': B_odds})
    df.apply(lambda x: x.str.replace(',', '.'))

    return df

#Updated function of get_factor that uses inner join
def get_factors_update(df_bwin, df_toto):
    df_factorresult = pd.DataFrame()
    df_full = pd.merge(df_bwin, df_toto, how='inner',on=['Team A', 'Team B'])

    for index, game in df_full.iterrows():

        team_A = game['Team A']
        team_B = game['Team B']
        if game['Odds A_x']>=game['Odds A_y']:
            odd_A = float(game['Odds A_x'])
            website_A = 'BWIN'
        else:
            odd_A = float(game['Odds A_y'])
            website_A = 'TOTO'
        if game['Odds B_x']>=game['Odds B_y']:
            odd_B = float(game['Odds B_x'])
            website_B = 'BWIN'
        else:
            odd_B = float(game['Odds B_y'])
            website_B = 'TOTO'
        
        factor = 1/odd_A+1/odd_B
        bet = factor<1

        game_row = {'Team A': team_A, 'Website A': website_A, 'Odd A': odd_A, 'Team B': team_B, 'Website B':website_B, 'Odd B':odd_B, 'Factor': factor, "Bet":bet}
        df_factorresult=df_factorresult.append(game_row, ignore_index=True)
    return df_factorresult

def get_factors(df_bwin, df_toto):
    team_A = []
    team_B = []
    high_A =[]
    web_A = []
    high_B = []
    web_B = []

    ##getting highest odds A
    for team in df_bwin['Team A']:
        for team_toto in df_toto['Team A']:
            if team == team_toto:
                team_A.append(team)
                odds_bwin = list(df_bwin[df_bwin['Team A'] == team]['Odds A'].reset_index(drop=True))[0]
                odds_toto = list(df_toto[df_toto['Team A'] == team]['Odds A'].reset_index(drop=True))[0]

                try:
                    highest = 0
                    highest = max(odds_bwin, odds_toto)
                    high_A.append(float(highest))

                    if highest == odds_bwin:
                        web_A.append('BWIN')

                    else:
                        web_A.append('TOTO')

                except:
                    high_A.append('N/A')
                    web_A.append('N/A')

            else:
                pass

    ##getting highest odds B
    for team in df_bwin['Team B']:
        for team_toto in df_toto['Team B']:
            if team == team_toto:
                team_B.append(team)
                odds_bwin = list(df_bwin[df_bwin['Team B'] == team]['Odds B'])[0]
                odds_toto = list(df_toto[df_toto['Team B'] == team]['Odds B'])[0]

                try:
                    #highest = 0
                    highest = max(odds_bwin, odds_toto)
                    high_B.append(float(highest))

                    if highest == odds_bwin:
                        web_B.append('BWIN')

                    else:
                        web_B.append('TOTO')

                except:
                    high_B.append('N/A')
                    web_B.append('N/A')

            else:
                pass


    #Dataframe output
    df_final = pd.DataFrame({'Team A' : team_A, 'Odds A' : high_A, 'Website A': web_A,  'Team B' : team_B, 'Odds B' : high_B, 'Website B': web_B})

    ##Enabling calculation
    df_final = df_final.astype({'Odds A' : np.float, 'Odds B' : np.float})

    ##Determining Factor
    conditions = [(df_final['Website A'] != df_final['Website B']), (df_final['Website A'] == df_final['Website B'])]
    values = [(1/df_final['Odds A'])+(1/df_final['Odds B']), 530]

    df_final['Factor'] = np.select(conditions, values)

    ##Determining whether to bid
    conds2 = [(df_final['Factor']<1), df_final['Factor']>=1]
    vals2 = [1,0]

    df_final['Bid (y/n)'] = np.select(conds2, vals2)

    return df_final




def winning_bet(df, balance_toto, balance_bwin):

    df_bets = pd.DataFrame()

    balance_ratio_toto_bwin = balance_toto/balance_bwin
    for index, winner in df.iterrows():
        odd_A = winner['Odd A']
        odd_B = winner['Odd B']

        A_par = 1/odd_A
        B_par = 1/odd_B

        por_A = A_par/(A_par+B_par)
        por_B = (1-por_A)

        #right amount
        if balance_toto>=balance_bwin:
            if winner['Website A']=='BWIN':
                bet_A = balance_bwin
                bet_B = (balance_bwin/por_A)*por_B
            if winner['Website A']=='TOTO':
                bet_B = balance_bwin
                bet_A = (balance_bwin/por_B)*por_A
        elif balance_toto<balance_bwin:
            if winner['Website A'] == 'BWIN':
                bet_B = balance_toto
                bet_A = (balance_toto / por_B) * por_A
            if winner['Website A'] == 'TOTO':
                bet_A = balance_toto
                bet_B = (balance_bwin / por_A) * por_B
        else:
            print("Something is wrong with the account balances.")

        profit = odd_A*bet_A-bet_A-bet_B

        df_winning_bet = {'TeamA': winner['Team A'], 'OddA':odd_A,'AmountA': bet_A, 'SiteA': winner['Website A'], 'TeamB': winner['Team B'], 'OddB':odd_B,'AmountB': bet_B, 'SiteB': winner['Website B'], 'Profit': profit}
        df_bets = df_bets.append(df_winning_bet, ignore_index=True)

    return df_bets

