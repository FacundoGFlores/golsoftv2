#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from mayavi.core.api import PipelineBase
from mayavi.core.ui.api import SceneEditor
from mayavi.core.ui.mayavi_scene import MayaviScene
from mayavi.tools.mlab_scene_model import MlabSceneModel

from traits.api import Bool, Enum, HasTraits, Range, Instance
from traitsui.api import View, Group, Item

from ..controllers.mask import MaskHandler


class Mask_model(HasTraits):
    use_masking = Bool(True)

    softness = Range(
        0., 30., 0.,
        mode="auto",
        enter_set=True,
        auto_set=False
    )

    radious_scale = Range(
        0., 2., 1.,
        mode="auto",
        enter_set=True,
        auto_set=False
    )

    use_zero_mask = Bool(True)
    zero_scale = Range(
        0., 2., 1.4,
        mode="auto",
        enter_set=True,
        auto_set=False,
        enabled_when="use_zero_mask"
    )

    use_cuttop = Bool(False)
    cuttop = Range(
        .00, .01, 0.,
        mode="auto",
        enter_set=True,
        auto_set=False,
        enabled_when="use_cuttop"
    )

    mask_vismode = Enum(
        "hibryd",
        "mask",
        "spectrum",
        label="Visualize"
    )

    scn_mask = Instance(MlabSceneModel, ())
    plt_mask = Instance(PipelineBase)
    vis_mask = Item(
        'scn_mask',
        editor=SceneEditor(scene_class=MayaviScene),
        show_label=False,
        resizable=True
    )

    grp_mask_parameters = Group(
        Group(
            "softness",
            "radious_scale",
            "use_zero_mask",
            Item("zero_scale", enabled_when="use_zero_mask"),
            "use_cuttop",
            Item("cuttop", enabled_when="use_cuttop"),
            label="Spectrum mask parameters",
            show_border=True,
        )
    )

    grp_mask_visualizer = Group(
        vis_mask,
        Item('mask_vismode', style='simple', show_label=False),
    )

    view = View(
        Group(
            grp_mask_parameters,
            grp_mask_visualizer
        ),
        handler=MaskHandler
    )

if __name__ == '__main__':
    m = Mask_model()
    m.configure_traits()
