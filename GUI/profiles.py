from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QButtonGroup, QDialog,
                             QPushButton, QComboBox, QToolButton, QMessageBox)

from GUI import gui_text
from GUI.misc_classes import ProfileSettings, STab


class NewProfile(QDialog):
    new_profile = pyqtSignal(str, STab)

    def __init__(self, profiles: dict, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(gui_text.newprof_window)
        self.profiles = profiles
        self.selected = STab(0)
        self.bg = QButtonGroup()
        self.bg.setExclusive(False)
        self.le_name = QLineEdit()
        self.pb_ok = QPushButton(gui_text.pb_ok)
        self.pb_cancel = QPushButton(gui_text.pb_cancel)

        for s in STab:
            chb = QCheckBox(s.name, self)
            self.bg.addButton(chb, id=s.value)

        self.bg.idToggled.connect(self.update_sel)
        self.bg.idToggled.connect(self.ok_enabled)
        self.pb_ok.clicked.connect(self.okay)
        self.pb_cancel.clicked.connect(self.reject)
        self.le_name.textChanged.connect(self.ok_enabled)

        self.do_layout()

    def update_sel(self, b_id: int, _: bool):
        self.selected ^= b_id

    def ok_enabled(self):
        self.pb_ok.setEnabled(bool(self.selected and
                                   self.le_name.text() and
                                   self.le_name.text().strip().lower() not in map(str.lower, self.profiles.keys())
                                   ))

    def open(self):
        for b in self.bg.buttons():
            b.setChecked(True)
        self.le_name.clear()
        self.le_name.setFocus()
        super().open()

    def okay(self):
        self.new_profile.emit(self.le_name.text().strip(), self.selected)
        self.accept()

    def do_layout(self):
        chb_lay = QVBoxLayout()
        chb_lay.setSpacing(0)
        chb_lay.setContentsMargins(0, 0, 0, 0)
        for b in self.bg.buttons():
            chb_lay.addWidget(b)

        bottom_buts = QHBoxLayout()
        bottom_buts.addStretch()
        bottom_buts.addWidget(self.pb_ok)
        bottom_buts.addWidget(self.pb_cancel)

        lay = QVBoxLayout(self)
        lay.setSpacing(lay.spacing() * 2)
        lay.addWidget(QLabel(gui_text.newprof_name_label))
        lay.addWidget(self.le_name)
        lay.addLayout(chb_lay)
        lay.addLayout(bottom_buts)


class Profiles(QWidget):
    new_profile = pyqtSignal()
    save_profile = pyqtSignal(str)
    load_profile = pyqtSignal(str)
    delete_profile = pyqtSignal(str)

    def __init__(self, *args):
        super().__init__(*args)
        self.combo = QComboBox()
        self.combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.buttons = []
        for txt in gui_text.profile_buttons:
            btn = QToolButton()
            btn.setText(txt)
            btn.clicked.connect(getattr(self, txt.lower()))
            self.buttons.append(btn)

        self.combo.currentIndexChanged.connect(self.disable_buttons)
        self.disable_buttons(self.combo.currentIndex())

        self.do_layout()

    def load(self):
        self.load_profile.emit(self.combo.currentData())

    def save(self):
        cur_prof_name: str = self.combo.currentData()

        if self.confirm(cur_prof_name, gui_text.prof_action_save):
            self.save_profile.emit(cur_prof_name)

    def new(self):
        self.new_profile.emit()

    def delete(self):
        cur_prof = self.combo.currentData()
        if self.confirm(cur_prof, gui_text.prof_action_del):
            self.delete_profile.emit(cur_prof)

    def confirm(self, profile: str, action: str):
        buts = QMessageBox.StandardButton
        conf_diag = QMessageBox(self)
        conf_diag.setStandardButtons(buts.Ok | buts.Cancel)
        conf_diag.setIcon(QMessageBox.Icon.Warning)
        conf_diag.setText(gui_text.prof_conf.format(profile=profile, action=action))
        return conf_diag.exec() == buts.Ok

    def refresh(self, profiles: dict[str, ProfileSettings]):
        if self.combo.count():
            self.combo.clear()
        for prof in sorted(profiles.values(), reverse=True):
            item_text = prof.name
            item_text += f' ({",".join(t.name[0] for t in prof.tabs)})'
            if prof.loaded:
                item_text += ' 🗸'
            self.combo.addItem(item_text, userData=prof.name)

    def disable_buttons(self, combo_idx: int):
        for i in (0, 1, 3):
            self.buttons[i].setDisabled(combo_idx == -1)

    def do_layout(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(5, 0, 0, 0)
        lay.setSpacing(3)
        lay.addWidget(QLabel(gui_text.profiles))
        lay.addWidget(self.combo)
        for b in self.buttons:
            lay.addWidget(b)
