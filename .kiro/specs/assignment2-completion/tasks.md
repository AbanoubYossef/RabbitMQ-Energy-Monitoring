# Implementation Plan - Assignment 2 Completion

This implementation plan breaks down the remaining work into discrete, manageable coding tasks. Each task builds on previous tasks and focuses on writing, modifying, or testing code.

## Task List

- [x] 1. Implement User Synchronization in Auth Service


  - Add RabbitMQ publisher to Auth Service that publishes user creation and deletion events to sync_queue
  - Integrate publisher calls into user creation and deletion endpoints
  - _Requirements: 1.1, 1.4_




- [x] 1.1 Add pika dependency to Auth Service


  - Add `pika==1.3.2` to `auth_service/requirements.txt`
  - _Requirements: 1.1_

- [x] 1.2 Create RabbitMQ publisher module for Auth Service


  - Create `auth_service/authentication/rabbitmq.py` with RabbitMQPublisher class
  - Implement `connect()`, `publish_user_created()`, `publish_user_deleted()`, and `close()` methods
  - Add connection pooling and error handling
  - _Requirements: 1.1, 1.4_

- [x] 1.3 Integrate publisher into Auth Service views

  - Modify `auth_service/authentication/views.py` to call `publish_user_created()` after successful user registration
  - Add `publish_user_deleted()` call to user deletion endpoint if it exists
  - Add try-catch blocks for RabbitMQ errors
  - _Requirements: 1.1, 1.4_

- [x] 1.4 Update Auth Service settings


  - Add RabbitMQ configuration to `auth_service/authentication/settings.py` or environment variables
  - Add RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS settings
  - _Requirements: 1.1_

- [x] 2. Implement User Synchronization Consumer in Device Service


  - Add RabbitMQ consumer to Device Service that listens to sync_queue for user events
  - Create or update user records in Device Service database based on sync messages
  - _Requirements: 1.2, 1.5_

- [x] 2.1 Add pika dependency to Device Service


  - Add `pika==1.3.2` to `device_service/requirements.txt`
  - _Requirements: 1.2_

- [x] 2.2 Create User model in Device Service


  - Create or verify `User` model exists in `device_service/devices/models.py`
  - Ensure model has id (UUID), username, role, and created_at fields
  - Create migration if needed
  - _Requirements: 1.2_

- [x] 2.3 Create sync consumer for Device Service


  - Create `device_service/devices/consumers.py` with UserSyncConsumer class
  - Implement `callback()`, `handle_user_created()`, `handle_user_deleted()` methods
  - Add error handling and message acknowledgment logic
  - _Requirements: 1.2, 1.5_

- [x] 2.4 Create management command to run consumer


  - Create `device_service/devices/management/commands/consume_sync.py`
  - Implement Django management command that starts the UserSyncConsumer
  - _Requirements: 1.2_

- [x] 2.5 Update Device Service entrypoint


  - Modify `device_service/entrypoint.sh` to start sync consumer in background
  - Add consumer startup to Docker container initialization
  - _Requirements: 1.2_

- [x] 3. Implement Device Synchronization in Device Service


  - Add RabbitMQ publisher to Device Service that publishes device creation, update, and deletion events
  - Integrate publisher calls into device CRUD endpoints
  - _Requirements: 2.1, 2.3, 2.5_

- [x] 3.1 Create device sync publisher module


  - Create `device_service/devices/rabbitmq.py` with DeviceSyncPublisher class
  - Implement `publish_device_created()`, `publish_device_updated()`, `publish_device_deleted()` methods
  - Reuse RabbitMQ connection utilities
  - _Requirements: 2.1, 2.3, 2.5_

- [x] 3.2 Integrate publisher into Device Service views


  - Modify `device_service/devices/views.py` to call `publish_device_created()` after device creation
  - Add `publish_device_updated()` call to device update endpoint
  - Add `publish_device_deleted()` call to device deletion endpoint
  - _Requirements: 2.1, 2.3, 2.5_

