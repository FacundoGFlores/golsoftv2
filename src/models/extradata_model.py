#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from ConfigParser import ConfigParser

from traits.api import Bool, Button, Color, HasTraits, Instance, Int, Range
from traitsui.api import Group, Handler, HGroup, Item, View

from ..controllers.extradata import ExtradataHandler


class Extradata_model(HasTraits):
    """ ModelView para el manejo de datos extra de los hologramas:
        Camaras y Wavelength
    """
    cameras = {}
    wavelengths = {}
    hnd_extra = ExtradataHandler()
    camera = hnd_extra.load_cameras(cameras)
    wavelength = hnd_extra.load_wavelengths(wavelengths)
    # Se utiliza un auto para mayor precision que el xslider
    wavelength_nm = Range(400., 750., 650., mode="auto", enter_set=True,
        auto_set=False)
    imagecolor = Color("(0,0,0)")
    imagewavelength = Int(0)

    use_sampled_image = Bool(True)
    btn_load_parameters = Button("Load")
    btn_save_parameters = Button("Save")

    grp_extradata = Group(
        "camera",
        HGroup(
            Item(
                "imagecolor",
                style='readonly',
                label="Color Dominante"
            ),
            Item(
                "imagewavelength",
                style="readonly",
                label="Wavelength dominante"
            )
        ),
        "wavelength",
        "wavelength_nm",
        HGroup(
            "use_sampled_image",
            "-",
            Item(
                "btn_save_parameters",
                label="Parameters"
            ),
            Item(
                "btn_load_parameters",
                show_label=False
            )
        )
    )

    view_extradata = View(
        grp_extradata,
        handler=ExtradataHandler
    )

if __name__ == '__main__':
    e = Extradata_model()
    e.configure_traits()
