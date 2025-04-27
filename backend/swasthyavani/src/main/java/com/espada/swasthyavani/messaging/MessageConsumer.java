/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.messaging;

import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import com.espada.swasthyavani.config.ApplicationConfiguration;
import com.espada.swasthyavani.model.KafkaMessagePayload;
import com.espada.swasthyavani.model.WebhookMessagePayload;
import com.espada.swasthyavani.service.MessageTask;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Service
public class MessageConsumer {


    @Autowired
    private ApplicationConfiguration applicationConfiguration;

    private ExecutorService executorService;


    public MessageConsumer() {
        executorService = null;
    }

    @PostConstruct
    public void init() throws Exception{
        executorService = Executors.newFixedThreadPool(10);

    }

    @KafkaListener(topics = "${swasthyavani.consumer.topic}", groupId = "${spring.kafka.consumer.group-id}")
    public void consumeMessage(String message) {
        System.out.println("Consumed message: " + message);

        processNewMessage(message);

    }

    private void processNewMessage(String message) {

        try {
            ObjectMapper objectMapper = new ObjectMapper();

            KafkaMessagePayload payload = objectMapper.convertValue(message, KafkaMessagePayload.class);
            payload.setSender(WebhookMessagePayload.SenderType.AI.getValue());

            if (payload.getCallId() != null) {
                System.out.println("Submitting message for callId: " + payload.getCallId() + " to executor service");
                executorService.submit(new MessageTask(payload));
            }

        } catch (Exception ex) {
            System.out.println("Error in sending message to WebSocket: " + ex.getMessage());
        }

    }

    @PreDestroy
    public void shutdown() throws InterruptedException {

        if (executorService != null) {
            executorService.shutdown();
            executorService.awaitTermination(10000, TimeUnit.MILLISECONDS);
        }
    }

}
