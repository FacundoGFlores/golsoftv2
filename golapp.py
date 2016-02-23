#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from traits.api import HasTraits, Str, Range, Enum, Bool, Instance, PrototypedFrom, on_trait_change
from traitsui.api import Item, HSplit, Group, View, Handler, Label

from src.models.datainput_model import Datainput_model
from src.models.extradata_model import Extradata_model
from src.models.overview_model import Overview_model


class Golapp(HasTraits):
    """ Aplicacion principal, la cual incorpora las diferentes vistas
        definidas dentro de los modelos.
    """
    datainput = Instance(Datainput_model, ())
    extradata = Instance(Extradata_model, ())
    overview = Instance(Overview_model, ())

    btn_update_hologram = PrototypedFrom('datainput')
    camera = PrototypedFrom('extradata')
    overview_vismode = PrototypedFrom('overview')

    grp_datainput = Group(
        Group(
            Item(name='datainput', style='custom'),
            show_labels=False
        ),
        label='Datos de Entrada',
        show_border=True
    )

    grp_extradata = Group(
        Group(
            Item(name='extradata', style='custom')
        ),
        label='Datos Extra',
        show_border=True
    )

    grp_overview = Group(
        Group(
            Item(name='overview', style='custom')
        ),
        label='Overview',
        show_border=True
    )

    view = View(
        HSplit(
            grp_overview,
            Group(
                grp_datainput,
                grp_extradata
            )
        ),
        title='Golsoft App v2',
        resizable=True,
    )

    @on_trait_change("btn_update_hologram")
    def print_camera(self):
        print "Golapp printing: %s" % self.camera
        print "Golapp printing: %s" % self.overview_vismode

if __name__ == '__main__':
    golapp = Golapp()
    golapp.configure_traits()
