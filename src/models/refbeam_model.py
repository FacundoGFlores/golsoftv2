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

from ..controllers.refbeam import RefbeamHandler


class Refbeam_model(HasTraits):
    use_ref_beam = Bool(False)

    use_auto_angles = Bool(True)

    cos_alpha = Range(
        -1., 1., 0.,
        mode="auto",
        enter_set=True,
        auto_set=False
    )

    cos_beta = Range(
        -1., 1., 0.,
        mode="auto",
        enter_set=True,
        auto_set=False
    )

    ref_beam_vismode = Enum(
        'ref_beam',
        'hologram x ref_beam',
        label="Visualize"
    )

    scn_ref_beam = Instance(MlabSceneModel, ())
    plt_ref_beam = Instance(PipelineBase)
    vis_ref_beam = Item(
        'scn_ref_beam',
        editor=SceneEditor(scene_class=MayaviScene),
        show_label=False
    )

    grp_ref_beam_parameters = Group(
        "use_ref_beam",
        Group(
            "use_auto_angles",
            Group(
                "cos_alpha",
                "cos_beta",
                enabled_when="not use_auto_angles"
            ),
            label="Reference beam parameters",
            show_border=True,
            visible_when ="use_ref_beam",
        )
    )

    grp_ref_beam_visualizer = Group(
        vis_ref_beam,
        Item('ref_beam_vismode', style='simple', show_label=False),
    )

    view = View(
        Group(
            grp_ref_beam_parameters,
            grp_ref_beam_visualizer
        ),
        handler = RefbeamHandler
    )

if __name__ == '__main__':
    r = Refbeam_model()
    r.configure_traits()
