#imported libraries
import bdb
from distutils import command
from fileinput import hook_encoded
from queue import Empty
import re
import tkinter
import tkinter as tk
from tkinter import *
from tkinter import ttk
from turtle import home, width
from xml.dom import WrongDocumentErr
from PIL import Image, ImageTk
import pandas as pd
import webbrowser

#defining tkinter root with title and size
root = tk.Tk()
root.title("NY Tourism")
root.geometry("1200x700")
#root.resizable(False, False)

# Reading Tourism data from excel file into a data frame
tourismData = pd.read_excel("TourismExcel.xlsx", skiprows=1)

# variables to hold the filter options and its index 
attractionListContents = ["Sightseeing", "Landmark", "Parks", "Entertainment", "Nature", "Shopping", "Restaurant", "Aquariums and Zoos", "Museums", "Beaches"]
attractionListIndexed = []
locationListContents = ["Manhattan", "Bronx", "Staten Island", "Liberty Island", "Long Island", "Brooklyn", "Queens"]
locationListIndexed = []
audienceListContents = ["Kids", "Groups", "Couples", "Rainy Day"]
audienceListIndexed = []
isFree = tk.BooleanVar()
isFree.set(False)
timeListContents = [8, 4, 2, 1]
timeListIndexed = []

# variable to hold the user selected filter options
selectedAttractions = []
selectedLocations = []
selectedAudiences = []
selectedTimes = []

# call back function onclick of attraction website URL
def open_url(event):
    txtString = event.widget.cget("text")
    txtList = txtString.split(": ")
    url = txtList[1]
    webbrowser.open_new_tab(url)

# prepares index for select option checkbox
def listIndexes(listname, indexedlist):      
    for element in range(len(listname)):
        # Append int variables for each checkbox
        option = IntVar()
        option.set(0)
        indexedlist.append(option)

# call listIndexes for each attribute list
listIndexes(attractionListContents, attractionListIndexed)
listIndexes(locationListContents, locationListIndexed)
listIndexes(audienceListContents, audienceListIndexed)
listIndexes(timeListContents, timeListIndexed)

# This is the callback function for the "Submit" button
# 1. First it gathers all the selected options from the check buttons into lists
# 2. Then it calls the filterResults function to filter and show the final results
def processSelectedOptions():

    # clear 
    selectedAttractions.clear()
    for i in range(len(attractionListIndexed)):
        if attractionListIndexed[i].get()>=1:
            selectedAttractions.append(attractionListContents[i])

    selectedLocations.clear()
    for i in range(len(locationListIndexed)):
        if locationListIndexed[i].get()>=1:
            selectedLocations.append(locationListContents[i])

    selectedAudiences.clear()
    for i in range(len(audienceListIndexed)):
        if audienceListIndexed[i].get()>=1:
            selectedAudiences.append(audienceListContents[i])

    selectedTimes.clear()
    for i in range(len(timeListIndexed)):
        if timeListIndexed[i].get()>=1:
            selectedTimes.append(timeListContents[i])

    makeResultFrame()

# This function makes the frame for the results to be displayed in
def makeResultFrame():
    resultFrame = tk.Frame(root, bg = "#c9e4ff", highlightthickness=5, highlightbackground="navy")
    resultFrame.place(rely=0.180, relx=0.385, relheight=0.79, relwidth=0.595)

    resultCanvas = Canvas(resultFrame)
    resultCanvas.pack(side=LEFT, fill="both", expand="yes")

    # Add Scrollbar to the result frame
    yscrollbar = ttk.Scrollbar(resultFrame, orient="vertical", command=resultCanvas.yview) 
    yscrollbar.pack(side = RIGHT, fill = "y")

    resultCanvas.config(bg = "#c9e4ff", yscrollcommand=yscrollbar.set)

    canvasFrame = Frame(resultCanvas, bg = "#c9e4ff")
    resultCanvas.create_window((0,0), window = canvasFrame, anchor="nw")

    resultCanvas.bind('<Configure>', lambda e: resultCanvas.config(scrollregion= resultCanvas.bbox('all')))
    
    label = tkinter.Label(canvasFrame, text="FILTER RESULTS", bg = "#c9e4ff", font = "Arial, 20 bold", fg ="navy")
    label.pack(pady=2)

    spaceFrame = tkinter.Frame(canvasFrame, width=700, height=1)
    spaceFrame.pack()
    filterResults(canvasFrame)

