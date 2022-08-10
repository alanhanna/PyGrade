# -*- coding: utf-8 -*-
"""
tkinter-based application for creating/recording assessment feedback
"""

import os
import re
import json
import base64
from datetime import datetime
import itertools
import pandas as pd
import numpy as np

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox, StringVar
from tkinter.ttk import Scrollbar, Notebook, Combobox
import tkinter.scrolledtext as scrolledtext

from commentbankwidget import commentbank

#pip install pandastable
from pandastable import Table

#conda install -c conda-forge pyperclip
import pyperclip as pc

#conda install -c conda-forge fpdf
from fpdf import FPDF

#Integration with canvas
#pip install canvasapi
from canvasapi import Canvas as cvs

#Turn off warning for now
pd.options.mode.chained_assignment = None 

#------------------------------------------------------------------------------

class PDF(FPDF):
  
    def header(self):
      
        title = self.title
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Calculate width of title and position
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(85, 0, 5)
        self.set_fill_color(214, 0, 13)
        self.set_text_color(255, 255, 255)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, title, 1, 1, 'C', 1)
        # Line break
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(255, 150, 150)
        # Title
        self.cell(0, 6, 'Chapter %d : %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, name):
        # Read text file
        with open(name, 'rb') as fh:
            txt = fh.read().decode('latin-1')
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()
        # Mention in italics
        self.set_font('', 'I')
        self.cell(0, 5, '(end of excerpt)')

    def print_chapter(self, num, title, name):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(name)


    def print_subheader(self, text):
        # Arial bold 15
        self.set_font('Arial', 'B', 12)
        # Calculate width of title and position
        w = self.get_string_width(text) + 6
        self.set_x((210 - w) / 2)
        # Colors of frame, background and text
        self.set_draw_color(255, 255, 255)
        self.set_fill_color(255, 255, 255)
        self.set_text_color(50, 50, 50)
        # Thickness of frame (1 mm)
        self.set_line_width(1)
        # Title
        self.cell(w, 9, text, 1, 1, 'C', 1)
        # Line break
        self.ln(5)

    def print_question(self, question):
        # Arial 12
        self.set_font('Arial', '', 12)
        # Background color
        self.set_fill_color(255, 200, 200)
        # Title
        self.cell(0, 6, question, 0, 1, 'L', 1)
        # Line break
        self.ln(1)
        
    def print_feedback(self, txt):
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, txt)
        # Line break
        self.ln()
    
    def print_bold(self, txt):
        self.set_font('Times', '', 12)
        # Mention in italics
        self.set_font('', 'B')
        self.multi_cell(0, 5, txt)
      
    def print_major(self, question, score, available, feedback):
      
      if score == "":
        self.print_question(question)
      elif int(available)>0:
        self.print_question(question + f" ({score}/{available})")
      else:
        self.print_question(question + f" ({score})")
      
      self.print_feedback(feedback)
      
    def print_minor(self, question, score, available, feedback):
      
      if score == "":
        self.print_question(question)
      elif int(available)>0:
        self.print_bold(question + f" ({score}/{available})")
      else:
        self.print_bold(question + f" ({score})")
      
      self.print_feedback(feedback)
      
#------------------------------------------------------------------------------
def clean(text):
  try:
    if isinstance(text,str):
      return text.strip()
  except:
      return str(text)

def numericcolumn(dfcol):
  return  pd.to_numeric(dfcol, errors='coerce')

def flatten(t):
    return [item for sublist in t for item in sublist]
  
def extractid(filename, n=8):
  """Extract digits from file matching student id"""
  x = re.findall('[0-9]+', filename)
  return [y for y in x if len(y)==n]

def shortstrnum(value):
  
  if float(value).is_integer():
    return str(int(value))
  else:
    return str(value)

