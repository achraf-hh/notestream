package com.notestream.notestream_api.domain.repository;

import com.notestream.notestream_api.domain.model.Question;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface QuestionRepository extends JpaRepository<Question, Long> {
    List<Question> findByCourseIdOrderByAskedAtDesc(Long courseId);
}