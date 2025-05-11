import flet as ft
import sqlite3
from datetime import datetime, timedelta
import os

# تنظیم پایگاه داده SQLite
def init_db():
    conn = sqlite3.connect("flashcards.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            meaning TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            word_id INTEGER,
            review_date TEXT NOT NULL,
            FOREIGN KEY (word_id) REFERENCES words(id)
        )
    """)
    conn.commit()
    conn.close()

# افزودن کلمه جدید و زمان‌بندی‌ها
def add_word(english, meaning):
    conn = sqlite3.connect("flashcards.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO words (english, meaning) VALUES (?, ?)", (english, meaning))
    word_id = cursor.lastrowid
    review_dates = [
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    ]
    for date in review_dates:
        cursor.execute("INSERT INTO reviews (word_id, review_date) VALUES (?, ?)", (word_id, date))
    conn.commit()
    conn.close()

# به‌روزرسانی زمان‌بندی در صورت عدم یادگیری
def update_review_schedule(word_id):
    conn = sqlite3.connect("flashcards.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE word_id = ?", (word_id,))
    review_dates = [
        (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
    ]
    for date in review_dates:
        cursor.execute("INSERT INTO reviews (word_id, review_date) VALUES (?, ?)", (word_id, date))
    conn.commit()
    conn.close()

# دریافت کلمات برای مرور امروز
def get_todays_words():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect("flashcards.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT w.id, w.english, w.meaning
        FROM words w
        JOIN reviews r ON w.id = r.word_id
        WHERE r.review_date = ?
    """, (today,))
    words = cursor.fetchall()
    conn.close()
    return words

# رابط کاربری با Flet
def main(page: ft.Page):
    page.title = "برنامه فلش‌کارت"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.BLUE_50
    page.fonts = {"BNazanin": "/assets/BNazanin.ttf"}
    init_db()

    # صفحه اصلی
    def show_home(e):
        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("فلش‌کارت", size=30, font_family="BNazanin", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                    ft.ElevatedButton(
                        "کلمه جدید",
                        on_click=show_add_word,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE_700,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=20
                        )
                    ),
                    ft.ElevatedButton(
                        "مرور کلمات امروز",
                        on_click=show_review,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE_700,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=20
                        )
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                alignment=ft.alignment.center
            )
        )
        page.update()

    # صفحه افزودن کلمه
    def show_add_word(e):
        english_field = ft.TextField(
            label="کلمه انگلیسی",
            text_align=ft.TextAlign.RIGHT,
            font_family="BNazanin",
            border_radius=10,
            bgcolor=ft.colors.WHITE
        )
        meaning_field = ft.TextField(
            label="معنی کلمه",
            text_align=ft.TextAlign.RIGHT,
            font_family="BNazanin",
            border_radius=10,
            bgcolor=ft.colors.WHITE
        )

        def save_word(e):
            if english_field.value and meaning_field.value:
                add_word(english_field.value, meaning_field.value)
                page.snack_bar = ft.SnackBar(
                    ft.Text("کلمه ذخیره شد!", font_family="BNazanin", text_align=ft.TextAlign.RIGHT),
                    bgcolor=ft.colors.GREEN_600
                )
                page.snack_bar.open = True
                show_home(None)
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text("لطفاً هر دو فیلد را پر کنید", font_family="BNazanin", text_align=ft.TextAlign.RIGHT),
                    bgcolor=ft.colors.RED_600
                )
                page.snack_bar.open = True
            page.update()

        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("افزودن کلمه جدید", size=24, font_family="BNazanin", color=ft.colors.BLUE_900),
                    english_field,
                    meaning_field,
                    ft.ElevatedButton(
                        "ذخیره کلمه",
                        on_click=save_word,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE_700,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=20
                        )
                    ),
                    ft.ElevatedButton(
                        "بازگشت",
                        on_click=show_home,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.GREY_400,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=20
                        )
                    ),
                ], spacing=20),
                padding=20,
                alignment=ft.alignment.center
            )
        )
        page.update()

    # صفحه مرور کلمات
    def show_review(e):
        words = get_todays_words()
        if not words:
            page.controls.clear()
            page.add(
                ft.Container(
                    content=ft.Column([
                        ft.Text("کلمات امروز مرور شده‌اند!", font_family="BNazanin", size=20, color=ft.colors.GREEN_700),
                        ft.ElevatedButton(
                            "بازگشت",
                            on_click=show_home,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_700,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=20
                            )
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
            page.update()
            return

        current_word_index = [0]

        def show_meaning(e):
            meaning_container.content = ft.Text(
                words[current_word_index[0]][2],
                font_family="BNazanin",
                size=20,
                color=ft.colors.BLUE_900,
                text_align=ft.TextAlign.RIGHT
            )
            meaning_container.visible = True
            page.update()

        def mark_known(e):
            if current_word_index[0] < len(words) - 1:
                current_word_index[0] += 1
                update_word_display()
            else:
                page.controls.clear()
                page.add(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("کلمات امروز مرور شده‌اند!", font_family="BNazanin", size=20, color=ft.colors.GREEN_700),
                            ft.ElevatedButton(
                                "بازگشت",
                                on_click=show_home,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.BLUE_700,
                                    color=ft.colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    padding=20
                                )
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=20,
                        alignment=ft.alignment.center
                    )
                )
            page.update()

        def mark_unknown(e):
            update_review_schedule(words[current_word_index[0]][0])
            if current_word_index[0] < len(words) - 1:
                current_word_index[0] += 1
                update_word_display()
            else:
                page.controls.clear()
                page.add(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("کلمات امروز مرور شده‌اند!", font_family="BNazanin", size=20, color=ft.colors.GREEN_700),
                            ft.ElevatedButton(
                                "بازگشت",
                                on_click=show_home,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.BLUE_700,
                                    color=ft.colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    padding=20
                                )
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=20,
                        alignment=ft.alignment.center
                    )
                )
            page.update()

        def update_word_display():
            word_text.value = words[current_word_index[0]][1]
            meaning_container.content = None
            meaning_container.visible = False
            page.update()

        word_text = ft.Text(words[current_word_index[0]][1], size=28, font_family="BNazanin", color=ft.colors.BLUE_900)
        meaning_container = ft.Container(content=None, visible=False, padding=10, bgcolor=ft.colors.BLUE_100, border_radius=10)

        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("مرور کلمات امروز", size=24, font_family="BNazanin", color=ft.colors.BLUE_900),
                    ft.Container(
                        content=word_text,
                        padding=20,
                        bgcolor=ft.colors.WHITE,
                        border_radius=10,
                        alignment=ft.alignment.center
                    ),
                    meaning_container,
                    ft.ElevatedButton(
                        "نمایش معنی",
                        on_click=show_meaning,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE_700,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=20
                        )
                    ),
                    ft.Row([
                        ft.ElevatedButton(
                            "بلد بودم",
                            on_click=mark_known,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN_600,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=20
                            )
                        ),
                        ft.ElevatedButton(
                            "بلد نبودم",
                            on_click=mark_unknown,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.RED_600,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=20
                            )
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.ElevatedButton(
                        "بازگشت",
                        on_click=show_home,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.GREY_400,
                            color=ft.colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=20
                        )
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                padding=20,
                alignment=ft.alignment.center
            )
        )
        page.update()

    show_home(None)

ft.app(target=main, assets_dir="assets")