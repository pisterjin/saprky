package com.example.backend.dto;

import lombok.Builder;
import lombok.Getter;
import java.util.List;
import java.util.Map;

@Getter
@Builder
public class StatsResponse {

    private Long totalSessions;
    private Long totalTurns;
    private Double avgResponseMs;
    private Long maskingHits;

    private List<Map<String, Object>> rows;

    public static StatsResponse ofRows(List<Map<String, Object>> rows) {
        return StatsResponse.builder().rows(rows).build();
    }

    public static StatsResponse ofOverview(Long sessions, Long turns, Double avgMs, Long maskings) {
        return StatsResponse.builder()
                .totalSessions(sessions)
                .totalTurns(turns)
                .avgResponseMs(avgMs)
                .maskingHits(maskings)
                .build();
    }
}
