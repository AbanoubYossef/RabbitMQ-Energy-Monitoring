/**
 * Socket Manager - Handles Socket.io connections and messaging
 */
class SocketManager {
    constructor(io) {
        this.io = io;
        this.userSockets = new Map(); // userId -> Set of socket IDs
        this.setupConnectionHandlers();
    }

    setupConnectionHandlers() {
        this.io.on('connection', (socket) => {
            const userId = socket.userId;
            const username = socket.username;
            const role = socket.role;

            console.log(`🔌 Client connected: ${username} (${role}) - Socket ID: ${socket.id}`);

            // Add socket to user's socket set
            if (!this.userSockets.has(userId)) {
                this.userSockets.set(userId, new Set());
            }
            this.userSockets.get(userId).add(socket.id);

            // Join user-specific room
            socket.join(`user:${userId}`);

            // Join role-specific room
            socket.join(`role:${role}`);

            // Send connection confirmation
            socket.emit('connected', {
                message: 'Connected to WebSocket server',
                userId: userId,
                username: username,
                role: role,
                timestamp: new Date().toISOString()
            });

            // Handle chat messages from client
            socket.on('chat_message', (data) => {
                console.log(`💬 Chat message from ${username}:`, data);
                // Echo back to sender (will be handled by customer support service)
                socket.emit('chat_message_received', {
                    ...data,
                    timestamp: new Date().toISOString()
                });
            });

            // Handle typing indicator
            socket.on('typing', (data) => {
                socket.broadcast.to(`user:${userId}`).emit('typing', {
                    username: username,
                    isTyping: data.isTyping
                });
            });

            // Handle disconnect
            socket.on('disconnect', () => {
                console.log(`🔌 Client disconnected: ${username} - Socket ID: ${socket.id}`);

                // Remove socket from user's socket set
                if (this.userSockets.has(userId)) {
                    this.userSockets.get(userId).delete(socket.id);
                    if (this.userSockets.get(userId).size === 0) {
                        this.userSockets.delete(userId);
                    }
                }
            });

            // Handle errors
            socket.on('error', (error) => {
                console.error(`❌ Socket error for ${username}:`, error);
            });
        });
    }

    /**
     * Send notification to specific user
     */
    sendNotificationToUser(userId, notification) {
        const room = `user:${userId}`;
        this.io.to(room).emit('notification', notification);
        console.log(`📢 Notification sent to user ${userId}:`, notification.type);
    }

    /**
     * Send notification to all users with specific role
     */
    sendNotificationToRole(role, notification) {
        const room = `role:${role}`;
        this.io.to(room).emit('notification', notification);
        console.log(`📢 Notification sent to role ${role}:`, notification.type);
    }

    /**
     * Broadcast notification to all connected clients
     */
    broadcastNotification(notification) {
        this.io.emit('notification', notification);
        console.log(`📢 Notification broadcasted to all:`, notification.type);
    }

    /**
     * Send chat message to specific user
     */
    sendChatMessage(userId, message) {
        const room = `user:${userId}`;
        this.io.to(room).emit('chat_message', message);
        console.log(`💬 Chat message sent to user ${userId}`);
    }

    /**
     * Send chat message to admin users
     */
    sendChatMessageToAdmins(message) {
        const room = 'role:admin';
        this.io.to(room).emit('admin_chat_message', message);
        console.log(`💬 Chat message sent to admins`);
    }

    /**
     * Get total number of connected clients
     */
    getConnectionCount() {
        return this.io.sockets.sockets.size;
    }

    /**
     * Get number of unique users connected
     */
    getUserCount() {
        return this.userSockets.size;
    }

    /**
     * Check if user is online
     */
    isUserOnline(userId) {
        return this.userSockets.has(userId) && this.userSockets.get(userId).size > 0;
    }
}

module.exports = SocketManager;
