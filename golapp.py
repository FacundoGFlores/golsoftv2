#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from traits.api import Float, HasTraits, Str, Range, Enum, Bool, Instance, PrototypedFrom, on_trait_change
from traitsui.api import Item, HSplit, Group, View, Handler, Label, Tabbed
import numpy as np

from lib.image import equalize, imread, normalize, subtract
from lib.image import limit_size
from lib.color import guess_wavelength

from src.models.datainput_model import Datainput_model
from src.models.extradata_model import Extradata_model
from src.models.overview_model import Overview_model

class Golapp(HasTraits):
    """ Aplicacion principal, la cual incorpora las diferentes vistas
        definidas dentro de los modelos.
    """

    def __init__(self):
        HasTraits.__init__(self)
        self.dx = Float()
        self.dy = Float()
        self.empty = None
        self.img_holo = None
        self.img_ref = None
        self.img_obj = None
        self.rgb_color = None
        self.hologram = None
        self.array = None # Actual array for showing in mayavi
        self.color = None # Actual color for showing in mayavi
        self.resolution_limit = .5
        self.wavelength = None
        self.rgbcolor = None

    idata = Instance(Datainput_model, ())
    edata = Instance(Extradata_model, ())
    oview = Instance(Overview_model, ())

    grp_datainput = Group(
        Group(
            Item(name='idata', style='custom'),
            show_labels=False
        ),
        label='Datos de Entrada',
        show_border=True
    )

    grp_extradata = Group(
        Group(
            Item(name='edata', style='custom'),
            show_labels=False
        ),
        label='Datos Extra',
        show_border=True
    )

    grp_overview = Group(
        Group(
            Item(name='oview', style='custom', show_label=False)
        ),
        show_border=True,
    )

    info_panel = Tabbed(
        Group(
            grp_datainput,
            grp_extradata
        ),
        label="Data"
    )
    view = View(
        HSplit(
            grp_overview,
            info_panel
        ),
        title='Golsoft App v2',
        resizable=True,
    )

    def update_holoimage(self):
        if self.idata.holo_filename:
            print "Updating hologram"
            self.rgbcolor, self.wavelength = guess_wavelength(
                imread(self.idata.holo_filename, False)
            )
            print "Image wavelength: %f" % self.wavelength
            self.edata.imagecolor = "(%d,%d,%d)" % self.rgbcolor
            self.edata.imagewavelength = int(
                round(self.wavelength)
            )

            image = imread(self.idata.holo_filename)

            if self.edata.use_sampled_image:
                image = limit_size(image, self.resolution_limit)

            self.img_holo = image
            self.empty = np.zeros_like(self.img_holo)

    def update_refimage(self):
        if self.idata.ref_filename:
            print "Updating reference image"

            image = imread(self.idata.ref_filename)

            if self.edata.use_sampled_image:
                image = limit_size(image, self.resolution_limit)

            self.img_ref = image

    def update_objimage(self):
        if self.idata.obj_filename:
            print("Updating object image")

            image = imread(self.idata.obj_filename)

            if self.edata.use_sampled_image:
                image = limit_size(image, self.resolution_limit)

            self.img_obj = image

    def opt_inputmap(self):
        self.array = self.hologram
        self.color = "bone"

    def opt_spectrum(self):
        self.array = normalize(self.mask) + equalize(self.centered_spectrum)
        self.color = "gist_stern"

    def opt_module(self):
        self.array = self.module
        self.color = "bone"

    def opt_phasemap(self):
        self.array = self.wrapped_phase
        self.color = "spectral"

    def opt_uwphase(self):
        self.array = self.unwrapped_phase
        self.color = "spectral"

    def opt_uwsurf(self):
        self.array = self.unwrapped_phase
        self.color = "spectral"
        self.rep_type = "surface"


    @on_trait_change("oview.overview_vismode")
    def update_overview_vis(self):
        vismode = self.oview.overview_vismode
        rep_type = "image"
        options = {
            "input map": self.opt_inputmap,
            "spectrum": self.opt_spectrum,
            "module": self.opt_module,
            "phase map": self.opt_phasemap,
            "unwrapped phase map": self.opt_uwphase,
            "unwrapped phase surface": self.opt_uwsurf,
        }
        # Do the switch
        options[vismode]()

        if rep_type == "image":
            if self.oview.plt_overview_surf:
                self.oview.plt_overview_surf.visible = False

            if self.oview.plt_overview is None:
                print("Creating new flat image")

                self.oview.plt_overview = self.oview.scn_overview.mlab.imshow(
                    self.array,
                    colormap=self.color,
                    figure=self.oview.scn_overview.mayavi_scene
                )
            else:
                self.oview.plt_overview.visible = True
                self.oview.plt_overview.mlab_source.lut_type = self.color
                self.oview.plt_overview.mlab_source.scalars = self.array
        else:
            warp_scale = 100 / self.array.ptp()
            if self.plt_overview:
                self.plt_overview.visible = False

            if self.plt_overview_surf is None:
                print("Creating new surface")

                self.oview.plt_overview_surf = \
                    self.oview.scn_overview.mlab.surf(
                    self.array,
                    colormap=self.color,
                    warp_scale=warp_scale,
                    figure=self.scn_overview.mayavi_scene
                )
            else:
                self.oview.plt_overview_surf.visible = True
                self.oview.plt_overview_surf.mlab_source.lut_type = self.color
                self.oview.plt_overview_surf.mlab_source.scalars = self.array
                self.oview.plt_overview_surf.mlab_source.warp_scale = warp_scale

    @on_trait_change("idata.btn_update_hologram")
    def update_hologram(self):
        print "Calculatin hologram"
        self.update_holoimage()
        self.update_refimage()
        self.update_objimage()
        self.hologram = subtract(self.img_holo, self.img_ref)
        self.hologram = subtract(self.hologram, self.img_obj)
        self.hologram = equalize(self.hologram)
        self.update_overview_vis()

    @on_trait_change("edata.camera")
    def update_camera(self):
        camera = self.edata.cameras[self.edata.camera]
        self.dx = eval(camera["dx"])
        self.dy = eval(camera["dy"])
        print self.dx, self.dy
        # TODO: Se debe establecer el tab para opciones de propagacion.
        # self.update_propagation()

if __name__ == '__main__':
    golapp = Golapp()
    golapp.configure_traits()
