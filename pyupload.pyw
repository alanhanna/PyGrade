# -*- coding: utf-8 -*-
"""
tkinter-based application for uploading assessment feedback to canvas
"""

import os
import json
import base64
from datetime import datetime
import pandas as pd

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import StringVar
from tkinter.ttk import Notebook
import tkinter.scrolledtext as scrolledtext

from pandastable import Table

#Integration with canvas
#pip install canvasapi
from canvasapi import Canvas as cvs

#Turn off warning for now
pd.options.mode.chained_assignment = None 


#------------------------------------------------------------------------------
class CanvasConfig(tk.Frame):
  
    def __init__(self, parent, owner):
      tk.Frame.__init__(self, parent)
      
      self.config = {}
      self.owner = owner
      self.df = pd.DataFrame()
      
      self.apikey = None
      self.courseid = None
      self.assignmentid = None
      
      self.apirul = "https://canvas.qub.ac.uk/"
      self.delimiter = ","
      
      self.f1 = tk.Frame(self, bd=0)
      self.f1.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
      self.f1.columnconfigure(0, weight=1)
      self.f1.rowconfigure(0, weight=1)
      
      self.lblapiurl = tk.Label(self.f1, text="API URL", anchor='w')
      self.lblapiurl.grid(row = 0, column = 0, sticky = 'w', pady=5, padx = 2)
      
      self.lblcanvasapikey = tk.Label(self.f1, text="API Key", anchor='w')
      self.lblcanvasapikey.grid(row = 1, column = 0, sticky = 'w', pady=5, padx = 2)
      
      self.lblmodulenumber = tk.Label(self.f1, text="Canvas Course id", anchor='w')
      self.lblmodulenumber.grid(row =2, column = 0, sticky = 'w', pady=5, padx = 2)
      
      self.lblassignmentnumber = tk.Label(self.f1, text="Canvas Assignment id", anchor='w')
      self.lblassignmentnumber.grid(row = 3, column = 0, sticky = 'w', pady=5, padx = 2)
      
      self.lblfolder = tk.Label(self.f1, text="Assignment Directory", anchor='w')
      self.lblfolder.grid(row = 4, column = 0, sticky = 'w', pady=5, padx = 2)
      
      self.lblfile = tk.Label(self.f1, text="Feedback File", anchor='w')
      self.lblfile.grid(row = 5, column = 0, sticky = 'w', pady=5, padx = 2)
      
      self.svapiurl = StringVar()
      self.svapiurl.set(self.apirul)
      w = tk.Entry(self.f1, width=5, justify='left', textvariable=self.svapiurl)
      w.grid(row = 0, column = 1, columnspan =2, sticky = 'we', pady=5, padx = 2)
      
      self.svapikey = StringVar()
      y = tk.Entry(self.f1, width=5, justify='left', textvariable=self.svapikey)
      y.grid(row = 1, column = 1, columnspan =2, sticky = 'we', pady=5, padx = 2)
      
      self.svmodulenumber = StringVar()
      w = tk.Entry(self.f1, width=5, justify='left', textvariable=self.svmodulenumber)
      w.grid(row = 2, column = 1, columnspan =2, sticky = 'we', pady=5, padx = 2)
      
      self.svassignmentnumber = StringVar()
      x = tk.Entry(self.f1, width=5, justify='left', textvariable=self.svassignmentnumber)
      x.grid(row = 3, column = 1, columnspan =2, sticky = 'we', pady=5, padx = 2)
      
      self.lblfolderselected = tk.Label(self.f1, text="...", anchor='w')
      self.lblfolderselected.grid(row = 4, column = 1, sticky = 'w', pady=5, padx = 2)
      
      self.lblfileselected = tk.Label(self.f1, text="...", anchor='w')
      self.lblfileselected.grid(row = 5, column = 1, sticky = 'w', pady=5, padx = 2)
      
      self.btnfolder = tk.Button(self.f1, text="...", anchor='e')
      self.btnfolder.grid(row=4, column=3, padx=5, sticky='w')
      self.btnfolder.bind("<Button-1>", self.selectfolder)
      self.btnfolder.columnconfigure(3, weight=0)
      
      self.btnfile = tk.Button(self.f1, text="...", anchor='e')
      self.btnfile.grid(row=5, column=3, padx=5, sticky='w')
      self.btnfile.bind("<Button-1>", self.selectfile)
      self.btnfile.columnconfigure(3, weight=0)
      
      self.f1.columnconfigure(0, weight=0)
      self.f1.columnconfigure(1, weight=1)
      self.f1.columnconfigure(2, weight=1)
      
      self.f2 = tk.Frame(self, bd=0)
      self.f2.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
      self.f2.columnconfigure(0, weight=0)
      self.f2.rowconfigure(0, weight=0)
      
      self.rowconfigure(0, weight=0)
      self.columnconfigure(0, weight=1)
      
      self.btnconfig = tk.Button(self.f2, text="Load Config", anchor='e')
      self.btnconfig.grid(row=4, column=0, padx=5, sticky='w')
      self.btnconfig.bind("<Button-1>", self.loadconfig)
      
      self.btnconfig = tk.Button(self.f2, text="Save Config", anchor='e')
      self.btnconfig.grid(row=4, column=1, padx=5, sticky='w')
      self.btnconfig.bind("<Button-1>", self.saveconfig)
      
      self.btnconnect = tk.Button(self.f2, text="Connect", anchor='e')
      self.btnconnect.grid(row=4, column=2, padx=5, sticky='w')
      self.btnconnect.bind("<Button-1>", self.connect)
      
      self.btnmapfiles = tk.Button(self.f2, text="Map files", anchor='e')
      self.btnmapfiles.grid(row=4, column=3, padx=5, sticky='w')
      self.btnmapfiles.bind("<Button-1>", self.mapfiles)
      
      self.btnupload = tk.Button(self.f2, text="Upload Files", anchor='e')
      self.btnupload.grid(row=4, column=4, padx=5, sticky='w')
      self.btnupload.bind("<Button-1>", self.uploadfiles)
      
      self.btnmapfeedback = tk.Button(self.f2, text="Map feedback", anchor='e')
      self.btnmapfeedback.grid(row=4, column=5, padx=5, sticky='w')
      self.btnmapfeedback.bind("<Button-1>", self.mapfeedback)
      
      self.btnuploadfeedback = tk.Button(self.f2, text="Upload feedback", anchor='e')
      self.btnuploadfeedback.grid(row=4, column=6, padx=5, sticky='w')
      self.btnuploadfeedback.bind("<Button-1>", self.uploadfeedback)
      
      self.overwrite = tk.IntVar()
      self.cboverwrite = tk.Checkbutton(self.f2, text='overwrite',variable=self.overwrite, onvalue=1, offvalue=0)# command=self.togglereturn)
      self.cboverwrite.grid(row=4, column=7, padx=0, sticky='e')
      
      self.log = scrolledtext.ScrolledText(self, undo=False, height = 15)
      self.log.tag_config("highlight", foreground="red")
      self.log.grid(row = 2, column = 0, columnspan=2, sticky = 'news', padx=5, pady=5)
      self.log.configure(state='disabled')
      
      self.rowconfigure(2, weight=10)
      
      
    def selectfolder(self, event=None):
      
      self.folder = fd.askdirectory(title="Select Config File", initialdir = os.getcwd())
      
      if self.folder=="":
        return 'break'
      
      self.lblfolderselected.config(text=self.folder)
      self.lblfolderselected.update_idletasks()
      
      self.config["uploadfolder"] = self.folder
      
      return 'break'
    
    def selectfile(self, event=None):
      
      self.feedbackfile = fd.askopenfilename(title="Select feedback file", initialdir = os.getcwd(), filetypes = [("txt", "*.txt"), ("csv", "*.csv")])
      
      if self.feedbackfile=="":
        return 'break'
      
      self.lblfileselected.config(text=self.feedbackfile)
      self.lblfileselected.update_idletasks()
      
      self.config["feedbackfile"] = self.feedbackfile
      
      return 'break'
    
    def loadconfig(self, event=None):
      
      self.log.configure(state='normal')
      self.log.delete('0.0', 'end')
      self.log.configure(state='disabled')
      
      self.configfile = fd.askopenfilename(title="Select Config File", initialdir = os.getcwd(), filetypes = [("config", "*.config")])
      
      if self.configfile=="":
        return 'break'
      
      os.chdir(os.path.dirname(self.configfile))
      
      try:
        with open(self.configfile, 'r') as f:
          self.config = json.load(f)
        
        if "apirul" in self.config:
          self.apirul = self.config["apirul"]
          self.svapiurl.set(self.apirul)
          
        if "delimiter" in self.config:
          self.delimiter = self.config["delimiter"]
        
        if "courseid" in self.config:
          self.svmodulenumber.set(self.config["courseid"])
        
        if "assignmentid" in self.config:
          self.svassignmentnumber.set(self.config["assignmentid"])
        
        if "apikey" in self.config:
          self.svapikey.set(self.config["apikey"])
        
        if "uploadfolder" in self.config:
          self.folder = self.config["uploadfolder"]
          self.lblfolderselected.config(text=self.folder)
          self.lblfolderselected.update_idletasks()
        
          #Validate folder
          if not(os.path.isdir(self.folder)):
            self.logmessage("\nInvalid folder name supplied: "+self.folder, alert = True)
            self.logmessage("Remember that paths must use double backslashes \\\\")
        
        if "feedbackfile" in self.config:
          self.feedbackfile = self.config["feedbackfile"]
          self.lblfileselected.config(text=self.feedbackfile)
          self.lblfileselected.update_idletasks()
        
          #Validate file name
          if not(os.path.isfile(self.feedbackfile)):
            self.logmessage("\nInvalid file path supplied: "+self.feedbackfile, alert = True)
            self.logmessage("Remember that paths must use double backslashes \\\\")
        
        return 'break'
      
      except Exception as e:
        self.logmessage("Unable to process config file", True)
        self.logmessage(str(e))
        return 'break'
    
    def saveconfig(self, event=None):
      
      try:
        
        self.readconfig()

        #update dictionary for values are are not event triggered
        self.config["courseid"] = int(self.svmodulenumber.get())
        self.config["assignmentid"] = int(self.svassignmentnumber.get())
        self.config["apikey"] = self.svapikey.get()        
        self.config["apirul"] = self.svapiurl.get()
        
        files = [('config files','*.config')]
        
        jsonfile = fd.asksaveasfile(filetypes = files, defaultextension = files)
        
        json.dump(self.config,jsonfile, indent=2)
        jsonfile.close()
        
        self.logmessage("Config file saved", True)
        return 'break'
        
      except:
        self.logmessage("Config save failed", True)
        return 'break'
    
    def readconfig(self):
      
      #read values fron controls
      self.courseid = int(self.svmodulenumber.get())
      self.assignmentid = int(self.svassignmentnumber.get())
      self.apikey = self.svapikey.get()
      self.apiurl = self.svapiurl.get()
    
    
    def connect(self, event=None):
      
      try:
        
        self.readconfig()
        
        self.canvas = cvs(self.apirul, self.apikey)
        self.course = self.canvas.get_course(self.courseid)
        
        self.logmessage(self.course.course_code + " > " + self.course.name)
        self.assignment = self.course.get_assignment(self.assignmentid)
        self.logmessage("Assignment > "+str(self.assignment))
      
        #Find students in canvas module
        users = self.course.get_users(enrollment_type=['student'])
        
        #Create a dictionary of students keyed on their qub ids
        self.students = {}

        for user in users:
            self.logmessage(str(user.sis_user_id) + " > " + str(user))
            self.students[user.sis_user_id] = dict({"userid": user.id, "sid": user.sis_user_id, "studentname": user.name})

        self.logmessage("Students found > "+str(len(self.students)))

        #Create df to map to files and marks
        self.df = pd.DataFrame.from_dict(self.students).T
        self.df.sid = self.df.sid.apply(str)
        self.df['canvasscore'] = ""
        self.df['uploadcount'] = 0
        self.df['uploads'] = ""
        
        self.df['file'] = ""
        self.df['added'] = ""
        
        self.df['score'] = ""
        self.df['feedback'] = ""
        
        #Retrieve the submissions
        self.submissions = self.assignment.get_submissions(include=['submission_comments'])
        
        for s in self.submissions:
          
          rowid = self.df.index[self.df.userid==s.user_id].tolist()
          
          if len(rowid)==1:
          
            previousuploads = []
            
          #Check for previous comments with uploads
            for c in s.submission_comments:
              if c['author_id'] != s.user_id:
                if 'attachments' in c:
                  for a in c['attachments']:
                    previousuploads.append(a['display_name'])
            
            self.df.uploadcount.loc[rowid[0]] = len(previousuploads)
            self.df.uploads.loc[rowid[0]] = "; ".join(previousuploads)
            
            if not(s.score==None):
              self.df.canvasscore.loc[rowid[0]] = s.score
            
        #update the grid on students on the dataframe tab
        self.owner.mappingtab.refresh(self.df)
        
      except Exception as e:
         self.logmessage("Error connecting to Canvas with supplied details", True)
         self.logmessage(str(e))

    def mapfiles(self, event=None):
      
      self.logmessage("\nMatching files in " + self.folder, True)
      
      for filename in os.listdir(self.folder):
          
          for index, row in self.df.iterrows():
            if str(row.sid) in filename:
              self.df.loc[index,"file"] = filename
              self.logmessage(f"{filename} mapped to {row.studentname} ({row.sid})")
              break
          else:
            self.logmessage("No matches found for " + filename)
        
      n = len(self.df[self.df.file!=""])
      m = len(self.df)
      self.logmessage(f"\nMatched files for {n} of {m} students", False)
      
      #update the grid on students on the dataframe tab
      self.owner.mappingtab.refresh(self.df)


    def uploadfiles(self, event=None):
      
      try:
        self.logmessage("Uploading files...", True)
        
        #Loop over submissions
        for s in self.submissions:
          
          rowid = self.df.index[self.df.userid==s.user_id].tolist()
          
          if len(rowid)==1:
          
            row = self.df.loc[rowid[0]]
            
            if row.file=="":
              self.logmessage(f"No file. Skipping {row.studentname}", False)
              continue
            
            if self.overwrite.get()==0 and row.uploadcount>0:
              self.logmessage(f"{row.studentname}: Skipping since existing file", False)
              self.df.added.loc[rowid] = "no"
              continue
            
          #Check for previous comments with uploads
            file = os.path.join(os.getcwd(), row.file)
            s.upload_comment(file)
            self.df.added.loc[rowid] = "yes"
            self.logmessage(f"{row.studentname}: uploaded {row.file}", False)
        
        #update the grid on students on the dataframe tab
        self.owner.mappingtab.refresh(self.df)
        self.logmessage("File upload complete")
        
      except Exception as e:
        self.logmessage("Error uploading files", True)
        self.logmessage(str(e))

    def mapfeedback(self, event=None):
      
      try:
        
        if len(self.df)==0:
          self.logmessage("Please connection to Canvas before mapping feedback")
          return
        
        self.logmessage("\nMatching students in " + self.feedbackfile, True)
        self.feedback = pd.read_csv(self.feedbackfile, header = None, sep = self.delimiter)
        
        if len(self.feedback.columns)==3:
          self.feedback.columns = ["sid", "score", "feedback"]
        elif len(self.feedback.columns)==2:
          self.feedback.columns = ["sid", "score"]
          self.feedback["feedback"] = ""
        
        #Force to string (since canvas dummy modules use strings)
        self.feedback.sid = self.feedback.sid.apply(str)
        
        self.df.drop(['score', 'feedback'], axis=1, inplace = True)
        self.df = pd.merge(left = self.df, right = self.feedback, left_on='sid', right_on='sid', how = 'left')
        
        #update the grid on students on the dataframe tab
        self.owner.mappingtab.refresh(self.df)
      
      except Exception as e:
        self.logmessage("Error mapping feedback to students", True)
        self.logmessage(str(e))
      
    def uploadfeedback(self, event=None):
      
       try:
        self.logmessage("Uploading feedback...", True)
        
        #Loop over submissions
        for s in self.submissions:
          
          rowid = self.df.index[self.df.userid==s.user_id].tolist()
          
          if len(rowid)==1:
          
            row = self.df.loc[rowid[0]]
            
            if not(row.score=="" or row.score==None or pd.isnull(row.score)):
              if self.overwrite.get()==1 or (s.score==None):
                s.edit(submission={'posted_grade':row.score})
                self.logmessage(f"{row.studentname}: Posting grade of {str(row.score)}")
            
            if not(row.feedback=="" or row.feedback==None or pd.isnull(row.feedback)):
              if self.overwrite.get()==1 or (len(s.submission_comments)==0):
                s.edit(comment={'text_comment':row.feedback})
                self.logmessage(f"{row.studentname}: posting comment")

        self.logmessage("Upload complete")

       except Exception as e:
         self.logmessage("Error uploading feedback", True)
         self.logmessage(str(e))

    def logmessage(self, newtext, timestamp=False, alert = False):
      
      #Unlock for edit
      self.log.configure(state='normal')
      
      if timestamp:
        self.log.insert(tk.END, "\n"+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n")
        
      if alert:
        self.log.insert(tk.END, newtext+"\n", "highlight")
      else:
        self.log.insert(tk.END, newtext+"\n")
      
      self.log.see(tk.END)
      
      #Lock post edit
      self.log.configure(state='disabled')


#------------------------------------------------------------------------------
class StatusBar(tk.Frame):
  
   def __init__(self, parent):
      tk.Frame.__init__(self, parent)
      self.label = tk.Label(self, bd = 1, relief = tk.SUNKEN, anchor = "w")
      self.label.pack(fill="x")
      self.default = "version 1.0.3.BETA"
      
   def settext(self, text, warning=False):
      
     if text == "":
       self.label.config(text = self.default)
       warning = False
     else:
       self.label.config(text = text)
      
     if warning:
       self.label.config(fg="red")
     else:
       self.label.config(fg="black")
      
     self.label.update_idletasks()
      
   def clear(self):
      self.label.config(text="")
      self.label.update_idletasks()
      
#------------------------------------------------------------------------------
class PandaFrame(tk.Frame):
    """Basic test frame for the table"""
    def __init__(self, parent, owner, df):
        tk.Frame.__init__(self, parent)
      
        self.parent = parent
        self.owner = owner

        self.table = Table(self, dataframe=df,
                                showtoolbar=True, showstatusbar=True)
        self.table.show()
        return
        
    def refresh(self, df):
      self.table.model.df = df
      self.table.redraw()
      
#------------------------------------------------------------------------------
class GUI():
  
  def __init__(self):

    self.root = tk.Tk()
    self.root.title('PyUpload')
    self.root.geometry("900x600")
    
    #Embed icon into exe file
    #https://stackoverflow.com/questions/3715493/encoding-an-image-file-with-base64
    icon = \
    """
    AAABAAEAQEAAAAEAGAAoMgAAFgAAACgAAABAAAAAgAAAAAEAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMPAOMPAOMOAOMOAOMPAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAeMnH+Q/OuV4dOurq/CztPG1tvK2t/O2t/O0tfGys/Cbme1aVek1L+UZDuMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMJAOM9OuV8eurBwvPi4/n6/f37/v38//38//38//38//38//38//38//37/v36/f32+PzQ0vaoqPBkYugQAOQPAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMLAONYVue0tPLo6vr9//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//34+/3W2PeRkO4hGeQQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuNLRea8u/Py9Pz8//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//36/f3k5fqNjOweFeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMiGeSYlu7t7vv8//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//37/f3S0vZiXugMAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAONKRObLy/b7/f38//38//38//38//38//39//38//38//39//38//38//38//38//38//38//38//38//38//38//38//38//39//38//38//38//38//38//38//3w8vuZmO4SAuMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAONnY+nk5fr8//38//38//38//38//38//37/v2MjvC3ufbT1fiOkfDs8Pu9vfb5/P3FyPb4+/3S1vnc3/qanfK4ufXj5fqyt/Tj5fuTlvLY2/n8//38//38//38//38//38//35/P24uPMsJeQQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMLAON/furu8Pv8//38//38//38//38//38//38//37/v2AguzV1/jg4/manfDu8PympPHu8ft/hfHKzfe8wPbT1vmLju6mp/K1t/N8fevg4vqrr/LLzvb8//38//38//38//38//38//38//38//3KyvY6NOYQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAON9euvw8/z8//38//38//38//38//38//38//38//37/v2Ghu6+wfbKzfadofLd3/p6d+3JyveKjfHO0fe/w/ff4vumrPK9wfX4+/2dofDs7/uZn/Hu8Pz8//38//38//38//38//38//38//38//38//3Pz/c3MOQQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAONdWujt7vv8//38//38//38//38//38//38//38//38//38//32+Pz3+vz7/v32+fz6/f31+Pz2+fz2+fz7/v35/P38/v35/f37/v38//36/f38//35/f38//38//38//38//38//38//38//38//38//38//38/v3CwvQiGuQQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAONBPubh4/n8//38//3z9vz8//38//38//38//38//38//38//38//38//38//38//38//38//3y9fyKje2oq/G9w/eFie3u8Pv8//38//38//38//38//38//38//38//38//38//38//38//38//38//33+vz4+/38//37/v2pqPALAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMWBePCwvX8//38//3t7/tsbenP0vf8//38//38//38//38//38//38//38//38//38//38//38//3u8vtiZel8f+xKTOdESOi2uPP8//38//38//38//38//38//38//38//38//38//38//38//38//32+fyTlu6jpPD8/v38//33+v12dOoQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOOJh+36/P38//309/xzdOoQAOM6OeXQ0/f8//38//38//38//38//38//38//38//38//38//38//38//3AxPWLjvBBQudESOhbW+jy9vz8//38//38//38//38//38//38//38//38//38//38//33+vyRlO4TBeMdFeS9v/T8//38//3i4/k3MeUQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOM2MeXk5fr8//37/v2rrfEIAOMQAOMQAOM0MuXQ0vf8//38//38//38//38//38//38//38//38//38//3p7PykpfGsrPJkaOstLOUyM+fEx/X8//38//38//38//38//38//38//38//38//38//32+fyRlO4QAOMQAOMQAONBQebk5/n8//39//2op/ARAuMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMPAOOlpPH8//38//3c3/klI+QQAOMQAOMQAOMQAOM5NuXO0Pb8//38//38//38//38//38//38//38//38//2rrfHFx/XFxfh3eOxeYeooKOZnaen6/f38//38//38//38//38//38//38//38//32+f2Tlu4TBeMQAOMQAOMQAOMPAOODhOz5/P38//3w8fxFPuYQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMzLeXq7Pv8//36/f17fOsQAOMQAOMQAOMQAOMQAOMQAOM3NeXP0vb8//38//38//38//38//38//38//35/P5ra+nm6/vIyvmusPZfYupGSeglJ+XN0Pb8//38//38//38//38//38//38//32+f2Ulu8SBuMQAOMQAOMQAOMQAOMQAOMUB+PP0vb8//38//2wsPIOAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMOAOOcm+77/v38//3Y2vggG+QQAOMQAOMQAOMQAOMQAOMQAOMQAOMyMeXP0vb8//38//38//38//38//38//3q7ftKTObz9/zP0Pq8vfe4vPReY+ovL+Z7fev6/f38//38//38//38//38//32+P2Ul+8PAeMQAOMQAOMQAOMQAOMQAOMQAOMQAONvcOr8/v78//3s7voxKuUQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMUA+PZ2vf8//38//309vyFhewQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOM4N+XN0fb8//38//38//38//38//3h4/kuK+Xo7vva3vvK0PnS1/mMi+5gZuomJOXg4vn8//38//38//38//32+P2Tle8TBuMQAOMQAOMQAOMQAOMQAOMQAOMQAOMZE+TKzPT8//38//37/f2Ske4PAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAONkYuf3+f38//38//38//32+P2EhOwOAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOM2NeXP0vb8//38//38//38//3j5vqQmO+4wPbT1vrS2Pvd4/vM0vlobOtPU+k6OOXU1vf8//38//33+vyRlO4SBuMQAOMQAOMQAOMQAOMQAOMQAOMQAOMnIuTIyvX8//38//38//38//3Oz/YIAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOOhoO/9//38//38//38//38//319/yGhuwPAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMyMeXO0Pb8//38//38//3l5/piY+k8O+gyMOh2fO22uvTO1fq6v/ZUWuhQUejc3vj8//32+fyQku4QAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMoIuTFx/T8//38//38//38//38//3r7PtEP+YQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMTBOPJyvX8//38//38//38//38//38//319/yFhuwQAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOM2NOXNz/b8//38//3j5vlfYek8Oudqb+xlauxES+lqb+2DhvAXDORoZ+r1+Pz2+fyOku0SBOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMhHOTGx/X8//38//38//38//38//38//37/v10cuoQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMuKOTq6/v8//38//38//38//38//38//38//32+PyGh+wPAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMzMeXO0fb8//3V2PehpPDu8fz5/P34+/3j5vu5vPOdovG1t/Pn6vr2+vyOku4RA+MQAOMQAOMQAOMQAOMQAOMQAOMQAOMrJ+TGx/X7/v38//38//38//38//38//38//39//2kofAQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOM5NeT5/P78//38//38//38//38//38//38//38//319/yIiOwQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMwLuXN0Pb3+v36/f38//38//38//38//38//38//38//31+P2Pku4QAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMoJOTFxvX8//38//38//38//38//38//38//38//38//3FxfQSAuMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAONRS+j7/f38//38//38//38//38//38//38//38//38//31+PyHh+wQAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOM3NeXMz/b8//38//38//38//38//38//38//32+P2Qku4SBuMQAOMQAOMQAOMQAOMQAOMQAOMQAOMfGeTIyvT8/v3s7/vMz/Xb3/n6/f38//38//38//38//38//3S0/cbEeMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOJhez7/v38//38//38//38//38//38//38//38//38//38//32+P2HiOwOAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMxMOXO0fb8//38//38//38//38//32+P2Qku4RA+MQAOMQAOMQAOMQAOMQAOMQAOMQAOMpJeTIyvX8/v3o6/pQUeYUCOMhGuSprPH7/v38//38//38//38//3g4fknIOQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOuru/8//38//38//38//38//38//33+/31+f31+f31+v35/f38//319/yHiOwQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMuLOXLz/b9//38//38//31+PyPkO4QAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMkH+TJy/T9//38//2qrPEOAONoaOh1dekSBOTy9vz8//38//38//38//3o6fstJ+QQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//36/f2Qk+5cXudcXudbXue+wfX8//38//31+PyGhuwQAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMzM+XLzvb8//32+fyOkO0SBeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMgGuTJy/b8//38//38//2oqvEOAOO8wPTV2Pk/QObz9/z8//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//35/P2HiO4XDOQQAOMNAOOsrvL8//38//38//32+P2Gh+wNAOMQAOMQAOMQAOMQAOMQAOMQAOMPAOMtK+XLzvaNj+4OAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMsKeTIyvX8//38//38//38//3n6vtkZulXV+eWmfGVl+/q8Pz8//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//3DxPUWDuQQAOMQAOMQAONqbOn3+fz8//38//38//319/yIie0QAOMQAOMQAOMQAOMQAOMfGOSQku2xtPNeYOmXmu+nqvFpaekRAeMQAOMQAOMQAOMQAOMoI+THx/X8//38//38//38//38//38//3w8/yjpfOipfKanfHu8fz8//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//31+P1VVOcQAOMQAOMQAOMQAOMQAOO2ufP8//38//38//38//31+P2IiewRAeMQAOMQAOMQAONJRuerrPHJy/W3u/XFyPXCxPSChO4XDuMQAOMQAOMQAOMlIeTJyvX8/v38//38//38//38//38//3y9fyLju2jpfJtbeoyMeaytfP8//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3c3vkmIeQQAOMQAOMQAOMQAOMQAONAP+bq7fv8//38//38//38//32+P2Jiu0PAOMQAOMPAOOusPHx9PzY2vnO0ffR0/ji5fr19/w2NOUQAOMQAOMuK+THyfX7/v38//38//38//38//38//309/x5eut+gO1MTecQAOMQAOOGiOzq7fv8//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3T1fYQAeMQAOMQAOMrLeUOAOMQAOMPAOOsrvH9//38//38//38//38//319/2Kiu0QAeMFAOPGyvb8//38//38//38//39//36/f1rbesQAOMkIOTIyvb8//38//38//38//38//38//38//2rrfAnJeVWWOkPAOMQAOMQAOMLAOOLje37/v38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3R0vcOAOMWDOQaE+QpJ+V1eOwyLuUZD+N7e+r7/v78//38//38//38//38//32+P2Gh+0KAOTp7Pq4uvSnqvH09/3a3PmNkO3l5/ujpO8WDOTKy/b8//38//38//38//38//38//38//38//1SUuYaE+QaE+QQAOMQAON0dem0t/N+f+r7/v38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3R0vcOAOMPAOM/ROdKTuhUVOinqPJscOtucun3+/38//38//38//38//38//32+fyMje6Bg+va3vmdoO50dero6/vExvUaEuXIzvbV1/gtL+XJzPb8//38//38//38//38//38//38//38//1gYegQAOMQAOMQAOMQAONrbenv8vvd4fr8//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3R0vclJOUWDOQKAONGSeY4OeZGP+hscOtucun3+/38//38//38//38//31+PyLje0PAOOBg+xsbukDAONnaOrh5Pqyt/QXDeQKAOOZnO9CReYqKOTLzvb8//38//38//38//38//38//38//3JzPYVDOQQAOMQAOMQAOMNAOPHyvT8//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3R0vdSUepESOhwdewmH+RfXetFP+hscOtucun3+/38//38//38//32+fyKjO0RAeMQAONxcenS1Pc4NeUKAONsbOtHR+cTBeOGhezMzvcZE+MQAOM1NeXM0Pb8//38//38//38//38//35/P37/f3S1PdtcOofGOQkH+Snq/Hq7fvX2vf8//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3R0vdTUupGS+h6f+0vKOR0bu5EPuhwdOxwcun4/P38//38//32+fyKjO0QAOMQAOMQAOMOAOOLju3U1viQku5WVudtbumxtPLN0PdISOYQAOMQAOMQAOMuLuXO0fb8//38//38//3s7/tZW+itsPLn6/rn6vrR1Pjg4/rV2PiChO15eur5/P38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3R0vdSUOpGS+h6f+0vKOR0bu5BPefY2/nV1/j8//38//31+PyLjO0RAeMQAOMQAOMQAOMQAOMOAONZWueoqfF3eeueo/GMju0oI+QQAOMQAOMQAOMQAOMQAOMwLuXLzvb8//38//3y9vyusfEoI+QAAOQWE+SNkO2TlO1LTecPAONOTufv8vz8//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//3u8fzO0PdITOh6f+0vKOR0bu5BPef2+fz8//38//31+P2Ji+0RAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMpJ+XJy/aLjO0QAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOM0MuXMz/b8//38//38//2BhO1VVegPAOMRAOMQAOMQAOMQAONLSufv8vv8//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//33+vxJTuh+gu0vKOR0bu5BPef2+fz8//319/2Ji+4QAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMuKuXJy/b8//32+fyMje0PAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMtK+XN0Pb8//38//3N0fYqJ+QQAOMQAOMQAOMQAOMOAOOMjez7/f38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//37/v3Gyfa4ufMuJuSamfJ5eez4+/z19/2KjO4RAuMQAOMQAOMQAOMQAOMQAOMQAOMQAOMjHuTLzfX8//38//38//32+fyMju0RAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMxL+XKzvb8//35/P17fuwRAONLTugwK+ZER+eYme7v8vz8//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//38//38//3o6/qHjO3u8fv3+vz2+P2Iie0RA+MQAOMQAOMQAOMQAOMQAOMQAOMQAOMoJeTMz/X8//38//38//38//38//33+vyLju0QAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMxMeXLzfbv8/yAg+stKuQtLOWChu2govC/w/b8//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//38//38//38//38//38//31+PyIiu0QAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMwLeXKy/b8//38//38//38//38//38//38//32+fyLjO0PAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMpJ+XMz/b8//3i5vrKzPXLzPXo6/v8//38//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//38//38//38//38//31+PyIiuwQAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMpJ+XLzff8//38//38//38//38//38//38//38//38//32+fyMju0RAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMvLuXKzfb8//38//38//38//38//38//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//38//38//38//32+fyIiuwQAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMwLeXMzvb8//38//38//38//38//38//38//38//38//38//38//33+vyNkO0RAuMQAOMQAOMQAOMQAOMQAOMQAOMQAOMwLuXMz/b8//38//38//38//38//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//38//38//31+PyIiuwQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMzMOXLzPbu8vzq7vvq7vvq7vvq7vvm6vuoqvDHyfXq7vvq7vvq7vvq7vvq7vvw8/uPkO0RAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMrKOXMz/b8//38//38//38//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//38//309/2HiO0QAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMoJeXMzvf9//2Bhe1jauxrcOxrcOxrcOxna+ygpO92eexscOxrcOxrcOxrcOxTWOnNz/b2+fyPkO0RAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMwLuXKzfb8//38//38//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//31+PyHh+4QAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMtLOXLzff8/v39//15e+zW2/mprPK8v/Tw8/z09/zS1Pfs7/v1+Pzf4fmvsfHHyvWqsPHLzPX8//33+vyPkO0RAuMQAOMQAOMQAOMQAOMQAOMQAOMQAOMvLeXLzvb8//38//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//309/yHh+4QAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMuK+XLzfX8//38//39//15e+zQ1fcAAOMAAONjY+iAgOwjHeRNTueGh+0uK+QBAOOWluuts/LLzPX8//38//33+fyNj+0QAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMlI+TJy/b8//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//31+PyGh+0QAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMmJOXMz/X8//38//38//39//15e+zQ1fc0LuahpvKHie1CROcPAOMgGuRdYuqdoPGGiu2Vluuts/LLzPX8//38//38//31+P2Jiu0QAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMuLOXJzPX8//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//32+fyGiOwQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMxL+XMzvf8//38//38//38//39//15e+zQ1fcAAOQpJeRyc+tyceoOAOMoJeSOj+5KSuYVDOOWluuts/LLzPX8//38//38//38//32+f2Iiu0PAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMrKeTLzvX8/v38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//23uvMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMyMeXLzff8//38//38//38//38//39//15e+zQ1fcwJ+aOke9naegzMeUPAOMaEONFRud9gOx8fOyVluuts/LLzPX8//38//38//38//38//31+PyLjO0QAeMQAOMQAOMQAOMQAOMQAOMQAOMQAOMpJ+Xw8/38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//2ytfIQAOMQAOMQAOMQAOMQAOMQAOMQAOMuLOXNz/f8//38//38//38//38//38//39//15e+zQ1fcAAORDROaChe1xcOsOAOMpJeSMjO9pauokIOSWluuts/LLzPX8//38//38//38//38//38//32+fyLjO0RAeMQAOMQAOMQAOMQAOMQAOMQAOMcE+Pt8P38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//2ytfIQAOMQAOMQAOMQAOMQAOMQAOM0M+XO0Pf8/v38//38//38//38//38//38//39//15e+zQ1fcsJOV6e+xDQuYgGeQQAOMTBeMoJeReX+hwcOqVluuts/LLzPX8//38//38//38//38//38//38//33+vyMje4QAeMQAOMQAOMQAOMQAOMQAOMcE+Pt8P38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//2ytfIQAOMQAOMQAOMQAOMQAOMyMOXLzvf8//38//38//38//38//38//38//38//39//14e+zQ1fcJAORbXeiWmfBycewOAOMrJuSQkfCHie48O+aVluuts/LKzPX8//38//38//38//38//38//38//38//32+fyNj+0RAeMQAOMQAOMQAOMQAOMcE+Pt8P38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//2ytfIQAOMQAOMQAOMQAOMpKOXO0Pf8//38//38//38//38//38//38//38//38//38//3O0fbl6PqqrPCTle0fGuQPAuNwc+ktK+UIAONUVeeqq+/Iy/PU2Pfw8vz8//38//38//38//38//38//38//38//38//32+fyNj+0RAeMQAOMQAOMQAOMcE+Pt8P38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//3U1veoqO+oqO+oqO+oqPDV2Pf8//38//38//38//38//38//38//38//38//38//38//38//38//38//37/v3h5PrO0vf3+vzn6vrJzfb09vz8//38//38//38//38//38//38//38//38//38//38//38//38//38//33+vyzs/KoqO+oqO+oqO+pqe/09/38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOOztO/8//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//38//3q6/suKeQQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAON9feqxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGxsvGlpPAhGeMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcTBOcTBOcTBOcRAuUQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMQAOMRAuUTBOcTBOcTBOcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
    """
    icondata= base64.b64decode(icon)
    ## The temp file is icon.ico
    tempFile= "tempicon.ico"
    iconfile= open(tempFile,"wb")
    ## Extract the icon
    iconfile.write(icondata)
    iconfile.close()
    self.root.wm_iconbitmap(tempFile)
    ## Delete the tempfile
    os.remove(tempFile)

    #self.root.iconbitmap(r".\images\qub.ico")
    
    #Create notebook for application tabs
    self.notebook = Notebook(self.root)
    self.notebook.pack(pady=2, fill='both', expand=True)
    
    #Create frames for each tab
    self.frame1 = tk.Frame(self.notebook, width=400, height=280)
    self.frame2 = tk.Frame(self.notebook, width=400, height=280)
    
    self.frame1.pack(fill='both', expand=True)
    self.frame2.pack(fill='both', expand=True)
    
    #Create status bar
    self.sb=StatusBar(self.root)
    self.sb.pack(pady=0, fill='x', expand=False, side = "bottom")
    
    #Create custom config frame for first tab
    self.canvastab = CanvasConfig(self.frame1, self)
    self.canvastab.pack(fill='both', expand=True, anchor = 'n')
    
    self.mappingtab = PandaFrame(self.frame2, self, self.canvastab.df)
    self.mappingtab.pack(fill='both', expand=True, anchor = 'n')
    
    # add frames to notebook
    self.notebook.add(self.frame1, text='Config')
    self.notebook.add(self.frame2, text='Students')
    
    self.sb.settext("")
  
  def mainloop(self):
    self.root.mainloop()
    

if __name__ == "__main__":
  
  gui = GUI()
  gui.mainloop()
