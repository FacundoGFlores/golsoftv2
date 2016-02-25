#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from traitsui.api import Handler


class MaskHandler(Handler):
    """ Controlador para el ModelView: Mask
    """
    def object_use_masking_changed(self, info):
        if info.object.use_masking:
            print "Using Mask"
        else:
            print "Not using Mask"

    def object_use_zero_mask_changed(self, info):
        if info.object.use_zero_mask:
            print "Using Zero Mask"
        else:
            print "Not using Zero Mask"

    def object_use_cuttop_changed(self, info):
        if info.object.use_cuttop:
            print "Using Cuttop"
        else:
            print "Not using Cuttop"
