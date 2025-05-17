import tkinter as tk
from tkinter import messagebox, scrolledtext
import re
import string
import joblib
import os
import numpy as np

class CommentClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Классификатор комментариев")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Настройка стилей
        self.root.configure(bg="#f0f0f0")
        self.font_header = ("Arial", 14, "bold")
        self.font_normal = ("Arial", 11)
        self.font_result = ("Arial", 12)
        
        # Загрузка моделей
        self.load_models()
        
        # Создание интерфейса
        self.create_widgets()
    
    def load_models(self):
        try:
            # Пути к моделям
            vectorizer_path = "tfidf_vectorizer_final_v5_target.joblib"
            model_path = "nlp_model_final_v5_target.joblib"
            
            # Проверка наличия файлов
            if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
                # Если файлы не найдены в текущей директории
                upload_dir = r"C:\Users\b1gtz\Desktop\IT Projects\Python\Intensive 4"
                vectorizer_path = os.path.join(upload_dir, "tfidf_vectorizer_final_v5_target.joblib")
                model_path = os.path.join(upload_dir, "nlp_model_final_v5_target.joblib")
            
            # Загрузка моделей
            self.vectorizer = joblib.load(vectorizer_path)
            self.model = joblib.load(model_path)
            
            # Определение категорий
            self.categories = [
                'Нравится скорость отработки заявок',
                'Нравится качество выполнения заявки',
                'Нравится качество работы сотрудников',
                'Понравилось выполнение заявки',
                'Вопрос решен',
                'Без категории'
            ]
            
            # Упрощенные названия категорий для отображения
            self.display_categories = [
                'Скорость',
                'Качество выполнения',
                'Сотрудники',
                'Выполнение заявки',
                'Вопрос решен',
                'Без категории'
            ]
            
            print("Модели успешно загружены")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки моделей", f"Не удалось загрузить модели: {str(e)}")
            print(f"Ошибка загрузки моделей: {str(e)}")
    
    def create_widgets(self):
        # Заголовок
        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        header_label = tk.Label(
            header_frame, 
            text="Классификатор комментариев", 
            font=self.font_header,
            bg="#f0f0f0"
        )
        header_label.pack()
        
        # Инструкция
        instruction_label = tk.Label(
            header_frame,
            text="Введите комментарий для классификации:",
            font=self.font_normal,
            bg="#f0f0f0",
            anchor="w"
        )
        instruction_label.pack(fill=tk.X, pady=(10, 5))
        
        # Поле ввода комментария
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        self.comment_input = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            font=self.font_normal,
            height=5
        )
        self.comment_input.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка классификации
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        classify_button = tk.Button(
            button_frame,
            text="Классифицировать",
            command=self.classify_comment,
            font=self.font_normal,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5
        )
        classify_button.pack()
        
        # Результаты классификации
        result_frame = tk.Frame(self.root, bg="#f0f0f0")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        result_label = tk.Label(
            result_frame,
            text="Результаты классификации:",
            font=self.font_normal,
            bg="#f0f0f0",
            anchor="w"
        )
        result_label.pack(fill=tk.X)
        
        # Фрейм для отображения результатов по категориям
        self.categories_frame = tk.Frame(result_frame, bg="#f0f0f0")
        self.categories_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Создаем метки и прогресс-бары для каждой категории
        self.category_labels = []
        self.progress_bars = []
        self.percentage_labels = []
        
        for i, category in enumerate(self.display_categories):
            # Фрейм для категории
            category_frame = tk.Frame(self.categories_frame, bg="#f0f0f0")
            category_frame.pack(fill=tk.X, pady=2)
            
            # Метка категории
            category_label = tk.Label(
                category_frame,
                text=f"{category}:",
                font=self.font_normal,
                width=20,
                anchor="w",
                bg="#f0f0f0"
            )
            category_label.pack(side=tk.LEFT)
            
            # Прогресс-бар
            progress_bar = tk.Canvas(
                category_frame,
                height=20,
                bg="white",
                highlightthickness=1,
                highlightbackground="#ddd"
            )
            progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            
            # Метка процента
            percentage_label = tk.Label(
                category_frame,
                text="0%",
                font=self.font_normal,
                width=5,
                bg="#f0f0f0"
            )
            percentage_label.pack(side=tk.RIGHT)
            
            self.category_labels.append(category_label)
            self.progress_bars.append(progress_bar)
            self.percentage_labels.append(percentage_label)
    
    def preprocess_text(self, text):
        """Предобработка текста перед классификацией"""
        text = str(text).lower()
        text = re.sub(f'[{re.escape(string.punctuation)}«»„\"…–—]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def classify_comment(self):
        """Классификация введенного комментария"""
        # Получаем текст комментария
        comment = self.comment_input.get("1.0", tk.END).strip()
        
        if not comment:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите комментарий для классификации.")
            return
        
        try:
            # Предобработка текста
            processed_comment = self.preprocess_text(comment)
            
            # Векторизация текста
            comment_vector = self.vectorizer.transform([processed_comment])
            
            # Получение предсказаний
            predictions = self.model.predict(comment_vector)[0]
            
            # Проверка, относится ли комментарий к какой-либо категории
            if not any(predictions):
                messagebox.showinfo("Результат", "Данный текст не может отнестись к какой-либо категории")
                # Очищаем прогресс-бары
                self.update_progress_bars([0] * len(self.categories))
                return
            
            # Получение вероятностей для каждой категории
            # Для MultiOutputClassifier нужно обрабатывать каждый классификатор отдельно
            probabilities = []
            
            # Проверяем тип модели и соответствующим образом получаем вероятности
            if hasattr(self.model, 'estimators_'):  # MultiOutputClassifier
                for i, estimator in enumerate(self.model.estimators_):
                    if hasattr(estimator, 'predict_proba'):
                        # Получаем вероятность положительного класса (класс 1)
                        prob = estimator.predict_proba(comment_vector)[0][1]
                        probabilities.append(prob)
                    else:
                        # Если классификатор не поддерживает predict_proba, используем бинарное предсказание
                        probabilities.append(float(predictions[i]))
            else:
                # Для обычных классификаторов
                proba_matrix = self.model.predict_proba(comment_vector)
                for i in range(len(self.categories)):
                    if i < len(proba_matrix):
                        # Берем вероятность положительного класса
                        probabilities.append(proba_matrix[i][0][1])
                    else:
                        probabilities.append(0.0)
            
            # Обновляем прогресс-бары с вероятностями
            self.update_progress_bars(probabilities)
            
            # Находим категорию с наибольшей вероятностью
            max_prob_index = np.argmax(probabilities)
            max_category = self.display_categories[max_prob_index]
            max_prob = probabilities[max_prob_index]
            
            # Выделяем категорию с наибольшей вероятностью
            for i, label in enumerate(self.category_labels):
                if i == max_prob_index:
                    label.config(font=("Arial", 11, "bold"), fg="#4CAF50")
                else:
                    label.config(font=("Arial", 11), fg="black")
            
        except Exception as e:
            messagebox.showerror("Ошибка классификации", f"Произошла ошибка при классификации: {str(e)}")
            print(f"Ошибка классификации: {str(e)}")
    
    def update_progress_bars(self, probabilities):
        """Обновление прогресс-баров с вероятностями"""
        for i, (progress_bar, percentage_label) in enumerate(zip(self.progress_bars, self.percentage_labels)):
            # Получаем вероятность для текущей категории
            prob = probabilities[i] if i < len(probabilities) else 0
            
            # Обновляем прогресс-бар
            progress_bar.delete("all")
            width = progress_bar.winfo_width()
            if width > 0:  # Проверка, что ширина больше 0
                fill_width = int(width * prob)
                progress_bar.create_rectangle(
                    0, 0, fill_width, 20, 
                    fill="#4CAF50" if prob > 0.5 else "#90EE90", 
                    outline=""
                )
            
            # Обновляем метку процента
            percentage_label.config(text=f"{int(prob * 100)}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = CommentClassifierApp(root)
    root.mainloop()
