#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from traitsui.api import Handler


class UnwrapHandler(Handler):
    """ Controlador para el ModelView: Unwrap
    """
    def object_use_use_unwrapping_changed(self, info):
        if info.object.use_unwrapping:
            print "Using Unwrapping"
        else:
            print "Not Using Unwrapping"
