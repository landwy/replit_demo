import numpy as np

class GridGenerator:
    def __init__(self, grid_spacing=2.0, search_radius=50.0):
        """
        Initialize grid generator with spacing and search radius
        """
        self.grid_spacing = grid_spacing
        self.search_radius = search_radius

    def generate_search_grid(self, center_x, center_y):
        """
        Generate search grid points around center position
        Returns: List of (x,y) coordinates for candidate points
        """
        # Calculate grid dimensions
        num_points = int(2 * self.search_radius / self.grid_spacing) + 1
        
        # Generate grid coordinates
        x_coords = np.linspace(
            center_x - self.search_radius,
            center_x + self.search_radius,
            num_points
        )
        y_coords = np.linspace(
            center_y - self.search_radius,
            center_y + self.search_radius,
            num_points
        )
        
        # Create grid points
        grid_points = []
        for x in x_coords:
            for y in y_coords:
                # Only include points within the search radius
                if np.sqrt((x - center_x)**2 + (y - center_y)**2) <= self.search_radius:
                    grid_points.append((x, y))
        
        return grid_points
