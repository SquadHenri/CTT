class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# How to use:
# print(Color.BOLD + "This text will be bold" + Color.GREEN + "This text will be bold and green" + Color.END + "This text will be normal")
# It is important to always use Color.END to stop with all modifications.