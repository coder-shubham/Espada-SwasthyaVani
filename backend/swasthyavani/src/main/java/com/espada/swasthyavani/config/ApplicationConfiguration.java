/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

import lombok.Data;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */

@Configuration
@Data
public class ApplicationConfiguration {

    @Value("${swasthyavani.producer.topic}")
    private String producerTopic;

    @Value("${swasthyavani.consumer.topic}")
    private String consumerTopic;

}
