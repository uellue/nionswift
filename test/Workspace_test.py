# standard libraries
import json
import logging
import unittest
import weakref

# third party libraries
import numpy

# local libraries
from nion.swift import Application
from nion.swift import DocumentController
from nion.swift import ImagePanel
from nion.swift.model import DataItem
from nion.swift.model import DocumentModel
from nion.swift.model import Storage
from nion.swift.test import DocumentController_test
from nion.ui import Geometry
from nion.ui import Test



def get_layout(layout_id):
    if layout_id == "2x1":
        d = { "type": "splitter", "orientation": "vertical", "splits": [0.5, 0.5], "children": [ { "type": "image", "selected": True }, { "type": "image" } ] }
    elif layout_id == "1x2":
        d = { "type": "splitter", "orientation": "horizontal", "splits": [0.5, 0.5], "children": [ { "type": "image", "selected": True }, { "type": "image" } ] }
    elif layout_id == "3x1":
        d = { "type": "splitter", "orientation": "vertical", "splits": [1.0/3, 1.0/3, 1.0/3], "children": [ { "type": "image", "selected": True }, { "type": "image" }, { "type": "image" } ] }
    elif layout_id == "2x2":
        d = { "type": "splitter", "orientation": "horizontal", "splits": [0.5, 0.5], "children": [ { "type": "splitter", "orientation": "vertical", "splits": [0.5, 0.5], "children": [ { "type": "image", "selected": True }, { "type": "image" } ] }, { "type": "splitter", "orientation": "vertical", "splits": [0.5, 0.5], "children": [ { "type": "image" }, { "type": "image" } ] } ] }
    elif layout_id == "3x2":
        d = { "type": "splitter", "orientation": "vertical", "splits": [1.0/3, 1.0/3, 1.0/3], "children": [ { "type": "splitter", "orientation": "horizontal", "splits": [0.5, 0.5], "children": [ { "type": "image", "selected": True }, { "type": "image" } ] }, { "type": "splitter", "orientation": "horizontal", "splits": [0.5, 0.5], "children": [ { "type": "image" }, { "type": "image" } ] }, { "type": "splitter", "orientation": "horizontal", "splits": [0.5, 0.5], "children": [ { "type": "image" }, { "type": "image" } ] } ] }
    else:  # default 1x1
        layout_id = "1x1"
        d = { "type": "image", "selected": True }
    return layout_id, d


