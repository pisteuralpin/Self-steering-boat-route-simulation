# ---------------------------------------------------------------------------- #
#                                 Prompt Module                                #
#                               Mathurin Roulier                               #
# ---------------------------------------------------------------------------- #

"""
This module contains some functions used to prompt the user via the terminal.

menu
----
Displays a menu and asks the user to make a choice among the proposed options.

"""
 
def menu(options:list, question:str="Faites votre choix :") -> tuple[int, str]:
    """Displays a menu and asks the user to make a choice among the proposed options.
    Return the chosen choice and option."""
    
    print(str(question))                                                        # Show the question
    for i in range(len(options)):                                               # For each option
        print(f"{str(i+1)} : {str(options[i])}")                                # Show the option number and the option
    choice=int(input(">>> "))                                                   # Ask the user to make a choice
    if choice <= len(options) and choice >= 0:                                  # If the choice is valid
        print(f"Your choice : {str(options[choice-1])} ({str(choice)})")        # Show the choice
    return choice, options[choice-1]                                            # Return the choice and the option
