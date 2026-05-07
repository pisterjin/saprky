package com.example.backend.repository;

import com.example.backend.entity.LogPolicy;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.util.List;

public interface LogPolicyRepository extends JpaRepository<LogPolicy, Long> {

    List<LogPolicy> findByChatLog_Id(Long chatLogId);

    @Query("""
        SELECT lp.policyId, lp.policyTitle, lp.category, COUNT(lp) AS impressions
        FROM LogPolicy lp
        GROUP BY lp.policyId, lp.policyTitle, lp.category
        ORDER BY impressions DESC
    """)
    List<Object[]> findTopPolicies(@Param("limit") int limit);
}