#------------------------------------------------------------------------------
#Widget for questions and feedback
class CustomWidget(tk.Frame):
  
    def __init__(self, parent, owner):
        tk.Frame.__init__(self, parent)
        
        self.owner = owner
        bgcolor = self.owner.config.config["bgcolor"]

        self.f1 = tk.Frame(self, bg=bgcolor, bd=0)
        self.f1.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
        
        self.keys = self.owner.config.classlist['key'].tolist()
        
        self.idcombo = Combobox(self.f1, values = self.keys, height=10, state="readonly")
        self.idcombo.grid(row=0, column=0, columnspan =2,  padx=5, sticky='nsew')
        self.idcombo.bind("<<ComboboxSelected>>", lambda event: self.idcomboselect())
        self.f1.columnconfigure(0, weight=1)
        
        #Select first value
        self.idcombo.current(0)
        
        self.btnpdf = tk.Button(self.f1, text="pdf", anchor='e')
        self.btnpdf.grid(row=0, column=3, padx=5, sticky='nsew')
        self.btnpdf.bind("<Button-1>", self.pdf)
        self.btnpdf.columnconfigure(3, weight=0)
        
        self.btnsave = tk.Button(self.f1, text="save", anchor='e')
        self.btnsave.grid(row=0, column=4, padx=5, sticky='nsew')
        self.btnsave.bind("<Button-1>", self.save)
        self.btnsave.columnconfigure(4, weight=0)
        
        self.feedbacktext = tk.Button(self.f1, text="...", anchor='e')
        self.feedbacktext.grid(row=0, column=5, padx=5, sticky='nsew')
        self.feedbacktext.bind("<Button-1>", self.feedbackpopup)
        self.feedbacktext.columnconfigure(5, weight=0)
        
        self.previousstudent = tk.Button(self.f1, text="<", anchor='e')
        self.previousstudent.grid(row=0, column=6, padx=5, sticky='nsew')
        self.previousstudent.bind("<Button-1>", self.moveback)
        self.previousstudent.columnconfigure(6, weight=0)
        
        self.nextstudent = tk.Button(self.f1, text=">", anchor='e')
        self.nextstudent.grid(row=0, column=7, padx=5, sticky='nsew')
        self.nextstudent.bind("<Button-1>", self.moveforward)
        self.nextstudent.columnconfigure(7, weight=0)
        
        self.total = tk.Label(self.f1, text='0', anchor='e', borderwidth=2, width=5, relief="groove", justify='center')
        self.total.grid(row=0, column=8, padx=0, sticky='ne')
        self.total.config(font=("Arial", 20))
        self.f1.columnconfigure(8, weight=0)
        
        self.f2 = tk.Frame(self, bg=bgcolor, bd=0)
        self.f2.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        
        self.canvas = tk.Canvas(self.f2, bg=bgcolor, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.f2.columnconfigure(0, weight=1)
        self.f2.rowconfigure(0, weight=1)
        
        self.rowconfigure(0, weight=0) 
        self.rowconfigure(1, weight=1) 
        self.columnconfigure(0, weight=1)
        
        #Now second frame for the components
        self.frame_components = tk.Frame(self.canvas, bg=bgcolor)
        self.frame_components.grid(row=0, column=0, padx=5, sticky='nsew')
        self.frame_components.columnconfigure(0, weight=1)
        self.frame_components.rowconfigure(0, weight=1)
        
        #Need for the scroll bar
        self.canvas.create_window((0, 0), window=self.frame_components, anchor='nw', tags="frame")
        self.canvas.grid(row=0, column=0, padx=5, sticky='nsew')
        self.canvas.columnconfigure(0, weight=0)

        df = self.owner.config.questions
        self.n = len(df)
        self.scrollbaron = (self.n>self.owner.config.config["maxquestionsonscreen"])
        
        self.nonscoringquestion = [np.isnan(self.owner.config.questions.marks.iloc[i]) for i in range(self.n)]
        
        #Dictionary to match id to question index
        self.index = df.question.tolist()
        self.hint = []
        self.hintlabel = []
        self.combo = []
        self.score = []
        self.scoresv = []
        self.text = []
        
        
        for i in range(self.n):
            
            if pd.isnull(df.iloc[i,2]):
              label = f'{str(df.iloc[i,0])}. {df.iloc[i,1]}'
            else:
              label = f'{str(df.iloc[i,0])}. {df.iloc[i,1]} [{df.iloc[i,2]}]'
            
            x = tk.Label(self.frame_components, text=label, anchor='w')
            
            h = StringVar()
            y = tk.Label(self.frame_components, text="<>", anchor='e', textvariable=h)
            self.hint.append(h)
            self.hintlabel.append(y)
            
            s = StringVar()
            self.scoresv.append(s)
            s.trace("w", lambda name, index, mode, var=s, i=i: self.entryupdate(var, i))
            z = tk.Entry(self.frame_components, width=5, justify='center', textvariable=s)
            
            qid = str(df.iloc[i,0])
            
            values = self.owner.config.combinedfeedback[self.owner.config.combinedfeedback.question==qid].feedback.tolist()
            values.insert(0,"")
            
            w = Combobox(self.frame_components, values = values, height=10, state="readonly")
            self.combo.append(w)
            
            #Stop frame scroll rolling combo boxes?!
            w.unbind_class("TCombobox", "<MouseWheel>")
            
            #Configure event handler
            w.bind("<<ComboboxSelected>>", lambda event, k=i: self.comboselect(k))
            
            if self.nonscoringquestion[i]:
              t = scrolledtext.ScrolledText(self.frame_components, undo=True, height = int(self.owner.config.config["feedbacklines"])*2, background =self.owner.config.config["feedbackbgcolor"])
            else:
              t = scrolledtext.ScrolledText(self.frame_components, undo=True, height = int(self.owner.config.config["feedbacklines"]), background =self.owner.config.config["feedbackbgcolor"])
                
            t['font'] = (self.owner.config.config["fontface"], self.owner.config.config["fontsize"])
            self.text.append(t)
            t.bind("<Key>", lambda event, k=i: self.textupdate(k))
            
            x.grid(row = 3*i+0, column = 0, sticky = 'nsew', pady=5, padx = 2)
            
            #Keep hidden for null feedback (i.e. overall)
            if not self.nonscoringquestion[i]:
              y.grid(row = 3*i+0, column = 1, sticky = 'nsew', pady=5, padx = 2)
              z.grid(row = 3*i+0, column = 2, sticky = 'nsew', pady=5, padx = 2)
            
            w.grid(row = 3*i+1, column = 0, columnspan=2, sticky = 'nsew', pady=2, padx = 5)
            t.grid(row = 3*i+2, column = 0, columnspan=2, sticky = 'nsew', pady=3, padx = 5)

            self.frame_components.columnconfigure(0, weight=1)
            self.frame_components.rowconfigure(tuple(range(0,3*self.n,3)), weight=1)
            self.frame_components.rowconfigure(tuple(range(1,3*self.n,3)), weight=1)
            self.frame_components.rowconfigure(tuple(range(2,3*self.n,3)), weight=20)

        self.sid = self.owner.config.classlist.id.iloc[0]
        self.loadstudent(self.sid)

        if self.scrollbaron:
          self.scrollbar = Scrollbar(self, orient='vertical', command=self.canvas.yview)
          self.scrollbar.grid(row=1, column=1, rowspan=1, sticky='ns')
          self.canvas.configure(yscrollcommand=self.scrollbar.set)
          
          #Update frame idle tasks to let tkinter calculate sizes
          self.frame_components.update_idletasks()
          self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind('<Configure>', self._configure_canvas)
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)

    def feedbackpopup(self, event=None):
      
      win = tk.Toplevel()
      win.wm_title("Feedback for " + self.idcombo.get())

      t = scrolledtext.ScrolledText(win, undo=True, background =self.owner.config.config["feedbackbgcolor"])
      t['font'] = (self.owner.config.config["fontface"], self.owner.config.config["fontsize"])
      t.grid(row = 0, column = 0, sticky = 'nsew', pady=3, padx = 3)

      win.columnconfigure(0, weight=1)
      win.rowconfigure(0, weight=1)
      
      df = self.owner.config.questions
      
      feedback = ""
      for i in range(self.n):
        
        feedback += f'{str(df.iloc[i,0])}. {df.iloc[i,1]} '
        
        if not pd.isnull(df.iloc[i,2]):
          score = clean(self.scoresv[i].get())
          feedback += f'[{score}/{df.iloc[i,2]}]\n\n'

        feedback += clean(self.text[i].get("1.0", "end"))
        feedback += "\n\n"
      
      t.insert('0.0', feedback)
      pc.copy(feedback)


    def moveback(self, event=None):
      i = self.idcombo.current()
      if i>0:
        self.idcombo.current(i-1)
        self.idcomboselect()
        

    def moveforward(self, event=None):
      i = self.idcombo.current()
      if i<len(self.keys)-1:
        self.idcombo.current(i+1)
        self.idcomboselect()

    def loadstudent(self, studentid):
      
      df = self.owner.config.outcomes[self.owner.config.outcomes.id == studentid]
      
      for i, q in enumerate(self.index):
        
        try:
          score    = df[df.question==q].score.iloc[0]
          feedback = df[(df.question==q)].feedback.iloc[0]
        except:
          score = ""
          feedback = ""
        
        if isinstance(score,str):
          self.scoresv[i].set("")
        elif np.isnan(score):
          self.scoresv[i].set("")
        else:
          x = float(score)
          if x.is_integer():
            self.scoresv[i].set(int(x))
          elif np.isnan(x):
            self.scoresv[i].set("")
          else:
            self.scoresv[i].set(score)
        
        self.text[i].delete('0.0', 'end')
        self.text[i].insert('0.0', feedback)
        self.updatehint(i)
        
        try:
          k = self.combo[i]['values'].index(feedback)
          self.combo[i].current(k)
          self.updatehint(i)
        except:
          self.combo[i].current(0)
          self.updatehint(i)
      
      self.owner.sb.settext("")

    def save(self, event=None):
      self.savestudent()
      
      #Reload to refresh ranges
      self.loadstudent(self.sid)

    def pdf(self, event=None):
      
      self.savestudent()
      
      df = self.owner.config.questions
      
      outcomes = self.owner.config.outcomes[self.owner.config.outcomes.id == self.sid]
      outcomes["major"] = [x.split('.',1)[0] for x in outcomes.question]
      
      firstname = self.owner.config.classlist.loc[self.owner.config.classlist.id == self.sid, 'first'][0]
      
      name = self.idcombo.get()
      
      pdf = PDF()
      
      if ("module" in self.owner.config.config) and ("assessment" in self.owner.config.config):
        title = f'{self.owner.config.config["module"]} {self.owner.config.config["assessment"]}'
      else:
        title = ""
      
      pdf.set_title(title)
      
      pdf.add_page()
      
      subtitle = "Feedback report for " + name
      pdf.print_subheader(subtitle)
      
      if len(df.major.unique())==len(df):

        for i in range(self.n):
          question = f'{str(df.iloc[i,0])}. {df.iloc[i,1]}'
          score = clean(self.scoresv[i].get())
          feedback = clean(self.text[i].get("1.0", "end"))
          feedback = feedback.replace("<name>", firstname)
          
          #Question with marks available?
          if pd.isnull(self.owner.config.questions.iloc[i,2]):
            available = ""
          else:
            available = shortstrnum(self.owner.config.questions.iloc[i,2])
          
          pdf.print_major(question, score, available, feedback)
      
      else:
        
        #Track question change
        major = ""
        
        for i in range(self.n):
          
          score = clean(self.scoresv[i].get())
          feedback = clean(self.text[i].get("1.0", "end"))
          print(classmember, type(classmember))
          feedback = feedback.replace("<name>", firstname)
          
          #Question with marks available?
          if pd.isnull(self.owner.config.questions.iloc[i,2]):
            available = ""
          else:
            available = shortstrnum(self.owner.config.questions.iloc[i,2])
          
          if df.minor[i]=="" and (available=="" or int(available)==0):
            question = f'{df.description[i]}'
            pdf.print_major(question, score, available, feedback)
          
          elif df.minor[i]=="":
            question = f'Question {str(df.major[i])}: {df.description[i]}'
            pdf.print_major(question, score, available, feedback)
              
          #Multipart question
          else:
            if major != df.major[i]:
              temp = outcomes[outcomes.major==df.major[i]]
              subscore = shortstrnum(sum(temp.score))
              
              temp = df[df.major==df.major[i]]
              subtotal = shortstrnum(sum(temp.marks))
              
              question = f'Question {str(df.major[i])} ({subscore}/{subtotal})'
              pdf.print_question(question)
            
            question = f'{str(df.iloc[i,0])}. {df.iloc[i,1]}'
            pdf.print_minor(question, score, available, feedback)
          
          major = df.major[i]
      
      total = self.total.cget("text")
      
      pdf.print_bold(f"\nTotal mark awarded: {total}")
      
      pdf.output(name + '.pdf', 'F')

    def savestudent(self):
      
      q = []
      f = []
      s = []
      
      for i in range(self.n):
        q.append(clean(self.index[i]))
        f.append(clean(self.text[i].get("1.0", "end")))
        s.append(clean(self.scoresv[i].get()))
        
      df = pd.DataFrame({"id" : [self.sid]* self.n , "question" : q, "score" : s, "feedback" : f})
      df['score'] = numericcolumn(df['score'])

      #delete existing entries
      self.owner.config.outcomes.drop(self.owner.config.outcomes[self.owner.config.outcomes.id == self.sid].index, inplace = True)
      
      #merge updates
      self.owner.config.outcomes = pd.concat([self.owner.config.outcomes, df], ignore_index=True)
      self.owner.refresh()
      self.owner.sb.settext("")

    def entryupdate(self, sv, i):
      self.owner.sb.settext("Unsaved changes", True)
      self.updatetotal()

    def textupdate(self, i):
      self.owner.sb.settext("Unsaved changes", True)

    def updatetotal(self):
      
      total = 0
      
      for sv in self.scoresv:
        try:
          value = float(sv.get())
          total += value
        except:
          pass
      
      self.total.config(text=total)
      self.total.update_idletasks()

    def idcomboselect(self):
      
      self.savestudent()
      
      stext = self.idcombo.get()
      
      #This approach worked when the student id was numeric
      #self.sid = int("".join([x for x in stext if x.isdigit()]))
      
      self.sid = stext.split("[")[1].split("]")[0]
      
      self.refreshlists()
      
      self.loadstudent(self.sid)
    
    def refreshlists(self):

      df = self.owner.config.combinedfeedback
      
      for i in range(self.n):
        
        qid = self.owner.config.questions.iloc[i,0]
        values = df[df.question==qid].feedback.tolist()
        values.insert(0,"")
        self.combo[i]['values'] = values

    
    def updatehint(self, index):
      
      try:
        if self.nonscoringquestion[index]:
          return
        
        q = self.index[index]
        stext = str(self.text[index].get('1.0', 'end-1c'))
        stext = clean(stext)
        
        df = self.owner.config.outcomes
        df = df[(df.question==q) & (df.feedback==stext)]

        values = df.score
        values = [x for x in values if isinstance(x,(int,float)) and not np.isnan(x)]
        
        self.hintlabel[index].config(fg="black")
        maxscore = self.owner.config.questions.marks[index]
        
        if len(values)==0:
          self.hint[index].set("[?]")
        else:
          a = min(values)
          b = max(values)
          
          if b>maxscore:
            self.hint[index].set("["+str(a)+"-"+str(b)+"] max exceeded!")
            self.hintlabel[index].config(fg="red")
          elif a==b:
            self.hint[index].set("["+str(a)+"]")
          else:
            self.hint[index].set("["+str(a)+"-"+str(b)+"]")
          
      except Exception as e:
        self.hint[index].set("[??]")
        print("error in updatehint:",e)

    def comboselect(self, index):
      try:
        
        #Update text
        stext = self.combo[index].get()
        
        if self.nonscoringquestion[index]:
          existing = clean(self.text[index].get("1.0", "end"))
          if len(existing)>0:
            stext = existing+"\n"+stext
        
        self.text[index].delete('0.0', 'end')
        self.text[index].insert('0.0', stext)
        
        #Update other components
        try:
          
          #Nothing to update for a pure feedback (no score) box
          if not(self.nonscoringquestion[index]):
            
            #Find question from index
            df = self.owner.config.questions
            
            #look up question name in class index variable
            q = self.index[index]
            
            #Look up and set feedback score
            df = self.owner.config.combinedfeedback
            score = df.score[(df.question==q) & (df.feedback==stext)].values[0]
            
            score = shortstrnum(score)
            self.scoresv[index].set(score)
            self.updatehint(index)
          
          self.owner.sb.settext("Unsaved changes", True)

        except:
          #not found
          self.scoresv[index].set(score)
          self.hint[index].set("?")
          self.owner.sb.settext("Unsaved changes", True)
        
        self.updatetotal()
        
      except:
        print("combo select exception")
        self.owner.sb.settext("Unsaved changes", True)
        self.updatetotal()

    def exportAllPDFs(self):
      
      #Save changes for current student just in case
      self.save()
      
      self.owner.config.logmessage("\nExporting PDFs (students with feedback only)", True )
      
      #Export all students with outcomes to PDF
      count = 0

      for i, row in self.owner.config.classlist.iterrows():
        
        sid = row.id
        
        if sid in self.owner.config.outcomes.id.unique():
          
          try:
            self.idcombo.current(i)
            self.loadstudent(sid)
            
            self.pdf()
            self.owner.config.logmessage(f"PDF exported for {self.idcombo.get()}")
            count += 1
            
          except:
            self.owner.config.logmessage(f"Error exporting PDF for {sid}", alert = True)
            
        else:
          self.owner.config.logmessage(f"Skipping {sid}: no feedback recorded")
        
      self.owner.config.logmessage(f"Exported {count} files")

    def _configure_canvas(self, event=None):
      
      if self.scrollbaron: #if self.n>self.owner.config.config["maxquestionsonscreen"]:
        self.canvas.itemconfig('frame', width=self.canvas.winfo_width())
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
      else:
        self.canvas.itemconfig('frame', width=self.canvas.winfo_width(), height=self.canvas.winfo_height())


    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units" )
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units" )

