import json
import os
import subprocess

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class GamesEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.json_path = "g.json"

        with open(self.json_path, "r", encoding="utf8") as f:
            self.games = json.load(f)

        self.setWindowTitle("Games JSON Editor")
        self.resize(1000, 600)

        layout = QHBoxLayout(self)

        self.listbox = QListWidget()
        self.listbox.currentRowChanged.connect(self.load_game)
        layout.addWidget(self.listbox, 1)

        right = QVBoxLayout()

        self.name = QLineEdit()
        self.gid = QLineEdit()
        self.flash = QCheckBox("Flash")
        self.url = QLineEdit()

        self.img = QLineEdit()
        browse = QPushButton("Browse")
        browse.clicked.connect(self.pick_image)

        imgrow = QHBoxLayout()
        imgrow.addWidget(self.img)
        imgrow.addWidget(browse)

        self.preview = QLabel()
        self.preview.setFixedSize(200, 200)
        self.preview.setAlignment(Qt.AlignCenter)

        right.addWidget(QLabel("Name"))
        right.addWidget(self.name)

        right.addWidget(QLabel("ID"))
        right.addWidget(self.gid)

        right.addWidget(self.flash)

        right.addWidget(QLabel("Image"))
        right.addLayout(imgrow)

        right.addWidget(QLabel("URL"))
        right.addWidget(self.url)

        right.addWidget(self.preview)

        save = QPushButton("Save JSON")
        save.clicked.connect(self.save)

        push = QPushButton("Save + Push")
        push.clicked.connect(self.save_and_push)

        add = QPushButton("Add Game")
        add.clicked.connect(self.add_game)

        delete = QPushButton("Delete Game")
        delete.clicked.connect(self.delete_game)

        right.addWidget(add)
        right.addWidget(delete)
        right.addWidget(save)
        right.addWidget(push)

        layout.addLayout(right, 2)

        self.refresh_list()

    def refresh_list(self):
        self.listbox.clear()

        for game in self.games:
            self.listbox.addItem(game["name"])

    def load_game(self, i):
        if i < 0:
            return

        g = self.games[i]

        self.name.setText(g.get("name", ""))
        self.gid.setText(g.get("id", ""))
        self.flash.setChecked(g.get("flash", False))
        self.img.setText(g.get("img", ""))
        self.url.setText(g.get("url", ""))

        path = g.get("img", "")

        if os.path.exists(path):
            pix = QPixmap(path)
            self.preview.setPixmap(
                pix.scaled(
                    200,
                    200,
                    Qt.KeepAspectRatio
                )
            )
        else:
            self.preview.clear()

    def save_current(self):
        i = self.listbox.currentRow()

        if i < 0:
            return

        g = self.games[i]

        g["name"] = self.name.text()
        g["id"] = self.gid.text()
        g["flash"] = self.flash.isChecked()
        g["img"] = self.img.text()

        if self.url.text():
            g["url"] = self.url.text()
        elif "url" in g:
            del g["url"]

        self.refresh_list()

    def save(self):
        self.save_current()

        with open(self.json_path, "w", encoding="utf8") as f:
            json.dump(
                self.games,
                f,
                indent=2,
                ensure_ascii=False
            )

        QMessageBox.information(self, "Saved", "JSON saved.")

    def save_and_push(self):
        self.save()

        subprocess.run(["git", "add", self.json_path])
        subprocess.run([
            "git",
            "commit",
            "-m",
            "Update games list"
        ])
        subprocess.run(["git", "push"])

        QMessageBox.information(
            self,
            "Git",
            "Changes pushed."
        )

    def add_game(self):
        self.games.append({
            "name": "New Game",
            "id": "",
            "flash": False,
            "img": ""
        })

        self.refresh_list()
        self.listbox.setCurrentRow(len(self.games) - 1)

    def delete_game(self):
        i = self.listbox.currentRow()

        if i >= 0:
            del self.games[i]

        self.refresh_list()

    def pick_image(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Select image"
        )

        if file:
            self.img.setText(file)


app = QApplication([])

w = GamesEditor()
w.show()

app.exec_()
