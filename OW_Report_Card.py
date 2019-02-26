from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
import OW_API_Pulls as ow

def run():
    fileName = tkFileDialog.askdirectory()
    print fileName
    userName1 = entry1.get()
    platform1 = platform.get()
    region1 = region.get()
    try:
        ow.createGraphic(str(userName1), str(region1), str(platform1), str(fileName))
    except:
        tkMessageBox.showinfo("Something When Wrong", "Either the account information is incorrect or the requested "
                                                      "account is set to private.")
    return

window = Tk()

window.title("Overwatch Report Card Generator")
window.geometry("228x125")
window.configure(bg="#2F2F2F")

label1 = Label(window, text="Username", bg="#2F2F2F", fg="white", font=("Helvetica", 16), justify=RIGHT)
label1.grid(row=0, column=0)
userName = StringVar()
entry1 = Entry(window, textvariable=userName)
entry1.grid(row=0, column=1)
label2 = Label(window, text="Platform", bg="#2F2F2F", fg="white", font=("Helvetica", 16), justify=RIGHT)
label2.grid(row=1, column=0)

platform = StringVar(window)
platform.set('pc')
option1 = OptionMenu(window, platform, "pc", "ps4", "xbox") ####################
option1.configure(font=('Helvetica',10), width=11, height=1, anchor='w', compound='right')
option1.grid(row=1, column=1)

label3 = Label(window, text="Region", bg="#2F2F2F", fg="white", font=("Helvetica", 16), justify=RIGHT)
label3.grid(row=2, column=0)
region = StringVar()
region.set('us')
option2 = OptionMenu(window, region, "us", "eu", "asia")  #####################
option2.configure(font=('Helvetica',10), width=11, height=1, anchor='w', compound='right')
option2.grid(row=2, column=1)

button1 = Button(window, text="Generate Report Card", width=25, command=run, bg="#D1D1D1", fg="#2F2F2F", font=("Helvetica", 10))
button1.grid(row=5, column=0, sticky=W+E, columnspan=2, padx=2)

window.mainloop()
