import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
from calendar import day_name


def get_csv_file_name_from_url(url):
    return url.split("/")[-1]


def download_csv_file(url):
    csv_file = get_csv_file_name_from_url(url)
    if not os.path.exists(csv_file):
        response = requests.get(url)
        if response.status_code == 200:
            with open(csv_file, "wb") as file:
                file.write(response.content)
            print("CSV file downloaded successfully.")
        else:
            print("Failed to download CSV file.")
    else:
        print("CSV file already exists.")


def create_dataframe_from_csv(url):
    csv_file = get_csv_file_name_from_url(url)
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        return df
    else:
        download_csv_file(url)
        return create_dataframe_from_csv(url)


def calculate_mental_illness_percentage(row):
    total = row.sum()
    if total == 0:
        return 0  # Zapobieganie dzieleniu przez zero
    # sprawdzenie czy kolumna True istnieje
    return (row[True] / total) * 100 if True in row else 0


def get_top_mental_illness_races(df):
    top_mental_illness = df['signs_of_mental_illness_percentage'].idxmax()
    return top_mental_illness


def create_day_of_week_column(df):
    df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()
    return df


def get_intervention_by_day_of_week(df):
    intervention_counts = df['day_of_week'].value_counts()
    return intervention_counts


def translate_and_sort_days_of_week(series):
    days_order = list(day_name)
    series = series.reindex(days_order)
    series.rename({
        'Monday': 'Poniedziałek',
        'Tuesday': 'Wtorek',
        'Wednesday': 'Środa',
        'Thursday': 'Czwartek',
        'Friday': 'Piątek',
        'Saturday': 'Sobota',
        'Sunday': 'Niedziela'
    }, inplace=True)
    return series


def plot_intervention_by_day_of_week(intervention_by_day):
    intervention_by_day.plot(kind='bar', figsize=(10, 6))
    plt.title('Liczba interwencji policji w poszczególne dni tygodnia')
    plt.xlabel('Dzień tygodnia')
    plt.ylabel('Liczba interwencji')
    plt.xticks(rotation=45)
    plt.tight_layout()
    for index, value in enumerate(intervention_by_day):
        plt.text(index, value, str(value), ha='center', va='bottom')
    plt.show()


def create_dataframe_from_html(url, table_index=0):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(response.text, header=0)
        if tables:
            return tables[table_index]
        else:
            print("No tables found at the provided URL.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None


def map_state_codes(df, states_codes_df):
    states_codes_df.drop_duplicates(subset=['USPS (& ANSI)'], inplace=True)
    df['state'] = df['state'].map(
        states_codes_df.set_index('USPS (& ANSI)')['Name'])
    return df


def map_state_population(df, states_population_df):
    states_population_df.drop_duplicates(subset=['State'], inplace=True)
    df['population 2010'] = df['state'].map(
        states_population_df.set_index('State')['Census population, April 1, 2010 [1][2]'])
    df['population 2020'] = df['state'].map(
        states_population_df.set_index('State')['Census population, April 1, 2020 [1][2]'])
    return df


def convert_date_to_year_only(df):
    df['date'] = pd.to_datetime(df['date']).dt.year
    df.rename(columns={'date': 'year'}, inplace=True)
    return df
