package com.example.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
public class ClickEventRequest {

    @NotBlank @Size(max = 64)
    @JsonProperty("session_id")
    private String sessionId;

    @NotBlank @Size(max = 64)
    @JsonProperty("policy_id")
    private String policyId;

    @Size(max = 200)
    @JsonProperty("policy_title")
    private String policyTitle;

    @Size(max = 50)
    private String category;

    @JsonProperty("clicked_at")
    private LocalDateTime clickedAt;
}
