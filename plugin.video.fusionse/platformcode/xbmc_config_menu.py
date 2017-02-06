# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# fusionse 5
# Copyright 2015 tvalacarta@gmail.com
# http://www.mimediacenter.info/foro/viewforum.php?f=36
#
# Distributed under the terms of GNU General Public License v3 (GPLv3)
# http://www.gnu.org/licenses/gpl-3.0.html
# ------------------------------------------------------------
# This file is part of fusionse 5.
#
# fusionse 5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fusionse 5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with fusionse 5.  If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------
# XBMC Config Menu
# ------------------------------------------------------------

import inspect
import os

import xbmcgui

from core import channeltools
from core import config
from core import logger


class SettingsWindow(xbmcgui.WindowXMLDialog):
    """ Clase derivada que permite utilizar cuadros de configuracion personalizados.

    Esta clase deriva de xbmcgui.WindowXMLDialog y permite crear un cuadro de dialogo con controles del tipo:
    Radio Button (bool), Cuadro de texto (text), Lista (list) y Etiquetas informativas (label).
    Tambien podemos personalizar el cuadro añadiendole un titulo (title).

    Metodo constructor:
        SettingWindow(listado_controles, dict_values, title, callback, item)
            Parametros:
                listado_controles: (list) Lista de controles a incluir en la ventana, segun el siguiente esquema:
                    (opcional)list_controls= [
                                {'id': "nameControl1",
                                  'type': "bool",                       # bool, text, list, label
                                  'label': "Control 1: tipo RadioButton",
                                  'color': '0xFFee66CC',                # color del texto en formato ARGB hexadecimal
                                  'default': True,
                                  'enabled': True,
                                  'visible': True
                                },
                                {'id': "nameControl2",
                                  'type': "text",                       # bool, text, list, label
                                  'label': "Control 2: tipo Cuadro de texto",
                                  'color': '0xFFee66CC',
                                  'default': "Valor por defecto",
                                  'hidden': False,                      # only for type = text Indica si hay que ocultar
                                                                            el texto (para passwords)
                                  'enabled': True,
                                  'visible': True
                                },
                                {'id': "nameControl3",
                                  'type': "list",                       # bool, text, list, label
                                  'label': "Control 3: tipo Lista",
                                  'color': '0xFFee66CC',
                                  'default': 0,                         # Indice del valor por defecto en lvalues
                                  'enabled': True,
                                  'visible': True,
                                  'lvalues':["item1", "item2", "item3", "item4"],  # only for type = list
                                },
                                {'id': "nameControl4",
                                  'type': "label",                       # bool, text, list, label
                                  'label': "Control 4: tipo Etiqueta",
                                  'color': '0xFFee66CC',
                                  'enabled': True,
                                  'visible': True
                                }]
                    Si no se incluye el listado_controles, se intenta obtener del xml del canal desde donde se hace la
                    llamada.
                    El formato de los controles en el xml es:
                        <?xml version="1.0" encoding="UTF-8" ?>
                        <channel>
                            ...
                            ...
                            <settings>
                                <id>nameControl1</id>
                                <type>bool</type>
                                <label>Control 1: tipo RadioButton</label>
                                <default>false</default>
                                <enabled>true</enabled>
                                <visible>true</visible>
                                <color>0xFFee66CC</color>
                            </settings>
                            <settings>
                                <id>nameControl2</id>
                                <type>text</type>
                                <label>Control 2: tipo Cuadro de texto</label>
                                <default>Valor por defecto</default>
                                <hidden>true</hidden>
                                <enabled>true</enabled>
                                <visible>true</visible>
                                <color>0xFFee66CC</color>
                            </settings>
                            <settings>
                                <id>nameControl3</id>
                                <type>list</type>
                                <label>Control 3: tipo Lista</label>
                                <default>0</default>
                                <enabled>true</enabled>
                                <color>0xFFee66CC</color>
                                <visible>true</visible>
                                <lvalues>item1</lvalues>
                                <lvalues>item2</lvalues>
                                <lvalues>item3</lvalues>
                                <lvalues>item4</lvalues>
                            </settings>
                            <settings>
                                <id>nameControl4</id>
                                <type>label</type>
                                <label>Control 4: tipo Etiqueta</label>
                                <enabled>true</enabled>
                                <visible>true</visible>
                                <color>0xFFee66CC</color>
                            </settings>
                            ...
                        </channel>


                    Los campos 'label', 'default' y 'lvalues' pueden ser un numero precedido de '@'. En cuyo caso se
                    buscara el literal en el archivo string.xml del idioma seleccionado.
                    Los campos 'enabled' y 'visible' admiten los comparadores eq(), gt() e it() y su funcionamiento se
                    describe en: http://kodi.wiki/view/Add-on_settings#Different_types

                (opcional)dict_values: (dict) Diccionario que representa el par (id: valor) de los controles de la
                lista.
                    Si algun control de la lista no esta incluido en este diccionario se le asignara el valor por
                    defecto.
                        dict_values={"nameControl1": False,
                                     "nameControl2": "Esto es un ejemplo"}

                (opcional) title: (str) Titulo de la ventana de configuracion. Se puede localizar mediante un numero
                precedido de '@'
                (opcional) callback (str) Nombre de la funcion, del canal desde el que se realiza la llamada, que sera
                invocada al pulsar
                    el boton aceptar de la ventana. A esta funcion se le pasara como parametros el objeto 'item' y el
                    dicionario 'dict_values'
            Retorno: Si se especifica 'callback' se devolvera lo que devuelva esta funcion. Si no devolvera None

    Ejemplos de uso:
        platformtools.show_channel_settings(): Así tal cual, sin pasar ningún argumento, la ventana detecta de que canal
        se ha hecho la llamada,
            y lee los ajustes del XML y carga los controles, cuando le das a Aceptar los vuelve a guardar.

        return platformtools.show_channel_settings(list_controls=list_controls, dict_values=dict_values, callback='cb',
        item=item):
            Así abre la ventana con los controles pasados y los valores de dict_values, si no se pasa dict_values, carga
            los valores por defecto de los controles,
            cuando le das a aceptar, llama a la función 'callback' del canal desde donde se ha llamado, pasando como
            parámetros, el item y el dict_values
    """
    def start(self, list_controls=None, dict_values=None, title="Opzioni", callback=None, item=None,
              custom_button=None):
        logger.info("[xbmc_config_menu] start")

        # Ruta para las imagenes de la ventana
        self.mediapath = os.path.join(config.get_runtime_path(), 'resources', 'skins', 'Default', 'media')

        # Capturamos los parametros
        self.list_controls = list_controls
        self.values = dict_values
        self.title = title
        self.callback = callback
        self.item = item
        self.custom_button = custom_button

        # Obtenemos el canal desde donde se ha echo la llamada y cargamos los settings disponibles para ese canal
        channelpath = inspect.currentframe().f_back.f_back.f_code.co_filename
        self.channel = os.path.basename(channelpath).replace(".py", "")

        # Si no tenemos list_controls, hay que sacarlos del xml del canal
        if not self.list_controls:

            # Si la ruta del canal esta en la carpeta "channels", obtenemos los controles y valores mediante chaneltools
            if os.path.join(config.get_runtime_path(), "channels") in channelpath:

                # La llamada se hace desde un canal
                self.list_controls, default_values = channeltools.get_channel_controls_settings(self.channel)

            # En caso contrario salimos
            else:
                return None

        # Si no se pasan dict_values, creamos un dict en blanco
        if self.values is None:
            self.values = {}

        # Ponemos el titulo
        if self.title == "":
            self.title = str(config.get_localized_string(30100)) + " -- " + self.channel.capitalize()

        elif self.title.startswith('@') and unicode(self.title[1:]).isnumeric():
            self.title = config.get_localized_string(int(self.title[1:]))

        # Muestra la ventana
        self.return_value = None
        self.doModal()
        return self.return_value

    @staticmethod
    def set_enabled(c, val):
        if c["type"] == "list":
            c["control"].setEnabled(val)
            c["downBtn"].setEnabled(val)
            c["upBtn"].setEnabled(val)
            c["label"].setEnabled(val)
        else:
            c["control"].setEnabled(val)

    @staticmethod
    def set_visible(c, val):
        if c["type"] == "list":
            c["control"].setVisible(val)
            c["downBtn"].setVisible(val)
            c["upBtn"].setVisible(val)
            c["label"].setVisible(val)
        else:
            c["control"].setVisible(val)

    def evaluate_conditions(self):
        for c in self.controls:
            if c["show"]:
                self.set_enabled(c, self.evaluate(self.controls.index(c), c["enabled"]))
                self.set_visible(c, self.evaluate(self.controls.index(c), c["visible"]))

    def evaluate(self, index, cond):
        import re

        # Si la condicion es True o False, no hay mas que evaluar, ese es el valor
        if type(cond) == bool:
            return cond

        # Si la condicion es un str representando un boleano devolvemos el valor
        if cond.lower() == "true":
            return True
        elif cond.lower() == "false":
            return False

        # Obtenemos las condiciones
        conditions = re.compile("(!?eq|!?gt|!?lt)?\(([^,]+),[\"|']?([^)|'|\"]*)['|\"]?\)[ ]*([+||])?").findall(cond)
        for operator, id, value, next in conditions:
            # El id tiene que ser un numero, sino, no es valido y devuelve False
            try:
                id = int(id)
            except:
                return False

            # El control sobre el que evaluar, tiene que estar dentro del rango, sino devuelve False
            if index + id < 0 or index + id >= len(self.controls):
                return False

            else:
                # Obtenemos el valor del control sobre el que se compara
                c = self.controls[index + id]
                if c["type"] == "bool":
                    control_value = bool(c["control"].isSelected())
                if c["type"] == "text":
                    control_value = c["control"].getText()
                if c["type"] == "list":
                    control_value = c["control"].getLabel()
                if c["type"] == "label":
                    control_value = c["control"].getLabel()

            # Operaciones lt "menor que" y gt "mayor que", requieren que las comparaciones sean numeros, sino devuelve
            # False
            if operator in ["lt", "!lt", "gt", "!gt"]:
                try:
                    value = int(value)
                except ValueError:
                    return False

            # Operacion eq "igual a" puede comparar cualquier cosa, como el valor lo obtenemos mediante el xml no
            # sabemos su tipo (todos son str) asi que intentamos detectarlo
            if operator in ["eq", "!eq"]:
                # valor int
                try:
                    value = int(value)
                except ValueError:
                    pass

                # valor bool
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False

            # operacion "eq" "igual a"
            if operator == "eq":
                if control_value == value:
                    ok = True
                else:
                    ok = False

            # operacion "!eq" "no igual a"
            if operator == "!eq":
                if not control_value == value:
                    ok = True
                else:
                    ok = False

            # operacion "gt" "mayor que"
            if operator == "gt":
                if control_value > value:
                    ok = True
                else:
                    ok = False

            # operacion "!gt" "no mayor que"
            if operator == "!gt":
                if not control_value > value:
                    ok = True
                else:
                    ok = False

            # operacion "lt" "menor que"
            if operator == "lt":
                if control_value < value:
                    ok = True
                else:
                    ok = False

            # operacion "!lt" "no menor que"
            if operator == "!lt":
                if not control_value < value:
                    ok = True
                else:
                    ok = False

            # Siguiente operación, si es "|" (or) y el resultado es True, no tiene sentido seguir, es True
            if next == "|" and ok is True:
                break
            # Siguiente operación, si es "+" (and) y el resultado es False, no tiene sentido seguir, es False
            if next == "+" and ok is False:
                break

            # Siguiente operación, si es "+" (and) y el resultado es True, Seguira, para comprobar el siguiente valor
            # Siguiente operación, si es "|" (or) y el resultado es False, Seguira, para comprobar el siguiente valor

        return ok

    def onInit(self):
        # Ponemos el título
        self.getControl(10002).setLabel(self.title)

        if self.custom_button is not None:
            if self.custom_button['method'] != "":
                self.getControl(10006).setLabel(self.custom_button['name'])
            else:
                self.getControl(10006).setVisible(False)
                self.getControl(10004).setPosition(self.getControl(10004).getX() + 80, self.getControl(10004).getY())
                self.getControl(10005).setPosition(self.getControl(10005).getX() + 80, self.getControl(10005).getY())

        # Obtenemos las dimensiones del area de controles
        self.controls_width = self.getControl(10007).getWidth() - 20
        self.controls_height = self.getControl(10007).getHeight()
        self.controls_pos_x = self.getControl(10007).getX() + self.getControl(10001).getX() + 10
        self.controls_pos_y = self.getControl(10007).getY() + self.getControl(10001).getY()
        self.height_control = 35
        font = "font12"

        # Creamos un listado de controles, para tenerlos en todo momento localizados y posicionados en la ventana
        self.controls = []

        x = 0
        for c in self.list_controls:
            # Posicion Y para cada control
            pos_y = self.controls_pos_y + x * self.height_control

            # Saltamos controles que no tengan los valores adecuados
            if "type" not in c:
                continue
            if "label" not in c:
                continue
            if c["type"] != "label" and "id" not in c:
                continue
            if c["type"] == "list" and "lvalues" not in c:
                continue
            if c["type"] == "list" and not type(c["lvalues"]) == list:
                continue
            if c["type"] == "list" and not len(c["lvalues"]) > 0:
                continue
            if c["type"] != "label" and c["id"] in [control["id"] for control in self.controls]:
                continue

            # Translation label y lvalues
            if c['label'].startswith('@') and unicode(c['label'][1:]).isnumeric():
                c['label'] = config.get_localized_string(int(c['label'][1:]))
            if c['type'] == 'list':
                lvalues = []
                for li in c['lvalues']:
                    if li.startswith('@') and unicode(li[1:]).isnumeric():
                        lvalues.append(config.get_localized_string(int(li[1:])))
                    else:
                        lvalues.append(li)
                c['lvalues'] = lvalues

            # Valores por defecto en caso de que el control no disponga de ellos
            if c["type"] == "bool" and "default" not in c:
                c["default"] = False
            if c["type"] == "text" and "default" not in c:
                c["default"] = ""
            if c["type"] == "text" and "hidden" not in c:
                c["hidden"] = False
            if c["type"] == "list" and "default" not in c:
                c["default"] = 0
            if c["type"] == "label" and "id" not in c:
                c["id"] = None
            if "color" not in c:
                c["color"] = "0xFF0066CC"
            if "visible" not in c:
                c["visible"] = True
            if "enabled" not in c:
                c["enabled"] = True

            # Para simplificar el codigo pasamos los campos a variables
            id = c["id"]
            label = c['label']
            ctype = c["type"]
            visible = c["visible"]
            enabled = c["enabled"]
            color = c["color"]
            if ctype == "list":
                lvalues = c["lvalues"]
            if ctype == "text":
                hidden = c["hidden"] if type(c["hidden"]) == bool else (
                    True if c["hidden"].lower() == 'true' else False)

            # Decidimos si usar el valor por defecto o el valor guardado
            if ctype in ["bool", "text", "list"]:
                default = c["default"]
                if id not in self.values:
                    if not self.callback:
                        self.values[id] = config.get_setting(id, self.channel)
                    else:
                        self.values[id] = default

                value = self.values[id]

            if ctype == "bool":
                c["default"] = bool(c["default"])
                self.values[id] = bool(self.values[id])

            # Control "bool"
            if ctype == "bool":
                # Creamos el control
                control = xbmcgui.ControlRadioButton(self.controls_pos_x - 10, -100, self.controls_width + 10,
                                                     self.height_control, label=label, font=font, textColor=color,
                                                     focusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                               'MenuItemFO.png'),
                                                     noFocusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                                 'MenuItemNF.png'),
                                                     focusOnTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                                 'radiobutton-focus.png'),
                                                     noFocusOnTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                                   'radiobutton-focus.png'),
                                                     focusOffTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                                  'radiobutton-nofocus.png'),
                                                     noFocusOffTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                                    'radiobutton-nofocus.png'))
                # Lo añadimos a la ventana
                self.addControl(control)

                # Cambiamos las propiedades
                control.setRadioDimension(x=self.controls_width + 10 - (self.height_control - 5), y=0,
                                          width=self.height_control - 5, height=self.height_control - 5)
                control.setSelected(value)
                control.setVisible(False)

                # Lo añadimos al listado
                self.controls.append({"id": id, "type": ctype, "control": control, "x": self.controls_pos_x - 10,
                                      "y": pos_y, "default": default, "enabled": enabled, "visible": visible})

            # Control "text"
            elif ctype == 'text':
                # Creamos el control
                control = xbmcgui.ControlEdit(self.controls_pos_x, -100, self.controls_width - 5, self.height_control,
                                              label, font=font, isPassword=hidden, textColor=color,
                                              focusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                        'MenuItemFO.png'),
                                              noFocusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                          'MenuItemNF.png'))
                # Lo añadimos a la ventana
                self.addControl(control)

                # Cambiamos las propiedades
                control.setVisible(False)
                control.setLabel(label)
                control.setText(value)
                control.setPosition(self.controls_pos_x, pos_y)
                control.setWidth(self.controls_width - 5)
                control.setHeight(self.height_control)

                # Lo añadimos al listado
                self.controls.append(
                    {"id": id, "type": ctype, "control": control, "x": self.controls_pos_x, "y": pos_y,
                     "default": default, "enabled": enabled, "visible": visible})

            # Control "list"
            elif ctype == 'list':
                # Creamos los controles el list se forma de 3 controles
                control = xbmcgui.ControlButton(self.controls_pos_x, -100, self.controls_width, self.height_control,
                                                label, font=font, textOffsetX=0, textColor=color,
                                                focusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                          'MenuItemFO.png'),
                                                noFocusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                            'MenuItemNF.png'))

                label = xbmcgui.ControlLabel(self.controls_pos_x, -100, self.controls_width - 30, self.height_control,
                                             lvalues[value], font=font, textColor=color, alignment=4 | 1)

                upBtn = xbmcgui.ControlButton(self.controls_pos_x + self.controls_width - 25, -100, 20, 15, '',
                                              focusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                        'spinUp-Focus.png'),
                                              noFocusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                          'spinUp-noFocus.png'))

                downBtn = xbmcgui.ControlButton(self.controls_pos_x + self.controls_width - 25, -100 + 15, 20, 15, '',
                                                focusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                          'spinDown-Focus.png'),
                                                noFocusTexture=os.path.join(self.mediapath, 'ChannelSettings',
                                                                            'spinDown-noFocus.png'))

                # Los añadimos a la ventana
                self.addControl(control)
                self.addControl(label)
                self.addControl(upBtn)
                self.addControl(downBtn)

                # Cambiamos las propiedades
                control.setVisible(False)
                label.setVisible(False)
                upBtn.setVisible(False)
                downBtn.setVisible(False)

                # Lo añadimos al listado
                self.controls.append(
                    {"id": id, "type": ctype, "control": control, "label": label, "downBtn": downBtn, "upBtn": upBtn,
                     "x": self.controls_pos_x, "y": pos_y, "lvalues": c["lvalues"], "default": default,
                     "enabled": enabled, "visible": visible})

            # Control "label"
            elif ctype == 'label':
                # Creamos el control
                control = xbmcgui.ControlLabel(self.controls_pos_x, -100, self.controls_width, height=30, label=label,
                                               alignment=4, font=font, textColor=color)

                # Lo añadimos a la ventana
                self.addControl(control)

                # Cambiamos las propiedades
                control.setVisible(False)

                # Lo añadimos al listado
                self.controls.append(
                    {"id": None, "type": ctype, "control": control, "x": self.controls_pos_x, "y": pos_y,
                     "enabled": enabled, "visible": visible})

            # Esto es para reposicionar el control en la ventana
            self.scroll(1)

            x += 1

        # Ponemos el foco en el primer control
        self.setFocus(self.controls[0]["control"])
        self.evaluate_conditions()
        self.check_default()
        self.check_ok(self.values)

    def move_up(self):
        # Subir el foco al control de arriba

        # Buscamos el control con el foco
        try:
            focus = self.getFocus()
        except:
            # Si ningún control tiene foco, seleccionamos el primero de la lista y salimos de la función
            control = self.controls[0]

            # Los label no tienen foco, si el primero es label, va saltando hasta encontrar uno que no lo sea
            while control["type"] == "label" and self.controls.index(control) < len(self.controls) - 1:
                control = self.controls[self.controls.index(control) + 1]

            self.setFocus(control["control"])
            return

        # Localizamos en el listado de controles el control que tiene el focus
        for x, control in enumerate(self.controls):
            if control["control"] == focus:
                # Sube uno en la lista
                x -= 1 if x > 0 else 0

                # Si es un label, sigue subiendo hasta llegar al primero o uno que nos sea label
                while self.controls[x]["type"] == "label" and x > 0:
                    x -= 1

                # Si llegado aqui sigue siendo un label es que no quedan mas controles que no sean label, sale de la
                # funcion
                if self.controls[x]["type"] == "label":
                    return

                # Si el control seleccionado no esta visible (esta fuera de la ventana en el scroll) sube el scroll
                # hasta que este visible
                while not self.controls[x]["show"]:
                    self.scroll(1)

                # Pasamos el foco al control
                self.setFocus(self.controls[x]["control"])

    def move_down(self):
        # Bajar el foco al control de abajo

        # Buscamos el control con el foco
        try:
            focus = self.getFocus()
        except:
            # Si ningún control tiene foco, seleccionamos el primero de la lista y salimos de la función
            control = self.controls[0]

            # Los label no tienen foco, si el primero es label, va saltando hasta encontrar uno que no lo sea
            while control["type"] == "label" and self.controls.index(control) < len(self.controls) - 1:
                control = self.controls[self.controls.index(control) + 1]

            self.setFocus(control["control"])
            return

        # Localizamos en el listado de controles el control que tiene el focus
        for x, control in enumerate(self.controls):
            if control["control"] == focus:

                # Baja uno en la lista
                x += 1

                # Si es un label, sigue bajando hasta llegar al primero o uno que nos sea label
                while x < len(self.controls) and self.controls[x]["type"] == "label":
                    x += 1

                # Si llegado aqui sigue siendo un label o no quedan mas controles pasa el foco los botones inferiores
                # y sale de la función
                if x >= len(self.controls) or self.controls[x]["type"] == "label":
                    self.setFocusId(10004)
                    return

                # Si el control seleccionado no esta visible (esta fuera de la ventana en el scroll) baja el scroll
                # hasta que este visible
                while not self.controls[x]["show"]:
                    self.scroll(-1)

                # Pasamos el foco al control
                self.setFocus(self.controls[x]["control"])

    def scroll(self, direction):

        # Establece los pixeles y la dirección donde se moveran los controles
        movimento = self.height_control * direction

        # Tope inferior, si el ultimo control es visible y se hace scroll hacia abajo, el movimiento es 0
        if movimento < 0 and self.controls[-1]["y"] + self.height_control < self.controls_pos_y + self.controls_height:
            movimento = 0

        # Tope superior, si el primer control es visible y se hace scroll hacia arriba, el movimiento es 0
        if movimento > 0 and self.controls[0]["y"] == self.controls_pos_y:
            movimento = 0

        # Mueve todos los controles una posicion
        for control in self.controls:

            # Asigna la nueva posición en la lista de controles
            control["y"] += movimento

            # Si el control está dentro del espació visible, lo coloca en la posición y lo marca como visible
            if control["y"] > self.controls_pos_y - self.height_control and control["y"] + \
                    self.height_control < self.controls_height + self.controls_pos_y:
                if control["type"] != "list":
                    control["control"].setPosition(control["x"], control["y"])
                    control["control"].setVisible(True)
                else:
                    control["control"].setPosition(control["x"], control["y"])
                    control["control"].setVisible(True)
                    control["label"].setPosition(control["x"], control["y"])
                    control["label"].setVisible(True)
                    control["upBtn"].setPosition(control["x"] + control["control"].getWidth() - 25, control["y"] + 3)
                    control["upBtn"].setVisible(True)
                    control["downBtn"].setPosition(control["x"] + control["control"].getWidth() - 25, control["y"] + 18)
                    control["downBtn"].setVisible(True)

                # Marca el control en la lista de controles como visible
                control["show"] = True

            # Si el control no está dentro del espació visible lo marca como no visible
            else:
                if control["type"] != "list":
                    control["control"].setVisible(False)
                else:
                    control["control"].setVisible(False)
                    control["label"].setVisible(False)
                    control["downBtn"].setVisible(False)
                    control["upBtn"].setVisible(False)

                # Marca el control en la lista de controles como no visible
                control["show"] = False

        # Calculamos la posicion y tamaño del ScrollBar
        show_controls = [control for control in self.controls if control["show"] == True]
        hidden_controls = [control for control in self.controls if control["show"] == False]
        position = self.controls.index(show_controls[0])

        scrollbar_height = self.getControl(10008).getHeight() - (len(hidden_controls) * 5)
        scrollbar_y = self.getControl(10008).getY() + (position * 5)
        self.getControl(10009).setPosition(self.getControl(10008).getX(), scrollbar_y)
        self.getControl(10009).setHeight(scrollbar_height)
        self.evaluate_conditions()

    def check_ok(self, dict_values=None):
        if not self.callback:
            if dict_values:
                self.init_values = dict_values.copy()
                self.getControl(10004).setEnabled(False)

            else:
                if self.init_values == self.values:
                    self.getControl(10004).setEnabled(False)
                else:
                    self.getControl(10004).setEnabled(True)

    def check_default(self):
        if not self.custom_button:
            def_values = dict([[c["id"], c["default"]] for c in self.controls])

            if def_values == self.values:
                self.getControl(10006).setEnabled(False)
            else:
                self.getControl(10006).setEnabled(True)

    def onClick(self, id):
        # Valores por defecto
        if id == 10006:
            #DrZ3r0
            if self.custom_button is not None and self.custom_button['method'] != "":
                self.close()
                cb_channel = None
                try:
                    cb_channel = __import__('channels.%s' % self.channel, fromlist=["channels.%s" % self.channel])
                except ImportError:
                    logger.error('Imposible importar %s' % self.channel)
                self.return_value = getattr(cb_channel, self.custom_button['method'])(self.item)
            else:
                for c in self.controls:
                    if c["type"] == "text":
                        c["control"].setText(c["default"])
                        self.values[c["id"]] = c["default"]
                    if c["type"] == "bool":
                        c["control"].setSelected(c["default"])
                        self.values[c["id"]] = c["default"]
                    if c["type"] == "list":
                        c["label"].setLabel(c["lvalues"][c["default"]])
                        self.values[c["id"]] = c["default"]

                self.evaluate_conditions()
                self.check_default()
                self.check_ok()

        # Boton Cancelar y [X]
        if id == 10003 or id == 10005:
            self.close()

        # Boton Aceptar
        if id == 10004:
            if not self.callback:
                for v in self.values:
                    config.set_setting(v, self.values[v], self.channel)
                self.close()
            else:
                self.close()
                cb_channel = None
                try:
                    cb_channel = __import__('channels.%s' % self.channel, fromlist=["channels.%s" % self.channel])
                except ImportError:
                    logger.error('Imposible importar %s' % self.channel)

                self.return_value = getattr(cb_channel, self.callback)(self.item, self.values)

        # Controles de ajustes, si se cambia el valor de un ajuste, cambiamos el valor guardado en el diccionario de
        # valores
        # Obtenemos el control sobre el que se ha echo click
        control = self.getControl(id)

        # Lo buscamos en el listado de controles
        for cont in self.controls:

            # Si el control es un "downBtn" o "upBtn" son los botones del "list"
            # en este caso cambiamos el valor del list
            if cont["type"] == "list" and (cont["downBtn"] == control or cont["upBtn"] == control):

                # Para bajar una posicion
                if cont["downBtn"] == control:
                    index = cont["lvalues"].index(cont["label"].getLabel())
                    if index > 0:
                        cont["label"].setLabel(cont["lvalues"][index - 1])

                # Para subir una posicion
                elif cont["upBtn"] == control:
                    index = cont["lvalues"].index(cont["label"].getLabel())
                    if index < len(cont["lvalues"]) - 1:
                        cont["label"].setLabel(cont["lvalues"][index + 1])

                # Guardamos el nuevo valor en el diccionario de valores
                self.values[cont["id"]] = cont["lvalues"].index(cont["label"].getLabel())

            # Si esl control es un "bool", guardamos el nuevo valor True/False
            if cont["type"] == "bool" and cont["control"] == control:
                self.values[cont["id"]] = bool(cont["control"].isSelected())

            # Si esl control es un "text", guardamos el nuevo valor
            if cont["type"] == "text" and cont["control"] == control:
                self.values[cont["id"]] = cont["control"].getText()

        self.evaluate_conditions()
        self.check_default()
        self.check_ok()

    def onAction(self, action):
        # Accion 1: Flecha derecha
        if action == 1:
            # Obtenemos el foco
            focus = self.getFocusId()

            # Si el foco no está en ninguno de los tres botones inferiores, y esta en un "list" cambiamos el valor
            if focus not in [10004, 10005, 10006]:
                control = self.getFocus()
                for cont in self.controls:
                    if cont["type"] == "list" and cont["control"] == control:
                        index = cont["lvalues"].index(cont["label"].getLabel())
                        if index > 0:
                            cont["label"].setLabel(cont["lvalues"][index - 1])

                        # Guardamos el nuevo valor en el listado de controles
                        self.values[cont["id"]] = cont["lvalues"].index(cont["label"].getLabel())

            # Si el foco está en alguno de los tres botones inferiores, movemos al siguiente
            else:
                if focus == 10006:
                    self.setFocusId(10005)
                if focus == 10005:
                    self.setFocusId(10004)

        # Accion 1: Flecha izquierda
        if action == 2:
            # Obtenemos el foco
            focus = self.getFocusId()

            # Si el foco no está en ninguno de los tres botones inferiores, y esta en un "list" cambiamos el valor
            if focus not in [10004, 10005, 10006]:
                control = self.getFocus()
                for cont in self.controls:
                    if cont["type"] == "list" and cont["control"] == control:
                        index = cont["lvalues"].index(cont["label"].getLabel())
                        if index < len(cont["lvalues"]) - 1:
                            cont["label"].setLabel(cont["lvalues"][index + 1])

                        # Guardamos el nuevo valor en el listado de controles
                        self.values[cont["id"]] = cont["lvalues"].index(cont["label"].getLabel())

            # Si el foco está en alguno de los tres botones inferiores, movemos al siguiente
            else:
                if focus == 10004:
                    self.setFocusId(10005)
                if focus == 10005:
                    self.setFocusId(10006)

        # Accion 4: Flecha abajo
        if action == 4:
            # Obtenemos el foco
            focus = self.getFocusId()

            # Si el foco no está en ninguno de los tres botones inferiores, bajamos el foco en los controles de ajustes
            if focus not in [10004, 10005, 10006]:
                self.move_down()

        # Accion 4: Flecha arriba
        if action == 3:
            # Obtenemos el foco
            focus = self.getFocusId()

            # Si el foco no está en ninguno de los tres botones inferiores, subimos el foco en los controles de ajustes
            if focus not in [10004, 10005, 10006]:
                self.move_up()

            # Si el foco está en alguno de los tres botones inferiores, ponemos el foco en el ultimo ajuste.
            else:
                self.setFocus(self.controls[-1]["control"])

        # Accion 104: Scroll arriba
        if action == 104:
            self.scroll(1)

        # Accion 105: Scroll abajo
        if action == 105:
            self.scroll(-1)

        # Accion 10: Back
        if action == 10:
            self.close()
