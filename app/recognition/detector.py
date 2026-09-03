from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image

CARD_RATIO = 88 / 63
DETECT_SIDE = 2000
CROP_HEIGHT = 720


def detect_card_boxes(image: Image.Image, max_cards: int = 40) -> list[np.ndarray]:
    """Return 4x2 float boxes in the original image's pixel coordinates."""
    rgb = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    h0, w0 = bgr.shape[:2]
    scale = min(1.0, DETECT_SIDE / max(h0, w0))
    if scale < 1:
        work = cv2.resize(bgr, (int(w0 * scale), int(h0 * scale)), interpolation=cv2.INTER_AREA)
    else:
        work = bgr
        scale = 1.0
    holes = _nms(_yellow_hole_boxes(work), iou_thr=0.40)
    closeups = _nms(_closeup_frame_boxes(work), iou_thr=0.40)
    if closeups:
        # Phone photos of one or two cards fill the frame. Those yellow
        # borders are outer contours, not the small inner holes a carpet grid makes.
        boxes = closeups
    elif len(holes) >= 4:
        filled = _fill_grid_gaps(work, holes)
        boxes = _split_double_boxes(holes + filled)
        boxes = _drop_contained(boxes)
        boxes = _nms(boxes, iou_thr=0.40)
    else:
        # One phone photo of a single card: a yellow energy symbol can look like a
        # hole, but it is not a carpet grid. Read the whole frame instead.
        boxes = [_inset_full_frame(work)]
    if scale != 1:
        boxes = [box / scale for box in boxes]
    boxes.sort(key=lambda b: (b[:, 1].mean() // 90, b[:, 0].mean()))
    return boxes[:max_cards]


def detect_card_crops(image: Image.Image, max_cards: int = 40, target_h: int = CROP_HEIGHT) -> list[Image.Image]:
    boxes = detect_card_boxes(image, max_cards=max_cards)
    rgb = np.array(image.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    crops = []
    h0, w0 = rgb.shape[:2]
    img_area = float(h0 * w0)
    for box in boxes:
        x1, y1, x2, y2 = _aabb(box)
        if ((x2 - x1) * (y2 - y1)) >= img_area * 0.70:
            crops.append(image)
            continue
        crop = warp_card(bgr, box, target_h=target_h)
        if crop is None:
            continue
        if _crop_is_carpet(crop):
            continue
        crops.append(Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))
    return crops


def warp_card(bgr: np.ndarray, box: np.ndarray, target_h: int = CROP_HEIGHT) -> np.ndarray | None:
    pts = _order_points(box.astype(np.float32))
    width = int(max(np.linalg.norm(pts[0] - pts[1]), np.linalg.norm(pts[2] - pts[3])))
    height = int(max(np.linalg.norm(pts[0] - pts[3]), np.linalg.norm(pts[1] - pts[2])))
    if min(width, height) < 28:
        return None
    dest = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(pts, dest)
    crop = cv2.warpPerspective(bgr, matrix, (width, height), flags=cv2.INTER_CUBIC)
    if crop.size == 0:
        return None
    ch, cw = crop.shape[:2]
    if cw > ch * 1.12:
        crop = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)
        ch, cw = crop.shape[:2]
    if ch > 0 and target_h:
        scale = target_h / ch
        crop = cv2.resize(crop, (max(1, int(cw * scale)), target_h), interpolation=cv2.INTER_CUBIC)
    return crop


def _yellow_hole_boxes(bgr: np.ndarray) -> list[np.ndarray]:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, w = bgr.shape[:2]
    img_area = h * w
    yellow = cv2.inRange(hsv, (14, 80, 80), (42, 255, 255))
    yellow = cv2.morphologyEx(yellow, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    contours, hierarchy = cv2.findContours(yellow, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    boxes: list[np.ndarray] = []
    if hierarchy is None:
        return boxes
    hierarchy = hierarchy[0]
    for i, contour in enumerate(contours):
        if hierarchy[i][3] < 0:
            continue
        area = cv2.contourArea(contour)
        if area < img_area * 0.0010 or area > img_area * 0.08:
            continue
        rect = cv2.minAreaRect(contour)
        rw, rh = rect[1]
        if min(rw, rh) < 14:
            continue
        ratio = max(rw, rh) / max(1.0, min(rw, rh))
        if not (1.05 <= ratio <= 2.15):
            continue
        box = _expand_box(cv2.boxPoints(rect), 1.10, w, h)
        boxes.append(box)
    return boxes


def _closeup_frame_boxes(bgr: np.ndarray) -> list[np.ndarray]:
    """Yellow card frames that fill a phone photo (outer contours, not grid holes)."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, w = bgr.shape[:2]
    img_area = float(h * w)
    yellow = cv2.inRange(hsv, (14, 80, 80), (42, 255, 255))
    yellow = cv2.morphologyEx(yellow, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    contours, hierarchy = cv2.findContours(yellow, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    boxes: list[np.ndarray] = []
    if hierarchy is None:
        return boxes
    parents = hierarchy[0]
    for i, contour in enumerate(contours):
        if parents[i][3] >= 0:
            continue
        rect = cv2.minAreaRect(contour)
        rw, rh = rect[1]
        if min(rw, rh) < 48:
            continue
        ratio = max(rw, rh) / max(1.0, min(rw, rh))
        if not (1.05 <= ratio <= 2.15):
            continue
        if (rw * rh) < img_area * 0.12:
            continue
        boxes.append(_expand_box(cv2.boxPoints(rect), 1.04, w, h))
    return boxes


def _inset_full_frame(bgr: np.ndarray) -> np.ndarray:
    h, w = bgr.shape[:2]
    pad_x, pad_y = max(2.0, w * 0.02), max(2.0, h * 0.02)
    return np.array(
        [
            [pad_x, pad_y],
            [w - 1 - pad_x, pad_y],
            [w - 1 - pad_x, h - 1 - pad_y],
            [pad_x, h - 1 - pad_y],
        ],
        dtype=np.float32,
    )


def _fill_grid_gaps(work: np.ndarray, boxes: list[np.ndarray]) -> list[np.ndarray]:
    if len(boxes) < 4:
        return []
    extras = _fill_along(work, boxes, axis=0) + _fill_along(work, boxes, axis=1)
    kept = []
    for box in extras:
        if any(_iou(box, existing) >= 0.35 for existing in boxes + kept):
            continue
        if _looks_like_card(work, box):
            kept.append(box)
    return kept


def _fill_along(work: np.ndarray, boxes: list[np.ndarray], axis: int) -> list[np.ndarray]:
    centers = np.array([box.mean(axis=0) for box in boxes])
    widths, heights = [], []
    for box in boxes:
        x1, y1, x2, y2 = _aabb(box)
        widths.append(x2 - x1)
        heights.append(y2 - y1)
    mw, mh = float(np.median(widths)), float(np.median(heights))
    step = mw if axis == 0 else mh
    other = mh if axis == 0 else mw
    groups = _cluster(range(len(boxes)), lambda i: centers[i, 1 - axis], 0.55 * other)
    extras: list[np.ndarray] = []
    h, w = work.shape[:2]
    for group in groups:
        group = sorted(group, key=lambda i: centers[i, axis])
        vals = centers[np.array(group), axis]
        others = centers[np.array(group), 1 - axis]
        for a in range(len(group) - 1):
            gap = vals[a + 1] - vals[a]
            missing = int(round(gap / step)) - 1
            if missing <= 0 or missing > 3:
                continue
            for k in range(1, missing + 1):
                t = k / (missing + 1)
                c_axis = vals[a] * (1 - t) + vals[a + 1] * t
                c_other = others[a] * (1 - t) + others[a + 1] * t
                extras.append(_aabb_box(c_axis, c_other, mw, mh, axis))
        for sign, origin in ((-1, vals[0]), (1, vals[-1])):
            c_axis = origin + sign * step
            c_other = float(np.mean(others))
            cx, cy = (c_axis, c_other) if axis == 0 else (c_other, c_axis)
            if not (mw * 0.35 < cx < w - mw * 0.35 and mh * 0.35 < cy < h - mh * 0.35):
                continue
            extras.append(_aabb_box(c_axis, c_other, mw, mh, axis))
    return extras


def _aabb_box(c_axis: float, c_other: float, mw: float, mh: float, axis: int) -> np.ndarray:
    cx, cy = (c_axis, c_other) if axis == 0 else (c_other, c_axis)
    return np.array(
        [
            [cx - mw / 2, cy - mh / 2],
            [cx + mw / 2, cy - mh / 2],
            [cx + mw / 2, cy + mh / 2],
            [cx - mw / 2, cy + mh / 2],
        ],
        dtype=np.float32,
    )


def _cluster(indices, coord_fn, thresh: float) -> list[list[int]]:
    groups: list[list[int]] = []
    for idx in sorted(indices, key=coord_fn):
        val = coord_fn(idx)
        placed = False
        for group in groups:
            if abs(float(np.mean([coord_fn(i) for i in group])) - val) < thresh:
                group.append(idx)
                placed = True
                break
        if not placed:
            groups.append([idx])
    return groups


def _looks_like_card(bgr: np.ndarray, box: np.ndarray) -> bool:
    x1, y1, x2, y2 = _aabb(box)
    x1, y1 = max(0, int(x1)), max(0, int(y1))
    x2, y2 = min(bgr.shape[1] - 1, int(x2)), min(bgr.shape[0] - 1, int(y2))
    if x2 - x1 < 24 or y2 - y1 < 24:
        return False
    patch = bgr[y1:y2, x1:x2]
    hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
    sat, val, hue = hsv[:, :, 1], hsv[:, :, 2], hsv[:, :, 0]
    yellow = cv2.inRange(hsv, (14, 80, 80), (42, 255, 255))
    yellow_frac = float(yellow.mean()) / 255.0
    sat_mean = float(np.mean(sat))
    skin = float(((hue < 25) & (sat > 40) & (sat < 140) & (val > 90) & (val < 200)).mean())
    if skin > 0.42:
        return False
    # Gap-fill proposals must still look like a yellow-bordered TCG card, not carpet.
    if yellow_frac >= 0.035 and sat_mean >= 40:
        return True
    return False


def _crop_is_carpet(bgr: np.ndarray) -> bool:
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    yellow = cv2.inRange(hsv, (14, 80, 80), (42, 255, 255))
    if float(np.mean(sat)) < 28 and float(yellow.mean()) / 255.0 < 0.02:
        return True
    return False


def _split_double_boxes(boxes: list[np.ndarray]) -> list[np.ndarray]:
    out: list[np.ndarray] = []
    for box in boxes:
        pts = _order_points(box.astype(np.float32))
        width = float(max(np.linalg.norm(pts[0] - pts[1]), np.linalg.norm(pts[2] - pts[3])))
        height = float(max(np.linalg.norm(pts[0] - pts[3]), np.linalg.norm(pts[1] - pts[2])))
        long_s, short_s = max(width, height), max(1.0, min(width, height))
        ratio = long_s / short_s
        if ratio < 2.05:
            out.append(box)
            continue
        if height >= width:
            mid = (pts[0] + pts[3]) / 2
            mid2 = (pts[1] + pts[2]) / 2
            out.append(np.array([pts[0], pts[1], mid2, mid]))
            out.append(np.array([mid, mid2, pts[2], pts[3]]))
        else:
            mid = (pts[0] + pts[1]) / 2
            mid2 = (pts[3] + pts[2]) / 2
            out.append(np.array([pts[0], mid, mid2, pts[3]]))
            out.append(np.array([mid, pts[1], pts[2], mid2]))
    return out


def _expand_box(box: np.ndarray, factor: float, w: int, h: int) -> np.ndarray:
    center = box.mean(axis=0)
    expanded = center + (box - center) * factor
    expanded[:, 0] = np.clip(expanded[:, 0], 0, w - 1)
    expanded[:, 1] = np.clip(expanded[:, 1], 0, h - 1)
    return expanded


def _aabb(box: np.ndarray) -> tuple[float, float, float, float]:
    return float(box[:, 0].min()), float(box[:, 1].min()), float(box[:, 0].max()), float(box[:, 1].max())


def _iou(a: np.ndarray, b: np.ndarray) -> float:
    ax1, ay1, ax2, ay2 = _aabb(a)
    bx1, by1, bx2, by2 = _aabb(b)
    ix1, iy1, ix2, iy2 = max(ax1, bx1), max(ay1, by1), min(ax2, bx2), min(ay2, by2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1, (bx2 - bx1) * (by2 - by1))
    return inter / (area_a + area_b - inter + 1e-6)


def _intersection_frac(inner: np.ndarray, outer: np.ndarray) -> float:
    ax1, ay1, ax2, ay2 = _aabb(inner)
    bx1, by1, bx2, by2 = _aabb(outer)
    ix1, iy1, ix2, iy2 = max(ax1, bx1), max(ay1, by1), min(ax2, bx2), min(ay2, by2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    area = max(1, (ax2 - ax1) * (ay2 - ay1))
    return inter / area


def _drop_contained(boxes: list[np.ndarray]) -> list[np.ndarray]:
    keep = []
    areas = [cv2.contourArea(b.astype(np.float32)) for b in boxes]
    for i, box in enumerate(boxes):
        contained = False
        for j, other in enumerate(boxes):
            if i == j or areas[i] >= areas[j] * 0.92:
                continue
            if _intersection_frac(box, other) >= 0.72:
                contained = True
                break
        if not contained:
            keep.append(box)
    return keep


def _nms(boxes: list[np.ndarray], iou_thr: float) -> list[np.ndarray]:
    scored = sorted(boxes, key=lambda b: -cv2.contourArea(b.astype(np.float32)))
    keep: list[np.ndarray] = []
    for box in scored:
        if all(_iou(box, k) < iou_thr for k in keep):
            keep.append(box)
    return keep


def _order_points(pts: np.ndarray) -> np.ndarray:
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    ordered = np.zeros((4, 2), dtype=np.float32)
    ordered[0] = pts[np.argmin(s)]
    ordered[2] = pts[np.argmax(s)]
    ordered[1] = pts[np.argmin(diff)]
    ordered[3] = pts[np.argmax(diff)]
    return ordered


def crop_previews(crops: list[Image.Image], max_n: int = 40) -> list[bytes]:
    out = []
    for crop in crops[:max_n]:
        thumb = crop.copy()
        thumb.thumbnail((160, 220))
        buf = io.BytesIO()
        thumb.save(buf, format="JPEG", quality=72)
        out.append(buf.getvalue())
    return out
