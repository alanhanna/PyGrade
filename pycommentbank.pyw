# -*- coding: utf-8 -*-
"""
tkinter-based application for managing a comment bank for assessment feedback
"""

import os
import base64
from datetime import datetime

import tkinter as tk
from tkinter import filedialog as fd
from tkinter.ttk import Notebook
import tkinter.scrolledtext as scrolledtext

from commentbankwidget import commentbank

#------------------------------------------------------------------------------
class Config(tk.Frame):
  
    def __init__(self, parent, owner):
        tk.Frame.__init__(self, parent)
        
        self.owner = owner
        
        self.btnselect = tk.Button(self, text="Select File", anchor='nw')
        self.btnselect.bind("<Button-1>", lambda event: self.selectfile())
        self.btnselect.grid(row = 0, column = 0, sticky = 'nw', padx=5, pady=5)
        
        self.lblfile = tk.Label(self, text="", anchor="w")
        self.lblfile.grid(row = 0, column = 1, sticky = 'new', padx=5, pady=5)
        
        self.log = scrolledtext.ScrolledText(self, undo=False, height = 20)
        self.log.tag_config("highlight", foreground="red")
        self.log.grid(row = 3, column = 0, columnspan=2, sticky = 'news', padx=5, pady=5)
        self.log.configure(state='disabled')
        
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)


    def resetlog(self):
      #Reset log
      self.log.configure(state='normal')
      self.log.delete('0.0', 'end')
      self.log.configure(state='disabled')

    def selectfile(self):
      
      self.resetlog()
      
      self.file = fd.askopenfilename(title="Select CommentBank File", initialdir = os.getcwd(), filetypes = [("txt", "*.txt"), ("csv", "*.csv")])
      
      if self.file=="":
        return 'break'
      
      os.chdir(os.path.dirname(self.file))
      
      try:
        self.owner.refresh(self.file)
      except:
        self.logmessage("Problem processing file. Check correctly configured", alert=True)
      
      self.lblfile.config(text=self.file)
      self.lblfile.update_idletasks()
      
      return 'break'

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
      self.default = "version 1.0.1.BETA"
      
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
class CommentBankGUI():
  
  def __init__(self):
    
    self.root = tk.Tk()
    self.root.title('QMS Comment Bank')
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
    self.frame1.pack(fill='both', expand=True)
    
    self.frame2 = tk.Frame(self.notebook, width=400, height=280)
    self.frame2.pack(fill='both', expand=True)
    
    #Create custom config frame for first tab
    self.config = Config(self.frame1, self)
    self.config.pack(fill='both', expand=True, anchor = 'n')
    
    self.bank = commentbank(self.frame2, "", self.config.logmessage)
    self.bank.pack(fill='both', expand=True, anchor = 'n')
    
    # add frames to notebook
    self.notebook.add(self.frame1, text='Configuration')
    self.notebook.add(self.frame2, text='Comment Bank')
    
    #Create status bar
    self.sb=StatusBar(self.root)
    self.sb.pack(pady=0, fill='x', expand=False, side = "bottom")
    self.sb.settext("")

  def refresh(self, filename):
    self.bank.loaddata(filename)
    self.bank.refresh()

  def mainloop(self):
    self.root.mainloop()


if __name__ == "__main__":
  
  gui = CommentBankGUI()
  gui.mainloop()
