package com.example.backend.repository;

import com.example.backend.entity.SessionMeta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import java.time.LocalDateTime;
import java.util.List;

public interface SessionMetaRepository extends JpaRepository<SessionMeta, String> {

    @Query(value = """
        SELECT COALESCE(age_group, 'unknown') AS grp, COUNT(*) AS cnt
        FROM session_meta WHERE started_at >= :from
        GROUP BY age_group ORDER BY cnt DESC
    """, nativeQuery = true)
    List<Object[]> ageGroupDistribution(@Param("from") LocalDateTime from);

    @Query(value = """
        SELECT COALESCE(gender, 'unknown') AS grp, COUNT(*) AS cnt
        FROM session_meta WHERE started_at >= :from
        GROUP BY gender ORDER BY cnt DESC
    """, nativeQuery = true)
    List<Object[]> genderDistribution(@Param("from") LocalDateTime from);

    @Query(value = """
        SELECT COALESCE(region, 'unknown') AS grp, COUNT(*) AS cnt
        FROM session_meta WHERE started_at >= :from
        GROUP BY region ORDER BY cnt DESC
    """, nativeQuery = true)
    List<Object[]> regionDistribution(@Param("from") LocalDateTime from);
}
