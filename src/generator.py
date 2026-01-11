"""
2D object rotation task generator.

Generates 1-5 simple 2D objects (circle, square, triangle, ellipse), computes
their geometric center, and produces a first frame (original) and last frame
(all objects rotated around the geometric center by X degrees, clockwise or
counterclockwise). Optionally produces a short video by interpolating the
rotation.
"""

import random
import math
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from core import BaseGenerator, TaskPair
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


SHAPES = ["circle", "square", "triangle", "ellipse"]
PALETTE = [
    "red", "blue", "green", "orange",
    "purple", "cyan", "yellow", "magenta",
]


def _rotate_point(x, y, cx, cy, angle_rad):
    dx = x - cx
    dy = y - cy
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rx = dx * cos_a - dy * sin_a
    ry = dx * sin_a + dy * cos_a
    return cx + rx, cy + ry


class TaskGenerator(BaseGenerator):
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")

    def generate_task_pair(self, task_id: str) -> TaskPair:
        # Sample objects (each object will rotate around its own geometric center)
        num_objects = random.randint(1, 5)
        w, h = self.config.image_size

        objects = []
        for i in range(num_objects):
            shape = random.choice(SHAPES + ["polygon"])  # allow irregular polygons
            color = random.choice(PALETTE)
            size = random.randint(int(min(w, h) * 0.06), int(min(w, h) * 0.22))

            # Place centers randomly but biased near center
            cx = int(w * 0.5 + random.randint(-int(w * 0.25), int(w * 0.25)))
            cy = int(h * 0.5 + random.randint(-int(h * 0.25), int(h * 0.25)))

            obj = {
                "shape": shape,
                "color": color,
                "size": size,
                "center": (cx, cy),
            }
            
            # Pre-generate polygon vertices for irregular shapes to ensure consistency
            if shape == "polygon":
                verts = []
                num_verts = random.randint(4, 8)
                for k in range(num_verts):
                    ang = 2 * math.pi * k / num_verts + random.uniform(-0.3, 0.3)
                    radius = random.uniform(size * 0.35, size * 0.95)
                    x = cx + math.cos(ang) * radius
                    y = cy + math.sin(ang) * radius
                    verts.append((x, y))
                obj["polygon_verts"] = verts
            
            objects.append(obj)

        # Direction and degrees
        direction = random.choice(["clockwise", "counterclockwise"])
        degrees = random.randint(10, 180)
        # angle_deg: positive for counterclockwise, negative for clockwise (math convention)
        # But we need to reverse this so direction matches visual rotation
        angle_deg = -degrees if direction == "counterclockwise" else degrees

        # Prepare prompt (English) and store last prompt
        prompt = get_prompt(objects, direction, degrees)
        self._last_prompt = prompt

        # Render first and last frames (pass metadata for overlay)
        first_image = self._render_frame(objects, None, 0.0, direction=direction, degrees=degrees)
        final_image = self._render_frame(objects, None, math.radians(angle_deg), direction=direction, degrees=degrees)

        # Generate video if possible
        video_path = None
        if self.config.generate_videos and self.video_generator:
            frames = []
            transition_frames = max(8, int(self.config.video_fps * 1.0))
            for i in range(transition_frames + 1):
                t = i / transition_frames
                interm_angle = math.radians(angle_deg) * t
                frames.append(self._render_frame(objects, None, interm_angle, direction=direction, degrees=degrees))

            temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
            temp_dir.mkdir(parents=True, exist_ok=True)
            out_path = temp_dir / f"{task_id}_ground_truth.mp4"
            try:
                res = self.video_generator.create_video_from_frames(frames, out_path)
                video_path = str(res)
            except Exception:
                video_path = None

        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path,
        )

    def _render_frame(self, objects: list[dict], geom_center: tuple[float, float], angle_rad: float, direction: str | None = None, degrees: int | None = None) -> Image.Image:
        # Create subplot layout: arrange objects in grid to avoid overlap
        num_obj = len(objects)
        if num_obj == 1:
            grid_cols, grid_rows = 1, 1
        elif num_obj == 2:
            grid_cols, grid_rows = 2, 1
        elif num_obj <= 4:
            grid_cols, grid_rows = 2, 2
        else:  # 5 objects
            grid_cols, grid_rows = 3, 2
        
        w, h = self.config.image_size
        cell_w = w // grid_cols
        cell_h = h // grid_rows
        
        base = Image.new("RGB", (w, h), (255, 255, 255))

        # For each object, render in grid cell centered position (independent subplot)
        for idx, o in enumerate(objects):
            # Compute cell position in grid
            cell_row = idx // grid_cols
            cell_col = idx % grid_cols
            cell_x0 = cell_col * cell_w
            cell_y0 = cell_row * cell_h
            cell_center_x = cell_x0 + cell_w // 2
            cell_center_y = cell_y0 + cell_h // 2

            # Draw object on its own RGBA layer so we can rotate the shape itself
            size = o["size"]
            layer_size = max(64, size * 3)
            layer = Image.new("RGBA", (layer_size, layer_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)

            cx = layer.width // 2.0
            cy = layer.height // 2.0

            color = o["color"]
            shape = o["shape"]

            outline = "black"
            stroke = max(2, int(size * 0.06))

            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Generate points for all shapes, then rotate them uniformly
            if shape == "circle":
                # Circle: approximate as many points on perimeter
                pts = []
                for angle in range(0, 360, 10):
                    rad = math.radians(angle)
                    x = cx + (size // 2) * math.cos(rad)
                    y = cy + (size // 2) * math.sin(rad)
                    pts.append((x, y))
            elif shape == "square":
                pts = [
                    (cx - size//2, cy - size//2),
                    (cx + size//2, cy - size//2),
                    (cx + size//2, cy + size//2),
                    (cx - size//2, cy + size//2),
                ]
            elif shape == "triangle":
                pts = [
                    (cx, cy - size//2),
                    (cx - size//2, cy + size//2),
                    (cx + size//2, cy + size//2),
                ]
            elif shape == "ellipse":
                # Ellipse: approximate as points on the perimeter
                pts = []
                major = size // 2
                minor = int(size * 0.3)
                for angle in range(0, 360, 10):
                    rad = math.radians(angle)
                    x = cx + major * math.cos(rad)
                    y = cy + minor * math.sin(rad)
                    pts.append((x, y))
            elif shape == "polygon":
                # Use pre-generated vertices to ensure consistency
                pts = o.get("polygon_verts", [])

            # For all non-circle shapes: ensure centroid is at (cx, cy)
            if shape != "circle":
                cx_pts = sum(p[0] for p in pts) / len(pts)
                cy_pts = sum(p[1] for p in pts) / len(pts)
                shift_x = cx - cx_pts
                shift_y = cy - cy_pts
                pts = [(x + shift_x, y + shift_y) for (x, y) in pts]

            # Rotate all points around (cx, cy)
            rot_pts = []
            for pt_x, pt_y in pts:
                dx = pt_x - cx
                dy = pt_y - cy
                rot_x = cx + dx * cos_a - dy * sin_a
                rot_y = cy + dx * sin_a + dy * cos_a
                rot_pts.append((rot_x, rot_y))

            # Draw the rotated shape
            if shape == "circle":
                draw.polygon(rot_pts, fill=color)
                draw.line(rot_pts + [rot_pts[0]], fill=outline, width=stroke)
            elif shape == "ellipse":
                draw.polygon(rot_pts, fill=color)
                draw.line(rot_pts + [rot_pts[0]], fill=outline, width=stroke)
            else:  # square, triangle, polygon
                draw.polygon(rot_pts, fill=color)
                draw.line(rot_pts + [rot_pts[0]], fill=outline, width=stroke)

            # Paste layer onto base image centered at cell center
            px = int(cell_center_x - layer.width / 2)
            py = int(cell_center_y - layer.height / 2)
            base.paste(layer, (px, py), layer)

            # Draw rotation arc, arrow, and degree label for this object in its cell
            r = int(max(size, 32) * 0.75) + 12

            # Arc from top (-90 deg = 12 o'clock)
            start_ang = -90
            if direction == "counterclockwise":
                # Counterclockwise: visual endpoint sweeps counterclockwise
                end_ang = start_ang - (degrees if degrees is not None else 0)
            else:  # clockwise
                # Clockwise: visual endpoint sweeps clockwise
                end_ang = start_ang + (degrees if degrees is not None else 0)

            # PIL arc: always goes counterclockwise from arc_start to arc_end
            # Normalize angles to ensure arc_start < arc_end for PIL to draw correctly
            # The visual endpoint where arrow should be is always at end_ang
            arc_start = min(start_ang, end_ang)
            arc_end = max(start_ang, end_ang)

            # Draw arc
            bbox = [cell_center_x - r, cell_center_y - r, cell_center_x + r, cell_center_y + r]
            draw_main = ImageDraw.Draw(base)
            draw_main.arc(bbox, start=arc_start, end=arc_end, fill="black", width=max(3, int(size * 0.08)))

            # Arrowhead at the true end_ang (visual endpoint)
            end_rad = math.radians(end_ang)
            tip_x = cell_center_x + r * math.cos(end_rad)
            tip_y = cell_center_y + r * math.sin(end_rad)
            
            # Tangent direction at arc end points along direction of rotation
            # Tangent is perpendicular to radius
            # Counterclockwise motion: tangent is -90° from radius
            # Clockwise motion: tangent is +90° from radius
            if direction == "counterclockwise":
                tangent_ang = end_rad - math.pi / 2
            else:  # clockwise
                tangent_ang = end_rad + math.pi / 2
            
            # Arrowhead: tip points in tangent direction, base is back from tip
            arrow_len = 12
            arrow_width = 8
            base_x = tip_x - arrow_len * math.cos(tangent_ang)
            base_y = tip_y - arrow_len * math.sin(tangent_ang)
            
            # Perpendicular to tangent for arrow width
            perp_ang = tangent_ang + math.pi / 2
            corner1_x = base_x + arrow_width * math.cos(perp_ang)
            corner1_y = base_y + arrow_width * math.sin(perp_ang)
            corner2_x = base_x - arrow_width * math.cos(perp_ang)
            corner2_y = base_y - arrow_width * math.sin(perp_ang)
            
            draw_main.polygon([(tip_x, tip_y), (corner1_x, corner1_y), (corner2_x, corner2_y)], fill="black")

            # Degree label at middle of arc
            mid_ang = (start_ang + end_ang) / 2
            mid_rad = math.radians(mid_ang)
            label_r = r + 14
            lx = cell_center_x + label_r * math.cos(mid_rad)
            ly = cell_center_y + label_r * math.sin(mid_rad)
            deg_text = f"{degrees}°" if degrees is not None else "?°"
            
            try:
                small_font = ImageFont.truetype("DejaVuSans.ttf", 14)
            except Exception:
                small_font = ImageFont.load_default()
            
            tb = draw_main.textbbox((0, 0), deg_text, font=small_font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            rect_pad = 4
            draw_main.rectangle([(lx - tw//2 - rect_pad, ly - th//2 - rect_pad), (lx + tw//2 + rect_pad, ly + th//2 + rect_pad)], fill=(255, 255, 255))
            draw_main.text((lx - tw//2, ly - th//2), deg_text, fill="black", font=small_font)

        # Draw a large centered title indicating direction and angle
        w = self.config.image_size[0]
        draw = ImageDraw.Draw(base)
        title_font = None
        for font_path in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "DejaVuSans.ttf"
        ]:
            try:
                title_font = ImageFont.truetype(font_path, 24)
                break
            except:
                continue
        if title_font is None:
            title_font = ImageFont.load_default()

        title_dir = direction.capitalize() if direction else "Unknown"
        title_deg = f"{degrees}°" if degrees is not None else "?°"
        title_text = f"{title_dir} Rotation {title_deg}"
        tbox = draw.textbbox((0, 0), title_text, font=title_font)
        t_w, t_h = tbox[2] - tbox[0], tbox[3] - tbox[1]
        draw.rectangle([(w//2 - t_w//2 - 8, 6), (w//2 + t_w//2 + 8, 6 + t_h + 6)], fill=(255,255,255))
        draw.text((w//2 - t_w//2, 9), title_text, fill="black", font=title_font)

        return base
