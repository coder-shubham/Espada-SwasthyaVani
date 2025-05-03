/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.service;

import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import com.espada.swasthyavani.config.ApplicationConfiguration;
import com.espada.swasthyavani.controller.ChatController;
import com.espada.swasthyavani.messaging.MessageProducer;
import com.espada.swasthyavani.model.KafkaMessagePayload;
import com.espada.swasthyavani.model.LanguageCode;
import com.espada.swasthyavani.model.PatientHistory;
import com.espada.swasthyavani.model.UserInfo;
import com.espada.swasthyavani.model.WebhookMessagePayload;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */

@Service
public class ChatService {

    private static final Logger logger = LoggerFactory.getLogger(ChatService.class);
    private final ApplicationConfiguration applicationConfiguration;
    private final SimpMessagingTemplate messagingTemplate;
    private final MessageProducer messageProducer;
    private final CacheService cacheService;

    @Autowired
    public ChatService(ApplicationConfiguration applicationConfiguration,
                       SimpMessagingTemplate messagingTemplate,
                       MessageProducer messageProducer,
                       CacheService cacheService) {
        this.applicationConfiguration = applicationConfiguration;
        this.messagingTemplate = messagingTemplate;
        this.messageProducer = messageProducer;
        this.cacheService = cacheService;
    }

    String startMessage = "Hello! \uD83D\uDC4B Welcome to SwasthyaVani.  \n"
            + "I am here to help you with your health-related problems.\n"
            + "\n"
            + "Please reply with the appropriate number:\n"
            + "\n"
            + "1\uFE0F⃣ Reply 1 for English  \n"
            + "2\uFE0F⃣ हिंदी के लिए उत्तर 2  \n"
            + "3\uFE0F⃣ मराठीसाठी उत्तर 3  \n"
            + "4\uFE0F⃣ తెలుగు కోసం జవాబు 4";

    @Async
    public void startChatSession(String chatId) throws Exception {
        // Start a chat session for the user
        logger.debug("Starting chat session for user: " + chatId);

        UserInfo userInfo = new UserInfo().setUserId(chatId).setLanguage(null);

        cacheService.saveToCache(chatId, userInfo);

        WebhookMessagePayload payload = new WebhookMessagePayload()
                .setChatId(chatId)
                .setContent(startMessage)
                .setMessageId(String.valueOf(System.currentTimeMillis()))
                .setType(WebhookMessagePayload.RequestType.TEXT.getValue())
                .setSender(WebhookMessagePayload.SenderType.SYSTEM.getValue())
                .setTimestamp(System.currentTimeMillis());

        Thread.sleep(2000);

        logger.debug("Sending start message to chatId: " + chatId);

        messagingTemplate.convertAndSend(String.format("/topic/chat-%s",chatId), payload);
    }

    @Async
    public void processUserMessage(Map<String, Object> message)  {
        // Process the user message here

        try{
            logger.debug("Processing user message: " + message);

            String chatId = (String) message.get("chatId");
            String userMessage = (String) message.get("content");
            String messageId = (String) message.get("messageId");

            UserInfo userInfo = (UserInfo) cacheService.getFromCache(chatId);

            if(userInfo.getLanguage() == null || userInfo.getLanguage().isEmpty()) {

                LanguageCode languageCode = LanguageCode.fromCode(userMessage);

                String language = languageCode.getLanguage();

                logger.debug("Language: " + language + "chatId: " + chatId);

                userInfo.setLanguage(language);

                cacheService.saveToCache(chatId, userInfo);

                sendIntroMessageAsPerLanguage(languageCode, chatId);

                return;

            }

            KafkaMessagePayload kafkaMessagePayload = new KafkaMessagePayload()
                    .setCallId(chatId)
                    .setContent(userMessage)
                    .setLanguage(userInfo.getLanguage())
                    .setRequestType(WebhookMessagePayload.RequestType.TEXT.getValue())
                    .setSender(WebhookMessagePayload.SenderType.USER.getValue())
                    .setTimestamp(System.currentTimeMillis())
                    .setMessageId(messageId);

            Object object = cacheService.getFromCache("telehistory");
            if(object != null){
                PatientHistory patientHistory = (PatientHistory) object;
                kafkaMessagePayload.setPatientHistory(patientHistory);
            }

            // Send the message to the Kafka topic

            ObjectMapper objectMapper = new ObjectMapper();

            messageProducer.sendMessage(applicationConfiguration.getProducerTopic(),
                    objectMapper.writeValueAsString(kafkaMessagePayload));
        }catch (Exception ex){
            logger.error("Exception in processing user message as: " + ex.getMessage());
        }catch (Error e){
            logger.error("Error in processing user message as: " + e.getMessage());
        }

    }

    private void sendIntroMessageAsPerLanguage(LanguageCode languageCode, String chatId) throws Exception {
        // Send the intro message as per the language code
        logger.debug("Sending intro message in " + languageCode + " to chatId: " + chatId);

        String message = switch (languageCode) {
            case HINDI -> "कृपया अपनी समस्या का विवरण दें।";
            case MARATHI -> "कृपया तुमची समस्या वर्णन करा.";
            case TELUGU -> "దయచేసి మీ సమస్యను వివరణ ఇవ్వండి.";
            default -> "Please describe your issue";
        };

        WebhookMessagePayload payload = new WebhookMessagePayload()
                .setChatId(chatId)
                .setContent(message)
                .setType(WebhookMessagePayload.RequestType.TEXT.getValue())
                .setSender(WebhookMessagePayload.SenderType.SYSTEM.getValue())
                .setTimestamp(System.currentTimeMillis());

        messagingTemplate.convertAndSend(String.format("/topic/chat-%s",chatId), payload);
    }


}
