# -*- coding: utf-8 -*-
#------------------------------------------------------------
# streamondemand - XBMC Plugin
# Lista de vídeos descargados
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand/
#------------------------------------------------------------
# Herramientas responsables de adaptar los diferentes 
# cuadros de dialogo a una plataforma en concreto,
# en este caso Kodi.
# version 1.3
# ------------------------------------------------------------
import xbmcgui
import xbmc
import os
from math import ceil
from core import config


def dialog_ok(heading, line1, line2="", line3=""):
    dialog = xbmcgui.Dialog()
    return dialog.ok(heading, line1, line2, line3)
    
def dialog_notification(heading, message, icon=0, time=5000, sound=True):
    dialog = xbmcgui.Dialog()
    l_icono=(xbmcgui.NOTIFICATION_INFO , xbmcgui.NOTIFICATION_WARNING, xbmcgui.NOTIFICATION_ERROR)
    dialog.notification (heading, message, l_icono[icon], time, sound)
    
def dialog_yesno(heading, line1, line2="", line3="", nolabel="No", yeslabel="Si", autoclose=""):
    dialog = xbmcgui.Dialog()
    if autoclose:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel, autoclose)
    else:
        return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)
  
def dialog_select(title, opciones): 
    resultado = xbmcgui.Dialog().select(title, opciones)
    if resultado ==-1: resultado = None
    return resultado
 
def dialog_progress(title, Texto):
  progreso = xbmcgui.DialogProgress()
  progreso.create(title , Texto)
  Progreso = DialogoProgreso(progreso,title)
  return Progreso   
    
def keyboard(Texto, Title="", Password=False):
    keyboard = xbmc.Keyboard(Texto, Title, Password)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return keyboard.getText()
    else:
        return None
    
class DialogoProgreso(object):
  Progreso=""
  Titulo=""
  Closed=False
  def __init__(self, Progreso, Titulo):
    self.Progreso = Progreso
    self.Titulo = Titulo
    self.Closed = False
  
  def iscanceled(self):
    return (self.Progreso.iscanceled() or self.Closed)

  def update(self,Porcentaje, Texto):
    Linea1=" "
    Linea2=" "
    Linea3=" "
    if len(Texto.split("\n"))>0:
      Linea1= Texto.split("\n")[0]
    if len(Texto.split("\n"))>1:
      Linea2= Texto.split("\n")[1]
    if len(Texto.split("\n"))>2:
      Linea3= Texto.split("\n")[2]
    self.Progreso.update(Porcentaje,Linea1,Linea2,Linea3)

  def close(self):
    self.Progreso.close()
    self.Closed = True    
    
    
    
#---------------------------------------------------------------------------
#  Clases para la pantalla de configuracion
#  Basadas en PyXBMCt
#
#
#----------------------------------------------------------------------------
_path_imagen= os.path.join(config.get_runtime_path(), 'resources', 'skins', 'Default', 'media')

# Text alighnment constants. Mixed variants are obtained by bit OR (|)
ALIGN_LEFT = 0
ALIGN_RIGHT = 1
ALIGN_CENTER_X = 2
ALIGN_CENTER_Y = 4
ALIGN_CENTER = 6
ALIGN_TRUNCATED = 8
ALIGN_JUSTIFY = 10

# XBMC key action codes.
## ESC action
ACTION_PREVIOUS_MENU = 10
## Backspace action
ACTION_NAV_BACK = 92
## Left arrow key
ACTION_MOVE_LEFT = 1
## Right arrow key
ACTION_MOVE_RIGHT = 2
## Up arrow key
ACTION_MOVE_UP = 3
## Down arrow key
ACTION_MOVE_DOWN = 4
## Mouse wheel up
ACTION_MOUSE_WHEEL_UP = 104
## Mouse wheel down
ACTION_MOUSE_WHEEL_DOWN = 105
## Mouse drag
ACTION_MOUSE_DRAG = 106
## Mouse move
ACTION_MOUSE_MOVE = 107


