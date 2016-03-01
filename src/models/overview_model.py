#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Autor: Flores Facundo
# Año: 2016
# Licencia: GNU/GPL V3 http://www.gnu.org/copyleft/gpl.html
# Estado: Produccion

from mayavi.core.ui.api import SceneEditor
from mayavi.core.ui.mayavi_scene import MayaviScene
from mayavi.tools.mlab_scene_model import MlabSceneModel
from traits.api import Button, Enum, HasTraits, Instance, PrototypedFrom
from traitsui.api import Group, Item, View

from datainput_model import Datainput_model

from ..controllers.overview import OverviewHandler


class Overview_model(HasTraits):
    overview_vismode = Enum(
        "input map",
        "spectrum",
        "module",
        "phase map",
        "unwrapped phase map",
        "unwrapped phase surface",
        label="Visualize"
    )

    scn_overview = Instance(MlabSceneModel, ())
    plt_overview = None
    plt_overview_surf = None
    vis_overview = Item(
        'scn_overview',
        editor=SceneEditor(scene_class=MayaviScene),
        show_label=False
    )

    # Se opta por show_label=False para ganar mas espacio en el overview
    grp_overview_visualizer = Group(
        Item('overview_vismode', style='simple', show_label=False),
        vis_overview,
    )

    view = View(grp_overview_visualizer, handler=OverviewHandler)

if __name__ == '__main__':
    o = Overview_model()
    o.configure_traits()
