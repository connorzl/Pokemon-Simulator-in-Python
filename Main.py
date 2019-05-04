from tkinter import *
from Application import Application
from ApplicationAutomated import ApplicationAutomated

# Creating a window from the application class
def main():
    root = Tk()
    root.title("Pokemon Battle")
    root.geometry("670x500")

    app = Application(root)
    #app = ApplicationAutomated(root)
    root.mainloop()

main()