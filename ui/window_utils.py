from PyQt5.QtWidgets import QApplication

def move_window_to_screen(window, screen_number=0, center=False):
    app = QApplication.instance()
    screens = app.screens()
    if screen_number < len(screens):
        geometry = screens[screen_number].geometry()
        if center:
            frame_geom = window.frameGeometry()
            frame_geom.moveCenter(geometry.center())
            window.move(frame_geom.topLeft())
        else:
            window.move(geometry.left(), geometry.top())
    else:
        window.move(100, 100)

def move_window_to_screen_center(window, screen_number=0, width=None, height=None):
    app = QApplication.instance()
    screens = app.screens()
    if screen_number < len(screens):
        geometry = screens[screen_number].geometry()
        if width and height:
            window.resize(width, height)
        frame_geom = window.frameGeometry()
        frame_geom.setWidth(width or frame_geom.width())
        frame_geom.setHeight(height or frame_geom.height())
        frame_geom.moveCenter(geometry.center())
        window.move(frame_geom.topLeft())
    else:
        if width and height:
            window.resize(width, height)
        window.move(100, 100)

def move_window_to_screen_right_of(window, reference_window, screen_number=0, width=None, height=None):
    app = QApplication.instance()
    screens = app.screens()
    if screen_number < len(screens):
        geometry = screens[screen_number].geometry()
        ref_geom = reference_window.frameGeometry()
        if width and height:
            window.resize(width, height)
        # Place to the right of the reference window, but within the screen
        x = ref_geom.right() + 10
        y = ref_geom.top()
        # If it would go off the screen, clamp to screen
        if x + (width or window.width()) > geometry.right():
            x = geometry.right() - (width or window.width())
        if y + (height or window.height()) > geometry.bottom():
            y = geometry.bottom() - (height or window.height())
        window.move(max(x, geometry.left()), max(y, geometry.top()))
    else:
        if width and height:
            window.resize(width, height)
        window.move(100, 100)