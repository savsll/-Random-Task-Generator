import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
from datetime import datetime
from typing import List, Dict, Any


class TaskGenerator:
    """Главный класс приложения для генерации случайных задач"""
    
    # Предустановленные задачи
    DEFAULT_TASKS = [
        {"text": "Прочитать статью по Python", "type": "учёба"},
        {"text": "Сделать утреннюю зарядку", "type": "спорт"},
        {"text": "Пробежать 2 км", "type": "спорт"},
        {"text": "Выучить 10 новых английских слов", "type": "учёба"},
        {"text": "Помыть посуду", "type": "работа"},
        {"text": "Сходить в магазин", "type": "работа"},
        {"text": "Посмотреть вебинар", "type": "учёба"},
        {"text": "Сделать 50 отжиманий", "type": "спорт"},
        {"text": "Убраться в комнате", "type": "работа"},
        {"text": "Написать пост в блог", "type": "работа"},
        {"text": "Решить 3 задачи на codewars", "type": "учёба"},
        {"text": "Помедитировать 10 минут", "type": "спорт"},
    ]
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("750x600")
        
        # Инициализация данных
        self.data_file = "data/tasks_history.json"
        self.tasks: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = []
        self.load_data()
        
        # Переменные
        self.current_task_var = tk.StringVar(value="Нажмите кнопку для генерации задачи")
        self.new_task_var = tk.StringVar()
        self.task_type_var = tk.StringVar(value="учёба")
        self.filter_type_var = tk.StringVar(value="Все")
        
        # Категории
        self.task_types = ["учёба", "спорт", "работа"]
        
        self.setup_ui()
        self.update_history_display()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.center_window()
        
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🎲 Генератор случайных задач", 
                                font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # === Левая панель (генерация) ===
        left_panel = ttk.LabelFrame(main_frame, text="Генератор", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Отображение текущей задачи
        self.task_display = tk.Text(left_panel, height=4, width=30, 
                                    font=("Arial", 12), wrap=tk.WORD,
                                    relief=tk.GROOVE, bd=2)
        self.task_display.insert(1.0, self.current_task_var.get())
        self.task_display.config(state=tk.DISABLED)
        self.task_display.grid(row=0, column=0, columnspan=2, pady=10, padx=5)
        
        # Кнопка генерации
        generate_btn = tk.Button(left_panel, text="🎲 Сгенерировать задачу 🎲",
                                 command=self.generate_task,
                                 bg="#4CAF50", fg="white",
                                 font=("Arial", 12, "bold"),
                                 padx=20, pady=10)
        generate_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # === Правая панель (добавление задач) ===
        right_panel = ttk.LabelFrame(main_frame, text="Управление задачами", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Добавление новой задачи
        ttk.Label(right_panel, text="Новая задача:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Entry(right_panel, textvariable=self.new_task_var, width=25).grid(
            row=0, column=1, padx=(5, 0), pady=5)
        
        ttk.Label(right_panel, text="Тип задачи:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        
        type_combo = ttk.Combobox(right_panel, textvariable=self.task_type_var,
                                   values=self.task_types, state="readonly", width=23)
        type_combo.grid(row=1, column=1, padx=(5, 0), pady=5)
        
        add_btn = ttk.Button(right_panel, text="➕ Добавить задачу", 
                             command=self.add_task)
        add_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Список всех задач
        ttk.Label(right_panel, text="Доступные задачи:", font=("Arial", 10, "bold")).grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Таблица задач
        columns = ("Задача", "Тип")
        self.tasks_tree = ttk.Treeview(right_panel, columns=columns, 
                                        show="headings", height=6)
        self.tasks_tree.heading("Задача", text="Задача")
        self.tasks_tree.heading("Тип", text="Тип")
        self.tasks_tree.column("Задача", width=180)
        self.tasks_tree.column("Тип", width=80)
        self.tasks_tree.grid(row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Кнопка удаления задачи
        del_btn = ttk.Button(right_panel, text="🗑 Удалить выбранную задачу",
                             command=self.delete_task)
        del_btn.grid(row=5, column=0, columnspan=2, pady=5)
        
        # === Нижняя панель (история) ===
        bottom_panel = ttk.LabelFrame(main_frame, text="История задач", padding="10")
        bottom_panel.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S),
                          pady=(10, 0))
        
        # Фильтр
        filter_frame = ttk.Frame(bottom_panel)
        filter_frame.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Фильтр по типу:").pack(side=tk.LEFT, padx=(0, 5))
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var,
                                     values=["Все", "учёба", "спорт", "работа"],
                                     state="readonly", width=15)
        filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_history_display())
        
        ttk.Button(filter_frame, text="🔄 Очистить историю", 
                   command=self.clear_history).pack(side=tk.LEFT, padx=(0, 5))
        
        # Таблица истории
        history_columns = ("Время", "Задача", "Тип")
        self.history_tree = ttk.Treeview(bottom_panel, columns=history_columns,
                                          show="headings", height=8)
        self.history_tree.heading("Время", text="Время")
        self.history_tree.heading("Задача", text="Задача")
        self.history_tree.heading("Тип", text="Тип")
        self.history_tree.column("Время", width=120)
        self.history_tree.column("Задача", width=300)
        self.history_tree.column("Тип", width=80)
        self.history_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(bottom_panel, orient=tk.VERTICAL, 
                                   command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Настройка веса
        bottom_panel.columnconfigure(0, weight=1)
        bottom_panel.rowconfigure(1, weight=1)
        
        # Загрузка задач в таблицу
        self.update_tasks_display()
        
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = 750
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def generate_task(self):
        """Генерация случайной задачи"""
        if not self.tasks:
            messagebox.showwarning("Нет задач", 
                                 "Список задач пуст. Добавьте хотя бы одну задачу!")
            return
            
        # Выбор случайной задачи
        selected_task = random.choice(self.tasks)
        
        # Обновление отображения
        self.task_display.config(state=tk.NORMAL)
        self.task_display.delete(1.0, tk.END)
        self.task_display.insert(1.0, f"✨ {selected_task['text']} ✨")
        self.task_display.config(state=tk.DISABLED)
        
        # Добавление в историю
        history_entry = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task": selected_task['text'],
            "type": selected_task['type']
        }
        self.history.append(history_entry)
        
        # Сохранение и обновление
        self.save_data()
        self.update_history_display()
        
        # Анимация (мигание)
        self.animate_task_display()
        
    def animate_task_display(self):
        """Анимация для отображения задачи"""
        def change_color(count=0):
            colors = ["#4CAF50", "#FF9800", "#2196F3"]
            if count < 6:
                self.task_display.config(bg=colors[count % 3])
                self.root.after(200, lambda: change_color(count + 1))
            else:
                self.task_display.config(bg="white")
        
        change_color()
        
    def add_task(self):
        """Добавление новой задачи"""
        task_text = self.new_task_var.get().strip()
        
        # Валидация: проверка на пустую строку
        if not task_text:
            messagebox.showwarning("Ошибка", "Введите текст задачи!")
            return
            
        # Проверка на дубликат
        for task in self.tasks:
            if task['text'].lower() == task_text.lower():
                messagebox.showwarning("Ошибка", "Такая задача уже существует!")
                return
                
        # Добавление задачи
        new_task = {
            "id": len(self.tasks) + 1,
            "text": task_text,
            "type": self.task_type_var.get()
        }
        self.tasks.append(new_task)
        
        # Очистка полей
        self.new_task_var.set("")
        
        # Сохранение и обновление
        self.save_data()
        self.update_tasks_display()
        
        messagebox.showinfo("Успех", "Задача добавлена!")
        
    def delete_task(self):
        """Удаление выбранной задачи"""
        selection = self.tasks_tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите задачу для удаления!")
            return
            
        if messagebox.askyesno("Подтверждение", "Удалить выбранную задачу?"):
            item = self.tasks_tree.item(selection[0])
            task_text = item['values'][0]
            
            # Удаление задачи
            self.tasks = [t for t in self.tasks if t['text'] != task_text]
            
            # Сохранение и обновление
            self.save_data()
            self.update_tasks_display()
            
    def update_tasks_display(self):
        """Обновление таблицы задач"""
        # Очистка таблицы
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
            
        # Заполнение таблицы
        for task in self.tasks:
            self.tasks_tree.insert("", tk.END, values=(task['text'], task['type']))
            
    def update_history_display(self):
        """Обновление истории с фильтрацией"""
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Фильтрация
        filter_type = self.filter_type_var.get()
        filtered_history = self.history
        if filter_type != "Все":
            filtered_history = [h for h in self.history if h['type'] == filter_type]
            
        # Заполнение таблицы
        for entry in reversed(filtered_history):  # Показываем последние сверху
            self.history_tree.insert("", tk.END, values=(
                entry['timestamp'],
                entry['task'],
                entry['type']
            ))
            
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", 
                               "Очистить всю историю задач? Это действие нельзя отменить!"):
            self.history = []
            self.save_data()
            self.update_history_display()
            messagebox.showinfo("Успех", "История очищена!")
            
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.history = data.get('history', [])
                    
                # Если нет задач, загружаем стандартные
                if not self.tasks:
                    self.tasks = []
                    for i, task in enumerate(self.DEFAULT_TASKS, 1):
                        self.tasks.append({"id": i, "text": task["text"], "type": task["type"]})
                        
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.init_default_data()
        else:
            self.init_default_data()
            
    def init_default_data(self):
        """Инициализация данных по умолчанию"""
        self.tasks = []
        for i, task in enumerate(self.DEFAULT_TASKS, 1):
            self.tasks.append({"id": i, "text": task["text"], "type": task["type"]})
        self.history = []
        self.save_data()
            
    def save_data(self):
        """Сохранение данных в JSON файл"""
        os.makedirs("data", exist_ok=True)
        try:
            data = {
                "tasks": self.tasks,
                "history": self.history
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGenerator(root)
    root.mainloop()