# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import re
import string
import os

class CSVMarkupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Инструмент разметки CSV")
        self.root.geometry("500x150") 

        self.file_path = None
        self.df = None
        self.labeled_df = None

        #Определения ключевых слов #
        self.keywords = {
            "Нравится скорость отработки заявок": {
                "positive": ["быстро", "оперативно", "скорость", "быстрый", "моментально", "сразу", "оперативный", "быстрая", "быстром", "быструю"],
                "negative": ["долго", "медленно", "затянуто", "неделю", "месяц", "задержка", "ожидание", "медленный", "долгий", "долгая", "долгом", "долгую"]
            },
            "Нравится качество выполнения заявки": {
                "positive": ["качественно", "отлично", "хорошо", "супер", "идеально", "профессионально", "грамотно", "четко", "полностью", "успешно", "решили", "помогли", "доволен", "довольна", "спасибо", "благодарю", "решена", "решен", "выполнено", "выполнена"],
                "negative": ["плохо", "ужасно", "некачественно", "отвратительно", "не решили", "не помогли", "проблема осталась", "не выполнили", "не работает", "не работает", "отказ", "недоволен", "недовольна", "некорректно"]
            },
            "Нравится качество работы сотрудников": {
                "positive": ["вежливый", "компетентный", "профессионал", "грамотный", "отзывчивый", "внимательный", "помог", "помогла", "объяснил", "объяснила", "приятный", "хороший сотрудник", "специалист", "мастер", "консультант"],
                "negative": ["грубый", "некомпетентный", "хамство", "невежливый", "неграмотный", "невнимательный", "не помог", "не объяснил", "плохой сотрудник", "не специалист"]
            },
            "Понравилось выполнение заявки": { # Общие позитивные/негативные
                "positive": ["понравилось", "доволен", "довольна", "отлично", "хорошо", "супер", "спасибо", "благодарю", "успешно", "решили", "помогли", "решена", "решен", "выполнено", "выполнена"],
                "negative": ["не понравилось", "недоволен", "недовольна", "плохо", "ужасно", "не решили", "не помогли", "проблема осталась", "не выполнили"]
            },
            "Вопрос решен": {
                "positive": ["решен", "решена", "решили", "устранили", "исправили", "починили", "заработало", "выполнено", "выполнена", "помогло", "помогли"],
                "negative": ["не решен", "не решена", "не решили", "не устранили", "не исправили", "не починили", "не заработало", "не выполнено", "не помогло", "проблема осталась"]
            }
        }
        self.target_columns = list(self.keywords.keys())

        #Элементы интерфейса
        # Верхний фрейм для операций с файлами
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X, pady=5)

        self.load_button = ttk.Button(top_frame, text="Загрузить CSV", command=self.load_csv)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.file_label = ttk.Label(top_frame, text="Файл не загружен.")
        self.file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Фрейм для элементов управления разметкой
        markup_frame = ttk.Frame(self.root, padding="10")
        markup_frame.pack(fill=tk.X, pady=5)

        self.markup_button = ttk.Button(markup_frame, text="Начать разметку", command=self.start_markup, state=tk.DISABLED)
        self.markup_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(markup_frame, text="Сохранить CSV", command=self.save_labeled_csv, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Строка состояния
        self.status_bar = ttk.Label(self.root, text="Готово", relief=tk.SUNKEN, anchor=tk.W, padding="2")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))
        self.default_status_color = self.status_bar.cget("foreground")

    # Обновление строки состояния
    def _update_status(self, message, color=None):
        self.status_bar.config(text=message)
        if color:
            self.status_bar.config(foreground=color)
        else:
            self.status_bar.config(foreground=self.default_status_color)
        self.root.update_idletasks()

    # Загрузка CSV файла
    def load_csv(self):
        self.file_label.config(text="Файл не загружен.")
        self.markup_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.df = None
        self.labeled_df = None
        self.file_path = None
        self._update_status("Готово") 

        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл для разметки",
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
        )
        if not file_path:
            self._update_status("Загрузка файла отменена.")
            return

        try:
            self.df = pd.read_csv(file_path)
            self.file_path = file_path
            self.file_label.config(text=f"Загружен: {os.path.basename(file_path)}")
            self._update_status(f"Файл {os.path.basename(file_path)} успешно загружен. Строк: {len(self.df)}.")
            
            if not self.df.empty and 'comment' in self.df.columns:
                self.markup_button.config(state=tk.NORMAL)
            elif self.df.empty:
                messagebox.showwarning("Пустой файл", "Выбранный CSV файл пуст.")
                self._update_status("Загруженный CSV файл пуст.")
            else: # Отсутствует колонка 'comment'
                messagebox.showwarning("Отсутствует колонка", "В CSV файле должна быть колонка 'comment' для разметки.")
                self._update_status("В CSV отсутствует колонка 'comment'.")

        except Exception as e:
            messagebox.showerror("Ошибка загрузки файла", f"Не удалось загрузить или прочитать CSV файл.\nОшибка: {e}")
            self._update_status("Ошибка загрузки файла.")
            self.file_label.config(text="Ошибка загрузки файла.")
            self.df = None
            self.file_path = None

    # Предобработка текста для разметки
    def preprocess_text_for_markup(self, text):
        text = str(text).lower()
        text = re.sub(f"[{re.escape(string.punctuation)}«»„\"…–—]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # Получение метки на основе ключевых слов
    def get_label(self, comment_processed, positive_keywords, negative_keywords):
        has_positive = any(keyword in comment_processed for keyword in positive_keywords)
        has_negative = any(keyword in comment_processed for keyword in negative_keywords)
        
        if has_positive and not has_negative:
            return 1
        elif not has_positive and has_negative:
            return 0
        return 0 

    # Начало процесса разметки
    def start_markup(self):
        if self.df is None or 'comment' not in self.df.columns:
            messagebox.showwarning("Нет данных или отсутствует колонка", "Пожалуйста, загрузите CSV файл с колонкой 'comment'.")
            return

        self._update_status("Идет процесс разметки...")

        self.labeled_df = self.df.copy()

        for category, criteria in self.keywords.items():
            positive_kws = criteria.get("positive", [])
            negative_kws = criteria.get("negative", [])
            
            self.labeled_df[category] = self.labeled_df['comment'].apply(
                lambda x: self.get_label(
                    self.preprocess_text_for_markup(x),
                    positive_kws,
                    negative_kws
                )
            )
        
        # Добавление колонки 'Без категории'
        self.labeled_df['Без категории'] = self.labeled_df[self.target_columns].sum(axis=1).apply(lambda x: 1 if x == 0 else 0)
        
        self._update_status("Разметка завершена. Готово к сохранению.")
        self.save_button.config(state=tk.NORMAL)
        messagebox.showinfo("Разметка завершена", "Данные были размечены, включая колонку 'Без категории'.")

    # Сохранение размеченного CSV
    def save_labeled_csv(self):
        if self.labeled_df is None:
            messagebox.showwarning("Нет размеченных данных", "Пожалуйста, сначала выполните разметку.")
            return

        default_filename = f"размеченный_{os.path.basename(self.file_path) if self.file_path else 'данные.csv'}"
        save_path = filedialog.asksaveasfilename(
            title="Сохранить размеченный CSV файл",
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv")],
            initialfile=default_filename
        )

        if not save_path:
            self._update_status("Операция сохранения отменена.")
            return

        try:
            self.labeled_df.to_csv(save_path, index=False, encoding='utf-8-sig')
            messagebox.showinfo("Сохранение успешно", f"Размеченные данные сохранены в: {save_path}")
            self._update_status(f"Файл сохранён: {os.path.basename(save_path)}", "green")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения файла", f"Не удалось сохранить размеченный CSV файл.\nОшибка: {e}")
            self._update_status("Ошибка сохранения файла.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVMarkupApp(root)
    root.mainloop()

