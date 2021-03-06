#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from traitsui.api import Handler

from lib.color import guess_wavelength
from lib.image import (equalize, imread, limit_size, normalize, phase_denoise,
                       subtract)


class DatainputHandler(Handler):
    """ Controlador para el ModelView: Datainput
    """
    def object_holo_filename_changed(self, info):
        print "--- Updating hologram ---"
