package com.notestream.notestream_api.api.dto;

import com.notestream.notestream_api.domain.model.Answer;
import com.notestream.notestream_api.domain.model.Chunk;
import com.notestream.notestream_api.domain.model.Question;

import java.time.LocalDateTime;
import java.util.List;

public record QuestionResponse(
        Long id,
        String question,
        String answer,
        LocalDateTime askedAt,
        LocalDateTime generatedAt,
        List<CitationResponse> citations
) {
    public static QuestionResponse from(Question question) {
        Answer answer = question.getAnswer();

        return new QuestionResponse(
                question.getId(),
                question.getText(),
                answer != null ? answer.getText() : null,
                question.getAskedAt(),
                answer != null ? answer.getGeneratedAt() : null,
                answer != null
                        ? answer.getCitations().stream().map(CitationResponse::from).toList()
                        : List.of()
        );
    }

    public record CitationResponse(
            Long chunkId,
            Integer chunkIndex,
            Long documentId,
            String documentFilename,
            String excerpt
    ) {
        public static CitationResponse from(Chunk chunk) {
            return new CitationResponse(
                    chunk.getId(),
                    chunk.getChunkIndex(),
                    chunk.getDocument().getId(),
                    chunk.getDocument().getFilename(),
                    chunk.getContent()
            );
        }
    }
}