#------------------------------------------------------------------------------
class Config(tk.Frame):
  
    def __init__(self, parent, owner, configfile = ""):
        tk.Frame.__init__(self, parent)
        
        self.owner = owner
        self.configfile = configfile
        self.config = dict()
        self.questioncount = None
        self.defaultconfig()
        
        self.btnselect = tk.Button(self, text="Select Config File", anchor='nw')
        self.btnselect.bind("<Button-1>", lambda event: self.selectconfigfile())
        self.btnselect.grid(row = 0, column = 0, sticky = 'nw', padx=5, pady=5)
        
        self.btncreate = tk.Button(self, text="Create Config File", anchor='n')
        self.btncreate.bind("<Button-1>", lambda event: self.createconfigfile())
        self.btncreate.grid(row = 1, column = 0, sticky = 'nw', padx=5, pady=5)
        
        self.lblfile = tk.Label(self, text="", anchor="w")
        self.lblfile.grid(row = 0, column = 1, sticky = 'new', padx=5, pady=5)
        
        self.btnTotals = tk.Button(self, text="Export Totals CSV", anchor='nw')
        self.btnTotals.bind("<Button-1>", lambda event: self.exporttotals())
        self.btnTotals.grid(row = 2, column = 0, sticky = 'nw', padx=5, pady=5)
        
        self.btnPDFs = tk.Button(self, text="Export PDFs", anchor='nw')
        self.btnPDFs.bind("<Button-1>", lambda event: self.exportAllPDFs())
        self.btnPDFs.grid(row = 2, column = 1, sticky = 'nw', padx=5, pady=5)
        
        self.log = scrolledtext.ScrolledText(self, undo=False, height = 20)
        self.log.tag_config("highlight", foreground="red")
        self.log.grid(row = 3, column = 0, columnspan=2, sticky = 'news', padx=5, pady=5)
        self.log.configure(state='disabled')
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        
        #Default data
        self.config["outcomes"] = "outcomes.txt"
        self.config["sep"] = ","
        
        self.questions = pd.DataFrame({"question":["1","2"], "description":["Introduction", "Analysis"], "marks":[50.0,50.0]})
        self.classlist = pd.DataFrame({"id":["888","999"], "first":["john", "jane"], "last":['dear','doe']})
        self.feedback = pd.DataFrame({"question":["1","2"], "score":[4,7], "feedback":["good", "bad"]})
        self.outcomes = pd.DataFrame({"id":["888","888"], "question":["1","2"], "score":[4,7], "feedback":["good", "bad"]})
        
        #Comment bank is now independent
        
        self.dummydata = True
        
        self.postloaddatafresh()

    def postloaddatafresh(self):
      
      self.config["buckets"][-1] = self.config["buckets"][-1] + 10**-10
      
      #Whether defaulted or loaded, ensure data is a consistent state
      #canvas permits non-integer ids so don't enforce this
      #self.classlist['id'] = pd.to_numeric(self.classlist['id'])
      self.classlist['key'] = self.classlist.apply(lambda x: x['last'] + ", " + x['first'] + " [" + str(x['id']) + "]", axis=1)
      
      #canvas permits non-integer ids so don't enforce this
      #self.outcomes['id'] = pd.to_numeric(self.outcomes['id'])
      self.outcomes.id = self.outcomes.id.apply(str)
      self.classlist.id = self.classlist.id.apply(str)
      
      #Convert float columns to avoid strings
      self.outcomes['score'] = numericcolumn(self.outcomes['score'])
      self.feedback['score'] = numericcolumn(self.feedback['score'])
      
      self.questions['major']=""
      self.questions['minor']=""
      
      for i, row in self.questions.iterrows():
        temp = row.question.split(".",1)
        
        if len(temp)==1:
          self.questions.major[i] = row.question
        else:
          self.questions.major[i] = temp[0]
          self.questions.minor[i] = temp[1]
      
      self.preparesummarytables()
    
    
    def preparesummarytables(self):
      
      #Start by saving the latest results
      filename = self.config["outcomes"]
      
      if not(self.dummydata):
        self.outcomes.to_csv(filename, sep=self.config["sep"], index = False, header=False)
      
      self.display = self.outcomes.merge(self.classlist, left_on='id', right_on='id', right_index=False, how="left")
      self.display = self.display[['id', 'last', 'first', 'question', 'score', 'feedback']]
      self.display['score'] = numericcolumn(self.display['score'])

      #take copy for merge below
      df = self.display[['question','score','feedback']].copy()
      
      #replace returns so all lines visible in summary
      self.display.feedback = self.display.feedback.apply(lambda x: x.replace("\n", " "))
      
      f = lambda x: x.iloc[0]
      nc = lambda x: len(x.dropna())
      tc = lambda x: len([y for y in x if y!=""])
      
      self.totals = self.display.groupby(['id']).agg({'id':f, 'last':f, 'first':f, 'score': 'sum'})
      
      #Create combined table for generic and custom feedback
      self.combinedfeedback = self.feedback.copy()
      
      self.scoring = self.questions.question[~np.isnan(self.questions.marks)].tolist()
      self.nonscoring = self.questions.question[np.isnan(self.questions.marks)].tolist()
      
      df1 = df[df.question.isin(self.scoring)]
      df2 = df[df.question.isin(self.nonscoring)]
      
      if len(df2)>0:
        small_dfs = [df1]
        for q in df2.question.unique():
          values = df2.feedback[df2.question==q].tolist()
          values = [str(x).split(chr(10)) for x in values if x != np.nan]
          values = flatten(values)
          values = [clean(x) for x in values]
          small_dfs.append(pd.DataFrame({'question':[q]*len(values),'score':[np.nan]*len(values),'feedback':values}))
          
        df1 = pd.concat(small_dfs, ignore_index=True)
      
      #Merge in a way so that the generic feedback stays at the top
      df1.sort_values(['question','feedback'], ascending=True, inplace=True)
      df1.drop_duplicates(inplace=True)
      
      #Depricated pandas method
      #self.combinedfeedback = self.combinedfeedback.append(df1)
      self.combinedfeedback = pd.concat([self.combinedfeedback, df1])
      
      self.combinedfeedback.drop_duplicates(['question','feedback'],inplace=True)
      self.combinedfeedback = self.combinedfeedback[self.combinedfeedback.feedback!=""]
     
      #Create dataframe to summarise marks per question and overall totals
      #df = self.display.merge(self.questions, left_on='question', right_on='question')
      df = pd.merge(self.display.assign(question=self.display.question.astype(str)), 
                    self.questions.assign(question=self.questions.question.astype(str)), 
                    how='left', on='question')
      df = df[['question','description', 'score', 'marks','feedback']]
      
      #Extract rows that represent student totals
      totals = self.totals[['id', 'last', 'score','score']].copy()
      totals['feedback'] = ""
      totals.columns = df.columns
      totals['question'] = "Total"
      totals['description'] = "Sum of marks"
      totals['marks'] = self.questions.marks.sum()
      
      #Depricated pandas method
      #df = df.append(totals)
      df = pd.concat([df, totals])
      
      #Create group by column to aggregate by question not question component
      #Need to sum by question before applying summary metrics
      #df['q']=df.question.str.split(".", n=1, expand=True)[0]
      
      self.summary = df.groupby(['question']).agg(question=('question', f), 
                                                    description=('description',f),
                                                    available=('marks',f),
                                                    mean=('score',np.nanmean),
                                                    std=('score',np.nanstd), 
                                                    low=('score',min),
                                                    high=('score',max),
                                                    numcount=('score',nc),
                                                    textcount=('feedback',tc))

      
      #Drop first column (a duplicate)
      #self.display.drop(self.display.columns[0], axis=1, inplace=True)
      
      #Sort
      self.display = self.display.sort_values(["last", "first"], ascending = (True, True))
      self.totals = self.totals.sort_values(["last", "first"], ascending = (True, True))
      
      
      df = pd.DataFrame({"score":totals['score'].values})
      df.dropna(inplace=True)
      df['bin'] = pd.cut(df['score'], self.config["buckets"], right=False).astype(str)
      
      self.distribution = df.groupby('bin').agg(interval = ('bin',f),
                                                count=('bin',len))

    def setdefault(self, key, defaultvalue):
      
      if not (key in self.config):
        self.config[key] = defaultvalue
      
    def defaultconfig(self):
      
        self.setdefault("sep", ",")
        self.setdefault("module", "XXX9999")
        self.setdefault("assessment", "Assignment X")
        self.setdefault("fontface", "arial")
        self.setdefault("fontsize", 12)
        self.setdefault("bgcolor", "#f0f0f0")
        self.setdefault("feedbackbgcolor", "#fdfdde")
        self.setdefault("maxquestionsonscreen", 8)
        self.setdefault("feedbacklines", 4)
        
        self.setdefault("questions", "questions.txt")
        self.setdefault("feedback", "feedback.txt")
        self.setdefault("classlist", "classlist.txt")
        self.setdefault("outcomes", "outcomes.txt")
        self.setdefault("commentbank", "commentbank.txt")
        
        self.setdefault("apiurl", "https://canvas.qub.ac.uk/")
        self.setdefault("apikey", "")
        self.setdefault("courseid", "")
        self.setdefault("assignmentid", "")
        
        try:
          if ("buckets" in self.config):
            text = str(self.config["buckets"])
            text.replace("[","")
            text.replace("]","")
            buckets = text.split(",")
            buckets = [float(x) for x in buckets]
            self.config["buckets"] = buckets
          else:
            self.config["buckets"] = [0,40,50,60,70,80,90,100]
        except:
          self.config["buckets"] = [0,40,50,60,70,80,90,100]
           

    def resetlog(self):
      #Reset log
      self.log.configure(state='normal')
      self.log.delete('0.0', 'end')
      self.log.configure(state='disabled')

    def selectconfigfile(self):
      
      self.resetlog()
      
      self.configfile = fd.askopenfilename(title="Select Config File", initialdir = os.getcwd(), filetypes = [("config", "*.config")])
      
      if self.configfile=="":
        return 'break'
      
      os.chdir(os.path.dirname(self.configfile))
      
      self.lblfile.config(text=self.configfile)
      self.lblfile.update_idletasks()
      self.processconfig()
      self.owner.configupdate()
      return 'break'

    def createconfigfile(self):
      #self.popup = popupConfigCreate(self.owner.root)
      self.popup = popupConfigCreate(self)
      self.wait_window(self.popup.top)
      
      #Create suitable dummy files and save config
      folder = os.path.dirname(self.configfile)
      n = self.questioncount
      
      if os.path.exists(folder):
        
        try:
          
          #Save config
          with open(self.configfile, 'w') as f:
            json.dump(self.config,f, indent=4)
          
          #Create default data (some columns need to be strings!)
          self.questions = pd.DataFrame({"question":list(range(1,n+1))+['O'], "description":["Q"+str(i) for i in range(1,n+1)]+['Ovearall'], "marks":[10.0]*n+[""]})
          self.classlist = pd.DataFrame({"id":["100000"+str(i) for i in range(1,10)], "first":["john"]*9, "last":['smith']*9})
          self.feedback = pd.DataFrame({"question":list(itertools.chain.from_iterable([[i,i] for i in range(1,n+1)]))+["O"], "score":[4,7]*n+[""], "feedback":["good", "bad"]*n+["Good work"]})
          self.outcomes = pd.DataFrame({"id":[], "question":[], "score":[], "feedback":[]})
          self.bank = pd.DataFrame({"category":["Analysis","Analysis","Methodology"], "feedback":["Good","Bad","Could be improved"]})
          
          file = os.path.join(folder, self.config["questions"])
          self.questions.iloc[:,0:3].to_csv(file, sep=self.config["sep"], header = False, index = False)
          
          file = os.path.join(folder, self.config["feedback"])
          self.feedback.to_csv(file, sep=self.config["sep"], header = False, index = False)
          
          file = os.path.join(folder, self.config["classlist"])
          self.classlist.iloc[:,0:3].to_csv(file, sep=self.config["sep"], header = False, index = False)
          
          file = os.path.join(folder, self.config["commentbank"])
          self.bank.to_csv(file, sep=self.config["sep"], header = False, index = False)
          
          self.logmessage("New config files created in " + folder)
          self.logmessage("Please now edit default files.")
        
        except:
          self.logmessage("Error processing supplied config information",alert=True)
      
      else:
        self.logmessage("Error creating config file",alert=True)
      
      return 'break'

    def exporttotals(self):
      self.totals[["id","score"]].to_csv("totals.txt", index = False, header=False)

    def exportAllPDFs(self):
      self.owner.widget.exportAllPDFs()

    def processconfig(self):
      
      try:
        with open(self.configfile, 'r') as f:
          self.config = json.load(f)
          
        self.defaultconfig()
        
        self.logmessage("*"*80)
        
        self.logmessage("Config file (plus defaults)")
        self.dummydata = False
        
        for k,v in self.config.items():
          self.logmessage(f"{k}: {v}")
        
        self.logmessage("")
        
        folder = os.path.dirname(self.configfile)
        os.chdir(folder)
        print("working directory:", os.getcwd())
        
        filename = self.config["questions"]
        self.questions = pd.read_csv(filename, header=None, sep=self.config["sep"])
        self.questions.columns = ["question","description","marks"]
        self.logmessage(f"{filename} > {len(self.questions)} questions found")
        
        filename = self.config["classlist"]
        self.classlist = pd.read_csv(filename, header=None, sep=self.config["sep"])
        self.classlist.columns = ["id","first","last"]
        self.logmessage(f"{filename} > {len(self.classlist)} students found")
        
        filename = self.config["feedback"]
        self.feedback = pd.read_csv(filename, header=None, sep=self.config["sep"])
        self.feedback.columns = ["question", "score", "feedback"]
        self.logmessage(f"{filename} > {len(self.feedback)} default feedback comments found for {len(self.feedback.question.unique())} questions", False)
        
        #This is the one file that is allowed to be blank
        try:
          filename = self.config["outcomes"]
          self.outcomes = pd.read_csv(filename, header=None, sep=self.config["sep"], keep_default_na=False)
          
          #Drop emails to clean any issues of duplicates
          self.outcomes= self.outcomes.drop_duplicates()
          
          self.outcomes.columns = ["id","question", "score", "feedback"]
          self.logmessage(f"{filename} > {len(self.outcomes)} individual feedback comments found for {len(self.outcomes.question.unique())} questions and {len(self.outcomes.id.unique())} students", False)
        except:
          self.logmessage(f"{filename} > currently empty")
          self.outcomes = pd.DataFrame({"id":[self.classlist.id[0]], "question":[self.questions.question[0]], "score":[0.0], "feedback":[""]})
        
        #Create timestamped backup of input file
        ext = filename.split(".")[-1]
        filename = filename.replace("."+ext, "_"+datetime.now().strftime("%Y%m%d_%H%M") + "." + ext)
        self.outcomes.to_csv(filename, sep=self.config["sep"], index = False, header=False)
        
        filename = self.config["commentbank"]
        #Ccomment bank is not independent
        #self.bank = pd.read_csv(filename, header=None, sep=self.config["sep"])
        #self.bank.columns = ["category","feedback"]
        #self.logmessage(f"{filename} > {len(self.bank)} individual feedback comments found for {len(self.bank.category.unique())} categories")
        
        self.logmessage("*"*80+"\n")
        
        self.winfo_toplevel().title("QMS Grader: " + self.config["module"] + " " + self.config["assessment"])
        
        self.postloaddatafresh()
        self.owner.refresh()
        
      except Exception as e:
        
        self.logmessage("*** Serious Error ***", alert=True)
        messagebox.showerror("Config File Error", e)

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
      self.default = "version 1.0.9.BETA"
      
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
class Canvas(tk.Frame):
  
    def __init__(self, parent, owner):
        tk.Frame.__init__(self, parent)
        
        self.owner = owner
        self.btn1 = tk.Button(self, text="Check Connections", anchor='nw')
        self.btn1.bind("<Button-1>", lambda event: self.checkconfig())
        self.btn1.grid(row = 0, column = 0, sticky = 'nw', padx=5, pady=5)
        
        self.btn2 = tk.Button(self, text="Upload files", anchor='nw')
        self.btn2.bind("<Button-1>", lambda event: self.uploadfiles())
        self.btn2.grid(row = 0, column = 1, sticky = 'nw', padx=5, pady=5)
        
        self.btn3 = tk.Button(self, text="Upload marks", anchor='nw')
        self.btn3.bind("<Button-1>", lambda event: self.uploadmarks())
        self.btn3.grid(row = 0, column = 2, sticky = 'nw', padx=5, pady=5)
        
        self.overwrite = tk.IntVar()
        self.cboverwrite = tk.Checkbutton(self, text='overwrite',variable=self.overwrite, onvalue=1, offvalue=0)# command=self.togglereturn)
        self.cboverwrite.grid(row=0, column=3, padx=0, sticky='w')
        
        self.log = scrolledtext.ScrolledText(self, undo=False, height = 20)
        self.log.tag_config("highlight", foreground="red")
        self.log.grid(row = 1, column = 0, columnspan=4, sticky = 'news', padx=5, pady=5)
        self.log.configure(state='disabled')
        
        self.columnconfigure(3, weight=1)
        self.rowconfigure(1, weight=1)
        
      
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


    def checkconfig(self):
      
      try:
        self.log.delete('0.0', 'end')
        
        self.apirul = self.owner.config.config["apiurl"]
        self.apikey = self.owner.config.config["apikey"]
        self.courseid = int(self.owner.config.config["courseid"])
        self.assignmentid = int(self.owner.config.config["assignmentid"])
        
        self.logmessage("CONFIGURATION")
        self.logmessage("apirul: "+ self.apirul)
        self.logmessage("apikey: "+ ("*"*40)+self.apikey[-4:])
        self.logmessage("courseid "+ str(self.courseid))
        self.logmessage("assignmentid: "+ str(self.assignmentid))
        self.logmessage("")
      
        #Connect to canvas and the module/assignment 
        self.logmessage("CANVAS")
        self.canvas = cvs(self.apirul, self.apikey)
        self.course = self.canvas.get_course(self.courseid)
        self.logmessage("Course: " + self.course.course_code + " > " + self.course.name)
        self.assignment = self.course.get_assignment(self.assignmentid)
        self.logmessage("Assignment: " + str(self.assignment))
        self.logmessage("")
        
        #Find students in canvas module
        users = self.course.get_users(enrollment_type=['student'])

        #Create a dictionary of students keyed on their qub ids
        self.students = {}
        self.logmessage("STUDENTS")

        for user in users:
            self.logmessage(str(user.sis_user_id) + " > " + str(user))
            self.students[user.sis_user_id] = user

        #Create df to map to files and marks
        self.df = pd.DataFrame({"qubid" : self.students.keys(), "user":self.students.values()})
        
        #AH test ids in canvas are non-numeric so stick with strings
        #self.df.qubid = pd.to_numeric(self.df.qubid)
        self.df.qubid = self.df.qubid.apply(str)

        #Extact userid to match assignments to students
        self.df['userid'] = ''

        for index, row in self.df.iterrows():
          self.df.loc[index,'userid'] = row.user.id

        self.df.set_index("qubid", drop=True, inplace=True)

        self.logmessage(f"\nTotal students found: {len(self.df)}\n")
        
        #Match files to student feedback
        self.df['file'] = ""
        self.logmessage("FILE MAPPING")
        
        for filename in os.listdir():
          if filename.endswith(".pdf"):
            
            for index, row in self.df.iterrows():
              if str(index) in filename:
                self.df.loc[index,"file"] = filename
                break
            else:
              self.logmessage("No matches found for " + filename)

        #Create student id col
        self.df['sid'] = self.df.index
        
        for index, row in self.df.iterrows():
          self.logmessage(f"{row.sid} \t {row.user} \t {row.file}")
          
        n = len(self.df[self.df.file!=""])
        m = len(self.df)
        self.logmessage(f"\nMatched files for {n} of {m} students")
        
        #Retrieve the submissions
        #http://siever.info/canvas/GetAllComments.py
        self.submissions = self.assignment.get_submissions(include=['submission_comments'])
      
      except:
          self.logmessage("Error connecting to canvas with this configuration", alert=True)
          self.logmessage("apiurl: " +self.owner.config.config["apiurl"])
          self.logmessage("apikey: " +self.owner.config.config["apikey"])
          self.logmessage("courseid: " +self.owner.config.config["courseid"])
          self.logmessage("assignmentid: " +self.owner.config.config["assignmentid"])
          self.logmessage("Please check and update the config file")
      
      
    def uploadfiles(self):
      self.logmessage("\nUploading files...", True)
      
      #Loop over submissions
      for s in self.submissions:
        
        rowid = self.df.index[self.df.userid==s.user_id].tolist()
        
        if len(rowid)==1:
        
          row = self.df.loc[rowid[0]]
          previousuploads = False
          
          if row.file=="":
            self.logmessage(f"No file. Skipping {row.user}")
            continue
          
        #Check for previous comments with uploads
          for c in s.submission_comments:
            if c['author_id'] != s.user_id:
              for a in c['attachments']:
                
                if a['display_name'] in row.file:
                  previousuploads = True
                  break
          
          if not(previousuploads):
            file = os.path.join(os.getcwd(), row.file)
            s.upload_comment(file)
            self.logmessage(f"Uploaded {row.file} for {row.user}")
          else:
            self.logmessage(f"Existing upload. Skipping {row.user}")


    def uploadmarks(self):
      
      try:
        self.logmessage("\nUploading marks...", True)
        totals = self.owner.config.totals.copy()
        
        #Loop over submissions
        for s in self.submissions:
          
          rowid = self.df.index[self.df.userid==s.user_id].tolist()
          
          if len(rowid)==1:
            
            rowid = rowid[0]
            
            if rowid in totals.index:
            
              #Remember totals is result of group by
              #Take care when accessing elements (use dict approach)
              row = totals.loc[rowid]
              first = row["first"]
              last = row["last"]
              qubid = row["id"]
              score = row["score"]
              
              if not(score=="" or score==None or pd.isnull(score)):
                if self.overwrite.get()==1 or (s.score==None):
                  s.edit(submission={'posted_grade':row.score})
                  
                  self.logmessage(f"{last}, {first} ({qubid}): Posting grade of {str(score)}")
                elif (s.score!=None):
                  self.logmessage(f"{last}, {first} ({qubid}): Skipping (already graded)")
            
        self.logmessage("Upload complete\n")

      except Exception as e:
        self.logmessage("Error uploading marks\n", alert = True)
        self.logmessage(str(e))
        

