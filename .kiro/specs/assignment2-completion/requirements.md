# Requirements Document - Assignment 2 Completion

## Introduction

This specification covers the remaining 30% (15 points) of Assignment 2 for the Energy Management System. The goal is to complete the missing synchronization mechanisms, device simulator, frontend visualization, and deployment documentation to achieve full functionality and maximum points.

## Glossary

- **System**: The complete Energy Management microservices architecture
- **Auth Service**: Microservice responsible for user authentication and management
- **Device Service**: Microservice responsible for device management
- **Monitoring Service**: Microservice responsible for energy consumption tracking and aggregation
- **RabbitMQ**: Message broker for asynchronous communication between services
- **Sync Queue**: RabbitMQ queue dedicated to synchronization events (user_created, device_created, etc.)
- **Device Data Queue**: RabbitMQ queue for smart meter readings
- **Simulator**: Standalone application that generates synthetic smart meter readings
- **JWT Token**: JSON Web Token used for authentication across services
- **Hourly Aggregation**: Process of combining 10-minute measurements into hourly totals

## Requirements

### Requirement 1: User Synchronization

**User Story:** As a system administrator, I want user data to be automatically synchronized across all microservices, so that when I create a user in the Auth Service, it is immediately available in all dependent services.

#### Acceptance Criteria

1. WHEN a new user is created through the Auth Service, THE System SHALL publish a synchronization message to the sync_queue containing the user's ID, username, and role
2. WHEN a user synchronization message is published, THE Device Service SHALL consume the message and create a corresponding user record in its local database
3. WHEN a user synchronization message is published, THE Monitoring Service SHALL consume the message and create a corresponding user record in its local database
4. WHEN a user is deleted through the Auth Service, THE System SHALL publish a deletion message to the sync_queue
5. WHEN a user deletion message is received, THE Device Service SHALL remove the corresponding user record from its local database
6. WHEN a user deletion message is received, THE Monitoring Service SHALL remove the corresponding user record from its local database

### Requirement 2: Device Synchronization

**User Story:** As a system administrator, I want device data to be automatically synchronized to the Monitoring Service, so that energy consumption data can be properly associated with devices.

#### Acceptance Criteria

1. WHEN a new device is created through the Device Service, THE System SHALL publish a synchronization message to the sync_queue containing the device's ID, name, description, and max_consumption
2. WHEN a device synchronization message is published, THE Monitoring Service SHALL consume the message and create a corresponding device record in its local database
3. WHEN a device is updated through the Device Service, THE System SHALL publish an update message to the sync_queue
4. WHEN a device update message is received, THE Monitoring Service SHALL update the corresponding device record in its local database
5. WHEN a device is deleted through the Device Service, THE System SHALL publish a deletion message to the sync_queue
6. WHEN a device deletion message is received, THE Monitoring Service SHALL remove the corresponding device record from its local database

### Requirement 3: Device Data Simulator

**User Story:** As a developer, I want a standalone application that simulates smart meter readings, so that I can test the monitoring system with realistic energy consumption patterns.

#### Acceptance Criteria

1. THE Simulator SHALL be a standalone Python application that can run independently of the Docker environment
2. THE Simulator SHALL read configuration from a JSON file containing device_id, interval_seconds, base_load_kwh, and RabbitMQ connection details
3. THE Simulator SHALL generate energy consumption values that simulate realistic patterns with lower consumption during night hours (0-6), moderate consumption during day hours (9-17), and higher consumption during evening hours (17-22)
4. THE Simulator SHALL send measurements to the device_data_queue every 10 minutes (configurable)
5. THE Simulator SHALL format messages as JSON with timestamp, device_id, and measurement_value fields
6. THE Simulator SHALL handle RabbitMQ connection errors gracefully and attempt to reconnect
7. THE Simulator SHALL log all sent messages to the console with timestamp and value
8. THE Simulator SHALL support command-line arguments to override configuration file settings

### Requirement 4: Frontend Energy Visualization

**User Story:** As a client user, I want to view my historical energy consumption as charts, so that I can understand my usage patterns and identify opportunities to reduce consumption.

#### Acceptance Criteria

1. THE Frontend SHALL display a dashboard page accessible to authenticated users
2. THE Dashboard SHALL include a device selector dropdown that lists all devices owned by the current user
3. THE Dashboard SHALL include a date picker calendar component for selecting the date to view
4. WHEN a user selects a device and date, THE Frontend SHALL fetch hourly consumption data from the Monitoring Service API
5. THE Dashboard SHALL display energy consumption as a bar chart with hours (0-23) on the X-axis and energy consumption (kWh) on the Y-axis
6. THE Dashboard SHALL display energy consumption as a line chart showing the trend throughout the day
7. THE Dashboard SHALL display summary cards showing total daily consumption, peak hour, and average hourly consumption
8. THE Dashboard SHALL handle cases where no data is available for the selected date by displaying an appropriate message
9. THE Dashboard SHALL update charts automatically when the user changes the selected device or date

### Requirement 5: Deployment Documentation

**User Story:** As a developer or evaluator, I want comprehensive deployment documentation including a UML deployment diagram, so that I can understand the system architecture and deploy it correctly.

#### Acceptance Criteria

1. THE System SHALL include a UML deployment diagram showing all containers (Traefik, PostgreSQL, RabbitMQ, Auth Service, User Service, Device Service, Monitoring Service, Frontend)
2. THE Deployment diagram SHALL show network connections between all components
3. THE Deployment diagram SHALL indicate port mappings for each service
4. THE Deployment diagram SHALL show RabbitMQ queue connections (device_data_queue, sync_queue)
5. THE Deployment diagram SHALL show database connections for each service
6. THE System SHALL include a README file with step-by-step build and execution instructions
7. THE README SHALL include troubleshooting steps for common issues
8. THE README SHALL include API endpoint documentation with example requests and responses