class SettingWindow( xbmcgui.WindowDialog ):
    ''' Clase derivada que permite utilizar cuadors de configuracion personalizados.
    
    Esta clase deriva de xbmcgui.WindowDialog y permite crear un cuadro de dialogo con controles del tipo:
    Radio Button (bool), Cuadro de texto (text), Lista (list) y Etiquetas informativas (label).
    Si se incluyen mas de 15 controles apareceran paginados en grupos de 15.
    Tambien podemos personalizar el cuadro añadiendole un titulo (caption).
    
    Metodo constructor:
        SettingWindow(listado_controles, dict_values, caption)
            Parametros:
                listado_controles: (list) Lista de controles a incluir en la ventana, segun el siguiente esquema:
                    list_controls= [{'id': "nameControl1",
                                  'type': "bool",                       # bool, text, list, label 
                                  'label': "Control 1: tipo RadioButton",
                                  'default': True,
                                  'enabled': True,
                                  'visible': True,
                                  'lvalues':"",                         # only for type = list
                                },
                                {'id': "nameControl2",
                                  'type': "text",                       # bool, text, list, label 
                                  'label': "Control 2: tipo Cuadro de texto",
                                  'default': "Valor por defecto",
                                  'enabled': True,
                                  'visible': True,
                                  'lvalues':"",                         # only for type = list
                                },
                                {'id': "nameControl3",
                                  'type': "list",                       # bool, text, list, label 
                                  'label': "Control 3: tipo Lista",
                                  'default': "item1",
                                  'enabled': True,
                                  'visible': True,
                                  'lvalues':["item1", "item2", "item3", "item4"],                         # only for type = list
                                },
                                {'id': "nameControl4",
                                  'type': "label",                       # bool, text, list, label 
                                  'label': "Control 4: tipo Etiqueta",
                                  'default': '0xFFee66CC',               # En este caso: valor opcional que representa el color del texto
                                  'enabled': True,
                                  'visible': True,
                                  'lvalues':"",                         # only for type = list
                                }]
                dict_values: (dict) Diccionario que representa el par (id: valor) de cada control de la lista.
                    Si algun control de la lista no esta incluido en este diccionario se le asignara el valor por defecto.
                        dict_values={"nameControl1": False,
                                     "nameControl2": "Esto es un ejemplo"}
                (opcional) caption: (str) Titulo de la ventana de configuracion.
    Metodos principales:
        get_values(): Retorna un diccionario con los pares (id: valor) obteniendo los datos de los controles de la ventana.
        isConfirmed(): Retorna True si se han confirmado los cambios en la ventana, False en caso contrario.
    '''
    window_next_page = None
    window_prev_page = None
    
    def __init__( self, list_controls , dict_values, caption=""):
        self.dict_values= dict_values
        self.modificado = False
        self.confirmado = False
        self.controles = {}
        
        # Definir ventana
        self.screen_x = 40
        self.screen_y = 30
        self.screen_w = 1080 - self.screen_x
        self.screen_h = 720 - int(self.screen_y * 1.5)
        self.num_controles_x_page = 15.0
        pos_y= self.screen_y + 10
        
        #           Fondo de ventana
        self.background = xbmcgui.ControlImage( self.screen_x, self.screen_y, self.screen_w, self.screen_h, 
                                                os.path.join(_path_imagen,'DialogBack.png'))
        self.addControl(self.background)
        
        #           Boton cerrar
        self.window_close_button = xbmcgui.ControlButton( self.screen_x + self.screen_w - 90 , pos_y + 10, 70, 40, '',
                        focusTexture=os.path.join(_path_imagen, 'DialogCloseButton-focus.png'),
                        noFocusTexture=os.path.join(_path_imagen, 'DialogCloseButton.png'))
        self.addControl(self.window_close_button)
        
        #           Titulo de ventana
        if caption:
            self.caption_background = xbmcgui.ControlImage(self.screen_x, pos_y , self.screen_w, 60, 
                                                            os.path.join(_path_imagen,'Controls', 'dialogheader.png'))
            self.addControl(self.caption_background)
            self.caption = xbmcgui.ControlLabel(self.screen_x, pos_y + 15 , self.screen_w, 40, caption, 
                                                alignment  = ALIGN_CENTER, textColor ='0xFFFFA500', font='font28_title')
            self.addControl(self.caption)
            
        #           Botones Aceptar y cancelar
            self.window_ok_button = xbmcgui.ControlButton( self.screen_x + self.screen_w - 350 , self.screen_y + self.screen_h - 70 , 150, 40, 'Aceptar',
                        alignment = ALIGN_CENTER,
                        focusTexture=os.path.join(_path_imagen, 'KeyboardKey.png'),
                        noFocusTexture=os.path.join(_path_imagen, 'KeyboardKeyNF.png'))
            self.addControl(self.window_ok_button)
            
            self.window_cancel_button = xbmcgui.ControlButton( self.screen_x + self.screen_w - 180 , self.screen_y + self.screen_h - 70 , 150, 40, 'Cancelar',
                        alignment = ALIGN_CENTER,
                        focusTexture=os.path.join(_path_imagen, 'KeyboardKey.png'),
                        noFocusTexture=os.path.join(_path_imagen, 'KeyboardKeyNF.png'))
            self.addControl(self.window_cancel_button)
            
            self.setFocus(self.window_ok_button)
            self.window_ok_button.controlRight(self.window_cancel_button)
            self.window_cancel_button.controlLeft(self.window_ok_button)
        
        #           Controles de paginacion
        
        self.total_paginas= int(ceil(len(list_controls) / self.num_controles_x_page))
        self.pagina_actual = 1
        if self.total_paginas > 1:
            pos_y += 70
            self.window_next_page = xbmcgui.ControlButton( self.screen_x + self.screen_w - 180 , pos_y , 150, 40, 'Siguiente',
                        alignment = ALIGN_CENTER,
                        focusTexture=os.path.join(_path_imagen, 'KeyboardKey.png'),
                        noFocusTexture=os.path.join(_path_imagen, 'KeyboardKeyNF.png'))
            self.addControl(self.window_next_page)
            self.window_prev_page = xbmcgui.ControlButton( self.screen_x + 30 , pos_y , 150, 40, 'Anterior',
                        alignment = ALIGN_CENTER,
                        focusTexture=os.path.join(_path_imagen, 'KeyboardKey.png'),
                        noFocusTexture=os.path.join(_path_imagen, 'KeyboardKeyNF.png'))
            self.addControl(self.window_prev_page)
            self.window_prev_page.setEnabled(False)
            self.labelPage = xbmcgui.ControlLabel(self.screen_x , pos_y , self.screen_w , 40, "Pagina %s de %s" %(self.pagina_actual, self.total_paginas), 
                                                alignment  = ALIGN_CENTER)#, textColor ='0xFFFFA500', font='font13')
            self.addControl(self.labelPage)
            
            self.window_prev_page.controlRight(self.window_next_page)
            self.window_next_page.controlLeft(self.window_prev_page)
            

        # Añadir controles y mostrar pagina
        self.__add_controles(list_controls, pos_y + 70)
        #self.__show_page()
    
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.__do_you_want_to_save()    
            self.close()
                   
    def onControl(self, control):
        if control == self.window_close_button:
            if not self.modificado:
                # Buscamos cambios en controlEdit (Desgraciadamente no provocan llamada a onControl)
                for v in self.controles.values(): 
                    if v['type'] == 'text' and v['value'] != v['control'].getText():
                        self.modificado =True
                        break
            if  self.modificado and dialog_yesno("Conservar cambios", "Algunos valores han sido modificados, ¿desea conservar los cambios?"):
                self.__save_values()  
            self.close()
            
        elif control == self.window_ok_button:    
            self.__save_values()
            self.close()
        
        elif control == self.window_cancel_button:    
            self.close()
        
        elif control == self.window_next_page:
            self.pagina_actual += 1
            self.window_prev_page.setEnabled(True)
            if self.pagina_actual == self.total_paginas:
                self.window_next_page.setEnabled(False)
            self.__show_page()
                        
        elif control == self.window_prev_page:
            self.pagina_actual -= 1
            self.window_next_page.setEnabled(True)
            if self.pagina_actual == 1:
                self.window_prev_page.setEnabled(False)
            self.__show_page()
            
        else:
            self.modificado =True
            if type(self.controles[control.getId()]['control']) == ListControl:
                self.controles[control.getId()]['control'].forwardInput()
            
    def __show_page(self):
        self.labelPage.setLabel("Pagina %s de %s" %(self.pagina_actual, self.total_paginas))
        num_control = 0
        for v in self.controles.values(): 
            if v['pagina'] != self.pagina_actual:
                v['control'].setVisible(False)
            else:
                v['control'].setVisible(v['visible'])
                '''
                # navegacion entre controles. Lo comento por q no parece funcionar bien
                if num_control == 0: 
                    # Primer control
                    if self.window_prev_page:
                        self.window_prev_page.controlDown(v['control'])
                        self.window_next_page.controlDown(v['control'])
                        v['control'].controlUp(self.window_next_page)
                    else:
                        self.window_ok_button.controlUp(v['control'])
                        self.window_cancel_button.controlup(v['control'])
                        v['control'].controlUp(self.window_ok_button)
                else:
                    # Controles intermedios
                    v['control'].controlUp(control_anterior)
                    control_anterior.controlDown(v['control'])
                
                num_control += 1
                if num_control == 16:
                    # Ultimo control
                    v['control'].controlDown(self.window_ok_button)
                    num_control = 0
                
                control_anterior = v['control']
                '''
                
    def __do_you_want_to_save(self):
        if not self.modificado:
            # Buscamos cambios en controlEdit (Desgraciadamente no provocan llamada a onControl)
            for v in self.controles.values(): 
                if v['type'] == 'text' and v['value'] != v['control'].getText():
                    self.modificado =True
                    break
        if  self.modificado and dialog_yesno("Conservar cambios", "Algunos valores han sido modificados, ¿desea conservar los cambios?"):
            self.__save_values()  
      
    def __save_values(self):
        self.confirmado = True
        for v in self.controles.values():
            if v['type'] == 'bool':
                self.dict_values[v['id']] = v['control'].isSelected()
            elif v['type'] == 'text':
                self.dict_values[v['id']] = v['control'].getText()
            elif v['type'] == 'list':
                self.dict_values[v['id']] = v['control'].getSelectedValue()    
           
    def __add_controles(self, list_controls, pos_ini):
                
        pos_x = self.screen_x + 20
        width_control = self.screen_w - 75
        pagina= 1
        pos_y = pos_ini
        num_control = 0
        
        for c in list_controls:
            # Fijar valores por defecto para cada control
            if not c.has_key('enabled') or c['enabled'] is None: c['enabled']= True
            if not c.has_key('visible') or c['visible'] is None: c['visible']= True
            if self.dict_values.has_key(c['id']): 
                c['value'] = self.dict_values[c['id']]
            else:
                c['value'] = c['default']
            
            c['pagina']= pagina
            if c['type'] == 'bool':
                control = xbmcgui.ControlRadioButton(pos_x, pos_y, width_control,  
                            height= 30, label= c['label'], font='font14', 
                            focusTexture= os.path.join(_path_imagen,'Controls', 'MenuItemFO.png'),
                            noFocusTexture= os.path.join(_path_imagen,'Controls', 'MenuItemNF.png'),
                            focusOnTexture= os.path.join(_path_imagen,'Controls', 'radiobutton-focus.png'), 
                            noFocusOnTexture= os.path.join(_path_imagen,'Controls', 'radiobutton-focus.png'), 
                            focusOffTexture= os.path.join(_path_imagen,'Controls', 'radiobutton-nofocus.png'),
                            noFocusOffTexture= os.path.join(_path_imagen,'Controls', 'radiobutton-nofocus.png'))
                self.addControl(control)
                control.setRadioDimension(x=width_control - 30, y=0, width=30, height=30)
                control.setSelected(c['value'])
                c['control']= control
                
                self.controles[control.getId()]= c
                
            elif c['type'] == 'text':
                control = xbmcgui.ControlEdit (-10, -10, width_control, 30, c['label'], font='font14',
                            focusTexture= os.path.join(_path_imagen,'Controls', 'MenuItemFO.png'),
                            noFocusTexture= os.path.join(_path_imagen,'Controls', 'MenuItemNF.png'))
                            
                self.addControl(control)
                control.setLabel(c['label'])
                control.setText(c['value'])
                control.setPosition(pos_x + 10, pos_y)
                control.setWidth(width_control - 10)
                control.setHeight (30)
                c['control']= control
                self.controles[control.getId()]= c
                
            elif c['type'] == 'list':
                control= ListControl(self, pos_x + 10, pos_y, width_control,30, c['label'], c['lvalues'], c['value'])
                self.addControl(control)
                c['control']= control
                self.controles[control.getId()-1] =  c # Boton up
                self.controles[control.getId()-2] =  c # Boton down
                
                
            elif c['type'] == 'label':
                if c['default'].startswith('0x'):
                    control= xbmcgui.ControlFadeLabel(pos_x + 10, pos_y, width_control, height=30, 
                                                      font='font24_title', textColor= c['default'])
                else:
                    control= xbmcgui.ControlFadeLabel(pos_x + 10, pos_y, width_control, height=30, 
                                                      font='font24_title', textColor= '0xFF0066CC')
                self.addControl(control)
                control.addLabel(c['label'])
                c['control']= control
                self.controles[control.getId()]= c
                
            else:
                # Control no soportado
                return
            
            # Comun para todos los controles   
            control.setEnabled(c['enabled'])
               
            if c['visible']:
                pos_y += 30
                control.setVisible(pagina == 1)
                num_control += 1
            else:
                control.setVisible(False)
            
            if (num_control % self.num_controles_x_page) == 0: 
                pos_y = pos_ini
                pagina +=1
        
        return 
 
    def get_values (self):
        return self.dict_values
    
    def isConfirmed(self):
        return self.confirmado  
        