#------------------------------------------------------------------------------
#Popup class to create new config file
class popupConfigCreate(object):
  
    def __init__(self,parent):
      
        #parent is the class rather than the window here
        self.top = tk.Toplevel(parent.owner.root)
        self.parent = parent
        
        self.top.title('QMS Grader')
        self.top.geometry("600x200")
        
        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.lblmodulecode = tk.Label(self.top, text="Module Code", anchor='w')
        self.lblmodulecode.grid(row = 0, column = 0, sticky = 'w', pady=5, padx = 2)
        
        self.lblassessmentname = tk.Label(self.top, text="Assessment Name", anchor='w')
        self.lblassessmentname.grid(row = 1, column = 0, sticky = 'w', pady=5, padx = 2)
        
        self.lblquestions = tk.Label(self.top, text="Questions", anchor='w')
        self.lblquestions.grid(row = 2, column = 0, sticky = 'w', pady=5, padx = 2)
        
        self.lblfolder = tk.Label(self.top, text="Assignment Directory", anchor='w')
        self.lblfolder.grid(row = 3, column = 0, sticky = 'w', pady=5, padx = 2)
        
        self.svmodulcode = StringVar()
        w = tk.Entry(self.top, width=5, justify='left', textvariable=self.svmodulcode)
        w.grid(row = 0, column = 1, columnspan =2, sticky = 'we', pady=5, padx = 2)
        
        self.svassessmentname = StringVar()
        w = tk.Entry(self.top, width=5, justify='left', textvariable=self.svassessmentname)
        w.grid(row = 1, column = 1, columnspan =2, sticky = 'we', pady=5, padx = 2)
        
        values = [str(i) for i in range(1,21)]
        values.insert(0,"")
        self.cmbquestions = Combobox(self.top, values = values, height=10, state="readonly")
        self.cmbquestions.grid(row = 2, column = 1, columnspan =2, sticky = 'we', pady=5, padx = 2)
        
        self.lblfolderselected = tk.Label(self.top, text="...", anchor='w')
        self.lblfolderselected.grid(row = 3, column = 1, sticky = 'w', pady=5, padx = 2)
        
        self.btnfolder = tk.Button(self.top, text="...", anchor='e')
        self.btnfolder.grid(row=3, column=3, padx=5, sticky='w')
        self.btnfolder.bind("<Button-1>", self.selectfolder)
        self.btnfolder.columnconfigure(3, weight=0)
        
        self.btnsave = tk.Button(self.top, text="Save", anchor='e')
        self.btnsave.grid(row=4, column=3, padx=5, sticky='w')
        self.btnsave.bind("<Button-1>", self.saveconfig)
        
        self.top.columnconfigure(0, weight=0)
        self.top.columnconfigure(1, weight=1)
        self.top.columnconfigure(2, weight=0)
        
        parent.owner.root.withdraw()
   
    def selectfolder(self, event=None):
      
      self.folder = fd.askdirectory(title="Select Config File", initialdir = os.getcwd())
      
      if self.folder=="":
        return 'break'
      
      self.lblfolderselected.config(text=self.folder)
      self.lblfolderselected.update_idletasks()
      
      return 'break'
      
      
    def on_closing(self):
        
        #Exit without saving
        self.parent.owner.root.deiconify()
        self.top.destroy()
      
    def saveconfig(self, parent):
        
        try:
          #Reset and then update values
          self.parent.defaultconfig()
          
          module = self.svmodulcode.get()
          assessment = self.svassessmentname.get()
          
          self.parent.config["assessment"] = assessment
          self.parent.config["module"] = module
          
          try:
            self.parent.questioncount = int(self.cmbquestions.get())
          except:
            self.parent.questioncount = 5
          
          file = os.path.join(self.lblfolderselected.cget("text"), module + "_" + assessment + ".config")
          
          self.parent.configfile = file
        
        except:
          pass
        
        #Return to main window
        self.parent.owner.root.deiconify()
        self.top.destroy()


