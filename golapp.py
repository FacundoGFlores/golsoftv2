#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

import numpy as np
from traits.api import (Bool, Enum, Float, HasTraits, Instance, PrototypedFrom,
                        Range, Str, on_trait_change)
from traitsui.api import Group, Handler, HSplit, Item, Label, Tabbed, View

from lib.autofocus import guess_focus_distance
from lib.automask import get_auto_mask
from lib.color import guess_wavelength
from lib.dft import get_shifted_dft, get_shifted_idft
from lib.extra import is_numpy_array
from lib.image import (equalize, imread, limit_size, normalize, phase_denoise,
                       subtract)
from lib.minimize import get_fitted_paraboloid
from lib.pea import (calculate_director_cosines, get_module, get_phase,
                     get_refbeam)
from lib.propagation import get_propagation_array
from lib.unwrap import (unwrap_cls, unwrap_pcg, unwrap_phasediff2, unwrap_qg,
                        unwrap_wls)
from src.models.datainput_model import Datainput_model
from src.models.extradata_model import Extradata_model
from src.models.mask_model import Mask_model
from src.models.overview_model import Overview_model
from src.models.propagation_model import Propagation_model
from src.models.refbeam_model import Refbeam_model
from src.models.unwrap_model import Unwrap_model

tau = 2 * np.pi


