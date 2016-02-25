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

from ..controllers.unwrap import UnwrapHandler

class Unwrap_model(HasTraits):
    """docstring for Unwrap_Model"""

    use_unwrapping = Bool(True)

    phase_denoise = Range(
        0, 19, 1,
        auto_set=False,
        enter_set=True
    )

    unwrapping_method = Enum(
        "Least Squares",
        "Congruent Least Squares",
        "Quality Guided",
        "PCG",
    )

    unwrapping_vismode = Enum(
        "phase",
        "hibryd",
        label="Visualize"
    )

    scn_unwrapping = Instance(MlabSceneModel, ())
    plt_unwrapping = Instance(PipelineBase)
    vis_unwrapping = Item(
        'scn_unwrapping',
        editor=SceneEditor(scene_class=MayaviScene),
        show_label=False,
        resizable=True
    )

    grp_unwrapping_parameters = Group(
        "use_unwrapping",
        Group(
            Item("unwrapping_method", show_label=False),
            "phase_denoise",
            visible_when="use_unwrapping",
            label="Unwrapping",
            show_border=True,
        ),
    )

    grp_unwrapping_visualizer = Group(
        vis_unwrapping,
        Item('unwrapping_vismode', style='simple', show_label=False),
    )

    view = View(
        Group(
            grp_unwrapping_parameters,
            grp_unwrapping_visualizer
        ),
        handler = UnwrapHandler
    )

if __name__ == '__main__':
    u = Unwrap_model()
    u.configure_traits()
