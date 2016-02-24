#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from traitsui.api import Handler


class PropagationHandler(Handler):
    """ Controlador para el ModelView: Propagation
    """
    def object_use_propagation_changed(self, info):
        if info.object.use_propagation:
            print "Using Propagation"
        else:
            print "Not using Propagation"
