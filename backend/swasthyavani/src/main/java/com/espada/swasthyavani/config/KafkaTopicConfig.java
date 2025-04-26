/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.config;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.kafka.core.KafkaAdmin;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
//@Configuration
public class KafkaTopicConfig {

//    @Value("${spring.kafka.bootstrap-servers}")
//    private String bootStrapServers;
//
//    @Bean
//    public NewTopic createTopic() {
//        return TopicBuilder.name("backend-topic")
//                .partitions(10)
//                .replicas(1)
//                .build();
//    }
//
//    @Bean
//    public KafkaAdmin kafkaAdmin() {
//        Map<String, Object> configs = new HashMap<>();
//        configs.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, bootStrapServers);
//        return new KafkaAdmin(configs);
//    }

}
