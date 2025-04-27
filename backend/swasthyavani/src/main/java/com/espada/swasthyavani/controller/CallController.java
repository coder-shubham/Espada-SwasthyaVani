/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.controller;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
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
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import com.espada.swasthyavani.config.ApplicationConfiguration;
import com.espada.swasthyavani.messaging.MessageProducer;
import com.espada.swasthyavani.model.KafkaMessagePayload;
import com.espada.swasthyavani.model.LanguageCode;
import com.espada.swasthyavani.model.UserInfo;
import com.espada.swasthyavani.model.WebhookMessagePayload;
import com.espada.swasthyavani.service.CacheService;
import com.espada.swasthyavani.service.CallService;
import com.espada.swasthyavani.utils.AudioChunkUtil;
import com.fasterxml.jackson.databind.ObjectMapper;

import jakarta.annotation.PostConstruct;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Controller
@RequestMapping("/api/calls")
public class CallController {

    private final ApplicationConfiguration applicationConfiguration;
    private final SimpMessagingTemplate messagingTemplate;
    private final MessageProducer messageProducer;
    private final CacheService cacheService;
    private final CallService callService;


    @Autowired
    public CallController(ApplicationConfiguration applicationConfiguration,
                          SimpMessagingTemplate messagingTemplate,
                          MessageProducer messageProducer,
                          CacheService cacheService,
                          CallService callService) {
        this.applicationConfiguration = applicationConfiguration;
        this.messagingTemplate = messagingTemplate;
        this.cacheService = cacheService;
        this.callService = callService;
        this.messageProducer = messageProducer;
    }

    String[] startAudioFiles = {
            "audio/audio1.mp3",
            "audio/audio2.mp3",
            "audio/select_your_lang.mp3",
            "audio/english_select.mp3",
            "audio/hindi_select.mp3",
            "audio/marathi_select.mp3",
            "audio/telugu_select.mp3",
    };

    @RequestMapping(value = "/start", method = RequestMethod.POST)
    private ResponseEntity<?> startCall() throws Exception {

        String callId = String.valueOf(System.currentTimeMillis());

        System.out.println("Starting call with ID: " + callId);

        startCallSession(callId);

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("callId", callId));

    }


    @RequestMapping(value = "/dtmf", method = RequestMethod.POST)
    private ResponseEntity<?> callDtmfReceiveFromCustomer(@RequestBody Map<String, String> payload
    ) {

        try {
            String digit = payload.get("digit");
            String messageId = payload.get("messageId");
            String callId = payload.get("callId");

            System.out.println("Received DTMF: " + digit);
            System.out.println("With messageId: " + messageId);

            processDtmfRequest(digit, messageId, callId);

            //TODO: Handle DTMF for other cases

        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            return ResponseEntity.status(500).body("Failed to process DTMF.");
        }

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("callId", System.currentTimeMillis()));

    }

    @RequestMapping(value = "/audio", method = RequestMethod.POST)
    private ResponseEntity<?> callAudioReceiveFromCustomer(
            @RequestParam("audio") MultipartFile audioFile,
            @RequestParam("messageId") String messageId,
            @RequestParam("callId") String callId
    ) {

        try {
            processAudioRequest(audioFile, messageId, callId);
        } catch (IOException e) {
            return ResponseEntity.status(500).body("Failed to read audio file.");
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            return ResponseEntity.status(500).body("Failed to process audio file.");
        }

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("callId", System.currentTimeMillis()));

    }

    @Async
    public void startCallSession(String callId) throws Exception{
        callService.startCallSession(callId);
    }

    @Async
    public void endCallSession(String callId) throws Exception{
        callService.endCallSession(callId);
    }

    @Async
    public void processDtmfRequest(String digit, String messageId, String callId) throws Exception{
        callService.processDtmfRequest(digit, messageId, callId);
    }

    @Async
    public void processAudioRequest(MultipartFile audioFile, String messageId, String callId) throws Exception{
        callService.processNewAudioMessage(audioFile, messageId, callId);
    }

    @Async
    public void sendAudioFileToAi(String messageData) throws Exception{
        messageProducer.sendMessage(applicationConfiguration.getProducerTopic(), messageData);
    }


    @Async
    public void sendLanguageAudioIntro(LanguageCode languageCode, String callId) throws Exception {

        switch (languageCode) {
            case HINDI:
                streamAudioFiles(new String[]{"audio/hindi_intro.mp3"}, WebhookMessagePayload.RequestType.AUDIO.getValue(),
                        String.valueOf(System.currentTimeMillis()), callId);
                break;
            case MARATHI:
                streamAudioFiles(new String[]{"audio/marathi_intro.mp3"}, WebhookMessagePayload.RequestType.AUDIO.getValue(),
                        String.valueOf(System.currentTimeMillis()), callId);
                break;
            case TELUGU:
                streamAudioFiles(new String[]{"audio/telugu_intro.mp3"}, WebhookMessagePayload.RequestType.AUDIO.getValue(),
                        String.valueOf(System.currentTimeMillis()), callId);
                break;
            default:
                streamAudioFiles(new String[]{"audio/english_intro.mp3"}, WebhookMessagePayload.RequestType.AUDIO.getValue(),
                        String.valueOf(System.currentTimeMillis()), callId);
        }


    }

    @Async
    public void streamAudioFiles(String[] audioFiles, String requestType, String messageId, String callId) throws Exception {

        for (String audioFile : audioFiles) {
            List<String> chunks = AudioChunkUtil.chunkAudioFile(audioFile, 1024 * 4); // 4KB chunks

            for (String chunk : chunks) {

                WebhookMessagePayload payload = new WebhookMessagePayload()
                        .setCallId(callId)
                        .setMessageId(messageId)
                        .setContent(chunk)
                        .setRequestMessageType(requestType)
                        .setType(requestType)
                        .setSender(WebhookMessagePayload.SenderType.SYSTEM.getValue())
                        .setTimestamp(System.currentTimeMillis());

                System.out.println("Sending message to callId: " + callId);

                messagingTemplate.convertAndSend(String.format("/topic/call-%s",callId), payload);

                Thread.sleep(500); //Stream
            }

            Thread.sleep(1000); //Pause
        }
    }

    @RequestMapping(value = "/end", method = RequestMethod.POST)
    private ResponseEntity<?> stopCall(@RequestBody Map<String, String> payload) throws Exception {

        String callId = payload.get("callId");

        System.out.println("Stopping call with ID: " + callId);

        endCallSession(callId);
        // Logic to stop the call

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("callId", callId));

    }


}
