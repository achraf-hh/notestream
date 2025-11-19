package com.notestream.notestream_api.domain.repository;

import com.notestream.notestream_api.domain.model.Document;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DocumentRepository extends JpaRepository<Document, Long> {
    List<Document> findByCourseId(Long courseId);
}