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

from lib.image import equalize, imread, normalize, subtract, phase_denoise
from lib.image import limit_size
from lib.color import guess_wavelength
from lib.automask import get_auto_mask
from lib.autofocus import guess_focus_distance
from lib.propagation import get_propagation_array
from lib.dft import get_shifted_idft, get_shifted_dft
from lib.pea import get_phase, get_module
from lib.unwrap import unwrap_phasediff2
from lib.unwrap import unwrap_qg, unwrap_wls, unwrap_cls, unwrap_pcg

from src.models.datainput_model import Datainput_model
from src.models.extradata_model import Extradata_model
from src.models.overview_model import Overview_model
from src.models.propagation_model import Propagation_model
from src.models.mask_model import Mask_model
from src.models.unwrap_model import Unwrap_model

tau = 2 * np.pi

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
        self.zero_scale = Float()
        self.cuttop = Float()
        self.mask = None
        self.masked_spectrum = None
        self.cnt_spectrum = None
        self.spectrum = None
        self.distance = Float()
        self.propagation_array = None
        self.propagated = None
        self.reconstructed = None
        self.module = None
        self.wrapped_phase = None
        self.phase_denoise = None
        self.unwrapped_phase = None

    idata = Instance(Datainput_model, ())
    edata = Instance(Extradata_model, ())
    oview = Instance(Overview_model, ())
    propa = Instance(Propagation_model, ())
    imask = Instance(Mask_model, ())
    iunwr = Instance(Unwrap_model, ())

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

    grp_propagation = Group(
        Group(
            Item(name='propa', style='custom', show_label=False)
        ),
        show_border=True,
    )

    grp_mask = Group(
        Group(
            Item(name='imask', style='custom', show_label=False)
        ),
        show_border=True
    )

    grp_unwrap = Group(
        Group(
            Item(name='iunwr', style='custom', show_label=False)
        ),
        show_border=True
    )

    info_panel = Tabbed(
        Group(
            grp_datainput,
            grp_extradata
        ),
        label="Data"
    )

    mask_panel = Tabbed(
        Group(
            grp_mask
        ),
        label="Mask Espectrum"
    )

    propagation_panel = Tabbed(
        Group(
            grp_propagation
        ),
        label="Propagation"
    )

    unwrap_panel = Tabbed(
        Group(
            grp_unwrap
        ),
        label="Unwrapping"
    )

    view = View(
        HSplit(
            grp_overview,
            Tabbed(
                info_panel,
                mask_panel,
                propagation_panel,
                unwrap_panel
            )
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

    def update_mask_vis(self):
        if self.imask.mask_vismode == "hibryd":
            self.array = normalize(self.mask) + equalize(self.cnt_spectrum)
        elif self.imask.mask_vismode == "mask":
            self.array = normalize(equalize(self.masked_spectrum))
        elif self.imask.mask_vismode == "spectrum":
            self.array = equalize(self.cnt_spectrum)
        else:
            pass

        if self.imask.plt_mask is None:
            self.imask.plt_mask = self.imask.scn_mask.mlab.imshow(
                self.array,
                colormap="gist_stern",
                figure=self.scn_mask.mayavi_scene
            )
        else:
            self.imask.plt_mask.mlab_source.set(scalars=self.array)

    @on_trait_change(
        "imask.use_masking, \
        imask.softness, \
        imask.radious_scale, \
        imask.user_zero_mask, \
        imask.zero_scale, \
        imask.use_cuttop, \
        imask.cuttop")
    def update_mask(self):
        if self.imask.use_masking:
            print "Updating mask"
            if self.imask.use_zero_mask:
                self.zero_scale = self.imask.zero_scale
            else:
                self.zero_scale = 0
            if self.imask.use_cuttop:
                self.cuttop = self.imask.cuttop
            else:
                self.cuttop = 0

            self.mask, self.masked_spectrum, self.cnt_spectrum = get_auto_mask(
                self.spectrum,
                self.imask.softness,
                self.imask.radious_scale,
                self.zero_scale,
                self.cuttop
            )

            self.update_mask_vis()
            self.update_overview_vis()
        else:
            self.masked_spectrum = self.spectrum

    @on_trait_change("propa.distance_m, propa.distance_cm")
    def compose_distance(self):
        self.distance = self.propa.distance_m + self.propa.distance_cm / 100

    @on_trait_change("btn_guess_focus")
    def guess_focus_distance(self):
        self.wavelength = self.wavelength_nm * 1e-9
        self.masked_spectrum = get_auto_mask(self.spectrum)[1]
        self.distance = guess_focus_distance(
            self.masked_spectrum,
            self.wavelength,
            (self.dx, self.dy)
        )

    @on_trait_change("propagation_vismode")
    def update_propagation_vis(self):
        if self.propa.propagation_vismode == "module":
            self.array = self.module
            self.color = "bone"
        elif self.propagation_vismode == "phase":
            self.array = self.wrapped_phase
            self.color = "bone"
        else:
            pass

        if self.propa.plt_propagation is None:
            self.propa.plt_propagation = self.propa.scn_propagation.mlab.imshow(
                self.array,
                colormap=self.color,
                figure=self.scn_propagation.mayavi_scene
            )
        else:
            self.propa.plt_propagation.mlab_source.set(scalars=self.array)

    @on_trait_change("iunwr.unwrapping_vismode")
    def update_unwrapping_vis(self):
        if self.iunwr.unwrapping_vismode == "phase":
            self.array = self.unwrapped_phase
            self.color = "spectral"
        elif self.unwrapping_vismode == "hibryd":
            self.array = self.unwrapped_phase
            self.color = "bone"
        else:
            pass

        if self.plt_unwrapping is None:
            self.plt_unwrapping = self.scn_propagation.mlab.imshow(
                self.array,
                colormap=self.color,
                figure=self.scn_unwrapping.mayavi_scene
            )
        else:
            self.iunwr.plt_unwrapping.mlab_source.set(scalars=self.array)

    @on_trait_change("iunwr.apping_method, iunwr.phase_denoise")
    def update_unwrapping_phase(self):
        if self.iunwr.use_unwrapping:
            print("Unwrapping phase")
            self.wrapped_phase = phase_denoise(
                self.wrapped_phase,
                self.iunwr.phase_denoise
            )
            method = self.iunwr.unwrapping_method
            if method == "PCG":
                self.unwrapped_phase = unwrap_pcg(self.wrapped_phase)
            if method == "Congruent Least Squares":
                self.unwrapped_phase = unwrap_cls(self.wrapped_phase)
            if method == "Least Squares":
                self.unwrapped_phase = unwrap_wls(self.wrapped_phase)
            if method == "Quality Guided":
                self.unwrapped_phase = unwrap_qg(
                    self.wrapped_phase,
                    self.module
                )
            else:
                pass

            self.update_unwrapping_vis()
            self.update_overview_vis()

    @on_trait_change(
        "propa.propagation_vismode, \
        propa.distance, \
        propa.wavelength_nm"
    )
    def update_propagation(self):
        if self.propa.use_propagation:
            print("Updating propagation")
            self.propagation_array = get_propagation_array(
                self.hologram.shape,
                self.distance,
                self.wavelength_nm * 1e-9,
                (self.dx, self.dy)
            )
            self.propagated = self.propagation_array * self.masked_spectrum
        else:
            self.propagated = self.masked_spectrum
        self.reconstructed = get_shifted_idft(self.propagated)
        self.module = normalize(get_module(self.reconstructed))
        self.wrapped_phase = get_phase(self.reconstructed)
        paraboloid = get_fitted_paraboloid(wrapped_phase)
        self.wrapped_phase = (wrapped_phase - paraboloid) % tau
        self.update_propagation_vis()
        self.update_overview_vis()
        self.update_unwrapping_phase()

if __name__ == '__main__':
    golapp = Golapp()
    golapp.configure_traits()
