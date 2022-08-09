import time


def is_horizontal_line_inside_box(line, bb):
    aa_line = (line[2], line[0], line[1])  # y, x1, x2
    aabb = (bb[1], bb[0], bb[3], bb[2])  # y, x, h, w

    return is_aa_line_inside_box(aa_line, aabb)


def is_vertical_line_inside_box(line, bb):
    return is_aa_line_inside_box(line, bb)


def is_aa_line_inside_box(line, bb):
    # static = coord component given once
    # dyn = coord component given twice
    static_l, dyn_l, dyn_l2 = line
    static_b, dyn_b, static_size_b, dyn_size_b = bb

    # static component not in range of aabb
    if not static_b <= static_l <= static_b + static_size_b:
        return False

    # dyn component 1 inside aabb
    if dyn_b <= dyn_l <= dyn_b + dyn_size_b:
        return True

    # dyn component 2 inside aabb
    if dyn_b <= dyn_l2 <= dyn_b + dyn_size_b:
        return True

    # dyn components enclose aabb
    if dyn_l < dyn_b and dyn_l2 > dyn_b + dyn_size_b:
        return True

    return False


class GridFinder:
    def __init__(self, w, h):
        self.grid = []
        self.runtime = 0

        self.w = w
        self.h = h

    def calculate_grid_positions(self, yolo_bb):
        t0 = time.time()

        grid = []

        if not len(yolo_bb) > 0:
            return grid

        first_item = GridFinder.find_first_item(yolo_bb)
        grid.append([first_item])

        y = first_item[0][1] + first_item[1][1]

        while y < self.h:
            for i in range(len(yolo_bb)):
                current_box = yolo_bb[i]
                current_box_xywh = (current_box[0][0], current_box[0][1], current_box[1][0], current_box[1][1])

                if current_box[0][1] < y:
                    continue

                scan_line = (grid[-1][0][0][0], grid[-1][0][0][0] + grid[-1][0][1][0], y)
                if is_horizontal_line_inside_box(scan_line, current_box_xywh):
                    grid.append([current_box])
                    y = current_box_xywh[1] + current_box_xywh[3]
                    break

            y += 1

        for row in range(len(grid)):
            box = grid[row][0]
            x = box[0][0]

            while x < self.w:
                for i in range(len(yolo_bb)):
                    # noinspection DuplicatedCode
                    current_box = yolo_bb[i]
                    current_box_xywh = (current_box[0][0], current_box[0][1], current_box[1][0], current_box[1][1])

                    if current_box == box:
                        continue

                    scan_line = (x, box[0][1], box[0][1] + box[1][1])
                    if is_vertical_line_inside_box(scan_line, current_box_xywh):
                        box = current_box
                        grid[row].append(box)
                        x = box[0][0]
                        break

                x += 1

        self.grid = grid

        t = time.time()

        self.runtime = t - t0

    @staticmethod
    def find_first_item(yolo_bb):
        item_in_first_row = GridFinder.find_item_in_first_row(yolo_bb)

        x = item_in_first_row[0][0]
        first_item = item_in_first_row

        while x >= 0:
            for i in range(len(yolo_bb)):
                # noinspection DuplicatedCode
                current_box = yolo_bb[i]
                current_box_xywh = (current_box[0][0], current_box[0][1], current_box[1][0], current_box[1][1])

                if current_box == first_item:
                    continue

                scan_line = (x, first_item[0][1], first_item[0][1] + first_item[1][1])
                if is_vertical_line_inside_box(scan_line, current_box_xywh):
                    first_item = current_box
                    x = first_item[0][0]
                    break

            x -= 1

        return first_item

    @staticmethod
    def find_item_in_first_row(yolo_bb):
        some_item = yolo_bb[0]
        item_in_first_row = some_item

        for i in range(1, len(yolo_bb)):
            current_box = yolo_bb[i]

            # box.y < box2.y
            if current_box[0][1] < item_in_first_row[0][1]:
                item_in_first_row = current_box

        return item_in_first_row