- [x] 4. Update Monitoring Service sync consumer for devices



  - Extend existing sync consumer in Monitoring Service to handle device events
  - Ensure device records are created/updated/deleted in Monitoring database
  - _Requirements: 2.2, 2.4, 2.6_

- [x] 4.1 Update Monitoring Service sync consumer


  - Modify `monitoring_service/monitoring/consumers.py` SyncConsumer class
  - Add `handle_device_created()`, `handle_device_updated()`, `handle_device_deleted()` methods
  - Update `callback()` method to route device events to appropriate handlers
  - _Requirements: 2.2, 2.4, 2.6_

- [x] 5. Create Device Data Simulator application


  - Build standalone Python application that generates realistic smart meter readings
  - Implement time-based consumption patterns (night/day/evening)
  - Send measurements to RabbitMQ device_data_queue
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [x] 5.1 Create simulator project structure


  - Create `device_simulator/` directory
  - Create `simulator.py`, `config.json`, `requirements.txt`, `README.md` files
  - _Requirements: 3.1_

- [x] 5.2 Implement configuration loading


  - Write code in `simulator.py` to load configuration from `config.json`
  - Support command-line arguments to override config values
  - Validate configuration (device_id format, positive values, etc.)
  - _Requirements: 3.2, 3.8_

- [x] 5.3 Implement energy pattern generator

  - Create `EnergyPatternGenerator` class with `generate_measurement()` method
  - Implement time-based multipliers (night: 0.5, morning: 1.2, day: 0.8, evening: 1.5, late: 0.7)
  - Add random fluctuation (±10%) to simulate realistic variations
  - _Requirements: 3.3_

- [x] 5.4 Implement RabbitMQ publisher for simulator

  - Create `SimulatorPublisher` class with connection management
  - Implement `send_measurement()` method that publishes to device_data_queue
  - Add connection retry logic with exponential backoff
  - _Requirements: 3.4, 3.5, 3.6_

- [x] 5.5 Implement main simulator loop

  - Create main loop that generates and sends measurements at configured interval
  - Add console logging for each sent message
  - Implement graceful shutdown on Ctrl+C
  - _Requirements: 3.4, 3.7_

- [x] 5.6 Write simulator README


  - Document installation steps (pip install -r requirements.txt)
  - Document configuration file format
  - Provide usage examples with command-line arguments
  - Include troubleshooting section
  - _Requirements: 3.1_

- [-] 6. Implement Frontend Energy Visualization

  - Add React components for energy consumption charts
  - Integrate with Monitoring Service API
  - Display bar charts and line charts with date/device selection
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_



- [ ] 6.1 Install chart library dependencies
  - Add `recharts` and `date-fns` to `frontend/package.json`
  - Run `npm install` to install dependencies


  - _Requirements: 4.5, 4.6_

- [ ] 6.2 Create Monitoring API service
  - Create `frontend/src/services/monitoringApi.ts`
  - Implement `getDailyConsumption()` function that calls `/api/monitoring/hourly/daily/`
  - Implement `getDateRangeConsumption()` function for date ranges
  - Add error handling and token management
  - _Requirements: 4.4_

- [ ] 6.3 Create DeviceSelector component
  - Create `frontend/src/components/DeviceSelector.tsx`
  - Implement dropdown that fetches and displays user's devices
  - Emit onChange event when device is selected
  - _Requirements: 4.2_

- [ ] 6.4 Create DatePicker component
  - Create `frontend/src/components/DatePicker.tsx`
  - Implement calendar date picker component
  - Emit onChange event when date is selected
  - Default to today's date
  - _Requirements: 4.3_

- [ ] 6.5 Create EnergyBarChart component
  - Create `frontend/src/components/EnergyBarChart.tsx`
  - Use Recharts BarChart to display hourly consumption
  - Configure X-axis (hours 0-23) and Y-axis (kWh)
  - Add tooltips and legend
  - _Requirements: 4.5_