class ListControl(xbmcgui.ControlLabel):

    options = []
    upBtn = None
    downBtn = None
    label = None
    window = None
    selectedIndex = 0
    
           
    def __new__(cls, *args, **kwargs):
        return super(ListControl, cls).__new__ (cls, args[1], args[2], args[3] -10 - (2*args[4]), args[4], "", alignment = ALIGN_RIGHT)
        
    def __init__(self, window, x, y, width, height, label, lvalues, value):
        self.options = lvalues
        self.window = window
        self.etiqueta = xbmcgui.ControlLabel(x, y, width, height, label)
        window.addControl(self.etiqueta)
        
        self.downBtn = xbmcgui.ControlButton( x +  width - height * 2 , y, height, height, '',
                        focusTexture=os.path.join(_path_imagen,'Controls', 'spinDown-Focus.png'),
                        noFocusTexture=os.path.join(_path_imagen,'Controls', 'spinDown-noFocus.png'))
        window.addControl(self.downBtn)
        
        self.upBtn = xbmcgui.ControlButton( x +  width - height, y, height, height, '', 
                        focusTexture=os.path.join(_path_imagen,'Controls', 'spinUp-Focus.png'),
                        noFocusTexture=os.path.join(_path_imagen,'Controls', 'spinUp-noFocus.png'))
        window.addControl(self.upBtn)
        self.selectedIndex = lvalues.index(value)
        self.__setSelected();
        
    def __setSelected(self):
        length = self.options.__len__()
        if self.selectedIndex < 0:
            self.selectedIndex = 0 
        elif self.selectedIndex > length - 1:
            self.selectedIndex = length - 1

        self.downBtn.setEnabled(self.selectedIndex != 0)
        self.upBtn.setEnabled(self.selectedIndex != length - 1)
        self.setLabel(self.options[self.selectedIndex])
        
    
    def forwardInput(self):
        focusedItem = self.window.getFocus()
        if focusedItem == self.upBtn:
            self.selectedIndex += 1
            self.__setSelected()   
        if focusedItem == self.downBtn:
            self.selectedIndex -= 1
            self.__setSelected()      
        return
           
    def setEnabled(self, enabled):
        self.etiqueta.setEnabled(enabled)
        self.downBtn.setEnabled(enabled)
        self.upBtn.setEnabled(enabled)
        super(ListControl, self).setEnabled(enabled)
        
    def setVisible(self, visible):
        self.etiqueta.setVisible(visible)
        self.downBtn.setVisible(visible)
        self.upBtn.setVisible(visible)
        super(ListControl, self).setVisible(visible)
    
    def getSelectedValue(self):
        return self.options[self.selectedIndex]
        
    def getSelectedIndex(self):
        return self.selectedIndex