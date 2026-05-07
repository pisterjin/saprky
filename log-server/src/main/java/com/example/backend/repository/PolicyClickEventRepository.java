package com.example.backend.repository;

import com.example.backend.entity.PolicyClickEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDateTime;
import java.util.List;

public interface PolicyClickEventRepository extends JpaRepository<PolicyClickEvent, Long> {

    List<PolicyClickEvent> findBySessionId(String sessionId);

    @Modifying
    @Query("DELETE FROM PolicyClickEvent p WHERE p.clickedAt < :before")
    int deleteByClickedAtBefore(@Param("before") LocalDateTime before);

    @Query("""
        SELECT pce.policyId, COUNT(pce) AS clicks
        FROM PolicyClickEvent pce
        GROUP BY pce.policyId
        ORDER BY clicks DESC
    """)
    List<Object[]> findClickCountByPolicy();

    @Query(value = """
        SELECT pce.policy_id, MAX(pce.policy_title) AS policy_title, pce.category, COUNT(*) AS clicks
        FROM policy_click_events pce
        WHERE pce.clicked_at >= :from
        GROUP BY pce.policy_id, pce.category
        ORDER BY clicks DESC
        LIMIT 10
    """, nativeQuery = true)
    List<Object[]> topClickedPolicies(@Param("from") LocalDateTime from);
}
