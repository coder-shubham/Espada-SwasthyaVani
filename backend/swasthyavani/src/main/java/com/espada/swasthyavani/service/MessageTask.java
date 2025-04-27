/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.service;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;

import com.espada.swasthyavani.model.KafkaMessagePayload;
import com.espada.swasthyavani.model.WebhookMessagePayload;
import com.espada.swasthyavani.model.WebhookMessagePayload.SenderType;


/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */
public class MessageTask implements Runnable{

    @Autowired
    public SimpMessagingTemplate messagingTemplate;

    private KafkaMessagePayload kafkaMessagePayload;

    private static final ConcurrentHashMap<String, ReentrantLock> locks = new ConcurrentHashMap<>();

    public MessageTask(){
    }

    public MessageTask(KafkaMessagePayload kafkaMessagePayload){
        this.kafkaMessagePayload = kafkaMessagePayload;
    }

    @Override public void run() {

        ReentrantLock lock = null;

        try {

            String callId = kafkaMessagePayload.getCallId();

            lock = locks.computeIfAbsent(callId, id -> new ReentrantLock());
            lock.lock();

            System.out.println("Processing message for callID/chatId: " + callId);


            WebhookMessagePayload webhookMessagePayload = new WebhookMessagePayload()
                    .setMessageId(kafkaMessagePayload.getMessageId())
                    .setCallId(callId)
                    .setChatId(callId)
                    .setContent(kafkaMessagePayload.getContent())
                    .setRequestMessageType(kafkaMessagePayload.getRequestType())
                    .setType(kafkaMessagePayload.getRequestType())
                    .setSender(SenderType.fromValue(kafkaMessagePayload.getSender().toLowerCase()).getValue())
                    .setTimestamp(kafkaMessagePayload.getTimestampInLong());


            System.out.println("Sending to callId/chatId: " + callId);

            if(webhookMessagePayload.getRequestMessageType().equals(WebhookMessagePayload.RequestType.AUDIO.getValue())
            || webhookMessagePayload.getRequestMessageType().equals(WebhookMessagePayload.RequestType.DTMF.getValue())){

                messagingTemplate.convertAndSend(String.format("/topic/call-%s",callId), webhookMessagePayload);

            }else{

                messagingTemplate.convertAndSend(String.format("/topic/chat-%s",callId), webhookMessagePayload);
            }



            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt(); // Restore the interrupted status
        } catch (Exception ex){
            System.out.println("Exception in MessageTask: " + ex.getMessage());
        } finally {
            if (lock != null) {
                lock.unlock();
            }
            locks.remove(kafkaMessagePayload.getCallId(), lock);
        }

    }
}
