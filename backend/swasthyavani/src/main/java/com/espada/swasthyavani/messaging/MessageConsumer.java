/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.messaging;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Service
public class MessageConsumer {

    @KafkaListener(topics = "backend-topic", groupId = "backend-group")
    public void consumeMessage(String message) {
        // Logic to consume message from Kafka topic
        System.out.println("Consumed message: " + message);
    }

}
