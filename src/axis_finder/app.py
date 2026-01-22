import argparse
from pathlib import Path

import panel as pn
from bokeh.models.formatters import PrintfTickFormatter

from axis_finder.image import draw_images, list_images


class App:
    def __init__(self, image_dir: Path):
        self._image_paths = list_images(image_dir)

        self._image_range = pn.widgets.EditableRangeSlider(
            name="Image range",
            start=1,
            end=800,
            value=(1, len(self._image_paths) // 2),
            step=1,
            format=PrintfTickFormatter(format="%d"),
            sizing_mode="stretch_width",
        )
        self._switch_show_diff = pn.widgets.Switch(
            name="Show Difference Image", value=True, sizing_mode="stretch_width"
        )
        self._switch_invert_colors = pn.widgets.Switch(
            name="Invert Colors", value=False, sizing_mode="stretch_width"
        )
        self._color_selection = pn.widgets.Select(
            name="Color Map",
            options=["yellow-blue", "magenta-green", "red-cyan"],
            value="yellow-blue",
            sizing_mode="stretch_width",
        )
        self._image_selection = pn.widgets.EditableIntSlider(
            name="Selected image index",
            start=1,
            end=len(self._image_paths) // 2,
            step=1,
            value=1,
            sizing_mode="stretch_width",
        )
        self._next_button = pn.widgets.Button(
            name="Next image", button_type="primary", sizing_mode="stretch_width"
        )
        self._prev_button = pn.widgets.Button(
            name="Previous image", button_type="primary", sizing_mode="stretch_width"
        )

        self._center_x_slider = pn.widgets.EditableIntSlider(
            name="Center X",
            start=0,
            end=self._image_paths[0].width,
            step=1,
            value=self._image_paths[0].width // 2,
            sizing_mode="stretch_width",
        )
        self._center_y_slider = pn.widgets.EditableIntSlider(
            name="Center Y",
            start=0,
            end=self._image_paths[0].height,
            step=1,
            value=self._image_paths[0].height // 2,
            sizing_mode="stretch_width",
        )
        self._crop_width_slider = pn.widgets.EditableIntSlider(
            name="Crop Width",
            start=1,
            end=self._image_paths[0].width,
            step=1,
            value=self._image_paths[0].width,
            sizing_mode="stretch_width",
        )
        self._crop_height_slider = pn.widgets.EditableIntSlider(
            name="Crop Height",
            start=1,
            end=self._image_paths[0].height,
            step=1,
            value=self._image_paths[0].height,
            sizing_mode="stretch_width",
        )
        self._summary_text = pn.pane.Markdown("", sizing_mode="stretch_width")
        self._export_button = pn.widgets.Button(
            name="Export", button_type="primary", sizing_mode="stretch_width"
        )

        center = (self._image_paths[0].width // 2, self._image_paths[0].height // 2)
        crop_size = (self._image_paths[0].width, self._image_paths[0].height)

        img_path_a = self._image_paths[0].path
        img_path_b = self._image_paths[len(self._image_paths) // 2].path

        self._overlap_img_viewer = pn.pane.image.Image(
            draw_images(img_path_a, img_path_b, center, crop_size),
            sizing_mode="stretch_both",
        )
        self._init_action()

        self.update_summary_text()

    def update_summary_text(self):
        center = (self._center_x_slider.value, self._center_y_slider.value)
        crop_size = (self._crop_width_slider.value, self._crop_height_slider.value)

        first_image_index = int(self._image_range.value[0] - 1)
        first_image_path = self._image_paths[first_image_index].path
        image_count = int(self._image_range.value[1] - self._image_range.value[0] + 1)

        self._summary_text.object = (
            f"### Summary:\n\n"
            f"```python\n"
            f"first_image_index = {first_image_index}\n"
            f"first_image_path = '{first_image_path}'\n"
            f"image_count = {image_count}\n\n"
            f"cx, cy, w, h = {center[0]}, {center[1]}, {crop_size[0]}, {crop_size[1]}\n"
            f"```"
        )

    def update_image_selection_slider(self):
        start, end = self._image_range.value
        n = int(end - start + 1)
        self._image_selection.end = n
        if self._image_selection.value > n:
            self._image_selection.value = n

    def update_overlap_image(self):
        idx = self._image_selection.value - 1
        start_idx, end_idx = map(int, self._image_range.value)

        img_a_path = self._image_paths[start_idx + idx].path
        img_b_path = self._image_paths[
            (start_idx + idx + (end_idx - start_idx + 1)) % len(self._image_paths)
        ].path

        center = (self._center_x_slider.value, self._center_y_slider.value)
        crop_size = (self._crop_width_slider.value, self._crop_height_slider.value)

        overlap_image = draw_images(
            img_a_path,
            img_b_path,
            center,
            crop_size,
            show_diff=self._switch_show_diff.value,
            invert_colors=self._switch_invert_colors.value,
            color_map=self._color_selection.value,
        )
        self._overlap_img_viewer.object = overlap_image

    def next_image(self):
        if self._image_selection.value < self._image_selection.end:
            self._image_selection.value += 1

    def prev_image(self):
        if self._image_selection.value > self._image_selection.start:
            self._image_selection.value -= 1

    def _init_action(self):
        self._next_button.on_click(lambda _: self.next_image())
        self._prev_button.on_click(lambda _: self.prev_image())
        self._image_range.param.watch(
            lambda _: self.update_image_selection_slider(), "value"
        )

        def on_slider_update(_):
            self.update_overlap_image()
            self.update_summary_text()

        self._image_range.param.watch(on_slider_update, "value")
        self._image_selection.param.watch(on_slider_update, "value")
        self._center_x_slider.param.watch(on_slider_update, "value")
        self._center_y_slider.param.watch(on_slider_update, "value")
        self._crop_width_slider.param.watch(on_slider_update, "value")
        self._crop_height_slider.param.watch(on_slider_update, "value")
        self._switch_show_diff.param.watch(on_slider_update, "value")
        self._switch_invert_colors.param.watch(on_slider_update, "value")
        self._color_selection.param.watch(on_slider_update, "value")

    def make(self):
        widget_box = pn.WidgetBox(
            pn.Column(
                pn.pane.Markdown(
                    "# Axis Finder\n"
                    "The image range specifies the images covering a rotation angle of 180°:"
                ),
                self._image_range,
                pn.pane.Markdown(
                    "Index of the currently selected image within the specified range:"
                ),
                self._image_selection,
                pn.pane.Markdown("### Crop settings:"),
                pn.Row(self._center_x_slider, self._center_y_slider),
                pn.Row(self._crop_width_slider, self._crop_height_slider),
                pn.Spacer(height=10),
                pn.Row(self._prev_button, self._next_button),
                pn.Spacer(height=10),
                pn.pane.Markdown("### Visualization settings:"),
                pn.Row(
                    pn.Column(self._switch_show_diff, self._switch_invert_colors),
                    self._color_selection,
                ),
                pn.Spacer(height=10),
                self._summary_text,
                margin=10,
            ),
            width=500,
        )
        return pn.Row(widget_box, self._overlap_img_viewer, margin=10)


def main():
    pn.extension()

    parser = argparse.ArgumentParser(description="GUI Axis Finder")
    parser.add_argument(
        "image_dir",
        type=Path,
        help="Directory containing the images",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable auto-reload for development",
    )
    args = parser.parse_args()

    app = App(args.image_dir)
    pn.serve(app.make(), title="GUI Axis Finder", show=True, autoreload=args.dev)
