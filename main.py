# 說明：在命令列執行這個檔案即可開啟 UI 視窗：
#   1) 先安裝依賴： pip install PyQt6
#   2) 切換到此專案目錄或以完整路徑執行
#   3) 執行： python main.py
try:
    from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QMessageBox
    from PyQt6 import uic
except Exception as e:
    # 如果 PyQt6 尚未安裝，顯示簡短安裝指令協助使用者
    print("需要 PyQt6 才能執行此程式。請先安裝：")
    print("    pip install PyQt6")
    raise

import os
import sys
import random
from PyQt6.QtWidgets import QApplication, QDialog, QPushButton, QMessageBox
from PyQt6 import uic

class UI01(QDialog):
    def __init__(self):
        super().__init__()
        # 載入與此檔案同目錄下的 project.ui，避免 working directory 問題
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'project.ui')
        if not os.path.exists(ui_path):
            QMessageBox.critical(None, "UI not found", f"找不到 UI 檔案:\n{ui_path}")
            raise FileNotFoundError(ui_path)
        uic.loadUi(ui_path, self)

        # 嘗試以多種常見名稱找到 quit 按鈕（含 project.ui 裡的 qtitButton）
        quit_names = ('quitButton', 'qtitButton', 'pushButton')
        quit_btn = None
        for name in quit_names:
            quit_btn = getattr(self, name, None)
            if quit_btn:
                break
        if quit_btn is None:
            # 若仍找不到，掃描所有 QPushButton，根據文字為 'quit'（不區分大小寫）來配對
            for child in self.findChildren(QPushButton):
                if child.text().strip().lower() == 'quit':
                    quit_btn = child
                    break
        if quit_btn:
            # use lambda to ignore clicked(bool) argument (avoids passing bool to close)
            quit_btn.clicked.connect(lambda checked=False: self.close())
        else:
            QMessageBox.warning(self, "No quit button", "找不到可用的 quit 按鈕（檔案中沒有 qtitButton/quitButton/pushButton，也沒有文字為 'quit' 的按鈕）。")

        # 連接 generate 按鈕到顯示 result.ui 的方法
        gen_btn = getattr(self, 'pushButton_2', None)
        if gen_btn:
            # wrap call so clicked's bool arg won't be passed into show_result
            gen_btn.clicked.connect(lambda checked=False: self.show_result())
        else:
            QMessageBox.warning(self, "No generate button", "找不到名為 pushButton_2 的 generate 按鈕。")

    def gather_conditions(self):
        """回傳主視窗被勾選的條件（以 checkbox 的 name 作為屬性鍵）。"""
        cond_names = ['nocoffee', 'jelly2', 'coconut', 'milk', 'jelly', 'bubble', 'fruittea', 'booba']
        selected = set()
        for name in cond_names:
            cb = getattr(self, name, None)
            if cb and getattr(cb, 'isChecked', lambda: False)():
                selected.add(name)
        return selected

    def show_result(self, required=None):
        # 載入並顯示 result.ui（以 modal dialog 顯示），並根據條件篩選結果
        result_ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'result.ui')
        if not os.path.exists(result_ui_path):
            QMessageBox.critical(self, "Result UI not found", f"找不到 result.ui:\n{result_ui_path}")
            return

        # 簡單飲料資料庫（可自行擴充）
        drinks = [
            {'name': '珍珠奶茶', 'attrs': {'bubble', 'milk'}},
            {'name': '水果茶（椰果）', 'attrs': {'fruittea', 'coconut'}},
            {'name': '粉粿鮮奶', 'attrs': {'jelly2', 'milk'}},
            {'name': '椰果茶凍', 'attrs': {'coconut', 'jelly'}},
            {'name': '波霸鮮奶', 'attrs': {'booba', 'milk'}},
            {'name': '無咖啡因水果茶', 'attrs': {'nocoffee', 'fruittea'}},
            {'name': '純茶（茶凍）', 'attrs': {'jelly'}},
        ]

        # 若未提供 required，從主視窗讀取目前 checkbox 狀態
        if required is None:
            required = self.gather_conditions()
        else:
            required = set(required)

        matches = [d for d in drinks if required.issubset(d['attrs'])]

        if matches:
            chosen = random.choice(matches)
            note = "符合所有條件"
        else:
            chosen = random.choice(drinks)
            note = "沒有完全符合的結果，已隨機挑選一項"

        dlg = QDialog(self)
        uic.loadUi(result_ui_path, dlg)

        # 若 result.ui 含有名為 quitbotton 的按鈕，連接其關閉動作
        quit_btn = getattr(dlg, 'quitbotton', None)
        if quit_btn:
            # ignore clicked(bool) arg
            quit_btn.clicked.connect(lambda checked=False: dlg.close())

        restart_btn = getattr(dlg, 'restartButton', None)
        if restart_btn:
            # clicked may pass a bool argument; accept it but ignore it, use captured 'required'
            restart_btn.clicked.connect(lambda checked, r=required: (dlg.close(), self.show_result(r)))

        # 將結果填入 result.ui（飲料名稱放到 drinklabel）
        if getattr(dlg, 'drinklabel', None):
            # 使用與 result.ui 預設相同的 HTML 格式（28pt、粗體、置中）
            dlg.drinklabel.setText(
                f"<html><head/><body>"
                f"<p align=\"center\"><span style=\" font-size:28pt; font-weight:700;\">{chosen['name']}</span></p>"
                f"</body></html>"
            )
        if getattr(dlg, 'label_2', None):
            attrs_text = ", ".join(sorted(chosen['attrs']))
            dlg.label_2.setText(f"{note}\n屬性：{attrs_text}")

        dlg.exec()

# 主程式
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI01()
    window.show()
    sys.exit(app.exec())