#This function uses the selected attributes and filters the results from the data frame 
def filterResults(canvasFrame):
    global tourismData

    if (len(selectedLocations)==0 and len(selectedAttractions) == 0 and len(selectedAudiences) == 0 and len(selectedTimes) == 0 and isFree.get()!=True):
        label = tkinter.Label(canvasFrame, text="Please select one or more filter option!",bg="#c9e4ff", font="Arial, 20 bold", fg ="navy")
        label.pack()
        return

    # Make dataframes for holding intermediate results
    resultDataFrame = tourismData
    locationDataFrame = pd.DataFrame()
    typesDataFrame = pd.DataFrame()
    audienceDataFrame = pd.DataFrame()
    timeDataFrame = pd.DataFrame()
    freeDataframe = pd.DataFrame()

    # Filter result for selected location
    if len(selectedLocations) > 0:
        for location in selectedLocations:
            results = resultDataFrame[(location == resultDataFrame["Location"])]
            locationDataFrame = locationDataFrame.append(results)
        resultDataFrame = locationDataFrame

    # Filter result for selected attraction
    index = 0
    if len(selectedAttractions) > 0:
        while index < len(selectedAttractions):
            results = resultDataFrame[(resultDataFrame[selectedAttractions[index]] == "yes")]
            typesDataFrame = typesDataFrame.append(results)
            index+=1
        resultDataFrame = typesDataFrame

    # Filter result for selected audience
    if len(selectedAudiences) > 0:
        for element in selectedAudiences:
            results = resultDataFrame[resultDataFrame["Good For"].str.contains(element)]
            audienceDataFrame = audienceDataFrame.append(results)
        resultDataFrame = audienceDataFrame

    # Filter result for selected time
    if len(selectedTimes) > 0:
        for time in selectedTimes:
            results = resultDataFrame[(resultDataFrame["Hours"]).le(time)]
            timeDataFrame = timeDataFrame.append(results)
        resultDataFrame = timeDataFrame

    # Filter result for free
    if isFree.get():
        results = resultDataFrame[(resultDataFrame["Free"] == "yes")]
        freeDataframe = freeDataframe.append(results)
        resultDataFrame = freeDataframe

    # Drop dupicates if any due place that falls into multiple selected attributes
    resultDataFrame = resultDataFrame.drop_duplicates()

    # If the final data frame is empty, 
    # this section of code goes to the most previously filtered data frame 
    # to get as accurate as possible results from the selections
    # these results wont be exactly what the user wanted, 
    # but will satisfy some of the user selections
    if resultDataFrame.empty:
        resultDataFrame = timeDataFrame
        lab = tkinter.Label(canvasFrame, text="We could find exactly what you wanted,\nbut here's some things you may enjoy!", bg = "#c9e4ff", font = "Arial, 20 bold", fg ="navy")
        lab.pack()
        if resultDataFrame.empty :
            resultDataFrame = audienceDataFrame
            if resultDataFrame.empty:
                resultDataFrame = typesDataFrame
                if resultDataFrame.empty:
                    resultDataFrame = locationDataFrame

    
    # Makes lists of desired collumns for displaying data
    placeNamesList = resultDataFrame["Place Name"]
    placeNamesList = list(placeNamesList)
    locationList = resultDataFrame["Location"]
    locationList = list(locationList)
    audienceList = resultDataFrame["Good For"]
    audienceList = list(audienceList)
    urlList = resultDataFrame["URL"]
    urlList = list(urlList)
    resultDataFrame = resultDataFrame.reset_index(drop = True)
    # print(resultDataFrame)

    types = (resultDataFrame == "yes").apply(lambda y: resultDataFrame.columns[y.tolist()].tolist(), axis = 1).to_dict()

    index = 0

    # Gets info for displaying current attraction/place
    while len(placeNamesList) > index:
        place = placeNamesList[index]
        filters = types.get(index)
        filters = ", ".join(filters)
        location = locationList[index]
        audience = audienceList[index]
        url = urlList[index]

        index += 1

        # Displays the Results and extra information in a Label            
        resultslabel = tkinter.Label(canvasFrame, text = ("\nPlace Name: " + place), bg = "#c9e4ff", font = 'Arial 19 bold', fg ="navy")
        resultslabel.pack(anchor = "w")
        resultslabel = tkinter.Label(canvasFrame, text = ("Types: " + filters), bg = "#c9e4ff", font = 'Arial 16', fg ="navy")
        resultslabel.pack(anchor = "w")
        resultslabel = tkinter.Label(canvasFrame, text = ("Location: " + location), bg = "#c9e4ff", font = 'Arial 16', fg ="navy")
        resultslabel.pack(anchor = "w")
        resultslabel = tkinter.Label(canvasFrame, text = ("Good For: " + audience ), bg = "#c9e4ff", font = 'Arial 16', fg ="navy")
        resultslabel.pack(anchor = "w")
        label= Label(canvasFrame, text="Click the URL for More Info: "+ url, cursor= "hand2", foreground= "indigo", bg = "#c9e4ff", font= ('Arial 16'))
        label.pack(anchor="w")
        # Bind the label with the URL to open in a new tab
        label.bind("<Button-1>", open_url)

