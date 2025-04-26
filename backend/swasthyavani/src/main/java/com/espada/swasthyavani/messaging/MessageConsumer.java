/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.messaging;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Service
public class MessageConsumer {

    @Autowired
    public SimpMessagingTemplate messagingTemplate;

    @KafkaListener(topics = "backend-topic", groupId = "backend-group")
    public void consumeMessage(String message) {
        // Logic to consume message from Kafka topic
        System.out.println("Consumed message: " + message);

        Thread thread = new Thread(() -> {
            try {
                // Simulate some processing time
                sendMessageToWebSocket(message);
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });

        thread.start();

    }

    private void sendMessageToWebSocket(String message)  {
        // Logic to send the consumed message to WebSocket

        try{
            ObjectMapper objectMapper = new ObjectMapper();

            Map<String, Object> messageMap = objectMapper.readValue(message, new TypeReference<Map<String, Object>>() {});
            String callId = (String) messageMap.getOrDefault("callId", "");

            Map<String, Object> newMessageObject =
                    Map.of("audioData", messageMap.get("content"),
                                "requestMessageType", messageMap.get("request_type"),
                            "type", messageMap.get("request_type"),
                            "sender", "System",
                                "callId", messageMap.get("user_id"),
                            "messageId", messageMap.get("request_id"),
                            "timestamp", System.currentTimeMillis());

            if(callId != null && !callId.isEmpty()) {
                System.out.println("Sending to callId: " + callId + " message to WebSocket: " + newMessageObject);
                messagingTemplate.convertAndSend(String.format("/topic/call-%s",callId), newMessageObject);
            }
        }catch (Exception ex){
            System.out.println("Error in sending message to WebSocket: " + ex.getMessage());
        }


    }

}
