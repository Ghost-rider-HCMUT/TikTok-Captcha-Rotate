def compute_rotate_slide_distance(angle: int, slide_bar_width: float, slide_button_width: float) -> int:
    return int((slide_bar_width-slide_button_width) * (abs(angle)/ 180))

