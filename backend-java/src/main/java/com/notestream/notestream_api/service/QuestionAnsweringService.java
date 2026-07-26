package com.notestream.notestream_api.service;

import com.notestream.notestream_api.api.dto.QuestionResponse;
import com.notestream.notestream_api.domain.model.Answer;
import com.notestream.notestream_api.domain.model.Chunk;
import com.notestream.notestream_api.domain.model.Course;
import com.notestream.notestream_api.domain.model.Question;
import com.notestream.notestream_api.domain.repository.AnswerRepository;
import com.notestream.notestream_api.domain.repository.ChunkRepository;
import com.notestream.notestream_api.domain.repository.CourseRepository;
import com.notestream.notestream_api.domain.repository.QuestionRepository;
import com.notestream.notestream_api.integration.AiClient;
import com.notestream.notestream_api.integration.AskResponse;
import jakarta.persistence.EntityNotFoundException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Service
public class QuestionAnsweringService {

    private final CourseRepository courseRepository;
    private final QuestionRepository questionRepository;
    private final AnswerRepository answerRepository;
    private final ChunkRepository chunkRepository;
    private final AiClient aiClient;
    private final int retrievalLimit;

    public QuestionAnsweringService(
            CourseRepository courseRepository,
            QuestionRepository questionRepository,
            AnswerRepository answerRepository,
            ChunkRepository chunkRepository,
            AiClient aiClient,
            @Value("${rag.retrieval-limit:5}") int retrievalLimit) {
        this.courseRepository = courseRepository;
        this.questionRepository = questionRepository;
        this.answerRepository = answerRepository;
        this.chunkRepository = chunkRepository;
        this.aiClient = aiClient;
        this.retrievalLimit = retrievalLimit;
    }

    @Transactional
    public QuestionResponse askQuestion(Long courseId, String rawQuestion) {
        String questionText = rawQuestion.trim();
        Course course = courseRepository.findById(courseId)
                .orElseThrow(() -> new EntityNotFoundException("Course not found: " + courseId));

        Question question = questionRepository.save(new Question(questionText, course));
        List<Chunk> retrievedChunks = retrieveRelevantChunks(courseId, questionText);

        Answer answer;
        if (retrievedChunks.isEmpty()) {
            answer = answerRepository.save(new Answer(
                    "I couldn't find any indexed course material for this course yet.",
                    question,
                    List.of()
            ));
        } else {
            AskResponse aiResponse = aiClient.ask(
                    questionText,
                    retrievedChunks.stream().map(Chunk::getContent).toList()
            );

            answer = answerRepository.save(new Answer(
                    aiResponse.answer(),
                    question,
                    mapCitations(aiResponse.citations(), retrievedChunks)
            ));
        }

        question.setAnswer(answer);
        return QuestionResponse.from(question);
    }

    @Transactional(readOnly = true)
    public List<QuestionResponse> getQuestionsByCourse(Long courseId) {
        if (!courseRepository.existsById(courseId)) {
            throw new EntityNotFoundException("Course not found: " + courseId);
        }

        return questionRepository.findByCourseIdOrderByAskedAtDesc(courseId).stream()
                .map(QuestionResponse::from)
                .toList();
    }

    private List<Chunk> retrieveRelevantChunks(Long courseId, String questionText) {
        List<float[]> embeddings = aiClient.embed(List.of(questionText));
        if (embeddings.isEmpty()) {
            throw new IllegalStateException("AI service returned no embedding for the question");
        }

        return chunkRepository.findSimilarChunks(
                courseId,
                Arrays.toString(embeddings.get(0)),
                retrievalLimit
        );
    }

    private List<Chunk> mapCitations(List<Integer> citationIndices, List<Chunk> retrievedChunks) {
        if (citationIndices == null || citationIndices.isEmpty()) {
            return List.of();
        }

        Set<Integer> validIndices = new LinkedHashSet<>();
        for (Integer citationIndex : citationIndices) {
            if (citationIndex != null && citationIndex >= 0 && citationIndex < retrievedChunks.size()) {
                validIndices.add(citationIndex);
            }
        }

        return validIndices.stream()
                .map(retrievedChunks::get)
                .toList();
    }
}
