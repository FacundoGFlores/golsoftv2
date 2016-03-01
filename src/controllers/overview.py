#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from traitsui.api import Handler

from lib.image import equalize, imread, normalize, phase_denoise, subtract


class OverviewHandler(Handler):
    """ Controlador para el ModelView: Overview
    """
    def object_overview_vismode_changed(self, info):
        print "Updating overview"
