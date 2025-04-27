/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.model;

import lombok.Data;
import lombok.Getter;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */

@Getter
public enum LanguageCode {

    ENGLISH("1", "en"),
    HINDI("2", "hi"),
    MARATHI("3", "mr"),
    TELUGU("4", "te");

    private final String code;

    private final String language;

    LanguageCode(String code, String language) {
        this.code = code;
        this.language = language;
    }

    public static LanguageCode fromCode(String code) {
        for (LanguageCode languageCode : LanguageCode.values()) {
            if (languageCode.getCode().equalsIgnoreCase(code)) {
                return languageCode;
            }
        }
        return ENGLISH;
    }


}
