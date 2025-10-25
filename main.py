import utils

police_shootings_data_url = 'https://uploads.kodilla.com/bootcamp/pro-data-visualization/files/fatal-police-shootings-data.csv'


def main():
    # 1. Pobranie pliku CSV i utworzenie DataFrame
    df = utils.create_dataframe_from_csv(police_shootings_data_url)

    # 2. Zestawienie  liczby ofiar wg rasy i oznak choroby psychicznej
    pivot_table = df.pivot_table(
        index='race', columns='signs_of_mental_illness', aggfunc='size')

    # 3. Obliczenie procentu ofiar z oznakami choroby psychicznej w każdej grupie rasowej
    pivot_table = utils.calculate_mental_illness_percentage(pivot_table)

    # Wyświetlenie rasy z najwyższym procentem ofiar z oznakami choroby psychicznej
    print(
        f"Najwyższy procent ofiar z oznakami choroby psychicznej: {utils.get_top_mental_illness_races(pivot_table)}")

    # 4. Dodanie kolumny z dniem tygodnia do oryginalnego DataFrame
    df = utils.create_day_of_week_column(df)

    # Zestawienie liczby interwencji policji w poszczególne dni tygodnia
    intervention_by_day = utils.get_intervention_by_day_of_week(df)
    intervention_by_day = utils.translate_and_sort_days_of_week(
        intervention_by_day)

    # Tworzenie wykresu słupkowego
    utils.plot_intervention_by_day_of_week(intervention_by_day)


if __name__ == "__main__":
    main()
