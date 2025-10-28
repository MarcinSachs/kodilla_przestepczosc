import utils

police_shootings_data_url = 'https://uploads.kodilla.com/bootcamp/pro-data-visualization/files/fatal-police-shootings-data.csv'
states_population_url = 'https://simple.wikipedia.org/wiki/List_of_U.S._states_by_population'
states_codes_url = 'https://en.wikipedia.org/wiki/List_of_U.S._state_abbreviations'


def main():
    # 1. Pobranie pliku CSV i utworzenie DataFrame
    df = utils.create_dataframe_from_csv(police_shootings_data_url)

    # 2. Zestawienie  liczby ofiar wg rasy i oznak choroby psychicznej
    pivot_table = df.pivot_table(
        index='race', columns='signs_of_mental_illness', aggfunc='size')

    # 3. Obliczenie procentu ofiar z oznakami choroby psychicznej w każdej grupie rasowej
    pivot_table['signs_of_mental_illness_percentage'] = pivot_table.apply(
        utils.calculate_mental_illness_percentage, axis=1)

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

    # Pobranie tabel z kodami stanów i populacją
    states_population_df = utils.create_dataframe_from_html(
        states_population_url, 0)
    states_codes_df = utils.create_dataframe_from_html(states_codes_url, 1)

    # Mapowanie kodów stanów na pełne nazwy w oryginalnym DataFrame
    df = utils.map_state_codes(df, states_codes_df)
    print(df.columns)
    # Mapowanie populacji stanów
    df = utils.map_state_population(df, states_population_df)

    final_df = df.groupby('state').agg({
        'name': 'count',
        'population': 'first'
    }).rename(columns={'name': 'total_shootings'}).reset_index()

    final_df['shootings_per_1k_people'] = (
        final_df['total_shootings'] / final_df['population']) * 1000

    print(final_df)


if __name__ == "__main__":
    main()
