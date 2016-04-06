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
from traits.api import Bool, Button, Enum, Float, HasTraits, Instance, Range
from traitsui.api import Group, Item, View

from ..controllers.propagation import PropagationHandler


class Propagation_model(HasTraits):
    use_propagation = Bool(False)
    btn_guess_focus = Button("Guess focus distance")
    distance = Float(0)

    distance_m = Range(
        -0.50, 0.50, 0.,
        enter_set=True,
        auto_set=False
    )
    distance_cm = Range(
        -5., 5., 0.,
        enter_set=True,
        auto_set=False
    )
    propagation_vismode = Enum(
        "module",
        "phase",
        label="Visualize"
    )

    scn_propagation = Instance(MlabSceneModel, ())
    plt_propagation = Instance(PipelineBase)
    vis_propagation = Item(
        'scn_propagation',
        editor=SceneEditor(scene_class=MayaviScene),
        show_label=False,
        resizable=True
    )

    grp_propagation_parameters = Group(
        "use_propagation",
        Group(
            "btn_guess_focus",
            "distance", "distance_m", "distance_cm",
            label="Propagation parameters",
            show_border=True
        )
    )

    grp_propagation_visualizer = Group(
        vis_propagation,
        Item(
            'propagation_vismode',
            style='simple',
            show_label=False
        )
    )

    view = View(
        Group(
            grp_propagation_parameters,
            grp_propagation_visualizer
        ),
        handler=PropagationHandler
    )

if __name__ == '__main__':
    p = Propagation_model()
    p.configure_traits()
