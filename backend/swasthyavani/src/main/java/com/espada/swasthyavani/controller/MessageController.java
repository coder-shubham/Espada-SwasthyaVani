/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.controller;

import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.espada.swasthyavani.messaging.MessageProducer;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */

@Controller
@RequestMapping("/api/message")
public class MessageController {

    private static final Logger logger = LoggerFactory.getLogger(MessageController.class);

    @Autowired
    private MessageProducer messageProducer;

    @RequestMapping(value = "/send", method = RequestMethod.POST)
    public ResponseEntity<?> sendMessage(@RequestBody Map<Object, String> message) {

        try{
            String topic = "backend-topic";

            ObjectMapper objectMapper = new ObjectMapper();
            String messageString = objectMapper.writeValueAsString(message);
            // Logic to send message to the specified topic
            logger.debug("Sending message to topic: " + topic);

            messageProducer.sendMessage(topic, messageString);

            return ResponseEntity.ok("Message sent to topic " + topic);
        }catch (Exception ex){
            logger.error("Error while sending message: " + ex.getMessage());
            return ResponseEntity.status(500).body("Error while sending message");
        }

    }

}
