# -*- coding: utf-8 -*-
"""
tkinter-based widget for managing a comment bank for assessment feedback
"""

import pandas as pd

import tkinter as tk
from tkinter import Listbox, StringVar
from tkinter.ttk import Scrollbar

import pyperclip as pc

#------------------------------------------------------------------------------
class commentbank(tk.Frame):
  
    def __init__(self, parent, filename="", logger=None):
        tk.Frame.__init__(self, parent)
        
        self.loaddata(filename)
        self.logger = logger
        
        self.catlabel = tk.Label(self, text='Category', anchor='w', borderwidth=2, justify='left')
        self.catlabel.grid(row=0, column=0, padx=0, sticky='nw')
        self.catlabel.config(font=("Arial", 20))
        
        self.category = Listbox(self, selectmode = "single", exportselection=False)
        
        self.sb1 = Scrollbar(self, orient='vertical', name = "category", command = self.category.yview)
        self.sb1.grid(row=1, column=1, rowspan=4, sticky='ns')
        
        self.category.bind('<<ListboxSelect>>', self.categoryselect)
        self.category.config(yscrollcommand = self.sb1.set)
        
        self.category.grid(row=1, column=0, rowspan = 4, columnspan =2,  padx=5, sticky='nsew')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(4, weight=1)
        
        self.catlabel = tk.Label(self, text='Feedback', anchor='w', borderwidth=2, justify='left')
        self.catlabel.grid(row=5, column=0, padx=0, sticky='nw')
        self.catlabel.config(font=("Arial", 20))
        
        self.includereturn = tk.IntVar()
        self.checkbox = tk.Checkbutton(self, text='with return',variable=self.includereturn, onvalue=1, offvalue=0, command=self.togglereturn, anchor='c')
        self.checkbox.grid(row=10, column=2, padx=0)
        
        self.feedback = Listbox(self, selectmode = "single")
        #Stop listbox losing selection
        self.feedback.configure(exportselection=False)
        self.feedback.bind('<<ListboxSelect>>', self.feedbackselect)
        
        self.sb2 = Scrollbar(self, orient='vertical', command = self.feedback.yview)
        self.sb2.grid(row=6, column=1, rowspan=4, sticky='ns')
        
        self.feedback.config(yscrollcommand = self.sb2.set)
        self.feedback.grid(row=6, column=0, rowspan=4, columnspan=2, padx=5, sticky='nsew')
        self.rowconfigure(9, weight=4)
        
        #Edit feedback
        self.feedbacktext = StringVar()
        fbt = tk.Entry(self, width=3, justify='left', textvariable=self.feedbacktext)
        fbt.grid(row = 10, column = 0, columnspan =1, sticky = 'we', pady=5, padx = 5)
        
        self.btnfeedbackadd = tk.Button(self, text="Add Category", anchor='c')
        self.btnfeedbackadd.bind("<Button-1>", self.categoryadd)
        self.btnfeedbackadd.grid(row=1, column=2, padx=5, pady=5, sticky='new')
        self.btnfeedbackadd.columnconfigure(2, weight=0)
        
        self.btnfeedbackadd = tk.Button(self, text="Remove Category", anchor='c')
        self.btnfeedbackadd.bind("<Button-1>", self.categoryremove)
        self.btnfeedbackadd.grid(row=2, column=2, padx=5, pady=5, sticky='new')
        self.btnfeedbackadd.columnconfigure(2, weight=0)
        
        self.btnfeedbackadd = tk.Button(self, text="Rename Category", anchor='c')
        self.btnfeedbackadd.bind("<Button-1>", self.categoryrename)
        self.btnfeedbackadd.grid(row=3, column=2, padx=5, pady=5, sticky='new')
        self.btnfeedbackadd.columnconfigure(2, weight=0)
        
        self.btnfeedbackadd = tk.Button(self, text="Add Feedback", anchor='c')
        self.btnfeedbackadd.bind("<Button-1>", self.feedbackadd)
        self.btnfeedbackadd.grid(row=7, column=2, padx=5, pady=5, sticky='new')
        self.btnfeedbackadd.columnconfigure(2, weight=0)
        
        self.btnfeedbackremove = tk.Button(self, text="Remove Feedback", anchor='c')
        self.btnfeedbackremove.bind("<Button-1>", self.feedbackremove)
        self.btnfeedbackremove.grid(row=8, column=2, padx=5, pady=5, sticky='new')
        self.btnfeedbackremove.columnconfigure(2, weight=0)
        
        self.btnfeedbackremove = tk.Button(self, text="Replace Feedback", anchor='c')
        self.btnfeedbackremove.bind("<Button-1>", self.feedbackreplace)
        self.btnfeedbackremove.grid(row=9, column=2, padx=5, pady=5, sticky='new')
        self.btnfeedbackremove.columnconfigure(2, weight=0)
        
        self.refresh()

    def loaddata(self, filename):
      
        try:
          
          #Default in case of failure
          self.bank = pd.DataFrame({"category":["Analysis","Analysis","Methodology"], "feedback":["Good","Bad","Could be improved"]})
          
          if not(filename)=="":
            self.filename = filename
            self.bank = pd.read_csv(filename, header=None)
            self.bank.columns = ["category","feedback"]
            self.logmessage("Loaded: "+self.filename)
            self.logmessage(str(len(self.bank)) + " items added")

        except:
          self.logmessage("Error loading file: "+self.filename)

    def refresh(self):
      
      self.category.delete(0,"end")
      
      for i, value in enumerate(self.bank.category.unique()):
        self.category.insert(i, value)
      
      self.category.select_set(0) #This only sets focus on the first item.
      self.category.event_generate("<<ListboxSelect>>")
      
      self.categoryselect()

    def logmessage(self, message):
      
      try:
        
        if self.logger:
          self.logger(message)
        
      except:
        pass


    def categoryselect(self, event = None):
      
      try:
        i = self.category.curselection()[0]
        cat =self.category.get(i)
        self.feedback.delete(0,"end")
        
        df = self.bank[self.bank.category==cat]
        
        for i, value in enumerate(df.feedback.sort_values(ascending=True)):
          self.feedback.insert(i, value)
          
        self.feedback.select_set(0) #This only sets focus on the first item.
        self.feedback.event_generate("<<ListboxSelect>>")
      
      except:
        pass
    
    
    def categoryadd(self, event = None):
      
      newcategory = self.feedbacktext.get()
      
      if newcategory.strip()=="":
        return
        
      if self.bank.category.str.contains(newcategory).any():
        return
      
      self.bank = pd.concat([self.bank, pd.DataFrame({"category": [newcategory], "feedback": ["<replace me>"]})], ignore_index=True)
      
      self.bank.sort_values(by=['category', 'feedback'], inplace=True)
      self.save()
      self.refresh()
      
      #Select replaced entry
      self.category.selection_clear(0, 'end')
      for i, listbox_entry in enumerate(self.category.get(0, "end")):
        if listbox_entry == newcategory:
          self.category.select_set(i)
          self.category.event_generate("<<ListboxSelect>>")
          break
    
    def feedbackadd(self, event = None):
      
      i = self.category.curselection()[0]
      cat =self.category.get(i)
      
      newcomment = self.feedbacktext.get()
      
      df = self.bank[self.bank.category==cat]
      
      if df.feedback.str.contains(newcomment).any():
        return
      
      if newcomment!="":
        self.bank = pd.concat([self.bank, pd.DataFrame({"category": [cat], "feedback": [newcomment]})], ignore_index=True)
        
        self.categoryselect()
        self.save()
        
    def categoryremove(self, event = None):
      
      try:
        i = self.category.curselection()[0]
        cat =self.category.get(i)
        
        
        k = self.bank.index[(self.bank.category==cat)]
        
        if len(k)>0:
          self.bank.drop(k, inplace=True)
        
        self.save()
        self.refresh()
      
      except:
        pass
    
    def categoryrename(self, event = None):
      
      try:
        i = self.category.curselection()[0]
        cat =self.category.get(i)
        
        newcategory = self.feedbacktext.get()
        
        if newcategory.strip()=="":
          return
        
        k = self.bank.index[(self.bank.category==cat)]
        
        if len(k)>0:
          self.bank.category[k]=newcategory
        
          self.save()
          self.refresh()
      
      except:
        pass
      
    def feedbackremove(self, event = None):
      
      i = self.category.curselection()[0]
      cat =self.category.get(i)
      
      j = self.feedback.curselection()[0]
      feedback = self.feedback.get(j)
      
      k = self.bank.index[(self.bank.category==cat) & (self.bank.feedback==feedback)]
      
      if len(k)>0:
        self.bank.drop(k, inplace=True)
      
      self.categoryselect()
      self.save()

    def feedbackreplace(self, event = None):
      
      i = self.category.curselection()[0]
      cat =self.category.get(i)
      
      j = self.feedback.curselection()[0]
      feedback = self.feedback.get(j)
      
      k = self.bank.index[(self.bank.category==cat) & (self.bank.feedback==feedback)]
      
      newcomment = self.feedbacktext.get()
      
      if len(k)>0:
        self.bank.feedback[k] = newcomment
      
        self.categoryselect()
        self.save()
        
        #Select replaced entry
        self.feedback.selection_clear(0, 'end')
        for i, listbox_entry in enumerate(self.feedback.get(0, "end")):
          if listbox_entry == newcomment:
            self.feedback.select_set(i)
            break


    def feedbackselect(self, event = None):
      try:
        i = self.feedback.curselection()[0]
        text = self.feedback.get(i)
        
        if self.includereturn.get():
          feedback = text+"\n"
        else:
          feedback = text
        
        pc.copy(feedback)
        
        self.feedbacktext.set(text)
        
      except:
        pass

    def togglereturn(self):
      self.feedbackselect()


    def save(self):
      
      try:
        self.bank.sort_values(by=['category', 'feedback'], inplace=True)
        
        if not(self.filename==""):
          self.bank.to_csv(self.filename, index = False, header=False)
          
      except:
        pass