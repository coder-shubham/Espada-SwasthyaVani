/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.espada.swasthyavani.messaging.MessageProducer;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */

@Controller
@RequestMapping("/api/message")
public class MessageController {

    @Autowired
    private MessageProducer messageProducer;

    @RequestMapping(value = "/send", method = RequestMethod.POST)
    public ResponseEntity<?> sendMessage(@RequestBody String message) {

        String topic = "backend-topic";
        // Logic to send message to the specified topic
        System.out.println("Message sent to topic " + topic + ": " + message);

        messageProducer.sendMessage(topic, message);

        return ResponseEntity.ok("Message sent to topic " + topic);
    }

}