#------------------------------------------------------------------------------
class GUI():
  
  def __init__(self):
    
    self.root = tk.Tk()
    self.root.title('QMS Grader')
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
    
    #Create notebook for application tabs
    self.notebook = Notebook(self.root)
    self.notebook.pack(pady=2, fill='both', expand=True)
    
    #Create frames for each tab
    self.frame1 = tk.Frame(self.notebook, width=400, height=280)
    self.frame2 = tk.Frame(self.notebook, width=400, height=280)
    self.frame3 = tk.Frame(self.notebook, width=400, height=280)
    self.frame4 = tk.Frame(self.notebook, width=400, height=280)
    self.frame5 = tk.Frame(self.notebook, width=400, height=280)
    self.frame6 = tk.Frame(self.notebook, width=400, height=280)
    self.frame7 = tk.Frame(self.notebook, width=400, height=280)
    self.frame8 = tk.Frame(self.notebook, width=400, height=280)
        
    self.frame1.pack(fill='both', expand=True)
    self.frame2.pack(fill='both', expand=True)
    self.frame3.pack(fill='both', expand=True)
    self.frame4.pack(fill='both', expand=True)
    self.frame5.pack(fill='both', expand=True)
    self.frame6.pack(fill='both', expand=True)
    self.frame7.pack(fill='both', expand=True)
    self.frame8.pack(fill='both', expand=True)
    
    #Create status bar
    self.sb=StatusBar(self.root)
    self.sb.pack(pady=0, fill='x', expand=False, side = "bottom")
    
    #Create custom config frame for first tab
    self.config = Config(self.frame1, self)
    self.config.pack(fill='both', expand=True, anchor = 'n')
    
    #Create custom widget for frame 3 (feedback)
    self.widget = CustomWidget(self.frame2, self)
    self.widget.pack(fill='both', expand=True, anchor = 'n')
    
    self.outcomes = PandaFrame(self.frame3, self, self.config.display)
    self.outcomes.pack(fill='both', expand=True, anchor = 'n')
    
    self.totals = PandaFrame(self.frame4, self, self.config.totals)
    self.totals.pack(fill='both', expand=True, anchor = 'n')
    
    self.summary = PandaFrame(self.frame5, self, self.config.summary)
    self.summary.pack(fill='both', expand=True, anchor = 'n')
    
    self.distribution = PandaFrame(self.frame6, self, self.config.distribution)
    self.distribution.pack(fill='both', expand=True, anchor = 'n')
    
    self.bank = commentbank(self.frame7, "", self.config.logmessage)
    self.bank.pack(fill='both', expand=True, anchor = 'n')
    
    self.canvas = Canvas(self.frame8, self)
    self.canvas.pack(fill='both', expand=True, anchor = 'n')
    
    # add frames to notebook
    self.notebook.add(self.frame1, text='Configuration')
    self.notebook.add(self.frame2, text='Grader')
    self.notebook.add(self.frame3, text='Breakdown')
    self.notebook.add(self.frame4, text='Totals')
    self.notebook.add(self.frame5, text='Summary')
    self.notebook.add(self.frame6, text='Distribution')
    self.notebook.add(self.frame7, text='Comment Bank')
    self.notebook.add(self.frame8, text='Canvas')
    
    self.sb.settext("")
  
  def configupdate(self):
    
    for widget in self.frame2.winfo_children():
      widget.destroy()

    self.widget = CustomWidget(self.frame2, self)
    self.widget.pack(fill='both', expand=True, anchor = 'n')
    self.widget._configure_canvas()
    
    print("updating bank", self.config.config["commentbank"])
    print("working directory:", os.getcwd())
    
    self.bank.loaddata(self.config.config["commentbank"])
    self.bank.refresh()
  
  def refresh(self):
    
    self.config.preparesummarytables()
    
    self.outcomes.refresh(self.config.display)
    self.summary.refresh(self.config.summary)
    self.totals.refresh(self.config.totals)
    self.distribution.refresh(self.config.distribution)
    
    self.config.logmessage(f"Feedback for {len(self.config.outcomes.id.unique())} of {len(self.config.classlist)} students")
    self.sb.settext("")
  
  def mainloop(self):
    self.root.mainloop()
    

if __name__ == "__main__":
  
  gui = GUI()
  gui.mainloop()