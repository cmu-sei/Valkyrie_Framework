import pandas as pd
import numpy as np
import logging

class Analyzer:
    def __init__(self, parquet_file, thresholds):
        self.parquet_file = parquet_file
        self.thresholds = thresholds
        self.results = None

    def analyze(self):
        logging.info("load data")
        data = pd.read_parquet(self.parquet_file)

        logging.info("aggregating")
        aggregated_data = self.aggregate_connections(data)

        logging.info("calculating metrics and scores")
        self.results = self.calculate_scores(aggregated_data)

    def aggregate_connections(self, data):
        data['datetime'] = pd.to_datetime(data['datetime'])

        grouped = data.groupby(['sip', 'dip', 'dns']).agg({
            'datetime': lambda x: sorted(x),
            'delta_ms': list,
            'dest_bytes': list,
            'port' : 'first',
            'proto' : 'first',
        }).reset_index()

        grouped['conn_count'] = grouped['datetime'].apply(len)

        #filter out low conn count
        grouped = grouped[grouped['conn_count'] > 0]

        return grouped

    def calculate_scores(self, grouped):
        # Calculate time deltas
        grouped['deltas'] = grouped['datetime'].apply(lambda x: pd.Series(x).diff().dt.total_seconds().dropna().tolist())

        # Advanced metrics for time deltas
        grouped['tsLow'] = grouped['deltas'].apply(lambda x: np.percentile(x, 20) if x else 0)
        grouped['tsMid'] = grouped['deltas'].apply(lambda x: np.percentile(x, 50) if x else 0)
        grouped['tsHigh'] = grouped['deltas'].apply(lambda x: np.percentile(x, 80) if x else 0)
        grouped['tsBowleyNum'] = grouped['tsLow'] + grouped['tsHigh'] - 2 * grouped['tsMid']
        grouped['tsBowleyDen'] = grouped['tsHigh'] - grouped['tsLow']
        grouped['tsSkew'] = grouped.apply(
            lambda x: x['tsBowleyNum'] / x['tsBowleyDen'] if x['tsBowleyDen'] != 0 else 0, axis=1
        )
        grouped['tsMadm'] = grouped['deltas'].apply(lambda x: np.median(np.abs(x - np.median(x))) if x else 0)

        #time connection division
        grouped['tsConnDiv'] = grouped['datetime'].apply(lambda x: (x[-1] - x[0]).total_seconds() / 90 if len(x) > 1 else 1)

        # Time delta scoring
        grouped['tsSkewScore'] = 1.0 - abs(grouped['tsSkew'])
        grouped['tsMadmScore'] = grouped['tsMadm'].apply(lambda x: max(0, 1.0 - x / 30.0))
        grouped['tsConnCountScore'] = (grouped['conn_count']) / (grouped['tsConnDiv'] + 1e-6)
        grouped['tsConnCountScore'] = grouped['tsConnCountScore'].apply(lambda x: min(1.0, x))
        grouped['tsScore'] = (grouped['tsSkewScore'] + grouped['tsMadmScore']) / 2.0

        # grouped['dsLow'] = grouped['dest_ip_bytes'].apply(lambda x: np.percentile(x, 20) if x else 0)
        # grouped['dsMid'] = grouped['dest_ip_bytes'].apply(lambda x: np.percentile(x, 50) if x else 0)
        # grouped['dsHigh'] = grouped['dest_ip_bytes'].apply(lambda x: np.percentile(x, 80) if x else 0)
        grouped['dsLow'] = grouped['dest_bytes'].apply(lambda x: np.percentile(x, 20) if x else 0)
        grouped['dsMid'] = grouped['dest_bytes'].apply(lambda x: np.percentile(x, 50) if x else 0)
        grouped['dsHigh'] = grouped['dest_bytes'].apply(lambda x: np.percentile(x, 80) if x else 0)

        grouped['dsBowleyNum'] = grouped['dsLow'] + grouped['dsHigh'] - 2 * grouped['dsMid']
        grouped['dsBowleyDen'] = grouped['dsHigh'] - grouped['dsLow']
        grouped['dsSkew'] = grouped.apply(
            lambda x: x['dsBowleyNum'] / x['dsBowleyDen'] if x['dsBowleyDen'] != 0 else 0, axis=1
        )
        # grouped['dsMadm'] = grouped['dest_ip_bytes'].apply(
        #     lambda x: np.median(np.abs(np.array(x) - np.median(x))) if x else 0
        # )
        grouped['dsMadm'] = grouped['dest_bytes'].apply(
            lambda x: np.median(np.abs(np.array(x) - np.median(x))) if x else 0
        )

        # Data size scoring
        grouped['dsSkewScore'] = 1.0 - abs(grouped['dsSkew'])
        grouped['dsMadmScore'] = grouped['dsMadm'].apply(lambda x: max(0, 1.0 - x / 60.0))
        grouped['dsScore'] = (grouped['dsSkewScore'] + grouped['dsMadmScore']) / 2.0

        #data size smallness score
        grouped['dsSmallnessScore'] = 1.0 - (grouped['dsMadm'] / 4096.0)
        grouped['dsSmallnessScore'] = grouped['dsSmallnessScore'].apply(lambda x: max(0, x))

        # Final score
        grouped['final_score'] = (grouped['tsScore'] + grouped['dsScore']) / 2.0

        return grouped

    def display_results(self):
        # Display top results
        print(self.results.sort_values(by='final_score', ascending=False)[
        ['sip', 'dip', 'port', 'proto', 'conn_count', 'tsSkewScore', 'tsMadmScore', 'tsConnCountScore', 'tsScore', 'dsScore', 'final_score', 'dns']
        ].head(30))

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

def main():
     # Example usage
    parquet_file = '/home/step-admin/bh_web/two_beacon_48_hr_noisy_deltas_20250303_183854.parquet'

    thresholds = {
    'deviation': [0.0, 0.2, 0.4, 0.6],
    'long_conn': 3600,
    'strobe': 80000,
    }

    while True:
        print("\n=== MADMOM MENU ===")
        print("1. Run Analysis")
        print("2. Change Parquet File")
        print("3. Modify Thresholds")
        print("4. Exit")

        choice = input("Select an option: ")

        if choice == '1':
            analyzer = Analyzer(parquet_file, thresholds)
            analyzer.analyze()
            analyzer.display_results()
        elif choice == '2':
            parquet_file = input("Enter new parquet file path: ")
            print(f"Parquet file changed to: {parquet_file}")
        elif choice == '3':
            try:
                thresholds['deviation'] = list(map(float, input("Enter deviation thresholds (comma separated): ").split(',')))
                thresholds['long_conn'] = int(input("Enter long connection threshold: "))
                thresholds['strobe'] = int(input("Enter strobe threshold: "))
                print("Thresholds updated successfully")
            except ValueError:
                print("invalid input. please try again")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("invalid choice.")


if __name__ == "__main__":
    main()