class TestWorkspaceClass(unittest.TestCase):

    def setUp(self):
        self.app = Application.Application(Test.UserInterface(), set_global=False)

    def tearDown(self):
        pass

    def test_basic_change_layout_results_in_correct_image_panel_count(self):
        document_controller = DocumentController_test.construct_test_document(self.app, workspace_id="library")
        workspace_1x1 = document_controller.document_model.workspaces[0]
        workspace_2x1 = document_controller.workspace_controller.new_workspace(*get_layout("2x1"))
        workspace_3x1 = document_controller.workspace_controller.new_workspace(*get_layout("3x1"))
        workspace_2x2 = document_controller.workspace_controller.new_workspace(*get_layout("2x2"))
        workspace_3x2 = document_controller.workspace_controller.new_workspace(*get_layout("3x2"))
        workspace_1x2 = document_controller.workspace_controller.new_workspace(*get_layout("1x2"))
        self.assertEqual(len(document_controller.document_model.workspaces), 6)
        document_controller.workspace_controller.change_workspace(workspace_1x1)
        self.assertEqual(len(document_controller.workspace_controller.image_panels), 1)
        document_controller.workspace_controller.change_workspace(workspace_1x1)
        self.assertEqual(len(document_controller.workspace_controller.image_panels), 1)
        document_controller.workspace_controller.change_workspace(workspace_2x1)
        self.assertEqual(len(document_controller.workspace_controller.image_panels), 2)
        document_controller.workspace_controller.change_workspace(workspace_3x1)
        self.assertEqual(len(document_controller.workspace_controller.image_panels), 3)
        document_controller.workspace_controller.change_workspace(workspace_2x2)
        self.assertEqual(len(document_controller.workspace_controller.image_panels), 4)
        document_controller.workspace_controller.change_workspace(workspace_3x2)
        self.assertEqual(len(document_controller.workspace_controller.image_panels), 6)
        document_controller.workspace_controller.change_workspace(workspace_1x2)
        self.assertEqual(len(document_controller.workspace_controller.image_panels), 2)
        document_controller.workspace_controller.change_workspace(workspace_1x1)
        self.assertEqual(len(document_controller.workspace_controller.image_panels), 1)

    def test_basic_change_layout_results_in_image_panel_being_destructed(self):
        document_model = DocumentModel.DocumentModel()
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        workspace_1x1 = document_controller.document_model.workspaces[0]
        workspace_2x1 = document_controller.workspace_controller.new_workspace(*get_layout("2x1"))
        document_controller.workspace_controller.change_workspace(workspace_1x1)
        image_panel_weak_ref = weakref.ref(document_controller.workspace_controller.image_panels[0])
        document_controller.workspace_controller.change_workspace(workspace_2x1)
        self.assertIsNone(image_panel_weak_ref())

    def test_image_panel_focused_when_clicked(self):
        # setup
        document_model = DocumentModel.DocumentModel()
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        workspace_2x1 = document_controller.workspace_controller.new_workspace(*get_layout("2x1"))
        data_item1 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        data_item2 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        document_model.append_data_item(data_item1)
        document_model.append_data_item(data_item2)
        document_controller.workspace_controller.change_workspace(workspace_2x1)
        document_controller.workspace_controller.image_panels[0].set_displayed_data_item(data_item1)
        document_controller.workspace_controller.image_panels[1].set_displayed_data_item(data_item2)
        root_canvas_item = document_controller.workspace_controller.image_row.children[0]._root_canvas_item()
        root_canvas_item.update_layout(Geometry.IntPoint(), Geometry.IntSize(width=640, height=480))
        # click in first panel
        modifiers = Test.KeyboardModifiers()
        root_canvas_item.canvas_widget.on_mouse_clicked(160, 240, modifiers)
        self.assertTrue(document_controller.workspace_controller.image_panels[0]._is_focused())
        self.assertTrue(document_controller.workspace_controller.image_panels[0]._is_selected())
        self.assertFalse(document_controller.workspace_controller.image_panels[1]._is_focused())
        self.assertFalse(document_controller.workspace_controller.image_panels[1]._is_selected())
        # now click the second panel
        root_canvas_item.canvas_widget.on_mouse_clicked(480, 240, modifiers)
        self.assertFalse(document_controller.workspace_controller.image_panels[0]._is_focused())
        self.assertFalse(document_controller.workspace_controller.image_panels[0]._is_selected())
        self.assertTrue(document_controller.workspace_controller.image_panels[1]._is_focused())
        self.assertTrue(document_controller.workspace_controller.image_panels[1]._is_selected())
        # and back to the first panel
        modifiers = Test.KeyboardModifiers()
        root_canvas_item.canvas_widget.on_mouse_clicked(160, 240, modifiers)
        self.assertTrue(document_controller.workspace_controller.image_panels[0]._is_focused())
        self.assertTrue(document_controller.workspace_controller.image_panels[0]._is_selected())
        self.assertFalse(document_controller.workspace_controller.image_panels[1]._is_focused())
        self.assertFalse(document_controller.workspace_controller.image_panels[1]._is_selected())

    def test_empty_image_panel_focused_when_clicked(self):
        # setup
        document_model = DocumentModel.DocumentModel()
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        workspace_2x1 = document_controller.workspace_controller.new_workspace(*get_layout("2x1"))
        if True:
            data_item1 = DataItem.DataItem(numpy.zeros((256), numpy.double))
            document_model.append_data_item(data_item1)
        document_controller.workspace_controller.change_workspace(workspace_2x1)
        if True:
            document_controller.workspace_controller.image_panels[0].set_displayed_data_item(data_item1)
        root_canvas_item = document_controller.workspace_controller.image_row.children[0]._root_canvas_item()
        root_canvas_item.update_layout(Geometry.IntPoint(), Geometry.IntSize(width=640, height=480))
        # click in first panel
        modifiers = Test.KeyboardModifiers()
        root_canvas_item.canvas_widget.on_mouse_clicked(160, 240, modifiers)
        self.assertTrue(document_controller.workspace_controller.image_panels[0]._is_focused())
        self.assertTrue(document_controller.workspace_controller.image_panels[0]._is_selected())
        self.assertFalse(document_controller.workspace_controller.image_panels[1]._is_focused())
        self.assertFalse(document_controller.workspace_controller.image_panels[1]._is_selected())

    def test_workspace_construct_and_deconstruct_result_in_matching_descriptions(self):
        # setup
        document_model = DocumentModel.DocumentModel()
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        workspace_2x1 = document_controller.workspace_controller.new_workspace(*get_layout("2x1"))
        data_item1 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        data_item2 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        document_model.append_data_item(data_item1)
        document_model.append_data_item(data_item2)
        document_controller.workspace_controller.change_workspace(workspace_2x1)
        root_canvas_item = document_controller.workspace_controller.image_row.children[0]._root_canvas_item()
        root_canvas_item.update_layout(Geometry.IntPoint(), Geometry.IntSize(width=640, height=480))
        # deconstruct
        desc1 = get_layout("2x1")[1]
        desc2 = document_controller.workspace_controller._deconstruct(root_canvas_item.canvas_items[0])
        self.assertEqual(desc1, desc2)

    def test_workspace_change_records_workspace_uuid(self):
        document_controller = DocumentController_test.construct_test_document(self.app, workspace_id="library")
        workspace_1x1 = document_controller.document_model.workspaces[0]
        workspace_2x1 = document_controller.workspace_controller.new_workspace(*get_layout("2x1"))
        self.assertEqual(document_controller.document_model.workspace_uuid, workspace_1x1.uuid)
        document_controller.workspace_controller.change_workspace(workspace_2x1)
        self.assertEqual(document_controller.document_model.workspace_uuid, workspace_2x1.uuid)
        document_controller.workspace_controller.change_workspace(workspace_1x1)
        self.assertEqual(document_controller.document_model.workspace_uuid, workspace_1x1.uuid)

    def test_workspace_change_records_workspace_data_item_contents(self):
        document_model = DocumentModel.DocumentModel()
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        workspace_1x1 = document_controller.document_model.workspaces[0]
        workspace_2x1 = document_controller.workspace_controller.new_workspace(*get_layout("2x1"))
        data_item1 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        data_item2 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        data_item3 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        document_model.append_data_item(data_item1)
        document_model.append_data_item(data_item2)
        document_model.append_data_item(data_item3)
        document_controller.workspace_controller.image_panels[0].set_displayed_data_item(data_item1)
        document_controller.workspace_controller.change_workspace(workspace_2x1)
        document_controller.workspace_controller.image_panels[0].set_displayed_data_item(data_item2)
        document_controller.workspace_controller.image_panels[1].set_displayed_data_item(data_item3)
        document_controller.workspace_controller.change_workspace(workspace_1x1)
        self.assertEqual(document_controller.workspace_controller.image_panels[0].get_displayed_data_item(), data_item1)
        document_controller.workspace_controller.change_workspace(workspace_2x1)
        self.assertEqual(document_controller.workspace_controller.image_panels[0].get_displayed_data_item(), data_item2)
        self.assertEqual(document_controller.workspace_controller.image_panels[1].get_displayed_data_item(), data_item3)

    def test_workspace_records_json_compatible_content_when_closing_document(self):
        library_storage = DocumentModel.FilePersistentStorage()
        document_model = DocumentModel.DocumentModel(library_storage=library_storage)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        workspace_1x1 = document_controller.document_model.workspaces[0]
        data_item1 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        document_model.append_data_item(data_item1)
        document_controller.workspace_controller.image_panels[0].set_displayed_data_item(data_item1)
        document_controller.close()
        json_str = json.dumps(library_storage.properties)
        properties = json.loads(json_str)
        self.assertEqual(properties, library_storage.properties)

    def test_workspace_records_and_reloads_image_panel_contents(self):
        data_reference_handler = DocumentModel.DataReferenceMemoryHandler()
        library_storage = DocumentModel.FilePersistentStorage()
        document_model = DocumentModel.DocumentModel(library_storage=library_storage, data_reference_handler=data_reference_handler)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        workspace_1x1 = document_controller.document_model.workspaces[0]
        data_item1 = DataItem.DataItem(numpy.zeros((256), numpy.double))
        document_model.append_data_item(data_item1)
        document_controller.workspace_controller.image_panels[0].set_displayed_data_item(data_item1)
        document_controller.close()
        # reload
        document_model = DocumentModel.DocumentModel(library_storage=library_storage, data_reference_handler=data_reference_handler)
        document_controller = DocumentController.DocumentController(self.app.ui, document_model, workspace_id="library")
        workspace_1x1 = document_controller.document_model.workspaces[0]
        self.assertEqual(document_controller.workspace_controller.image_panels[0].get_displayed_data_item(), document_model.data_items[0])


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
