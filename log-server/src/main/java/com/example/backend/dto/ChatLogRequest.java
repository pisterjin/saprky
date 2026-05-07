package com.example.backend.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import java.util.List;

@Getter
@Setter
public class ChatLogRequest {

    @NotBlank @Size(max = 64)
    private String uuid;
    private Integer turnNo;

    @NotBlank @Size(max = 2000)
    private String question;

    @Size(max = 10000)
    private String answer;

    @Size(max = 50)
    private String domain;

    private List<@Size(max = 64) String> policyIds;
    private Boolean isClarifying;
    private Integer responseTimeMs;

    @Valid
    private UserProfileDto userProfile;

    @Getter
    @Setter
    public static class UserProfileDto {
        @Size(max = 32) private String ageGroup;
        @Size(max = 16) private String gender;
        @Size(max = 32) private String region;
        @Size(max = 64) private String uuid;
    }
}