- [ ] 6.6 Create EnergyLineChart component
  - Create `frontend/src/components/EnergyLineChart.tsx`
  - Use Recharts LineChart to display consumption trend
  - Configure axes, tooltips, and styling
  - _Requirements: 4.6_

- [ ] 6.7 Create SummaryCards component
  - Create `frontend/src/components/SummaryCards.tsx`
  - Display cards for total daily consumption, peak hour, and average consumption
  - Calculate statistics from hourly data
  - _Requirements: 4.7_

- [ ] 6.8 Create EnergyDashboard page
  - Create `frontend/src/pages/EnergyDashboard.tsx`
  - Integrate DeviceSelector, DatePicker, charts, and summary cards
  - Implement data fetching logic when device or date changes
  - Handle loading and error states
  - Display "No data available" message when appropriate
  - _Requirements: 4.1, 4.4, 4.8, 4.9_

- [ ] 6.9 Add dashboard route
  - Update `frontend/src/App.tsx` or routing configuration
  - Add route for `/dashboard` or `/energy` pointing to EnergyDashboard
  - Add navigation link in main menu
  - _Requirements: 4.1_

- [x] 7. Create Deployment Diagram


  - Design UML deployment diagram showing complete system architecture
  - Include all containers, connections, ports, and queues
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7.1 Create deployment diagram


  - Use draw.io, PlantUML, or Lucidchart to create diagram
  - Show all 8 containers: Traefik, PostgreSQL, RabbitMQ, Auth Service, User Service, Device Service, Monitoring Service, Frontend
  - Show network connections between components
  - Indicate port mappings (80, 5432, 5672, 15672, 8000-8003)
  - Show RabbitMQ queues (device_data_queue, sync_queue) and their connections
  - Show database connections (auth_db, user_db, device_db, monitoring_db)
  - Export as PNG and PDF formats
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 8. Create Comprehensive README




  - Write detailed README with build, execution, and troubleshooting instructions
  - Document all API endpoints with examples
  - _Requirements: 5.6, 5.7, 5.8_

- [x] 8.1 Write main README file


  - Create or update `README.md` in project root
  - Add project overview and architecture description
  - Document prerequisites (Docker, Docker Compose, Node.js, Python)
  - Write step-by-step build instructions
  - Write step-by-step execution instructions
  - Document how to access each service (URLs, credentials)
  - Add troubleshooting section for common issues
  - _Requirements: 5.6, 5.7_

- [x] 8.2 Document API endpoints


  - Create `API_DOCUMENTATION.md` file
  - Document all Monitoring Service endpoints with request/response examples
  - Include authentication instructions
  - Provide curl and PowerShell examples
  - _Requirements: 5.8_

- [ ] 9. End-to-End Testing
  - Test complete data flow from user creation to chart visualization
  - Verify all synchronization mechanisms work correctly
  - _Requirements: All_

- [ ] 9.1 Test user synchronization
  - Create a new user via Auth Service API
  - Verify user appears in Device Service database
  - Verify user appears in Monitoring Service database
  - Delete user and verify removal from all services
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ] 9.2 Test device synchronization
  - Create a new device via Device Service API
  - Verify device appears in Monitoring Service database
  - Update device and verify changes sync
  - Delete device and verify removal
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 9.3 Test simulator and data flow
  - Configure simulator with test device ID
  - Run simulator for 1 hour (6 measurements)
  - Verify measurements appear in device_measurements table
  - Verify hourly aggregation is created
  - Query API to verify data is accessible
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [ ] 9.4 Test frontend charts
  - Login to frontend application
  - Navigate to energy dashboard
  - Select device and date with data
  - Verify bar chart displays correctly
  - Verify line chart displays correctly
  - Verify summary cards show correct values
  - Test with date that has no data
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

- [ ] 9.5 Verify deployment documentation
  - Follow README instructions on a clean system
  - Verify all services start correctly
  - Verify deployment diagram accurately represents system
  - Test all documented API endpoints
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
