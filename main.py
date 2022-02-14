def main():
    """ Main program """
    import functions
    import telegrambot
    #komt dit in de testbranch
    #Defining urls (Basketball US)
    toto_url = 'https://sport.toto.nl/wedden/5/basketbal/wedstrijden?preselectedFilters=19'
    bwin_url = 'https://sports.bwin.com/en/sports/basketball-7/betting/north-america-9'

    #Master script
    toto_account = 504
    bwin_account = 700

    telegrambot.start_bot(toto_url, toto_account, bwin_url, bwin_account)
    return 0

if __name__ == "__main__":
    main()