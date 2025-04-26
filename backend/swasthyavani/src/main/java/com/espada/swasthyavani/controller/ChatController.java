/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.controller;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Controller
@RequestMapping("/api/chat")
public class ChatController {

    @Autowired
    public SimpMessagingTemplate messagingTemplate;

    @RequestMapping(value = "/message", method = RequestMethod.POST)
    private ResponseEntity<?> userChatMessage(@RequestBody Map<String, Object> message) throws Exception {

        System.out.println("Message: " + message);

        messagingTemplate.convertAndSend("/topic/chat",
                Map.of("content", "Hello World!",
                        "type", "chat",
                        "sender", "System",
                        "timestamp", System.currentTimeMillis()));
        return ResponseEntity.status(HttpStatus.OK).body(Map.of("success", true));

    }

}
