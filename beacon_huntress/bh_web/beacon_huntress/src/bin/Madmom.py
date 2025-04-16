import pandas as pd
import numpy as np
import logging

class Analyzer:
    def __init__(self, parquet_file, thresholds):
        self.parquet_file = parquet_file
        self.results = None
        self.thresholds = thresholds

    def analyze(self):
        logging.info("load data")
        data = pd.read_parquet(self.parquet_file)

        logging.info("aggregating")
        aggregated_data = self.aggregate_connections(data)

        logging.info("calculating metrics and scores")
        self.results = self.calculate_scores(aggregated_data)

    def aggregate_connections(self, data):

        data.rename(columns={
            'ts': 'datetime', 
            'source_ip' : 'sip', 
            'destination_ip' : 'dip',
            'destination_bytes' : 'dest_bytes',
        }, inplace=True)

        data['datetime'] = pd.to_datetime(data['datetime'], unit='ms')
        prevalence = data.groupby('dip')['sip'].nunique().reset_index(name='unique_sips')
        data = data.merge(prevalence, on='dip')
        data = data[data['unique_sips'] <= 3]

        grouped = data.groupby(['sip', 'dip', "dns"]).agg({
            'datetime': list,
            'dest_bytes': list,
            'port' : 'first',
            'proto' : 'first',
        }).reset_index()

        grouped['datetime'] = grouped['datetime'].apply(lambda x: sorted(x))
        grouped['conn_count'] = grouped['datetime'].apply(len)

        #filter out low conn count
        grouped = grouped[grouped['conn_count'] > 100]

        return grouped

    def calculate_scores(self, grouped):

        #data scoring
        grouped['dsMadm'] = grouped['dest_bytes'].apply(
        lambda x: np.median(np.abs(np.array(x) - np.median(x))) if x else 0)
        grouped['dsSkew'] = grouped['dest_bytes'].apply(
        lambda x: (np.percentile(x, 20) + np.percentile(x, 80) - 2 * np.percentile(x, 50)) / (np.percentile(x, 80) - np.percentile(x, 20)) if len(x) >= 3 and (np.percentile(x, 80) - np.percentile(x, 20)) != 0 else 0)

        grouped['dsMadmScore'] = grouped['dsMadm'].apply(lambda x: 1.0 / (1.0 + np.sqrt(x)))
        grouped['dsSkewScore'] = grouped['dsSkew'].apply(lambda x: max(0.0, 1.0 - abs(x)))
        grouped['dsScore'] = (grouped['dsMadmScore'] + grouped['dsSkewScore']) / 2.0

        # Calculate time deltas
        grouped['deltas'] = grouped['datetime'].apply(
        lambda x: pd.Series(x).diff().dt.total_seconds().dropna().tolist()
        )

        # Bowley skew components
        grouped['tsLow'] = grouped['deltas'].apply(lambda x: np.percentile(np.array(x), 20) if x else 0)
        grouped['tsMid'] = grouped['deltas'].apply(lambda x: np.percentile(np.array(x), 50) if x else 0)
        grouped['tsHigh'] = grouped['deltas'].apply(lambda x: np.percentile(np.array(x), 80) if x else 0)

        grouped['tsBowleyNum'] = grouped['tsLow'] + grouped['tsHigh'] - 2 * grouped['tsMid']
        grouped['tsBowleyDen'] = grouped['tsHigh'] - grouped['tsLow']

        grouped['tsSkew'] = grouped.apply(
        lambda x: x['tsBowleyNum'] / x['tsBowleyDen']
        if x['tsBowleyDen'] != 0 and x['tsMid'] != x['tsLow'] and x['tsMid'] != x['tsHigh']
        else 0.0,
        axis=1
        )

        # Median Absolute Deviation
        grouped['tsMadm'] = grouped['deltas'].apply(
        lambda x: np.median(np.abs(np.array(x) - np.median(x))) if x else 0
        )

        # Optional: normalized connection duration (used in RITA)
        grouped['tsConnDiv'] = grouped['datetime'].apply(
        lambda x: (x[-1].to_pydatetime() - x[0].to_pydatetime()).seconds / 90 if len(x) > 1 else 0
        )

        # Normalize scores
        grouped['tsMadmScore'] = grouped['tsMadm'].apply(lambda x: 1.0 / (1.0 + np.sqrt(x + 1e-6)))
        grouped['tsSkewScore'] = grouped['tsSkew'].apply(lambda x: max(0.0, 1.0 - abs(x)))

        # Final composite score
        grouped['tsScore'] = 0.5 * grouped['tsMadmScore'] + 0.5 * grouped['tsSkewScore']
        grouped['final_score'] = (grouped['tsScore'] + grouped['dsScore']) / 2

        # Filter if needed
        grouped = grouped[grouped['final_score'] > 0.1]

        return grouped

    def display_results(self):
        # Display top results
        results = self.results.sort_values(by='final_score', ascending=False)[
        ['sip', 'dip', 'port', 'conn_count', 'tsSkewScore', 'tsMadmScore', 'tsScore', 'final_score']
        ]

        print(results)
        print(f"\n Total number of unique (sip, dip, port) connections analyzed: {len(self.results)}")
        #results.to_csv('madmom_output.txt', index=False)

    def get_results(self, likelihood = 0.0):
        return self.results.\
            loc[self.results["final_score"] >= likelihood].sort_values(by='final_score', ascending=False)[
            ['sip', 'dip', 'port', 'proto', 'conn_count', 'tsScore', 'dsScore', 'final_score', 'dns']
            ]

def run_mad(max_delta_file,likelihood):

        # RUN MADMOM ALGO 
        # MEDIAN AVG DEVIATION OF THE MEAN OF OBSERVATIONS MEANS

        # DEFAULT THRESHOLDS
        thresholds = {
        'deviation': [0.0, 0.2, 0.4, 0.6],
        'long_conn': 3600,
        'strobe': 80000,
        }

        analyzer = Analyzer(max_delta_file, thresholds)
        analyzer.analyze()
        df_mad = analyzer.get_results(likelihood)

        # CONVERT SCORES TO PERCENTAGES
        df_mad['tsScore'] = df_mad['tsScore'] * 100.00
        df_mad['dsScore'] = df_mad['dsScore'] * 100.00
        df_mad['final_score'] = df_mad['final_score'] * 100.00

        return df_mad

# def main():
#      # Example usage
#     parquet_file = ''

#     while True:
#         print("\n=== MADMOM MENU ===")
#         print("1. Run Analysis")
#         print("2. Change Parquet File")
#         print("3. Exit")

#         choice = input("Select an option: ")

#         if choice == '1':
#             analyzer = Analyzer(parquet_file)
#             analyzer.analyze() 
#             analyzer.display_results()
#         elif choice == '2':
#             parquet_file = input("Enter new parquet file path: ")
#             print(f"Parquet file changed to: {parquet_file}")
#         elif choice == '3':
#             print("Exiting...")
#             break
#         else:
#             print("invalid choice.")


# if __name__ == "__main__":
#     main()
