package com.example.backend.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class PolicyItemDto {
    private String policyId;
    private String title;
    private String category;
    private String source;
    private Integer rankPos;
}
