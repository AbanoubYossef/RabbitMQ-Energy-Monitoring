const amqp = require('amqplib');

/**
 * RabbitMQ Consumer - Consumes messages from queues and forwards to WebSocket clients
 */
class RabbitMQConsumer {
    constructor(socketManager) {
        this.socketManager = socketManager;
        this.connection = null;
        this.channel = null;
        this.notificationQueue = process.env.NOTIFICATION_QUEUE || 'notification_queue';
        this.chatQueue = process.env.CHAT_QUEUE || 'chat_messages_queue';
    }

    async connect() {
        const maxRetries = 5;
        const retryDelay = 2000;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const rabbitUrl = `amqp://${process.env.RABBITMQ_USER}:${process.env.RABBITMQ_PASS}@${process.env.RABBITMQ_HOST}:${process.env.RABBITMQ_PORT}`;

                console.log(`🐰 Connecting to RabbitMQ (attempt ${attempt}/${maxRetries})...`);
                this.connection = await amqp.connect(rabbitUrl);
                this.channel = await this.connection.createChannel();

                // Declare queues
                await this.channel.assertQueue(this.notificationQueue, { durable: true });
                await this.channel.assertQueue(this.chatQueue, { durable: true });

                console.log(`✅ Connected to RabbitMQ`);
                console.log(`✅ Listening on queues: ${this.notificationQueue}, ${this.chatQueue}`);

                // Handle connection errors
                this.connection.on('error', (err) => {
                    console.error('❌ RabbitMQ connection error:', err);
                });

                this.connection.on('close', () => {
                    console.log('⚠️  RabbitMQ connection closed. Reconnecting...');
                    setTimeout(() => this.connect(), retryDelay);
                });

                return true;
            } catch (error) {
                console.error(`❌ RabbitMQ connection attempt ${attempt} failed:`, error.message);
                if (attempt < maxRetries) {
                    console.log(`⏳ Retrying in ${retryDelay / 1000} seconds...`);
                    await new Promise(resolve => setTimeout(resolve, retryDelay));
                } else {
                    console.error('❌ Failed to connect to RabbitMQ after all retries');
                    return false;
                }
            }
        }
    }

    async start() {
        const connected = await this.connect();
        if (!connected) {
            console.error('❌ Cannot start consumers without RabbitMQ connection');
            return;
        }

        // Start consuming notifications
        this.consumeNotifications();

        // Start consuming chat messages
        this.consumeChatMessages();
    }

    async consumeNotifications() {
        try {
            await this.channel.consume(this.notificationQueue, (msg) => {
                if (msg !== null) {
                    try {
                        const notification = JSON.parse(msg.content.toString());
                        console.log('📬 Received notification:', notification);

                        // Process overconsumption notification
                        if (notification.type === 'overconsumption' || notification.device_id) {
                            this.handleOverconsumptionNotification(notification);
                        } else {
                            // Generic notification
                            this.handleGenericNotification(notification);
                        }

                        // Acknowledge message
                        this.channel.ack(msg);
                    } catch (error) {
                        console.error('❌ Error processing notification:', error);
                        // Reject and requeue
                        this.channel.nack(msg, false, true);
                    }
                }
            }, { noAck: false });

            console.log(`✅ Consuming from ${this.notificationQueue}`);
        } catch (error) {
            console.error('❌ Error setting up notification consumer:', error);
        }
    }

    async consumeChatMessages() {
        try {
            await this.channel.consume(this.chatQueue, (msg) => {
                if (msg !== null) {
                    try {
                        const chatMessage = JSON.parse(msg.content.toString());
                        console.log('📬 Received chat message:', chatMessage);

                        this.handleChatMessage(chatMessage);

                        // Acknowledge message
                        this.channel.ack(msg);
                    } catch (error) {
                        console.error('❌ Error processing chat message:', error);
                        // Reject and requeue
                        this.channel.nack(msg, false, true);
                    }
                }
            }, { noAck: false });

            console.log(`✅ Consuming from ${this.chatQueue}`);
        } catch (error) {
            console.error('❌ Error setting up chat consumer:', error);
        }
    }

    handleOverconsumptionNotification(notification) {
        // Format notification for frontend
        const formattedNotification = {
            type: 'overconsumption',
            title: 'Overconsumption Alert',
            message: `Device exceeded maximum consumption limit`,
            deviceId: notification.device_id,
            consumption: notification.consumption,
            maxConsumption: notification.max_consumption,
            severity: notification.severity || 'medium',
            timestamp: notification.timestamp || new Date().toISOString(),
            data: notification
        };

        // Send to specific user if user_id is provided
        if (notification.user_id) {
            this.socketManager.sendNotificationToUser(notification.user_id, formattedNotification);
        }
        // Send to all admins
        else {
            this.socketManager.sendNotificationToRole('admin', formattedNotification);
        }
    }

    handleGenericNotification(notification) {
        const formattedNotification = {
            type: notification.type || 'info',
            title: notification.title || 'Notification',
            message: notification.message,
            timestamp: notification.timestamp || new Date().toISOString(),
            data: notification
        };

        // Broadcast to all or specific user/role
        if (notification.user_id) {
            this.socketManager.sendNotificationToUser(notification.user_id, formattedNotification);
        } else if (notification.role) {
            this.socketManager.sendNotificationToRole(notification.role, formattedNotification);
        } else {
            this.socketManager.broadcastNotification(formattedNotification);
        }
    }

    handleChatMessage(chatMessage) {
        // Send chat message to recipient
        if (chatMessage.recipient_id) {
            this.socketManager.sendChatMessage(chatMessage.recipient_id, chatMessage);
        }

        // If it's a user message to admin, notify all admins
        if (chatMessage.to_admin) {
            this.socketManager.sendChatMessageToAdmins(chatMessage);
        }
    }

    async close() {
        try {
            if (this.channel) {
                await this.channel.close();
            }
            if (this.connection) {
                await this.connection.close();
            }
            console.log('✅ RabbitMQ connection closed');
        } catch (error) {
            console.error('❌ Error closing RabbitMQ connection:', error);
        }
    }
}

module.exports = RabbitMQConsumer;
