package com.notestream.notestream_api.api;

import com.notestream.notestream_api.api.dto.AskQuestionRequest;
import com.notestream.notestream_api.api.dto.QuestionResponse;
import com.notestream.notestream_api.service.QuestionAnsweringService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/courses/{courseId}/questions")
public class QuestionController {

    private final QuestionAnsweringService questionAnsweringService;

    public QuestionController(QuestionAnsweringService questionAnsweringService) {
        this.questionAnsweringService = questionAnsweringService;
    }

    @PostMapping
    public ResponseEntity<QuestionResponse> askQuestion(
            @PathVariable Long courseId,
            @Valid @RequestBody AskQuestionRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(questionAnsweringService.askQuestion(courseId, request.question()));
    }

    @GetMapping
    public ResponseEntity<List<QuestionResponse>> getQuestions(@PathVariable Long courseId) {
        return ResponseEntity.ok(questionAnsweringService.getQuestionsByCourse(courseId));
    }
}
