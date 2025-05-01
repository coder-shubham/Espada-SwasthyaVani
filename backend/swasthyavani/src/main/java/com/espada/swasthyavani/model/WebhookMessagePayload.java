/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.model;

import lombok.Data;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.experimental.Accessors;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */

@Data
@NoArgsConstructor
@Accessors(chain = true)
public class WebhookMessagePayload {

    private String content;
    private String requestMessageType;
    private String callId;
    private String chatId;
    private String messageId;
    private String type;
    private String sender;
    private long timestamp;


    @Getter
    public enum RequestType{
        DTMF("dtmf-request"),
        AUDIO("audio"),
        TEXT("text");

        private final String value;

        RequestType(String value) {
            this.value = value;
        }
    }

    @Getter
    public enum SenderType {
        SYSTEM("system"),
        AI("ai"),
        USER("user");
        private final String value;

        SenderType(String value) {
            this.value = value;
        }

        public static SenderType fromValue(String value) {
            for (SenderType senderType : SenderType.values()) {
                if (senderType.getValue().equalsIgnoreCase(value)) {
                    return senderType;
                }
            }
            throw new IllegalArgumentException("Unknown value: " + value);
        }
    }

}
