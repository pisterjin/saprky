package com.example.backend.service;

import com.example.backend.dto.ChatLogRequest;
import com.example.backend.entity.ChatLog;
import com.example.backend.entity.SessionMeta;
import com.example.backend.repository.ChatLogRepository;
import com.example.backend.repository.SessionMetaRepository;
import com.example.backend.util.MaskingUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.ZoneOffset;

@Service
@RequiredArgsConstructor
public class ChatLogService {

    private final ChatLogRepository chatLogRepo;
    private final SessionMetaRepository sessionMetaRepo;

    @Async
    @Transactional
    public void save(ChatLogRequest req) {
        LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
        String sessionId = req.getUuid();

        ChatLogRequest.UserProfileDto profile = req.getUserProfile();
        String ageGroup = profile != null ? profile.getAgeGroup() : null;
        String gender   = profile != null ? profile.getGender()   : null;
        String region   = profile != null ? profile.getRegion()   : null;

        chatLogRepo.save(ChatLog.builder()
                .sessionId(sessionId)
                .turnNo(req.getTurnNo() != null ? req.getTurnNo() : 1)
                .ageGroup(ageGroup)
                .gender(gender)
                .region(region)
                .question(MaskingUtil.maskText(req.getQuestion()))
                .answer(MaskingUtil.maskText(req.getAnswer()))
                .domain(req.getDomain())
                .isClarifying(req.getIsClarifying())
                .responseTimeMs(req.getResponseTimeMs())
                .build());

        sessionMetaRepo.findById(sessionId).ifPresentOrElse(
                meta -> meta.onTurn(req.getDomain(), now),
                () -> {
                    SessionMeta meta = SessionMeta.builder()
                            .sessionId(sessionId)
                            .startedAt(now)
                            .ageGroup(ageGroup)
                            .gender(gender)
                            .region(region)
                            .build();
                    meta.onTurn(req.getDomain(), now);
                    sessionMetaRepo.save(meta);
                }
        );
    }
}