#This function creates the frame that holds the check buttons and submit button
def createAttractionTab(): #function for tab to click on for attractions
    tab()
    frame2 = tk.Frame(root, bg = "#c9e4ff", highlightthickness=5, highlightbackground="navy")
    frame2.place(rely=0.180, relx=0.015, relwidth=0.356789, relheight=0.79, anchor="nw")
    label = tk.Label(frame2, text="FILTER OPTIONS", bg = "#c9e4ff", font = "Arial, 20 bold", fg ="navy")
    label.pack(pady=2)


    label = Label(frame2, text='TYPE OF ATTRACTION', bg = "#c9e4ff", font = "Arial, 15 bold")
    label.configure(foreground="Navy")
    label.place(relx=0, rely=0.075)
    check_Sightseeing = tkinter.Checkbutton(frame2, text = 'Sightseeing', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[0],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.12)

    check_Landmark = tkinter.Checkbutton(frame2, text = 'Landmark', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[1],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.165)

    check_Parks = tkinter.Checkbutton(frame2, text = 'Parks', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[2],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.21)

    check_Entertainment= tkinter.Checkbutton(frame2, text = 'Entertainment', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[3],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.255)

    check_Nature= tkinter.Checkbutton(frame2, text = 'Nature', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[4],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.30)

    check_Shopping= tkinter.Checkbutton(frame2, text = 'Shopping', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[5],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.345)

    check_Restaurant= tkinter.Checkbutton(frame2, text = 'Restaurant', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[6],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.39)

    check_AquaandZoos= tkinter.Checkbutton(frame2, text = 'Aquariums and Zoos', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[7],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.435)

    check_Museums= tkinter.Checkbutton(frame2, text = 'Museums', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[8],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.48)

    check_Beaches= tkinter.Checkbutton(frame2, text = 'Beaches', font = "Arial, 13 bold", bg = "#c9e4ff", variable = attractionListIndexed[9],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.525)


    label = Label(frame2, text='TARGET AUDIENCE', bg = "#c9e4ff", font = "Arial 15 bold")
    label.configure(foreground="Navy")
    label.place(relx=0, rely=0.615)
    check_Good4Kids= tkinter.Checkbutton(frame2, text = 'Good For Kids', font = "Arial, 13 bold", bg = "#c9e4ff", variable = audienceListIndexed[0],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.66)

    check_Good4BigGroups= tkinter.Checkbutton(frame2, text = 'Good for Big Groups', font = "Arial, 13 bold", bg = "#c9e4ff", variable = audienceListIndexed[1],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.705)

    check_Good4Couples= tkinter.Checkbutton(frame2, text = 'Good for Couples', font = "Arial, 13 bold", bg = "#c9e4ff", variable = audienceListIndexed[2],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.75)

    check_Good4RainyDay= tkinter.Checkbutton(frame2, text = 'Good for Rainy Day', font = "Arial, 13 bold", bg = "#c9e4ff", variable = audienceListIndexed[3],
            onvalue = 1, offvalue = 0).place(relx=0, rely=0.795)


    label = Label(frame2, text='LOCATION', bg = "#c9e4ff", font = "Arial 15 bold")
    label.configure(foreground="Navy")
    label.place(relx=0.55, rely=0.075)
    check_Manhattan = tkinter.Checkbutton(frame2, text = "Manhattan", font = "Arial, 13 bold", bg = "#c9e4ff", variable = locationListIndexed[0],
            onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.12)
    
    check_Bronx = tkinter.Checkbutton(frame2, text = "Bronx", font = "Arial, 13 bold", bg = "#c9e4ff", variable = locationListIndexed[1],
            onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.165)

    check_Statisland = tkinter.Checkbutton(frame2, text = "Staten Island", font = "Arial, 13 bold", bg = "#c9e4ff", variable = locationListIndexed[2],
            onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.21)

    check_LongIsland = tkinter.Checkbutton(frame2, text = "Long Island", font = "Arial, 13 bold", bg = "#c9e4ff", variable = locationListIndexed[4],
            onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.255)

    check_Brooklyn = tkinter.Checkbutton(frame2, text = "Brooklyn", font = "Arial, 13 bold", bg = "#c9e4ff", variable = locationListIndexed[5],
    onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.3)

    check_Queens = tkinter.Checkbutton(frame2, text = "Queens", font = "Arial, 13 bold", bg = "#c9e4ff", variable = locationListIndexed[6],
    onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.345)

    label = Label(frame2, text='FREE', bg = "#c9e4ff", font = "Arial 15 bold")
    label.configure(foreground="Navy")
    label.place(relx=0.55, rely=0.435)
    check_Free = tkinter.Checkbutton(frame2, text = "Free", font = "Arial, 13 bold", bg = "#c9e4ff", variable = isFree, 
    onvalue = True, offvalue= False).place(relx=0.55, rely=0.48)

    label = Label(frame2, text='TIME', bg = "#c9e4ff", font = "Arial 15 bold")
    label.configure(foreground="Navy")
    label.place(relx=0.55, rely=0.58)
    check_FullDay = tkinter.Checkbutton(frame2, text = "Full Day", font = "Arial, 13 bold", bg = "#c9e4ff", variable = timeListIndexed[0],
    onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.625)

    check_Half2FullDay = tkinter.Checkbutton(frame2, text = "Half Day to Full Day", font = "Arial, 13 bold", bg = "#c9e4ff", variable = timeListIndexed[1],
    onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.67)

    check_2plus = tkinter.Checkbutton(frame2, text = "2+ Hours", font = "Arial, 13 bold", bg = "#c9e4ff", variable = timeListIndexed[2],
    onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.715)

    check_1plus = tkinter.Checkbutton(frame2, text = "1+ Hours", font = "Arial, 13 bold", bg = "#c9e4ff", variable = timeListIndexed[3],
    onvalue = 1, offvalue = 0).place(relx=0.55, rely=0.76)

    submitbutton = tkinter.Button(frame2, text = "SUBMIT", fg="navy", font="Arial 30 bold", highlightthickness=5, highlightbackground="#c9e4ff", command=processSelectedOptions)
    submitbutton.place(relx=0, rely=0.9, relwidth=1.0, relheight=0.1)


