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
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import com.espada.swasthyavani.messaging.MessageProducer;
import com.espada.swasthyavani.utils.AudioChunkUtil;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Controller
@RequestMapping("/api/calls")
public class CallController {

    @Autowired
    public SimpMessagingTemplate messagingTemplate;

    @Autowired
    private MessageProducer messageProducer;

    private static String CALL_ID = "callId";

    @RequestMapping(value = "/start", method = RequestMethod.POST)
    private ResponseEntity<?> startCall() throws Exception {

        CALL_ID = String.valueOf(System.currentTimeMillis());

        System.out.println("Starting call with ID: " + CALL_ID);

        streamAudioFiles(String.valueOf(System.currentTimeMillis()));

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("callId", CALL_ID));

    }

    @RequestMapping(value = "/audio", method = RequestMethod.POST)
    private ResponseEntity<?> callAudioReceiveFromCustomer(
            @RequestParam("audio") MultipartFile audioFile,
            @RequestParam("messageId") String messageId
    ) {

        try {
            byte[] audioBytes = audioFile.getBytes();
            String originalFilename = audioFile.getOriginalFilename();

            System.out.println("Received audio file: " + originalFilename);
            System.out.println("With messageId: " + messageId);
            System.out.println("File size: " + audioBytes.length + " bytes");

            String UPLOAD_DIR = "../../tmp/userAudioData";
            File uploadDir = new File(UPLOAD_DIR);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }

            String fileName = messageId + "_" + System.currentTimeMillis() + "_" + audioFile.getOriginalFilename();
            Path filePath = Paths.get(UPLOAD_DIR, fileName);

            Files.write(filePath, audioFile.getBytes());

            System.out.println("File saved at: " + filePath.toString());

            Map<String, Object> messageData = Map.of(
                    "content", filePath.toString(),
                    "request_id", messageId,
                    "request_type", "audio",
                    "user_id", CALL_ID
            );

            ObjectMapper objectMapper = new ObjectMapper();

            sendAudioFileToAi(objectMapper.writeValueAsString(messageData));

//            streamAudioFiles(messageId);

        } catch (IOException e) {
            return ResponseEntity.status(500).body("Failed to read audio file.");
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            return ResponseEntity.status(500).body("Failed to process audio file.");
        }

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("callId", System.currentTimeMillis()));

    }

    @Async
    public void sendAudioFileToAi(String messageData) throws Exception{
        messageProducer.sendMessage("ml-topic", messageData);
    }

    @Async
    public void streamAudioFiles(String messageId) throws Exception {

        String[] audioFiles = {
                "audio/audio1.mp3",
                "audio/audio2.mp3",
                "audio/audio3.mp3"
        };

        ObjectMapper objectMapper = new ObjectMapper();

        for (String audioFile : audioFiles) {
            List<String> chunks = AudioChunkUtil.chunkAudioFile(audioFile, 1024 * 4); // 4KB chunks

            for (String chunk : chunks) {
                Map<String, Object> messageData = Map.of(
                        "audioData", chunk,
                        "messageId", "messageId",
                        "requestMessageType", "audio",
                        "sender", "System",
                        "type", "audio",
                        "callId", CALL_ID,
                        "timestamp", System.currentTimeMillis()
                );

//                Map<String, Object> messageData = Map.of(
//                        "content", chunk,
//                        "request_id", messageId,
//                        "request_type", "audio",
//                        "user_id", CALL_ID
//                );

                System.out.println("Sending message to callId: " + CALL_ID);

                messagingTemplate.convertAndSend(String.format("/topic/call-%s",CALL_ID), messageData);

//                messageProducer.sendMessage("ml-topic", objectMapper.writeValueAsString(messageData));

                Thread.sleep(500); //Stream
            }

            Thread.sleep(1000); //Pause
        }
    }

    @RequestMapping(value = "/end", method = RequestMethod.POST)
    private ResponseEntity<?> stopCall() throws Exception {

        System.out.println("Stopping call with ID: " + CALL_ID);

        // Logic to stop the call

        return ResponseEntity.status(HttpStatus.OK).body(Map.of("callId", CALL_ID));

    }


}
