# ParkNext - Parking Management System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [User Roles and Permissions](#user-roles-and-permissions)
6. [Key Features](#key-features)
7. [Core Workflows](#core-workflows)
8. [Development Guide](#development-guide)
9. [Troubleshooting](#troubleshooting)
10. [Change Log](#change-log)

## System Overview

ParkNext is a comprehensive parking management system designed to streamline the process of parking spot reservation, management, and administration. The system serves three primary user types:

- **Users**: Can register, log in, browse available spots, make bookings, and manage their reservations.
- **Staff**: Responsible for approving bookings, managing vehicle entry/exit, and overseeing daily operations.
- **Administrators**: Have full control over the system, including spot management, staff oversight, and system-wide reporting.

## Architecture

The application follows a Model-View-Controller (MVC) pattern:

- **Model**: Database interaction is managed through direct SQL queries via a connection established with `get_db_connection()`.
- **View**: Frontend templates are built using Jinja2 templating engine with HTML/CSS/JavaScript.
- **Controller**: Flask routes in app.py and specialization files (staff_routes.py, auth_routes.py) handle business logic.

### Core Files

- `app.py`: Main application file with most route definitions
- `staff_routes.py`: Staff-specific route handlers
- `auth_routes.py`: Authentication-related route handlers
- `db.py`: Database connection and initialization
- `templates/`: Frontend Jinja2 templates
- `static/`: Static assets (CSS, JavaScript, images)

## Database Schema

The system uses a MySQL database with the following primary tables:

### users
- `user_id`: Primary key, auto-increment
- `username`: User's login name
- `email`: User's email address
- `password`: User's password
- `phone`: Optional phone number
- `created_at`: Account creation timestamp

### staff
- `staff_id`: Primary key, auto-increment
- `username`: Staff login name
- `password`: Staff password
- `email`: Staff email address
- `name`: Staff member's full name

### admin
- `admin_id`: Primary key, auto-increment
- `username`: Admin login name
- `password`: Admin password
- `email`: Admin email address

### parking_spots
- `spot_id`: Primary key, auto-increment
- `location`: Description of spot location
- `status`: Current status ('available', 'reserved', 'occupied')
- `price_per_hour`: Hourly rate (in ₱)

### bookings
- `booking_id`: Primary key, auto-increment
- `user_id`: Foreign key to users
- `spot_id`: Foreign key to parking_spots
- `start_time`: Reservation start time
- `end_time`: Reservation end time
- `status`: Booking status ('pending', 'confirmed', 'cancelled', 'entry', 'exited')
- `created_at`: Booking creation timestamp
- `amount`: Total cost of booking
- `payment_status`: Payment status ('paid', 'unpaid')
- `entry_time`: Actual vehicle entry time
- `exit_time`: Actual vehicle exit time

### transactions
- `transaction_id`: Primary key, auto-increment
- `booking_id`: Foreign key to bookings
- `amount`: Payment amount
- `payment_method`: Method of payment
- `transaction_time`: Payment timestamp
- `status`: Transaction status

### deleted_bookings
- `id`: Primary key, auto-increment
- `booking_id`: Original booking ID
- `user_id`: User ID from original booking
- `spot_id`: Spot ID from original booking
- `start_time`, `end_time`, `status`, etc: Preserved booking data
- `deleted_at`: Deletion timestamp

### admin_activity_log
- `id`: Primary key, auto-increment
- `admin_id`: Admin who performed the action
- `action_type`: Type of action (add, edit, delete, restore)
- `action_details`: Description of the action
- `booking_id`: Related booking if applicable
- `action_time`: Timestamp of action

### staff_activity_log
- `id`: Primary key, auto-increment
- `staff_id`: Staff who performed the action
- `action_type`: Type of action (approve, cancel, entry, exit)
- `action_details`: Description of the action
- `booking_id`: Related booking if applicable
- `action_time`: Timestamp of action

## API Endpoints

### Authentication

- `GET/POST /login`: User/staff/admin login
- `GET/POST /register`: New user registration
- `GET /logout`: Log out current user

### User Routes

- `GET /user/dashboard`: User dashboard with bookings overview
- `GET/POST /user/profile`: View/edit user profile
- `GET /user/booking_history`: View past bookings
- `POST /user/book`: Create a new booking
- `GET /user/make_payment/<booking_id>`: Make payment for a booking
- `GET /user/cancel_booking/<booking_id>`: Cancel an existing booking

### Staff Routes

- `GET /staff/dashboard`: Staff dashboard with pending bookings
- `GET /staff/verify_booking`: Verify booking details
- `GET /staff/parked_vehicles`: View currently parked vehicles
- `GET /staff/activity_history`: View staff activity log
- `GET /staff/approve_booking/<booking_id>`: Approve a booking
- `GET /staff/decline_booking/<booking_id>`: Decline a booking
- `GET /staff/handle_entry_exit/<booking_id>/<action_type>`: Process vehicle entry/exit

### Admin Routes

- `GET /admin/dashboard`: Admin dashboard with system overview
- `GET /admin/booking_history`: View booking history
- `GET /admin/deleted_bookings`: View deleted bookings
- `GET /admin/restore_booking/<deleted_id>`: Restore a deleted booking
- `GET /admin/permanent_delete_booking/<deleted_id>`: Permanently delete a booking
- `POST /admin/add_spot`: Add a new parking spot
- `GET/POST /admin/edit_spot/<spot_id>`: Edit an existing spot
- `GET /admin/delete_spot/<spot_id>`: Delete a parking spot
- `GET/POST /admin/generate_report`: Generate system reports
- `GET /admin/download_report`: Download report as CSV

### API Endpoints

- `GET /api/available_spots`: Get count of available spots
- `GET /api/payment_details/<booking_id>`: Get payment details for a booking

## User Roles and Permissions

### Users
- Browse and book available parking spots
- View their own booking history
- Make payments for their bookings
- Cancel their own pending bookings
- Update their profile information

### Staff
- View and manage all pending bookings
- Approve or decline booking requests
- Process vehicle entry and exit
- View currently parked vehicles
- Access activity history logs

### Administrators
- All staff permissions
- Manage parking spots (add, edit, delete)
- View and restore deleted bookings
- Permanently delete bookings from the system
- Generate and export system reports
- Access system-wide analytics and metrics

## Key Features

### Booking Management
The system provides a comprehensive booking lifecycle management:
- Creation: Users can browse available spots and create bookings
- Approval: Staff review and approve pending bookings
- Entry/Exit: Staff record actual vehicle entry and exit times
- Cancellation: Users can cancel pending bookings, staff can cancel confirmed bookings
- Deletion: Admins can soft-delete bookings (moved to deleted_bookings table)
- Restoration: Admins can restore deleted bookings

### Parking Spot Management
Administrators can:
- Add new parking spots with location and pricing details
- Edit existing spots to update information
- Delete unused spots (only if they have no active bookings)
- View spot utilization and booking history

### Payment Processing
The system handles booking payments:
- Calculate charges based on duration and hourly rate
- Process payments through various methods
- Track payment status and transaction history
- Generate receipts for completed payments

### Reporting and Analytics
Administrators can generate various reports:
- Booking Activity: Overview of all bookings in a specified period
- Revenue Analysis: Financial performance and trends
- Occupancy Reports: Parking spot utilization statistics
- Export data to CSV format for external analysis

## Core Workflows

### User Booking Workflow
1. User logs in and browses available parking spots
2. User selects a spot and specifies start/end times
3. System creates a pending booking and calculates the amount
4. User makes payment to confirm the booking
5. Staff approves the booking
6. On arrival, staff records vehicle entry
7. On departure, staff records vehicle exit

### Booking Approval Workflow
1. Staff logs in to staff dashboard and views pending bookings
2. Staff reviews booking details including payment status
3. If approved, system changes booking status to 'confirmed' and spot status to 'reserved'
4. The approving staff's action is logged in the staff_activity_log

### Vehicle Entry/Exit Workflow
1. Staff verifies the booking ID when vehicle arrives
2. Staff records entry time, system changes booking status to 'entry' and spot status to 'occupied'
3. When vehicle leaves, staff records exit time
4. System changes booking status to 'exited' and spot status to 'available'

### Deleted Booking Management
1. Admin soft-deletes a booking (moves data to deleted_bookings table)
2. Booking can be viewed in the Deleted Bookings History page
3. Admin can choose to restore the booking or delete it permanently
4. If restored, booking data is moved back to the bookings table
5. If permanently deleted, booking data is completely removed from the system

## Development Guide

### Setting Up Development Environment
1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies from requirements.txt
4. Configure database connection in db.py
5. Initialize the database using db.py
6. Run the application using app.py

### Code Organization
- Routes are organized by user type (user, staff, admin)
- Database queries are embedded directly in route functions
- Templates are organized in subdirectories by user type
- Static assets are separated by type (CSS, JS, images)

### Adding New Features
1. Design database changes if needed
2. Update or create route handlers in app.py or specialized route files
3. Create or modify templates in the templates directory
4. Add any required static assets
5. Update this documentation to reflect new features

### Best Practices
- Always use parameterized SQL queries to prevent SQL injection
- Log all significant actions in the appropriate activity log
- Check user permissions before allowing access to protected routes
- Implement proper error handling and user feedback
- Keep documentation updated as the system evolves

## Troubleshooting

### Common Issues

#### Database Connectivity
If you encounter database connection issues:
1. Verify MySQL server is running
2. Check database credentials in db.py
3. Ensure the database exists and has correct permissions
4. Look for connection errors in the log files

#### Booking Status Issues
If bookings don't show correct status:
1. Check the booking status in the database directly
2. Verify that status update queries are executing correctly
3. Ensure that the associated parking spot status is also updated

#### Available Spots Not Updating
If the available spots count doesn't update correctly:
1. Verify that spot status is being updated when bookings are approved/completed
2. Check the query that counts available spots in the staff_dashboard function
3. Ensure the query is specifically filtering for spots with status='available'

#### Payment Processing Issues
If payment processing fails:
1. Check transaction table for error records
2. Verify that amount calculations are correct
3. Ensure correct booking IDs are being passed to payment functions

## Change Log

### May 15, 2025
- Fixed foreign key constraint error when deleting parking spots by implementing an archiving system for historical bookings
- Updated parking spot deletion process to maintain data integrity while allowing spot removal

### May 6, 2025
- Updated home page to use peso sign (₱) in the Spot Details section and bookings table to ensure currency consistency

### May 5, 2025
- Created comprehensive documentation system
- Updated README.md with latest features and setup instructions

### May 1, 2025
- Changed currency symbol from $ to ₱ in home page to align with Philippine currency

### April 30, 2025
- Fixed Available Spots count in staff dashboard to accurately reflect spots with status='available'
- Updated staff_approve_booking function to properly refresh available spots count

### April 29, 2025
- Added "Delete Permanently" feature for deleted bookings
- Implemented permanent deletion functionality in app.py
- Added UI confirmation dialog for permanent deletion
- Fixed admin activity logging in booking restoration (changed target_id to booking_id)

### Older Updates
- Fixed payment details display in staff dashboard
- Corrected inconsistent parking spot status values
- Updated booking status values to ensure proper display of Accept/Decline buttons
- Implemented comprehensive database fixes for data consistency
