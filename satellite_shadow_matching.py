import numpy as np
import logging
from utils.data_parser import DataParser
from utils.grid_generator import GridGenerator
from utils.visibility_calculator import VisibilityCalculator

class SatelliteShadowMatching:
    def __init__(self, grid_spacing=2.0, search_radius=50.0, snr_threshold=30):
        """
        Initialize shadow matching system
        """
        self.data_parser = DataParser()
        self.grid_generator = GridGenerator(grid_spacing, search_radius)
        self.visibility_calculator = VisibilityCalculator(snr_threshold)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def process_epoch(self, satellite_data, initial_position, buildings):
        """
        Process single epoch of data
        """
        self.logger.info(f"Processing epoch with {len(satellite_data)} satellites")
        
        # Generate search grid
        grid_points = self.grid_generator.generate_search_grid(
            initial_position['X'],
            initial_position['Y']
        )
        self.logger.info(f"Generated {len(grid_points)} candidate points")
        
        # Calculate scores for each grid point
        scores = []
        for point in grid_points:
            point_score = 0
            receiver_pos = {
                'X': point[0],
                'Y': point[1],
                'Z': initial_position['Z']  # Keep original height
            }
            
            # Check each satellite
            for sat in satellite_data:
                # Predict visibility
                predicted_visible = self.visibility_calculator.predict_satellite_visibility(
                    sat, receiver_pos, buildings
                )
                
                # Check observed visibility
                observed_visible = self.visibility_calculator.check_observed_visibility(
                    sat['SNR']
                )
                
                # Score matching
                if predicted_visible == observed_visible:
                    point_score += 1
                    
            scores.append((point_score, point))
        
        # Find best position
        max_score = max(score for score, _ in scores)
        best_points = [point for score, point in scores if score == max_score]
        
        # Calculate final position (average of best points)
        final_x = np.mean([p[0] for p in best_points])
        final_y = np.mean([p[1] for p in best_points])
        
        return {
            'X': final_x,
            'Y': final_y,
            'Z': initial_position['Z'],
            'score': max_score,
            'num_best_points': len(best_points)
        }

    def run(self, satellite_file, position_file, building_file, output_file):
        """
        Run shadow matching for all epochs
        """
        # Parse input data
        self.logger.info("Parsing input data...")
        satellite_data = self.data_parser.parse_satellite_data(satellite_file)
        position_data = self.data_parser.parse_position_data(position_file)
        buildings = self.data_parser.parse_building_data(building_file)
        
        # Process each epoch
        results = {}
        for epoch in satellite_data.keys():
            if epoch in position_data:
                self.logger.info(f"Processing epoch {epoch}")
                results[epoch] = self.process_epoch(
                    satellite_data[epoch],
                    position_data[epoch],
                    buildings
                )
            else:
                self.logger.warning(f"No position data for epoch {epoch}")
        
        # Write results
        self.logger.info("Writing results...")
        with open(output_file, 'w') as f:
            f.write("Epoch,X,Y,Z,Score,NumBestPoints\n")
            for epoch, result in results.items():
                f.write(f"{epoch},{result['X']},{result['Y']},{result['Z']},"
                       f"{result['score']},{result['num_best_points']}\n")
        
        self.logger.info("Processing complete")
        return results

if __name__ == "__main__":
    # Example usage
    matcher = SatelliteShadowMatching()
    results = matcher.run(
        "satellite_data.txt",
        "initial_positions.pos",
        "buildings.txt",
        "shadow_matching_results.csv"
    )
