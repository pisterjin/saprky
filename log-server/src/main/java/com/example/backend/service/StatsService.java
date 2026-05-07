package com.example.backend.service;

import com.example.backend.repository.ChatLogRepository;
import com.example.backend.repository.PolicyClickEventRepository;
import com.example.backend.repository.SessionMetaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class StatsService {

    private final ChatLogRepository chatLogRepo;
    private final SessionMetaRepository sessionMetaRepo;
    private final PolicyClickEventRepository clickRepo;

    private static final int DAYS_30 = 30;
    private static final int DAYS_7  = 7;

    public Map<String, Object> overview() {
        LocalDateTime from = LocalDateTime.now().minusDays(DAYS_7);
        LocalDateTime to   = LocalDateTime.now();

        long sessions   = Optional.ofNullable(chatLogRepo.countDistinctSessions(from, to)).orElse(0L);
        long questions  = Optional.ofNullable(chatLogRepo.countTurns(from, to)).orElse(0L);
        double avgMs    = Optional.ofNullable(chatLogRepo.avgResponseMs(from, to)).orElse(0.0);
        long masking    = Optional.ofNullable(chatLogRepo.countMaskingHits(from, to)).orElse(0L);
        long clarifying = Optional.ofNullable(chatLogRepo.countClarifying(from, to)).orElse(0L);
        double clarifyingPct = questions > 0 ? Math.round(clarifying * 1000.0 / questions) / 10.0 : 0.0;

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("sessions",       sessions);
        result.put("questions",      questions);
        result.put("avgResponseMs",  Math.round(avgMs));
        result.put("maskingHits",    masking);
        result.put("clarifyingPct",  clarifyingPct);
        result.put("periodDays",     DAYS_7);
        return result;
    }

    public List<Map<String, Object>> daily() {
        LocalDateTime from = LocalDateTime.now().minusDays(DAYS_30);
        List<Object[]> rows = chatLogRepo.dailyStats(from);
        List<Map<String, Object>> result = new ArrayList<>();
        for (Object[] r : rows) {
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("date",       r[0] != null ? r[0].toString() : null);
            row.put("sessions",   toLong(r[1]));
            row.put("questions",  toLong(r[2]));
            row.put("avgMs",      toLong(r[3]));
            row.put("clarifying", toLong(r[4]));
            result.add(row);
        }
        return result;
    }

    public List<Map<String, Object>> domain() {
        LocalDateTime from = LocalDateTime.now().minusDays(DAYS_30);
        List<Object[]> rows = chatLogRepo.domainDistribution(from);
        long total = rows.stream().mapToLong(r -> toLong(r[1])).sum();
        List<Map<String, Object>> result = new ArrayList<>();
        for (Object[] r : rows) {
            long cnt = toLong(r[1]);
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("domain", r[0]);
            row.put("count",  cnt);
            row.put("pct",    total > 0 ? Math.round(cnt * 1000.0 / total) / 10.0 : 0.0);
            result.add(row);
        }
        return result;
    }

    public Map<String, List<Map<String, Object>>> profile() {
        LocalDateTime from = LocalDateTime.now().minusDays(DAYS_30);
        Map<String, List<Map<String, Object>>> result = new LinkedHashMap<>();
        result.put("age",    toLabelCount(sessionMetaRepo.ageGroupDistribution(from)));
        result.put("gender", toLabelCount(sessionMetaRepo.genderDistribution(from)));
        result.put("region", toLabelCount(sessionMetaRepo.regionDistribution(from)));
        return result;
    }

    public List<Map<String, Object>> topPolicies() {
        LocalDateTime from = LocalDateTime.now().minusDays(DAYS_30);
        List<Object[]> rows = clickRepo.topClickedPolicies(from);
        long total = rows.stream().mapToLong(r -> toLong(r[3])).sum();
        List<Map<String, Object>> result = new ArrayList<>();
        for (Object[] r : rows) {
            long clicks = toLong(r[3]);
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("policyId", r[0]);
            row.put("title",    r[1] != null ? r[1] : r[0]);
            row.put("category", r[2]);
            row.put("clicks",   clicks);
            row.put("pct",      total > 0 ? Math.round(clicks * 1000.0 / total) / 10.0 : 0.0);
            result.add(row);
        }
        return result;
    }

    public List<Map<String, Object>> clarifying() {
        LocalDateTime from = LocalDateTime.now().minusDays(DAYS_30);
        List<Object[]> rows = chatLogRepo.clarifyingByDomain(from);
        List<Map<String, Object>> result = new ArrayList<>();
        for (Object[] r : rows) {
            long total = toLong(r[1]);
            long clar  = toLong(r[2]);
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("domain",      r[0]);
            row.put("total",       total);
            row.put("clarifying",  clar);
            row.put("pct",         total > 0 ? Math.round(clar * 1000.0 / total) / 10.0 : 0.0);
            result.add(row);
        }
        return result;
    }

    private List<Map<String, Object>> toLabelCount(List<Object[]> rows) {
        long total = rows.stream().mapToLong(r -> toLong(r[1])).sum();
        List<Map<String, Object>> list = new ArrayList<>();
        for (Object[] r : rows) {
            long cnt = toLong(r[1]);
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("label", r[0]);
            m.put("count", cnt);
            m.put("pct",   total > 0 ? Math.round(cnt * 1000.0 / total) / 10.0 : 0.0);
            list.add(m);
        }
        return list;
    }

    private long toLong(Object o) {
        if (o == null) return 0L;
        if (o instanceof Number) return ((Number) o).longValue();
        try { return Long.parseLong(o.toString()); } catch (Exception e) { return 0L; }
    }
}
