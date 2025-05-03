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
 * Created by shubhamsarraf on 03/05/25
 */

@Data
@NoArgsConstructor
@Accessors(chain = true)
public class PatientHistory {

    private String patientId;
    private String summary;
    private String specialist;

}
