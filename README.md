# Pokédex Web Application

A comprehensive Pokémon information system with advanced search capabilities, details on all generations, and team-building functionality.

## Features

- **Complete Pokémon Database**: Data for all Pokémon up to Generation 9
- **Advanced Search**: Find Pokémon by name, type, ability, and more
- **Detailed Information**: Comprehensive stats, evolutions, moves, and abilities
- **Team Builder**: Create and analyze your perfect Pokémon team
- **Type Calculator**: Check weaknesses and resistances for battle strategy
- **Modern UI**: Responsive design with generation-based themes
- **API Access**: RESTful API for programmatic data access

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **API**: RESTful API with JSON responses
- **Caching**: Flask-Caching for performance optimization

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB 4.0+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pokedex-webapp.git
   cd pokedex-webapp
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Make sure MongoDB is running on localhost:27017

6. Run the setup script to populate the database:
   ```
   python pokedex_app/scripts/import_data.py
   ```

7. Start the application:
   - Windows: `run.bat`
   - macOS/Linux: `./run.sh`

8. Open your browser and navigate to http://localhost:5000

## Project Structure

```
pokedex_app/
├── app/                  # Main application directory
│   ├── models/           # Database models
│   ├── routes/           # Route definitions
│   ├── services/         # Business logic and services
│   ├── static/           # Static files (CSS, JS, images)
│   ├── templates/        # Jinja2 HTML templates
│   └── utils/            # Utility functions
├── scripts/              # Data import and maintenance scripts
└── config.py             # Application configuration
```

## API Documentation

The API provides access to Pokémon data through the following endpoints:

- `/api/pokemon` - List all Pokémon (supports pagination)
- `/api/pokemon/<id>` - Get details for a specific Pokémon
- `/api/types` - List all Pokémon types
- `/api/moves` - List all Pokémon moves

For detailed documentation, visit `/api/docs` after starting the application.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes only. All Pokémon content is copyright of Nintendo, Game Freak, and The Pokémon Company. 