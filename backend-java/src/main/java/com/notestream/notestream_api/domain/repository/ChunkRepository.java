package com.notestream.notestream_api.domain.repository;

import com.notestream.notestream_api.domain.model.Chunk;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChunkRepository extends JpaRepository<Chunk, Long> {

    List<Chunk> findByDocumentId(Long documentId);

    // Vector similarity search using pgvector cosine distance
    @Query(value = """
        SELECT c.* FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE d.course_id = :courseId
        ORDER BY c.embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
        """, nativeQuery = true)
    List<Chunk> findSimilarChunks(
        @Param("courseId") Long courseId,
        @Param("embedding") String embedding,
        @Param("limit") int limit
    );
}