#fuction for default window
def tab():
    backGroundFrame = tk.Frame(root)
    backGroundFrame.place(relwidth=1, relheight=1)
    backGroundImage = Image.open('nycimage1.jpg')
    backGroundImage = backGroundImage.resize((1500, 1000), Image.ANTIALIAS)
    backGroundImage = ImageTk.PhotoImage(backGroundImage)

    photo_label = tk.Label(backGroundFrame, image=backGroundImage)
    photo_label.image = backGroundImage
    photo_label.pack()
    
    frame = tk.Frame(root, bg = "#c9e4ff", bd=10, highlightthickness=5, highlightbackground="navy")
    frame.place(rely=0.09, relx=0.5, anchor="center" ,relwidth=0.97, relheight=0.16)

    label = tk.Label(frame, text='NEW YORK TOURIST ATTRACTIONS', font = "Arial, 40 bold")
    label.configure(foreground="navy", background="#c9e4ff")
    label.place(relx=0.5, rely=0.3, anchor="center")

    homeButton = tk.Button(frame, text = "HOME", fg="navy", font="Arial 25 bold", highlightthickness=5, highlightbackground="#c9e4ff", command=tab)
    homeButton.place(relx=0, rely=0.6, relheight=0.4, relwidth=0.5, anchor="nw")

    attractionButton = tk.Button(frame, text = "FIND ATTRACTIONS", fg="navy", font="Arial 25 bold", highlightthickness=5, highlightbackground="#c9e4ff", command=createAttractionTab)
    attractionButton.place(relx=0.5, rely=0.6, relheight=0.4, relwidth=0.5, anchor="nw")

    frameMessage= tk.Frame(root, bg = "#c9e4ff", highlightthickness=5, highlightbackground="navy", width=670, height=200)
    frameMessage.pack(pady = 200, anchor="center")

    label = tk.Label(frameMessage, text='NEW YORK HAS SO MUCH TO OFFER! \nCLICK FIND ATTRACTIONS TO DISCOVER THE BEST THINGS TO DO FOR YOU \nON YOUR DAY IN NEW YORK', font = "Arial, 20 bold")
    label.configure(foreground="navy", background="#c9e4ff")
    label.pack()


tab()
root.mainloop()