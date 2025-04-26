/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.utils;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
public class AudioChunkUtil {

    public static List<String> chunkAudioFile(String filePath, int chunkSize) throws Exception {
        List<String> chunks = new ArrayList<>();
        try (InputStream is = AudioChunkUtil.class.getClassLoader().getResourceAsStream(filePath)) {
            if (is == null) throw new IllegalArgumentException("File not found: " + filePath);

            byte[] buffer = new byte[chunkSize];
            int bytesRead;

            while ((bytesRead = is.read(buffer)) != -1) {
                byte[] actual = new byte[bytesRead];
                System.arraycopy(buffer, 0, actual, 0, bytesRead);
                String base64Chunk = Base64.getEncoder().encodeToString(actual);
                chunks.add(base64Chunk);
            }
        }
        return chunks;
    }

}
