package com.notestream.notestream_api.api.dto;

import jakarta.validation.constraints.NotBlank;

public record AskQuestionRequest(@NotBlank String question) {}
