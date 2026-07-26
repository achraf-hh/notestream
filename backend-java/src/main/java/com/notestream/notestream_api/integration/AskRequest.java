package com.notestream.notestream_api.integration;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record AskRequest(
        String question,
        @JsonProperty("contextChunks") List<String> contextChunks
) {}
