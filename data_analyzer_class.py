import pandas as pd
import textwrap
import re

class DataAnalyzer:

    def main(self, df):
        while True:
            choice = self.get_wanted_action()

            if choice == "1":
                basic_info_dict = self.get_basic_info(df)
                self.print_basic_info(basic_info_dict)

            elif choice == "2":
                print("Enter your search")
                search = input(">>")
                results_df = self.search_engine(df, search)
                if results_df.empty:
                    print("No results found")
                else:
                    print(results_df)

            elif choice == "3":
                time_of_streaming = self.get_length_of_song_streaming(df)
                self.print_length_of_song_streaming(time_of_streaming)

            elif choice == "4":
                self.artist_search_action(df)

            elif choice == "5":
                self.search_by_date_action(df)

            else:
                print("Number from 1 to 5 required")

            self.continue_or_exit()


    def get_wanted_action(self):
        introduction = ("""
        Actions you can do:
        1 - check basic information
        2 - search for song or artist (search engine) 
        3 - check how long have you been listening to specific song
        4 - check information about specific artist
        5 - find out all songs you have listened to specific month/day/hour
         """)

        print(textwrap.dedent(introduction))

        choice = input(">> ")
        return choice

    def get_basic_info(self, df):
        music = df["msPlayed"].sum()
        start_date = df["endTime"].min()
        end_date = df["endTime"].max()
        _time = self.convert_ms_to_readable_form(music)
        num_of_artists = df["artistName"].nunique()
        num_of_songs = df["trackName"].nunique()
        top_artists = df["artistName"].value_counts().index.tolist()[:10]
        top_songs = df["trackName"].value_counts().index.tolist()[:10]

        basic_info_dict = {
            "the earliest date": start_date,
            "the latest date": end_date,
            "lasting": _time,
            "number of artists": num_of_artists,
            "top 10 artists": top_artists,
            "number of songs": num_of_songs,
            "top 10 songs": top_songs
        }
        return basic_info_dict

    def print_basic_info(self, basic_info_dict):

        text = (f"""
        {"-" * 40}
        Basic information:
        {"-" * 40}
        Start of streaming: {basic_info_dict["the earliest date"]}
        End of streaming: {basic_info_dict["the latest date"]}
        Length of streaming: {basic_info_dict["lasting"]}
        Number of artists you have ever listened to: {basic_info_dict["number of artists"]}
        Number of songs you have ever listened to: {basic_info_dict["number of songs"]}""")

        print(textwrap.dedent(text))
        print("-" * 40)
        print("Top 10 artists which have been listened to most often:")
        print(*basic_info_dict["top 10 artists"], sep="\n")
        print("-" * 40)
        print("Top 10 songs which have been listened to most often:")
        print(*basic_info_dict["top 10 songs"], sep="\n")
        print("-" * 40)

    def search_engine(self, df, search):
        df = df[["artistName", "trackName"]].loc[(df["artistName"].str.contains(search, flags=re.I, regex=True)) |
                                                  (df["trackName"].str.contains(search, flags=re.I, regex=True))]
        df = df.drop_duplicates()
        df = df.sort_values(["artistName", "trackName"])
        df = df.reset_index(drop=True)

        return df

    def get_length_of_song_streaming(self, df):
        choice = input("Enter the name of song which you are searching for: ")
        name_pattern = f"^{choice}$"
        sum_of_ms = df["msPlayed"].loc[df["trackName"].str.contains(name_pattern, flags=re.I, regex=True)].sum()
        time_of_streaming = self.convert_ms_to_readable_form(sum_of_ms)

        return time_of_streaming

    def print_length_of_song_streaming(self, time_of_streaming):
        if time_of_streaming == "0:0:0":
            print("No song with such title")
        else:
            print(f"The song have been listened to for {time_of_streaming}")

    def artist_search_engine(self, df, artist_search):
        df = df["artistName"].loc[df["artistName"].str.contains(artist_search, flags=re.I, regex=True)]
        df = df.unique()
        return df

    def get_artist_info(self, df, search):
        df = df.loc[df["artistName"] == search]

        music = df["msPlayed"].sum()
        _time = self.convert_ms_to_readable_form(music)
        num_of_songs = df["trackName"].nunique()

        artist_info = {
            "artist": search,
            "time of listening": _time,
            "number of songs": num_of_songs,
        }

        return artist_info

    def get_artist_df(self, df, search):
        df = df.loc[df["artistName"] == search]

        artist_df = {"trackName": [], "msPlayed": [], "streamingDuration [h:m:s]": [], "numberOfTimes": []}
        artist_df = pd.DataFrame(artist_df)

        for index, row in df.iterrows():
            track_name = row["trackName"]
            ms = int(row["msPlayed"])

            index_of_occurrence = artist_df.index[artist_df["trackName"] == track_name].tolist()

            if len(index_of_occurrence) == 0:
                artist_df.loc[len(artist_df.index)] = [track_name, ms, "", 1]
            elif len(index_of_occurrence) > 0:
                for _index in index_of_occurrence:
                    new_ms = artist_df.loc[_index]["msPlayed"] + ms
                    artist_df.at[_index, "msPlayed"] = new_ms
                    artist_df.at[_index, "numberOfTimes"] = artist_df.loc[_index]["numberOfTimes"] + 1

        for index, row in artist_df.iterrows():
            duration = self.convert_ms_to_readable_form(int(row["msPlayed"]))
            artist_df.at[index, "streamingDuration [h:m:s]"] = duration

        convert_dict = {"msPlayed": int,
                        "numberOfTimes": int}
        artist_df = artist_df.astype(convert_dict)
        artist_df = artist_df.sort_values(by=["numberOfTimes"], ascending=False)
        artist_df = artist_df.reset_index(drop=True)

        return artist_df

    def artist_search_action(self, df):

        artist_search = input(
            "Enter part on artist's name and search if you're not sure how to write it precisely (if not needed - leave blank): ")
        if len(artist_search) > 0:
            artist_search_result = self.artist_search_engine(df, artist_search)
            print(artist_search_result)

        exact_artist_search = input("Enter artist's name (carefully): ")
        artist_info = self.get_artist_info(df, exact_artist_search)
        artist_df = self.get_artist_df(df, exact_artist_search)

        text = f"""
        {"-" * 40}
        Artist: {artist_info["artist"]}
        Entire time of listening: {artist_info["time of listening"]}
        Number of their songs: {artist_info["number of songs"]}
        {"-" * 40}"""

        print(textwrap.dedent(text))
        print("Songs:")
        print(artist_df)
        print(f"{'-' * 40}")

    def search_by_date_action(self, df):
        search = input("Enter a date [using (yyyy-mm), (yyyy-mm-dd) or (yyyy-mm-dd hh) format]: ")

        does_match_month = re.match(r"^\d{4}-\d{2}$", search)
        does_match_day = re.match(r"^\d{4}-\d{2}-\d{2}$", search)
        does_match_hour = re.match(r"^\d{4}-\d{2}-\d{2}\s\d{2}$", search)

        if does_match_month is None and does_match_day is None and does_match_hour is None:
            print("No records in the given date or invalid syntax")

        else:
            if does_match_month is not None:
                df = df[df['endTime'].dt.to_period('M') == search]
            if does_match_day is not None:
                df = df[df['endTime'].dt.to_period('D') == search]
            if does_match_hour is not None:
                df = df[df['endTime'].dt.to_period('H') == search]
            num_of_songs = df['msPlayed'].nunique()
            ms = df["msPlayed"].sum()
            duration = self.convert_ms_to_readable_form(ms)

            print(df)
            print(f"You have listened to {num_of_songs} song{'s' if num_of_songs > 0 else ''}")
            print(f"And it lasted {duration}")

    def convert_ms_to_readable_form(self, ms):
        in_seconds = ms // 1000
        seconds = in_seconds % 60
        minutes = in_seconds // 60 % 60
        hours = in_seconds // 60 // 60 % 24
        days = in_seconds // 60 // 60 // 24
        if days == 0:
            _time = f"{hours}:{minutes}:{seconds}"
        elif days > 0:
            _time = f"{days} day{'s' if days > 1 else ''} {hours}:{minutes}:{seconds}"
        else:
            raise Exception
        return _time

    def continue_or_exit(self):
        answer = input("Do you want to continue? [Y/n]: ").lower()
        print("")
        if answer != "y":
            exit()
