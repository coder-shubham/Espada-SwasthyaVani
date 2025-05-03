/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.model;

import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */


@Data
@NoArgsConstructor
@Accessors(chain = true)
public class KafkaMessagePayload {


    private String content;

    @JsonProperty("request_type")
    private String requestType;

    @JsonProperty("user_id")
    private String callId;

    @JsonProperty("request_id")
    private String messageId;

    private String specialization;
    private String summary;

    private String language;
    private String type;
    private String sender;
    private Object timestamp;
    @JsonProperty("isFinished")
    private Boolean isFinished;
    private transient long lastUpdateTime;
    private PatientHistory patientHistory;

    public KafkaMessagePayload(String content, String requestType, String callId, String messageId,
                               String language, String type,
                               String sender, Object timestamp,String summary,
                               Boolean isFinished, String specialization, PatientHistory patientHistory) {
        this.content = content;
        this.requestType = requestType;
        this.callId = callId;
        this.messageId = messageId;
        this.language = language;
        this.type = type;
        this.sender = sender;
        this.timestamp = timestamp;
        this.isFinished = isFinished;
        this.summary = summary;
        this.specialization = specialization;
        this.patientHistory = patientHistory;
    }

    public long getTimestampInLong() {

        if (timestamp instanceof String) {
            return Long.parseLong((String) timestamp);
        } else if (timestamp instanceof Number) {
            return ((Number) timestamp).longValue();
        } else {
            return System.currentTimeMillis();
        }


    }

}
