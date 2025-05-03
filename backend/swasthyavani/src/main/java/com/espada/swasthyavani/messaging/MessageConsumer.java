/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.messaging;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import com.espada.swasthyavani.config.ApplicationConfiguration;
import com.espada.swasthyavani.controller.ChatController;
import com.espada.swasthyavani.model.KafkaMessagePayload;
import com.espada.swasthyavani.model.PatientHistory;
import com.espada.swasthyavani.model.WebhookMessagePayload;
import com.espada.swasthyavani.service.CacheService;
import com.espada.swasthyavani.service.MessageTask;
import com.espada.swasthyavani.utils.AudioChunkUtil;
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

    private static final Logger logger = LoggerFactory.getLogger(MessageConsumer.class);


    @Autowired
    private ApplicationConfiguration applicationConfiguration;

    @Autowired
    private SimpMessagingTemplate messagingTemplate;

    @Autowired
    private CacheService cacheService;

    private ExecutorService executorService;

    private Map<String, KafkaMessagePayload> messageCache;

    public MessageConsumer() {
        executorService = null;
    }

    @PostConstruct
    public void init() throws Exception{
        logger.debug("Initializing MessageConsumer...");
        executorService = Executors.newFixedThreadPool(10);
        messageCache = new HashMap<>();
    }

    @KafkaListener(topics = "${swasthyavani.consumer.topic}", groupId = "${spring.kafka.consumer.group-id}")
    public void consumeMessage(String message) {

        logger.debug("Message received from Kafka: " + message);

        processNewMessage(message);

    }

    public void processNewMessage(String message) {

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
                        cachePayload.setContent(cachePayload.getContent() +
                                (payload.getContent().isEmpty() ? "" : payload.getContent()));
                        payload = cachePayload;
                        messageCache.remove(payload.getMessageId());

                        logger.debug("Message is finished. Sending the message with messageId: " + payload.getMessageId());
                    }

                }else if(payload.getContent() != null && !payload.getContent().isEmpty()){
                    if(cachePayload != null) {
                        cachePayload.setContent(cachePayload.getContent() + payload.getContent());
                        cachePayload.setLastUpdateTime(System.currentTimeMillis());
                        messageCache.put(payload.getMessageId(), cachePayload);
                    }else{
                        payload.setLastUpdateTime(System.currentTimeMillis());
                        messageCache.put(payload.getMessageId(), payload);
                    }


                    logger.debug("Message is not finished yet. Caching the message with messageId: " + payload.getMessageId());
                    return;
                }else{
                    logger.debug("Message is empty. Not sending the message with messageId: " + payload.getMessageId() +
                            "sessionId: " + payload.getCallId());
                    return;
                }

            }


            if(payload.getContent() == null || payload.getContent().isEmpty()){
                logger.debug("Message is empty. Not sending the message with messageId: " + payload.getMessageId() +
                        "sessionId: " + payload.getCallId());
                return;
            }

            if (payload.getCallId() != null) {
                logger.debug("Sending message to callId: " + payload.getCallId());
                executorService.submit(new MessageTask(messagingTemplate, payload));
            }

            if(payload.getSpecialization() != null && !payload.getSpecialization().isEmpty()){
                PatientHistory patientHistory = new PatientHistory()
                        .setPatientId(payload.getCallId())
                        .setSpecialist(payload.getSpecialization())
                        .setSummary(payload.getSummary());

                cacheService.saveToCache("telehistory", patientHistory);

                sendTeleConsultationBookedMessage(payload);

            }

        } catch (Exception ex) {
            logger.error("Error in processing message to Websocket: " + ex.getMessage());
        }

    }


    @Async
    public void sendTeleConsultationBookedMessage(KafkaMessagePayload payload)
            throws Exception {

        KafkaMessagePayload newPayload = new KafkaMessagePayload()
                .setCallId(payload.getCallId())
                .setContent(payload.getContent())
                .setLanguage(payload.getLanguage())
                .setRequestType(payload.getRequestType())
                .setSender(WebhookMessagePayload.SenderType.AI.getValue())
                .setTimestamp(System.currentTimeMillis())
                .setMessageId(payload.getMessageId());

        if(payload.getRequestType().equalsIgnoreCase(WebhookMessagePayload.RequestType.TEXT.getValue())){

            switch (payload.getLanguage()){
                case "en":
                    newPayload.setContent("We have booked your teleconsultation with required specialist and here is the link for same");
                    break;
                case "hi":
                    newPayload.setContent("हमने आपके लिए आवश्यक विशेषज्ञ के साथ टेलीपरामर्श बुक कर दिया है। यह रहा उसका लिंक");
                    break;
                case "mr":
                    newPayload.setContent("आवश्यक तज्ञासोबत तुमचं टेली-कन्सल्टेशन बुक केलं आहे. हा त्यासाठीचा लिंक आहे");
                    break;
                case "te":
                    newPayload.setContent("అవసరమైన నిపుణుడితో మీ టెలీకాన్సల్టేషన్\u200Cను బుక్ చేశాము. దీనికిగిన లింక్ ఇది");
                    break;
                default:
                    payload.setContent("Your teleconsultation has been booked successfully.");
            }

            newPayload.setContent(String.format("%s:https://meet.google.com/%s", newPayload.getContent(),
                    System.currentTimeMillis()));

            newPayload.setRequestType(WebhookMessagePayload.RequestType.TEXT.getValue());

            logger.debug("Sending message to chatId: {} for teleconsultation ",payload.getCallId());

            executorService.submit(new MessageTask(messagingTemplate, newPayload));

        }else{

            String audioFile;
            switch (payload.getLanguage()){
                case "hi":
                    audioFile = "audio/hindi_tele.mp3";
                    break;
                case "mr":
                    audioFile = "audio/marathi_tele.mp3";
                    break;
                case "te":
                    audioFile = "audio/telugu_tele.mp3";
                    break;
                default:
                    audioFile = "audio/english_tele.mp3";
            }

            List<String> chunks = AudioChunkUtil.chunkAudioFile(audioFile, 1024 * 10); // 4KB chunks

            logger.debug("Sending message to callId: {} for teleconsultation ",payload.getCallId());

            for(String chunk: chunks){
                newPayload.setContent(chunk);

                newPayload.setRequestType(WebhookMessagePayload.RequestType.AUDIO.getValue());
                executorService.submit(new MessageTask(messagingTemplate, newPayload));
                Thread.sleep(500); //Stream
            }

        }
        }

    @Scheduled(fixedDelay = 10000)
    public void cleanUpCache() {
        System.out.println("Checking up finished message...");
        for(Map.Entry<String, KafkaMessagePayload> entry : messageCache.entrySet()){
            KafkaMessagePayload payload = entry.getValue();
            long currentTime = System.currentTimeMillis();
            if(currentTime - payload.getLastUpdateTime() > 10000){
                logger.debug("Removing inactive message with messageId: " + payload.getMessageId());
                logger.debug("Submitting message for callId: " + payload.getCallId() + " to executor service from Cleaning");
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
