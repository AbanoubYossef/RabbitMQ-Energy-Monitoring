require('dotenv').config();
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const RabbitMQConsumer = require('./rabbitmqConsumer');
const SocketManager = require('./socketManager');

const app = express();
const server = http.createServer(app);

// CORS configuration
app.use(cors({
  origin: '*',
  credentials: true
}));

// Socket.io server with CORS
const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
    credentials: true
  },
  path: '/socket.io/'
});

// JWT Authentication Middleware for Socket.io
io.use((socket, next) => {
  const token = socket.handshake.auth.token || socket.handshake.headers.authorization?.split(' ')[1];
  
  if (!token) {
    console.log('❌ Connection rejected: No token provided');
    return next(new Error('Authentication error: No token provided'));
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET_KEY);
    socket.userId = decoded.user_id;
    socket.username = decoded.username;
    socket.role = decoded.role;
    console.log(`✅ User authenticated: ${socket.username} (${socket.role})`);
    next();
  } catch (err) {
    console.log('❌ Connection rejected: Invalid token');
    return next(new Error('Authentication error: Invalid token'));
  }
});

// Initialize Socket Manager
const socketManager = new SocketManager(io);

// Initialize RabbitMQ Consumer
const rabbitmqConsumer = new RabbitMQConsumer(socketManager);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    service: 'websocket-service',
    connections: socketManager.getConnectionCount(),
    timestamp: new Date().toISOString()
  });
});

// Start server
const PORT = process.env.PORT || 8004;
server.listen(PORT, () => {
  console.log('='.repeat(70));
  console.log('  WEBSOCKET SERVICE - Energy Management System');
  console.log('='.repeat(70));
  console.log(`✅ Server running on port ${PORT}`);
  console.log(`✅ Socket.io path: /socket.io/`);
  console.log(`✅ Health check: http://localhost:${PORT}/health`);
  console.log('='.repeat(70));
  
  // Start RabbitMQ consumers
  rabbitmqConsumer.start();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed');
    rabbitmqConsumer.close();
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('\nSIGINT signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed');
    rabbitmqConsumer.close();
    process.exit(0);
  });
});
