import pandas as pd
import sankey as sk


class API:

    def __init__(self):
        self.stats = None

    def load_stats(self, filename):
        """ Load the player stats dataset. """
        self.stats = pd.read_csv(filename, delimiter=";", encoding="ISO-8859-1")  # or 'latin1'
  # Ensure correct CSV parsing

    def get_position(self):
        """ Retrieve unique player positions. """
        if 'Pos' not in self.stats.columns:
            raise KeyError(f"Column 'Pos' not found. Available columns: {', '.join(self.stats.columns)}")

        players = self.stats.copy()
        players['Pos'] = players['Pos'].astype(str).str.upper()

        # Handle multi-position players
        play = set()
        for p in players['Pos']:
            for pos in str(p).split(";"):  # Split positions
                play.add(pos.strip())

        return sorted(play)

    def extract_local_network(self):
        """ Extract player scoring flow for Sankey visualization (Player → Shot Type → Points). """

        # Select relevant columns
        scoring_data = self.stats[['Player', '3P', '2P', 'FT']].copy()

        # Convert wide format to long format for Sankey (melt function)
        scoring_data = scoring_data.melt(id_vars=['Player'],
                                         var_name="Shot Type",
                                         value_name="Points")

        # Remove zero values (players who didn't score in that category)
        local = scoring_data[scoring_data["Points"] > 0]

        return local


def main():
    """ Main function to run the Sankey diagram visualization. """
    # Initialize API and load data
    api = API()
    api.load_stats('2023-2024 NBA Player Stats - Playoffs.csv')

    # Extract scoring contribution data
    local = api.extract_local_network()

    # Print for debugging
    print(local)

    # Generate Sankey diagram for Player → Shot Type → Points
    sk.show_sankey(local, 'Player', 'Shot Type', vals='Points')


if __name__ == '__main__':
    main()