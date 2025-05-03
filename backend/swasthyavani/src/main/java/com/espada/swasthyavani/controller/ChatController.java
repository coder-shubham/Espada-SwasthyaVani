/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.controller;

import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.espada.swasthyavani.messaging.MessageProducer;
import com.espada.swasthyavani.service.ChatService;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Controller
@RequestMapping("/api/chat")
public class ChatController {

    private static final Logger logger = LoggerFactory.getLogger(ChatController.class);

    private final ChatService chatService;
    private final MessageProducer messageProducer;


    @Autowired
    public ChatController(ChatService chatService, MessageProducer messageProducer) {
        this.chatService = chatService;
        this.messageProducer = messageProducer;
    }

    @RequestMapping(value = "/start", method = RequestMethod.POST)
    public ResponseEntity<?> startCall() throws Exception {

        String chatId = String.valueOf(System.currentTimeMillis());

        System.out.println("Chat ID: " + chatId);
        logger.debug("Starting chat with ID: " + chatId);

        chatService.startChatSession(chatId);

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("chatId", chatId));

    }

    @RequestMapping(value = "/message", method = RequestMethod.POST)
    public ResponseEntity<?> userChatMessage(@RequestBody Map<String, Object> message){

        try{

            logger.debug("Message Received from User over SMS: " + message);

            chatService.processUserMessage(message);

            //        processUserMessage(message);
            return ResponseEntity.status(HttpStatus.OK).body(Map.of("success", true));
        }catch (Exception ex){
            logger.error("Error in processing message: " + ex.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("error", "Internal Server Error"));
        }

    }

}
