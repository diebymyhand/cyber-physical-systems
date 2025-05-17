import customtkinter as ctk
from db import *

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()

        ctk.set_appearance_mode("dark")
        self.geometry("900x500")
        self.title("Облік лічильників")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        buttons_frame = ctk.CTkFrame(self)

        main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        buttons_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.textbox = ctk.CTkTextbox(main_frame, font=("Arial", 12))
        self.textbox.pack(expand=True, fill="both", padx=10, pady=10)

        buttons = [
            ("Додати/Оновити", self.add_meter_window),
            ("Історія", self.show_history),
            ("Налаштування", self.settings_window),
        ]

        for label, command in buttons:
            button = ctk.CTkButton(master=buttons_frame, text=label, command=command, width=180, height=40)
            button.pack(pady=10)

    def add_meter_window(self):
        AddMeterWindow(self, self.db, self.textbox)

    def show_history(self):
        self.textbox.delete("1.0", "end")  # очистити поле
        history = self.db.get_history()

        if not history:
            self.textbox.insert("end", "Історія порожня.\n")
            return

        for row in history:
            var, meter_id, date, day_tariff, night_tariff, used_day, used_night, bill = row
            self.textbox.insert("end", f"""--- Запис ---
                                ID лічильника: {meter_id}
                                Дата: {date}
                                Показник день: {day_tariff} грн/кВт-год
                                Показник ніч: {night_tariff} грн/кВт-год
                                Спожито день: {used_day} кВт
                                Спожито ніч: {used_night} кВт
                                Сума до сплати: {bill:.2f} грн
                                ------------------
                                """)

    def settings_window(self):
        AppSettingsWindow(self)

class AddMeterWindow(ctk.CTkToplevel):
    def __init__(self, parent, db, textbox):
        super().__init__(parent)

        self.geometry("400x250")
        self.title("Додати лічильник")

        self.db = db
        self.textbox = textbox

        self.meter_id_entry = ctk.CTkEntry(self, placeholder_text="ID лічильника")
        self.day_entry = ctk.CTkEntry(self, placeholder_text="День (кВт)")
        self.night_entry = ctk.CTkEntry(self, placeholder_text="Ніч (кВт)")
        self.date_entry = ctk.CTkEntry(self, placeholder_text="Дата (YYYY-MM-DD)")

        self.meter_id_entry.pack(pady=10)
        self.day_entry.pack(pady=10)
        self.night_entry.pack(pady=10)
        self.date_entry.pack(pady=10)

        ctk.CTkButton(self, text="Зберегти", command=self.save_and_calculate_meter).pack(pady=10)

    def save_and_calculate_meter(self):
        tariffs = self.db.get_tariffs()
        tariffs_dict = {
            "DAY_TARIFF": tariffs[0],
            "NIGHT_TARIFF": tariffs[1],
            "MARKUP_KW_DAY": tariffs[2],
            "MARKUP_KW_NIGHT": tariffs[3]
        }

        meter_id = self.meter_id_entry.get()
        day_usage = float(self.day_entry.get())
        night_usage = float(self.night_entry.get())
        date = self.date_entry.get()

        old_meter_id = self.db.get_last_meter_id()
        if old_meter_id is None or old_meter_id < 1:
            self.db.save_meter(meter_id, day_usage, night_usage, date)
            self.textbox.insert("end", "❗ Недостатньо даних для розрахунку квитанції.\n")
            return

        if old_meter_id == 1:
            self.textbox.insert("end", "📄 Квитанція не розраховується, оскільки це перший лічильник.\n")
            self.db.save_meter(meter_id, day_usage, night_usage, date)
            self.destroy()
            return

        self.db.save_meter(meter_id, day_usage, night_usage, date)

        old_data = self.db.get_meter(old_meter_id)
        new_data = self.db.get_meter(meter_id)
        if not old_data or not new_data:
            self.textbox.insert("end", "❗ Немає необхідних показників для розрахунку.\n")
            return

        old_day, old_night = old_data[1], old_data[2]

        used_day = day_usage - old_day
        used_night = night_usage - old_night

        if used_day < 0:
            used_day = tariffs_dict["MARKUP_KW_DAY"]
            self.textbox.insert("end",
                                f"❗ Показник для дня занижений. Накрутка: {tariffs_dict['MARKUP_KW_DAY']} кВт.\n")
        if used_night < 0:
            used_night = tariffs_dict["MARKUP_KW_NIGHT"]
            self.textbox.insert("end",
                                f"❗ Показник для ночі занижений. Накрутка: {tariffs_dict['MARKUP_KW_NIGHT']} кВт.\n")

        bill = used_day * tariffs_dict["DAY_TARIFF"] + used_night * tariffs_dict["NIGHT_TARIFF"]
        bill = round(bill, 2)

        self.db.add_history(meter_id, date, tariffs_dict["DAY_TARIFF"], tariffs_dict["NIGHT_TARIFF"] ,used_day, used_night, bill)

        result = f"""📄 Квитанція
                    ------------------------
                    День: {used_day} кВт
                    Ніч: {used_night} кВт
                    Сума до оплати: {bill} грн
                    ------------------------\n"""

        self.textbox.insert("end", result)

        self.destroy()

class AppSettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.geometry("250x400")
        self.title("Налаштування тарифів")

        self.entries = {}
        self.labels = ["День (кВт)", "Ніч (кВт)", "Накрутка день (кВт)", "Накрутка ніч (кВт)"]
        self.fields = ["day_rate", "night_rate", "fake_day", "fake_night"]

        for label, field in zip(self.labels, self.fields):
            ctk.CTkLabel(self, text=label).pack(pady=2)
            entry = ctk.CTkEntry(self, placeholder_text=label)
            entry.pack(pady=2)
            self.entries[field] = entry

        ctk.CTkButton(self, text="Зберегти", command=self.save_tariffs).pack(pady=10)

        tariffs = self.parent.db.get_tariffs()
        if tariffs:
            self.entries["day_rate"].insert(0, str(tariffs[0]))
            self.entries["night_rate"].insert(0, str(tariffs[1]))
            self.entries["fake_day"].insert(0, str(tariffs[2]))
            self.entries["fake_night"].insert(0, str(tariffs[3]))

    def save_tariffs(self):
        try:
            day_rate = float(self.entries["day_rate"].get())
            night_rate = float(self.entries["night_rate"].get())
            fake_day = int(self.entries["fake_day"].get())
            fake_night = int(self.entries["fake_night"].get())

            self.parent.db.update_tariffs(day_rate, night_rate, fake_day, fake_night)
            self.destroy()

            ctk.CTkLabel(self, text="Тарифи успішно збережені!", text_color="green").pack(pady=10)
        except ValueError:
            ctk.CTkLabel(self, text="Помилка! Невірний формат даних.", text_color="red").pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()