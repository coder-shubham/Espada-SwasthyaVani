/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.messaging;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import com.espada.swasthyavani.controller.ChatController;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */

@Service
public class MessageProducer {

    private static final Logger logger = LoggerFactory.getLogger(MessageProducer.class);

    private final KafkaTemplate<String, String> kafkaTemplate;

    public MessageProducer(KafkaTemplate<String, String> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    public void sendMessage(String topic, String message) {

        try{
            kafkaTemplate.send(topic, message);

            logger.debug("Message sent to topic: " + topic + ", message: " + message);

        }catch (Exception e){
            logger.error("Exception while sending message to Kafka topic: " + topic, e);
        }catch (Error e){
            logger.error("Error while sending message to Kafka topic: " + topic, e);
        }

    }

}
