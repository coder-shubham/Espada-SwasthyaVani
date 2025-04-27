/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.model;

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
public class UserInfo {

    private String userId;
    private String language;

}
