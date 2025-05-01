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
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.espada.swasthyavani.service.ChatService;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Controller
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService chatService;

    @Autowired
    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @RequestMapping(value = "/start", method = RequestMethod.POST)
    private ResponseEntity<?> startCall() throws Exception {

        String chatId = String.valueOf(System.currentTimeMillis());

        System.out.println("Starting chat with ID: " + chatId);

        chatService.startChatSession(chatId);

//        startChatSession(chatId);

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("chatId", chatId));

    }

    @RequestMapping(value = "/message", method = RequestMethod.POST)
    private ResponseEntity<?> userChatMessage(@RequestBody Map<String, Object> message) throws Exception {

        System.out.println("Message Received from User over SMS: " + message);
        chatService.processUserMessage(message);

//        processUserMessage(message);
        return ResponseEntity.status(HttpStatus.OK).body(Map.of("success", true));

    }


//    @Async
//    private void startChatSession(String chatId) throws Exception {
//        chatService.startChatSession(chatId);
//    }
//
//    @Async
//    private void processUserMessage(Map<String, Object> message) throws Exception {
//        chatService.processUserMessage(message);
//    }

}
