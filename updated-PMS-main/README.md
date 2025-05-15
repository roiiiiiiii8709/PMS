# ParkNext - Parking Management System

A comprehensive web application for managing parking facilities in the Philippines. This system enables users to book parking spots, staff to manage parking operations, and administrators to oversee the entire system.

## Key Features

### For Users
- Account registration and profile management
- Browse and book available parking spots
- View booking history and current bookings
- Make payments for reservations
- Cancel pending bookings

### For Staff
- Verify and approve booking details
- Process vehicle entry and exit
- View currently parked vehicles
- Track staff activity history

### For Administrators
- Comprehensive dashboard with system overview
- Manage parking spots (add, edit, delete)
- View deleted bookings with restore options
- Generate various reports (bookings, revenue)
- Export reports as CSV files

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Jinja2 templates

## Installation and Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd updated-PMS-main
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install flask mysql-connector-python
   ```

4. Configure the database:
   - Edit the database configuration in `compl/db.py` to match your MySQL setup
   - By default, it uses:
     - Host: localhost
     - User: root
     - Password: (blank)
     - Database: parking_db

5. Initialize the database:
   ```
   python compl/db.py
   ```

6. Run the application:
   ```
   python compl/app.py
   ```

7. Access the application:
   - Open a browser and go to `http://localhost:5000`

## Recent Updates

- Fixed Available Spots count in staff dashboard to accurately reflect parking spot status
- Changed currency symbol from $ to ₱ to align with Philippine currency
- Added permanent deletion feature for deleted bookings
- Fixed booking restoration functionality with proper activity logging
- Various bug fixes and UI improvements

## Documentation

For detailed documentation about the system architecture, API endpoints, database schema, and developer guides, please refer to the [DOCUMENTATION.md](compl/DOCUMENTATION.md) file.

## Security Notes

- For production use, replace the secret key in `app.py` with a secure value
- Implement proper password hashing for production environments
- Set up HTTPS for secure communications

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, feature requests, or questions, please open an issue in the repository or contact the system administrator.

Last Updated: May 5, 2025
