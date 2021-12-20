class System:
    def Clear():
        from platform import platform; from os import system
        system('cls') if platform().startswith('Windows') else system('clear')