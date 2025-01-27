import pandas as pd
from faker import Faker
import random

fake = Faker()

def generate_fake_data(num_entries=10):
    data = []

    for _ in range(num_entries):
        entry = {
            "Name": fake.name(),
            "Address": fake.address(),
            "Email": fake.email(),
            "Phone Number": fake.phone_number(),
            "Date of Birth": fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%Y-%m-%d"),
            "Random Number": random.randint(1, 100),
            "Job Title": fake.job(),
            "Company": fake.company(),
            "Lorem Ipsum Text": fake.text(),
        }
        data.append(entry)

    return pd.DataFrame(data)

if __name__ == "__main__":
    num_entries = 10  # You can adjust the number of entries you want to generate
    fake_data_df = generate_fake_data(num_entries)

    # Mostrar todas las columnas y ajustar el ancho máximo
    pd.set_option("display.max_columns", None)  # Muestra todas las columnas
    pd.set_option("display.width", 1000)       # Ajusta el ancho máximo para evitar saltos de línea

    print(fake_data_df)