class Golapp(HasTraits):
    """ Aplicacion principal, la cual incorpora las diferentes vistas
        definidas dentro de los modelos.
    """

    def __init__(self):
        HasTraits.__init__(self)
        self.empty = np.zeros((200, 200))
        self.dx = None
        self.dy = None
        self.empty = None
        self.img_holo = None
        self.img_ref = None
        self.img_obj = None
        self.rgb_color = None
        self.hologram = None
        self.array = None  # Actual array for showing in mayavi
        self.color = None  # Actual color for showing in mayavi
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
        self.r_hologram = None

    idata = Instance(Datainput_model, ())
    edata = Instance(Extradata_model, ())
    oview = Instance(Overview_model, ())
    propa = Instance(Propagation_model, ())
    imask = Instance(Mask_model, ())
    iunwr = Instance(Unwrap_model, ())
    irefb = Instance(Refbeam_model, ())

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

    grp_refbeam = Group(
        Group(
            Item(name='irefb', style='custom', show_label=False)
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

    refbeam_panel = Tabbed(
        Group(
            grp_refbeam
        ),
        label="Refbeam"
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
            print "Updating object image"

            image = imread(self.idata.obj_filename)

            if self.edata.use_sampled_image:
                image = limit_size(image, self.resolution_limit)

            self.img_obj = image

    def opt_inputmap(self):
        self.array = self.hologram
        self.color = "bone"

    def opt_spectrum(self):
        self.array = normalize(self.mask) + equalize(self.cnt_spectrum)
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
        self.rep_type = "image"
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

        if self.rep_type == "image":
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
            wrp_scale = 100 / self.array.ptp()
            if self.oview.plt_overview:
                self.oview.plt_overview.visible = False

            if self.oview.plt_overview_surf is None:
                print("Creating new surface")

                self.oview.plt_overview_surf = \
                    self.oview.scn_overview.mlab.surf(
                        self.array,
                        colormap=self.color,
                        warp_scale=wrp_scale,
                        figure=self.oview.scn_overview.mayavi_scene
                    )
            else:
                self.oview.plt_overview_surf.visible = True
                self.oview.plt_overview_surf.mlab_source.lut_type = self.color
                self.oview.plt_overview_surf.mlab_source.scalars = self.array
                self.oview.plt_overview_surf.mlab_source.warp_scale = wrp_scale

    @on_trait_change("idata.btn_update_hologram")
    def update_hologram(self):
        print "Reading camera values"
        camera = self.edata.cameras[self.edata.camera]
        self.dx = eval(camera["dx"])
        self.dy = eval(camera["dy"])
        print "Calculating hologram"
        self.update_holoimage()
        self.update_refimage()
        self.update_objimage()
        if is_numpy_array(self.img_holo) and is_numpy_array(self.img_holo):
            self.hologram = subtract(self.img_holo, self.img_ref)
        if is_numpy_array(self.img_holo) and is_numpy_array(self.img_obj):
            self.hologram = subtract(self.hologram, self.img_obj)
        if is_numpy_array(self.hologram):
            self.hologram = equalize(self.hologram)
            self.update_ref_beam()
            self.update_overview_vis()
        else:
            print "No hologram available"

    @on_trait_change("edata.camera")
    def update_camera(self):
        print "Reading camera values"
        camera = self.edata.cameras[self.edata.camera]
        self.dx = eval(camera["dx"])
        self.dy = eval(camera["dy"])
        self.update_propagation()

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
                figure=self.imask.scn_mask.mayavi_scene
            )
        else:
            self.imask.plt_mask.mlab_source.set(scalars=self.array)

    @on_trait_change(
        "imask.use_masking, \
        imask.softness, \
        imask.radious_scale, \
        imask.use_zero_mask, \
        imask.zero_scale, \
        imask.use_cuttop, \
        imask.cuttop")
    def update_mask(self):
        if self.imask.use_masking:
            print "Using mask - Updating mask"
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
            self.update_propagation()
            self.update_mask_vis()
            self.update_overview_vis()
        else:
            print "Not Using mask - Updating"
            self.masked_spectrum = self.spectrum

    @on_trait_change("propa.distance_m, propa.distance_cm")
    def update_distance(self):
        print "Updating distance"
        self.propa.distance = self.propa.distance_m + self.propa.distance_cm / 100
        self.update_propagation()


    @on_trait_change("propa.btn_guess_focus")
    def guess_focus_distance(self):
        "Guessing distance"
        self.wavelength = self.edata.wavelength_nm * 1e-9
        self.masked_spectrum = get_auto_mask(self.spectrum)[1]
        self.propa.distance = guess_focus_distance(
            self.masked_spectrum,
            self.wavelength,
            (self.dx, self.dy)
        )
        self.update_propagation()

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
            self.propa.plt_propagation = \
                self.propa.scn_propagation.mlab.imshow(
                    self.array,
                    colormap=self.color,
                    figure=self.propa.scn_propagation.mayavi_scene
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

        if self.iunwr.plt_unwrapping is None:
            self.iunwr.plt_unwrapping = self.propa.scn_propagation.mlab.imshow(
                self.array,
                colormap=self.color,
                figure=self.iunwr.scn_unwrapping.mayavi_scene
            )
        else:
            self.iunwr.plt_unwrapping.mlab_source.set(scalars=self.array)

    @on_trait_change("iunwr.unwrapping_method, iunwr.phase_denoise")
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
        propa.distance,\
        edata.wavelength_nm"
    )
    def update_propagation(self):
        print("Updating propagation")
        print "Using (dx, dy):" + str(self.dx) + " " + str(self.dy)
        if self.propa.use_propagation:
            print "Using propagation."
            self.propagation_array = get_propagation_array(
                self.hologram.shape,
                self.propa.distance,
                self.edata.wavelength_nm * 1e-9,
                self.dx, self.dy
            )
            self.propagated = self.propagation_array * self.masked_spectrum
        else:
            self.propagated = self.masked_spectrum
        self.reconstructed = get_shifted_idft(self.propagated)
        self.module = normalize(get_module(self.reconstructed))
        self.wrapped_phase = get_phase(self.reconstructed)
        paraboloid = get_fitted_paraboloid(self.wrapped_phase)
        self.wrapped_phase = (self.wrapped_phase - paraboloid) % tau
        self.update_propagation_vis()
        self.update_overview_vis()
        self.update_unwrapping_phase()

    @on_trait_change(
        "irefb.use_ref_beam, \
        irefb.use_auto_angles, \
        edata.wavelength_nm"
    )
    def calculate_director_cosines(self):
        if self.irefb.use_ref_beam and self.irefb.use_auto_angles:
            cos_alpha, cos_beta = calculate_director_cosines(
                self.hologram,
                self.edata.wavelength_nm * 1e-9,
                (self.dx, self.dy)
            )
            self.cos_alpha, self.cos_beta = cos_alpha, cos_beta
            self.irefb.cos_alpha, self.irefb.cos_beta = cos_alpha, cos_beta

    @on_trait_change(
        "irefb.cos_alpha, \
        irefb.cos_beta, \
        irefb.use_ref_beam, \
        edata.wavelength_nm"
    )
    def update_ref_beam(self):
        print "Getting ref beam"
        if self.irefb.use_ref_beam:
            print("Updating reference beam")
            self.irefb.ref_beam = get_refbeam(
                self.hologram.shape,
                self.irefb.cos_alpha,
                self.irefb.cos_beta,
                self.edata.wavelength_nm * 1e-9,
                (self.dx, self.dy))
            self.r_hologram = self.irefb.ref_beam * self.irefb.hologram
        else:
            self.ref_beam = self.empty
            self.r_hologram = self.hologram

        self.spectrum = get_shifted_dft(self.r_hologram)
        self.update_overview_vis()
        self.update_mask()

    @on_trait_change("irefb.ref_beam_vismode")
    def update_ref_beam_vis(self):
        if self.irefb.ref_beam_vismode == "hologram x":
            self.array = get_module(self.r_hologram)
        else:
            self.array = self.ref_beam.real

        if self.irefb.plt_ref_beam is None:
            self.irefb.plt_ref_beam = self.irefb.scn_ref_beam.mlab.imshow(
                self.array,
                colormap="black-white",
                figure=self.scn_ref_beam.mayavi_scene
            )
        else:
            self.irefb.plt_ref_beam.mlab_source.set(scalars=self.array)

if __name__ == '__main__':
    golapp = Golapp()
    golapp.configure_traits()
