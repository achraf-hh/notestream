package com.notestream.notestream_api.integration;

import java.util.List;

public record AskRequest(
        String question,
        List<String> contextChunks
) {}
