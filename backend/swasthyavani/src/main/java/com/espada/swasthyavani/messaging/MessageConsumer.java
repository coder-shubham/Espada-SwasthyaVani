/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.messaging;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import com.espada.swasthyavani.config.ApplicationConfiguration;
import com.espada.swasthyavani.model.KafkaMessagePayload;
import com.espada.swasthyavani.model.WebhookMessagePayload;
import com.espada.swasthyavani.service.MessageTask;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonNode;
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

    @Autowired
    private SimpMessagingTemplate messagingTemplate;

    private ExecutorService executorService;

    private Map<String, KafkaMessagePayload> messageCache;

    public MessageConsumer() {
        executorService = null;
    }

    @PostConstruct
    public void init() throws Exception{
        executorService = Executors.newFixedThreadPool(10);
        messageCache = new HashMap<>();

    }

    @KafkaListener(topics = "${swasthyavani.consumer.topic}", groupId = "${spring.kafka.consumer.group-id}")
    public void consumeMessage(String message) {
        System.out.println("Consumed message: " + message);

        processNewMessage(message);

    }

    private void processNewMessage(String message) {

        try {
            ObjectMapper objectMapper = new ObjectMapper();

            objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

            JsonNode node = objectMapper.readTree(message);
            KafkaMessagePayload payload = objectMapper.treeToValue(node, KafkaMessagePayload.class);

            payload.setSender(WebhookMessagePayload.SenderType.AI.getValue());

            if(payload.getRequestType().equalsIgnoreCase(WebhookMessagePayload.RequestType.TEXT.getValue())){
                KafkaMessagePayload cachePayload = messageCache.getOrDefault(payload.getMessageId(), null);

                if(payload.getIsFinished()){
                    if(cachePayload != null) {
                        cachePayload.setContent(cachePayload.getContent() + "\n" + payload.getContent());
                        payload = cachePayload;
                        messageCache.remove(payload.getMessageId());

                        System.out.println("Message is finished. Sending the message with messageId: " + payload.getMessageId());
                    }

                }else{
                    if(cachePayload != null) {
                        cachePayload.setContent(cachePayload.getContent() + "\n" + payload.getContent());
                        cachePayload.setLastUpdateTime(System.currentTimeMillis());
                        messageCache.put(payload.getMessageId(), cachePayload);
                    }else{
                        payload.setLastUpdateTime(System.currentTimeMillis());
                        messageCache.put(payload.getMessageId(), payload);
                    }

                    System.out.println("Message is not finished yet. Caching the message with messageId: " + payload.getMessageId());
                    return;
                }

            }

            if (payload.getCallId() != null) {
                System.out.println("Submitting message for callId: " + payload.getCallId() + " to executor service");
                executorService.submit(new MessageTask(messagingTemplate, payload));
            }

        } catch (Exception ex) {
            System.out.println("Error in sending message to WebSocket: " + ex.getMessage());
        }

    }

    @Scheduled(fixedDelay = 10000)
    public void cleanUpCache() {
        System.out.println("Checking up finished message...");
        for(Map.Entry<String, KafkaMessagePayload> entry : messageCache.entrySet()){
            KafkaMessagePayload payload = entry.getValue();
            long currentTime = System.currentTimeMillis();
            if(currentTime - payload.getLastUpdateTime() > 10000){
                System.out.println("Removing inactive message with messageId: " + payload.getMessageId());
                System.out.println("Submitting message for callId: " + payload.getCallId() + " to executor service from Cleaning");
                executorService.submit(new MessageTask(messagingTemplate, payload));
                messageCache.remove(entry.getKey());
            }
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
