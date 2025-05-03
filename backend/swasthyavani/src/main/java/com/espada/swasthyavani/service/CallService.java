/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.service;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import com.espada.swasthyavani.config.ApplicationConfiguration;
import com.espada.swasthyavani.controller.ChatController;
import com.espada.swasthyavani.messaging.MessageProducer;
import com.espada.swasthyavani.model.KafkaMessagePayload;
import com.espada.swasthyavani.model.LanguageCode;
import com.espada.swasthyavani.model.PatientHistory;
import com.espada.swasthyavani.model.UserInfo;
import com.espada.swasthyavani.model.WebhookMessagePayload;
import com.espada.swasthyavani.utils.AudioChunkUtil;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */
@Service
public class CallService {

    private static final Logger logger = LoggerFactory.getLogger(CallService.class);

    private final ApplicationConfiguration applicationConfiguration;
    private final SimpMessagingTemplate messagingTemplate;
    private final MessageProducer messageProducer;
    private final CacheService cacheService;

    String[] startAudioFiles = {
            "audio/audio1.mp3",
            "audio/audio2.mp3",
            "audio/select_your_lang.mp3",
            "audio/english_select.mp3",
            "audio/hindi_select.mp3",
            "audio/marathi_select.mp3",
            "audio/telugu_select.mp3",
    };

    @Autowired
    public CallService(ApplicationConfiguration applicationConfiguration,
                       SimpMessagingTemplate messagingTemplate,
                       MessageProducer messageProducer,
                       CacheService cacheService) {
        this.applicationConfiguration = applicationConfiguration;
        this.messagingTemplate = messagingTemplate;
        this.messageProducer = messageProducer;
        this.cacheService = cacheService;
    }


    public void startCallSession(String callId) throws Exception {

        UserInfo userInfo = new UserInfo().setUserId(callId).setLanguage(null);

        cacheService.saveToCache(callId, userInfo);

        streamAudioFiles(startAudioFiles, WebhookMessagePayload.RequestType.DTMF.getValue(),
                String.valueOf(System.currentTimeMillis()), callId);

    }

    public void endCallSession(String callId) throws Exception {
        logger.debug("Ending call session for callId: " + callId);

        cacheService.removeFromCache(callId);

    }

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


    public void processNewAudioMessage(MultipartFile audioFile,
                                       String messageId,
                                       String callId) throws Exception {

        byte[] audioBytes = audioFile.getBytes();
        String originalFilename = audioFile.getOriginalFilename();


        logger.debug("Received audio file: " + originalFilename);
        logger.debug("With messageId: " + messageId + " and callId: " + callId);
        logger.debug("File size: " + audioBytes.length + " bytes");

        String UPLOAD_DIR = "/mnt/shared-dir/";
        File uploadDir = new File(UPLOAD_DIR);
        if (!uploadDir.exists()) {
            uploadDir.mkdirs();
        }

        String fileName = messageId + "_" + System.currentTimeMillis() + "_" + audioFile.getOriginalFilename();
        Path filePath = Paths.get(UPLOAD_DIR, fileName);

        Files.write(filePath, audioBytes);

        logger.debug("File saved at: " + filePath.toString());

        UserInfo userInfo = (UserInfo) cacheService.getFromCache(callId);

        KafkaMessagePayload payload = new KafkaMessagePayload()
                .setCallId(callId)
                .setMessageId(messageId)
                .setContent(fileName)
                .setLanguage(userInfo.getLanguage())
                .setRequestType(WebhookMessagePayload.RequestType.AUDIO.getValue())
                .setTimestamp(System.currentTimeMillis());

        Object object = cacheService.getFromCache("telehistory");
        if(object != null){
            PatientHistory patientHistory = (PatientHistory) object;
            payload.setPatientHistory(patientHistory);
        }

        ObjectMapper objectMapper = new ObjectMapper();

        messageProducer.sendMessage(applicationConfiguration.getProducerTopic(),
                objectMapper.writeValueAsString(payload));


    }

    public void processDtmfRequest(String digit, String messageId, String callId) throws Exception {

        Object object = cacheService.getFromCache(callId);

        UserInfo userInfo = (UserInfo) object;

        logger.debug("UserInfo: " + userInfo);

        if (userInfo.getLanguage() == null || userInfo.getLanguage().isEmpty()) {

            LanguageCode languageCode = LanguageCode.fromCode(digit);

            String language = languageCode.getLanguage();

            logger.debug("Language: " + language + "callId: " + callId);

            userInfo.setLanguage(language);

            cacheService.saveToCache(callId, userInfo);

            sendLanguageAudioIntro(languageCode, callId);

            return;
        }

    }


    private void streamAudioFiles(String[] audioFiles, String requestType, String messageId, String callId) throws Exception {

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

                logger.debug("Sending message to callId: " + callId);

                messagingTemplate.convertAndSend(String.format("/topic/call-%s", callId), payload);

                Thread.sleep(500); //Stream
            }

            Thread.sleep(1000); //Pause
        }
    }


}
